import numpy as np
from scipy.stats import lognorm
from .base import Distribution

class LogNormal(Distribution):

    @property
    def use_log_scale(self):
        return True
    
    def pdf(self, x, params):

        sigma = params["sigma"]
        scale = np.exp(params["mu"])

        return lognorm.pdf(x, s=sigma, scale=scale)

    def logpdf(self, x, params):

        sigma = params["sigma"]
        scale = np.exp(params["mu"])

        return lognorm.logpdf(x, s=sigma, scale=scale)

    def sample(self, n, params):

        mu = params["mu"]
        sigma = params["sigma"]

        return np.random.lognormal(mu, sigma, n)

    def initialize(self, x, y):

        positive_x = x[x > 0]

        return {
            "mu": np.mean(np.log(positive_x)),
            "sigma": np.std(np.log(positive_x))
        }
        
    def create_initial_params(
        self,
        center,
        sigma,
        amplitude
    ):
        return {
            "mu": np.log(center),
            "sigma": sigma,
            "amplitude": amplitude
        }
        
    def pack_theta(self, params):
        return [
            params["mu"],
            params["sigma"],
            params["amplitude"]
        ]

    def unpack_theta(self, theta):
        return {
            "mu": theta[0],
            "sigma": abs(theta[1]),
            "amplitude": abs(theta[2])
        }

    def bounds(self):
        return [
            (None, None),   # mu
            (0.05, None),   # sigma
            (0.0, None)     # amplitude
        ]
        
    def gui_center_value(self, params):
        return params["mu"]

    def gui_width_value(self, params):
        return params["sigma"]
        
    def table_info(self, params):
        mu = params["mu"]
        sigma = params["sigma"]
        amp = params["amplitude"]

        # diamètre modal
        micron = np.exp(mu - sigma**2)

        # hauteur maximale
        hauteur = (
            amp *
            self.pdf(
                np.array([micron]),
                params
            )[0]
        )

        return {
            "micron": micron,
            "phi": mu,
            "hauteur": hauteur,
            "params_table": {
                "σ": sigma
            }
        }
        
    def formula_description(self):
        return (
            "f(x)=H/(xσ√(2π)) exp(-(ln(x)-μ)²/(2σ²))\n\n"
            "Paramètres du modèle :\n"
            "μ : moyenne de ln(x)\n"
            "σ : écart-type de ln(x)\n"
            "H : aire (poids) de la composante"
        )
        
    def derived_quantities_description(self):
        return (
            "Grandeurs dérivées :\n"
            "µm = exp(μ)"
        )