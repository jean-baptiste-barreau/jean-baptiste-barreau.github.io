import math
import numpy as np
import pandas as pd
from datetime import datetime
from tkinter import messagebox
from lmfit.models import GaussianModel
import re

class ModelManager:
    def __init__(self, app):
        self.app = app

    def extract_sigma_value(self, text):
        m = re.search(r'σ\s*=\s*([\d.]+)', text)
        return float(m.group(1)) if m else None

    def extract_amplitude_value(self, text):
        for line in text.split('\n'):
            if line.strip().startswith('A='):
                try:
                    return float(line.split('=')[1])
                except:
                    return None
        return None

    def calcul_resultats(self):
        listeX = self.app.m_textX.get("1.0", "end").strip().replace(",", ".")
        listeY = self.app.m_textY.get("1.0", "end").strip().replace(",", ".")
        self.app.m_titre_graphique = self.app.m_titre_entry.get()

        try:
            self.app.m_chiffresX_µ = [float(x) for x in listeX.splitlines()]
            self.app.m_chiffresY_µ = [float(y) for y in listeY.splitlines()]
            if self.app.uniteX.get() == "µ":
                self.app.m_chiffresX_phi = [
                    -math.log10(x / 1000) / math.log10(2) if x != 0 else 0
                    for x in self.app.m_chiffresX_µ
                ]
            else:
                self.app.m_chiffresX_phi = self.app.m_chiffresX_µ
            self.app.m_chiffresY_phi = self.app.m_chiffresY_µ
        except ValueError:
            messagebox.showerror(self.app.t("error"), self.app.t("invalid_data"))
            return

        if len(self.app.m_init_centers_selected) > 1:
            self.calculer_modele()

    def create_gaussian_model(self):
        model = None
        params = None
        keys = list(self.app.m_annotations.keys())

        for i in range(1, len(self.app.m_init_centers_selected) + 1):
            gauss = GaussianModel(prefix=f'g{i}_')
            if model is None:
                model = gauss
                params = gauss.make_params()
            else:
                model += gauss
                params.update(gauss.make_params())

            center_val = self.app.m_init_centers_selected[i-1]
            sigma_val = self.extract_sigma_value(self.app.m_annotations[keys[i-1]].get_text())
            amp_val = self.extract_amplitude_value(self.app.m_annotations[keys[i-1]].get_text())

            sigma_val = max(sigma_val, self.app.m_min_sigma)

            params[f'g{i}_center'].set(value=center_val)
            params[f'g{i}_sigma'].set(value=sigma_val, min=self.app.m_min_sigma)
            params[f'g{i}_amplitude'].set(value=amp_val)

        return model, params

    def calculer_modele(self):
        model, params = self.create_gaussian_model()
        self.app.m_fig1_X = pd.Series(self.app.m_chiffresX_phi)
        self.app.m_fig1_Y = pd.Series(self.app.m_chiffresY_µ)

        self.app.progress["maximum"] = len(self.app.m_init_centers_selected)
        self.app.progress["value"] = 0

        titre = self.app.m_titre_graphique
        self.app.m_tous_les_resultats = [
            r for r in self.app.m_tous_les_resultats
            if r["Echantillon"] != titre
        ]
        
        for i, _ in enumerate(self.app.m_init_centers_selected):
            self.app.progress["value"] = i + 1
            self.app.root.update_idletasks()
            self.app.m_model = model.fit(self.app.m_fig1_Y, params, x=self.app.m_fig1_X)
            self.app.m_components_model = self.app.m_model.eval_components(x=self.app.m_fig1_X)

        n = len(self.app.m_init_centers_selected)
        self.app.m_centres_phi = [self.app.m_model.params[f'g{i}_center'].value for i in range(1, n + 1)]
        self.app.m_sigmas =      [self.app.m_model.params[f'g{i}_sigma'].value  for i in range(1, n + 1)]
        self.app.m_amplitudes =  [self.app.m_model.params[f'g{i}_amplitude'].value for i in range(1, n + 1)]
        self.app.m_centres_microns = [1000 * (2 ** (-phi)) for phi in self.app.m_centres_phi]

        self.app.m_proportions = self.calculer_aires_et_proportions()
        
        best_fit_y = self.app.m_model.best_fit
        self.app.m_last_error_metrics = self.calculer_erreurs(self.app.m_fig1_Y, best_fit_y, self.app.m_fig1_X)
        for i, (µ, phi, A, σ, p) in enumerate(
            zip(self.app.m_centres_microns,
                self.app.m_centres_phi,
                self.app.m_amplitudes,
                self.app.m_sigmas,
                self.app.m_proportions)
        ):
            self.app.m_tous_les_resultats.append({
                "Echantillon": self.app.m_titre_graphique,
                "Date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "Composante": i+1,
                "Centre (µm)": µ,
                "Proportion": p,
                "Centre (phi)": phi,
                # "Amplitude": A,
                "Amplitude": A / (σ * (2 * np.pi)**0.5),
                "Sigma": σ,
                **self.app.m_last_error_metrics
            })

        messagebox.showinfo(self.app.t("info"), self.app.t("model_success"))

    def calculer_aires_et_proportions(self):
        n = len(self.app.m_init_centers_selected)
        if self.app.m_model is None or n == 0:
            return []
        areas = []
        total = 0.0
        for i in range(1, n + 1):
            amp = self.app.m_model.params[f'g{i}_amplitude'].value
            sigma = self.app.m_model.params[f'g{i}_sigma'].value
            area = amp * np.sqrt(2 * np.pi) * sigma
            areas.append(area)
            total += area
        if total <= 0:
            return [0] * n
        return [a / total for a in areas]

    def calculer_erreurs(self, y_observe, y_modele, x):
        erreur_absolue = np.trapz(np.abs(y_observe - y_modele), x)

        aire_observee = np.trapz(y_observe, x)
        erreur_relative = 100 * erreur_absolue / aire_observee if aire_observee != 0 else np.nan

        mse = np.mean((y_observe - y_modele) ** 2)

        ss_tot = np.sum((y_observe - np.mean(y_observe)) ** 2)
        ss_res = np.sum((y_observe - y_modele) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else np.nan

        return {
            "Erreur absolue": erreur_absolue,
            "Erreur relative (%)": erreur_relative,
            "MSE": mse,
            "R²": r_squared
        }