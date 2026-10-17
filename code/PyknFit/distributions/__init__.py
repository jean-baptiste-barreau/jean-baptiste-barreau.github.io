from .base import Distribution
from .gaussian import Gaussian
from .lognormal import LogNormal
from .weibull import Weibull

DISTRIBUTIONS = {
    "Gaussienne": Gaussian,
    "Log-normale": LogNormal,
    "Weibull": Weibull,
}

__all__ = [
    "Distribution",
    "Gaussian",
    "LogNormal",
    "Weibull",
    "DISTRIBUTIONS"
]