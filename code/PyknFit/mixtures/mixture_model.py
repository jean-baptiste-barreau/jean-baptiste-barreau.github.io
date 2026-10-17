import math
import numpy as np

from tkinter import messagebox
from scipy.optimize import minimize, least_squares
from pyknfit.distributions import DISTRIBUTIONS
from pyknfit.distributions.gaussian import Gaussian
from pyknfit.distributions.lognormal import LogNormal
from pyknfit.distributions.weibull import Weibull

class Parameter:

    def __init__(self, value):
        self.value = value


class MixtureModel:

    def __init__(self, app, distributions):

        self.app = app

        self.distributions = distributions

        self._params = []

        self.params_gui = {}

        self.components = []

        self.last_fit = None

    # ==========================================================
    # Compatibilité GUI/lmfit
    # ==========================================================

    @property
    def params(self):
        return self.params_gui

    # ==========================================================
    # Lecture des données GUI
    # ==========================================================

    def calcul_resultats(self):

        listeX = (
            self.app.m_textX
            .get("1.0", "end")
            .strip()
            .replace(",", ".")
        )

        listeY = (
            self.app.m_textY
            .get("1.0", "end")
            .strip()
            .replace(",", ".")
        )

        self.app.m_titre_graphique = (
            self.app.m_titre_entry.get()
        )

        try:

            self.app.m_chiffresX_µ = [
                float(x)
                for x in listeX.splitlines()
            ]

            self.app.m_chiffresY_µ = [
                float(y)
                for y in listeY.splitlines()
            ]

            # conversion µm -> phi
            if self.app.uniteX.get() == "µ":

                self.app.m_chiffresX_phi = [

                    -math.log10(x / 1000)
                    / math.log10(2)

                    if x != 0 else 0

                    for x in self.app.m_chiffresX_µ
                ]

            else:

                self.app.m_chiffresX_phi = (
                    self.app.m_chiffresX_µ
                )

                self.app.m_chiffresY_phi = (
                    self.app.m_chiffresY_µ
                )

        except ValueError:

            messagebox.showerror(
                self.app.t("error"),
                self.app.t("invalid_data")
            )

            return

        if len(self.app.m_init_centers_selected) >= 1:
            self.fit_gui_model()

    # ==========================================================
    # Évaluation du modèle
    # ==========================================================

    def evaluate(self, x):

        total = np.zeros_like(x, dtype=float)

        for dist, params in zip(
            self.distributions,
            self._params
        ):

            amp = params["amplitude"]

            total += (
                amp
                * dist.pdf(x, params)
            )

        return total

    def eval(self, x):

        return self.evaluate(x)

    # ==========================================================
    # Évaluation composantes
    # ==========================================================

    def eval_components(self, x):

        out = {}

        for i, (dist, params) in enumerate(
            zip(
                self.distributions,
                self._params
            ),
            start=1
        ):

            amp = params["amplitude"]

            out[f"g{i}_"] = amp * dist.pdf(x, params)

        return out

    # ==========================================================
    # Optimisation
    # ==========================================================
    def fit(self, x, y):
        n = len(self.app.m_init_centers_selected)

        # Reconstruire les distributions selon le type choisi
        dist_type = getattr(self.app, 'current_distribution_type', 'Gaussienne')
        cls = DISTRIBUTIONS.get(dist_type, Gaussian)
        self.distributions = [cls() for _ in range(n)]

        self._params = []
        keys = list(self.app.m_annotations.keys())

        for i in range(n):
            center_val = self.app.m_init_centers_selected[i]

            from pyknfit.distributions.weibull import Weibull
            from pyknfit.distributions.lognormal import LogNormal

            if isinstance(self.distributions[i], (Weibull, LogNormal)):
                center_val = 1000 * (2 ** (-center_val))
                
            annotation = self.app.m_annotations[keys[i]].get_text()
            
            sigma = 1.0
            amplitude = 1.0
            
            for line in annotation.split("\n"):
                if line.startswith("σ="):
                    sigma = float(line.split("=")[1])
                elif line.startswith("A="):
                    amplitude = float(line.split("=")[1])
            
            sigma = max(sigma, self.app.m_min_sigma)
            
            # Initialisation spécifique à la distribution
            dist = self.distributions[i]
            self._params.append(
                dist.create_initial_params(
                    center=center_val,
                    sigma=sigma,
                    amplitude=amplitude
                )
            )
        
        # Préparation des paramètres initiaux pour l'optimisation
        initial = []
        for dist, p in zip(
            self.distributions,
            self._params
        ):
            initial.extend(
                dist.pack_theta(p)
            )
        
        # Fonction de coût
        def objective(theta):
            idx = 0
            params = []

            for dist in self.distributions:
                n = len(dist.bounds())
                theta_slice = theta[idx:idx+n]
                params.append(
                    dist.unpack_theta(theta_slice)
                )
                idx += n
            
            y_pred = np.zeros_like(x)
            for dist, p in zip(self.distributions, params):
                y_pred += p["amplitude"] * dist.pdf(x, p)
            
            weights = 1.0 / (y + 0.05)
            return np.mean(
                weights * (y - y_pred) ** 2
            )
        
        # Optimisation
        bounds = []
        for dist in self.distributions:
            bounds.extend(
                dist.bounds()
            )

        result = minimize(
            objective,
            initial,
            method='L-BFGS-B',
            bounds=bounds
        )
        theta = result.x
        
        # Reconstruction des paramètres
        self._params = []
        idx = 0
        params = []

        for dist in self.distributions:

            n = len(dist.bounds())

            theta_slice = theta[idx:idx+n]

            params.append(
                dist.unpack_theta(theta_slice)
            )

            idx += n
        
        self._params = params
        
        # Compatibilité GUI
        self.params_gui = {}
        for i, (dist, p) in enumerate(
            zip(self.distributions, self._params),
            start=1
        ):

            self.params_gui[f"g{i}_center"] = Parameter(
                dist.gui_center_value(p)
            )

            self.params_gui[f"g{i}_sigma"] = Parameter(
                dist.gui_width_value(p)
            )

            self.params_gui[f"g{i}_amplitude"] = Parameter(
                p["amplitude"]
            )

    # ==========================================================
    # Interface GUI
    # ==========================================================

    def fit_gui_model(self):
        distribution_type = self.app.distribution_type.get()
        if distribution_type in ["Log-normale", "Weibull"]:
            x = np.array(self.app.m_chiffresX_µ)
        else:
            x = np.array(self.app.m_chiffresX_phi)
            
        y = np.array(self.app.m_chiffresY_μ)  # ← changement ici : u → μ
        n = len(self.app.m_init_centers_selected)

        # Récupérer la valeur du Combobox au moment du calcul
        self.app.current_distribution_type = self.app.distribution_type.get()
        distribution_type = self.app.current_distribution_type
        
        # Créer les distributions selon le type choisi
        dist_class = DISTRIBUTIONS[distribution_type]
        self.distributions = [
            dist_class()
            for _ in range(n)
        ]

        # Indicateur simple
        self.app.progress.config(mode='indeterminate')
        self.app.progress.start(10)
        self.app.root.update_idletasks()

        # Calcul
        self.fit(x, y)

        # Fin de l'indicateur
        self.app.progress.stop()
        self.app.progress.config(mode='determinate')
        self.app.progress["value"] = 100

        # Suite normale...
        self.app.m_fig1_X = x
            
        self.app.m_fig1_Y = y
        self.app.m_model = self
        self.app.m_model_params = self._params
        best_fit_y = self.eval(x)
        self.app.m_last_error_metrics = self.calculer_erreurs(y, best_fit_y, x)
        self.sauvegarder_resultats()

    # ==========================================================
    # Proportions
    # ==========================================================

    def calculer_aires_et_proportions(self):
        """Calcule les aires et proportions de chaque composante"""
        import numpy as np
        
        areas = []
        total = 0
        
        # Créer un axe x dense pour l'intégration numérique
        distribution_type = getattr(
            self.app,
            "current_distribution_type",
            "Gaussienne"
        )

        if hasattr(self.app, 'm_fig1_X') and self.app.m_fig1_X is not None:
            xmin = min(self.app.m_fig1_X)
            xmax = max(self.app.m_fig1_X)

            use_log_scale = (
                len(self.app.m_model.distributions) > 0
                and self.app.m_model.distributions[0].use_log_scale
            )
            
            if use_log_scale:
                x_dense = np.geomspace(
                    max(xmin, 1e-6),
                    xmax,
                    5000
                )
            else:
                x_dense = np.linspace(
                    xmin,
                    xmax,
                    5000
                )
        else:
            x_dense = np.linspace(-5, 5, 5000)
        
        for i, (dist, p) in enumerate(zip(self.distributions, self._params)):
            amp = p["amplitude"]
            
            # Calcul de l'aire par intégration numérique (plus robuste)
            y_comp = amp * dist.pdf(x_dense, p)
            area = np.trapezoid(y_comp, x_dense)
            
            areas.append(area)
            total += area
        
        if total <= 0:
            return [0] * len(self.distributions)
        
        return [a / total for a in areas]

    # ==========================================================
    # Erreurs
    # ==========================================================

    def calculer_erreurs(
        self,
        y_observe,
        y_modele,
        x
    ):

        erreur_absolue = np.trapezoid(
            np.abs(y_observe - y_modele),
            x
        )

        aire_observee = np.trapezoid(
            y_observe,
            x
        )

        erreur_relative = (
            100
            * erreur_absolue
            / aire_observee
            if aire_observee != 0
            else np.nan
        )

        mse = np.mean(
            (y_observe - y_modele) ** 2
        )

        ss_tot = np.sum(
            (y_observe - np.mean(y_observe)) ** 2
        )

        ss_res = np.sum(
            (y_observe - y_modele) ** 2
        )

        r_squared = (
            1 - (ss_res / ss_tot)
            if ss_tot != 0
            else np.nan
        )

        return {
            "Erreur absolue": erreur_absolue,
            "Erreur relative (%)": erreur_relative,
            "MSE": mse,
            "R²": r_squared
        }
        
    # ==========================================================
    # Sauvegarde
    # ==========================================================
    def sauvegarder_resultats(self):
        from pyknfit.distributions.lognormal import LogNormal
        from pyknfit.distributions.weibull import Weibull
        
        """Sauvegarde les résultats de la décomposition dans m_tous_les_resultats"""
        if self._params is None or len(self._params) == 0:
            return
        
        # Calculer les proportions
        proportions = self.calculer_aires_et_proportions()
        
        # Récupérer le type de distribution
        distribution_type = getattr(self.app, 'current_distribution_type', 'Gaussienne')
        
        # Récupérer les données
        centres_microns = []
        centres_phi = []
        sigmas = []
        hauteurs = []
        
        for i, p in enumerate(self._params, start=1):
            # from pyknfit.distributions.weibull import Weibull
            dist = self.distributions[i-1]
            
            if isinstance(dist, Weibull):
                k = p['k']
                sigma = p['lambda']

                micron = sigma * ((k - 1)/k)**(1/k) if k > 1 else 0

                phi = -np.log2(micron/1000) if micron > 0 else np.nan

                if np.isfinite(micron) and micron > 0:
                    hauteur = p['amplitude'] * dist.pdf(micron, p)
                else:
                    hauteur = 0
            elif isinstance(dist, LogNormal):
                from pyknfit.distributions.lognormal import LogNormal
                
                micron = np.exp(p["mu"])
                phi = -np.log2(micron / 1000)
                sigma = p["sigma"]
                hauteur = p["amplitude"] * dist.pdf(micron, p)
            else:
                phi = p['mu']
                sigma = p['sigma']

                micron = 1000 * (2 ** (-phi))

                hauteur = p['amplitude'] / (sigma * np.sqrt(2*np.pi))
            
            centres_microns.append(micron)
            centres_phi.append(phi)
            sigmas.append(sigma)
            hauteurs.append(hauteur)
        
        # Trier par diamètre
        sorted_indices = sorted(range(len(centres_microns)), key=lambda i: centres_microns[i])
        
        # Supprimer les anciens résultats pour cet échantillon
        titre = self.app.m_titre_graphique
        self.app.m_tous_les_resultats = [
            r for r in self.app.m_tous_les_resultats 
            if r.get("Echantillon") != titre
        ]
        
        # Ajouter les nouveaux résultats avec le type de distribution
        from datetime import datetime
        for idx in sorted_indices:
            self.app.m_tous_les_resultats.append({
                "Echantillon": titre,
                "Date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "Distribution": distribution_type,  # <-- AJOUTÉ
                "Composante": idx + 1,
                "Centre (µm)": centres_microns[idx],
                "Proportion (%)": proportions[idx] * 100,  # En pourcentage
                "Centre (phi)": centres_phi[idx],
                "Amplitude": hauteurs[idx],
                "Sigma": sigmas[idx],
                **self.app.m_last_error_metrics
            })
            
    def formula_description(self):
        if len(self.distributions) == 0:
            return ""

        return self.distributions[0].formula_description()


    def derived_quantities_description(self):
        if len(self.distributions) == 0:
            return ""

        return self.distributions[0].derived_quantities_description()