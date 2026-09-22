import numpy as np
from scipy.stats import weibull_min
from .base import Distribution

class Weibull(Distribution):

    @property
    def use_log_scale(self):
        return True
    
    def pdf(self, x, params):
        k = params["k"]
        lam = params["lambda"]
        return weibull_min.pdf(x, c=k, scale=lam)

    def logpdf(self, x, params):
        k = params["k"]
        lam = params["lambda"]
        return weibull_min.logpdf(x, c=k, scale=lam)

    def sample(self, n, params):
        k = params["k"]
        lam = params["lambda"]
        return weibull_min.rvs(c=k, scale=lam, size=n)

    def mode(self, params):
        k = params["k"]
        lam = params["lambda"]

        if k <= 1:
            return np.nan

        return lam * ((k - 1) / k) ** (1.0 / k)

    def mean(self, params):
        from scipy.special import gamma

        k = params["k"]
        lam = params["lambda"]

        return lam * gamma(1 + 1/k)

    def initialize(self, x, y):
        idx = np.argmax(y)
        return {
            "k": 2.0,
            "lambda": x[idx]
        }
        
    def create_initial_params(
        self,
        center,
        sigma,
        amplitude
    ):
        return {
            "k": 2.0,
            "lambda": center,
            "amplitude": amplitude
        }
        
    def pack_theta(self, params):
        return [
            params["k"],
            params["lambda"],
            params["amplitude"]
        ]

    def unpack_theta(self, theta):
        return {
            "k": abs(theta[0]),
            "lambda": abs(theta[1]),
            "amplitude": abs(theta[2])
        }

    def bounds(self):
        return [
            (1.01, 8.0),
            (0.01, None),
            (0.0, None)
        ]
        
    def gui_center_value(self, params):
        return params["k"]

    def gui_width_value(self, params):
        return params["lambda"]
        
    def table_info(self, params):

        amp = params["amplitude"]

        micron = self.mode(params)

        hauteur = (
            amp *
            self.pdf(
                np.array([micron]),
                params
            )[0]
        )

        return {
            "micron": micron,
            "phi": np.nan,
            "hauteur": hauteur,
            "params_table": {
                "λ": params["lambda"],
                "k": params["k"]
            }
        }
        
    def formula_description(self):
        return (
            "f(x)=H(k/λ)(x/λ)^(k-1) exp(-(x/λ)^k)\n\n"
            "Paramètres du modèle :\n"
            "λ : paramètre d'échelle\n"
            "k : paramètre de forme\n"
            "H : aire (poids) de la composante"
        )
        
    def derived_quantities_description(self):
        return (
            "Grandeurs dérivées :\n"
            "µm = λ ((k-1)/k)^(1/k)"
        )