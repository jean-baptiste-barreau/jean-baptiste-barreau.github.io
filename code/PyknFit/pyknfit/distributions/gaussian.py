import numpy as np
from scipy.stats import norm
from .base import Distribution

class Gaussian(Distribution):

    def pdf(self, x, params):
        mu = params["mu"]
        sigma = params["sigma"]

        return norm.pdf(x, loc=mu, scale=sigma)

    def logpdf(self, x, params):
        mu = params["mu"]
        sigma = params["sigma"]

        return norm.logpdf(x, loc=mu, scale=sigma)

    def sample(self, n, params):
        mu = params["mu"]
        sigma = params["sigma"]

        return np.random.normal(mu, sigma, n)

    def initialize(self, x, y):

        idx = np.argmax(y)

        return {
            "mu": x[idx],
            "sigma": np.std(x)
        }
        
    def create_initial_params(
        self,
        center,
        sigma,
        amplitude
    ):
        return {
            "mu": center,
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
            (None, None),
            (0.05, None),
            (0.0, None)
        ]
        
    def gui_center_value(self, params):
        return params["mu"]

    def gui_width_value(self, params):
        return params["sigma"]
        
    def table_info(self, params):

        mu = params["mu"]
        sigma = params["sigma"]
        amp = params["amplitude"]

        micron = 1000 * (2 ** (-mu))

        hauteur = amp / (
            sigma * np.sqrt(2*np.pi)
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
            "f(x)=H/(σ√(2π)) exp(-(x-μ)²/(2σ²))\n\n"
            "Paramètres du modèle :\n"
            "μ : moyenne (centre)\n"
            "σ : écart-type\n"
            "H : aire (poids) de la composante"
        )
        
    def derived_quantities_description(self):
        return (
            "Grandeurs dérivées :\n"
            "µm = 1000 × 2^(-μ)"
        )