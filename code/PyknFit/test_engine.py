import numpy as np
import matplotlib.pyplot as plt

from pyknfit.distributions.gaussian import Gaussian
from pyknfit.distributions.weibull import Weibull

from pyknfit.mixtures.mixture_model import MixtureModel

x = np.linspace(0.01, 10, 500)

y = (
    0.6 * Gaussian().pdf(
        x,
        {"mu": 3, "sigma": 0.5}
    )
    +
    0.4 * Weibull().pdf(
        x,
        {"k": 2, "lambda": 6}
    )
)

model = MixtureModel([
    Gaussian(),
    Weibull()
])

model.fit(x, y)

y_pred = model.evaluate(x)

plt.plot(x, y)
plt.plot(x, y_pred)

plt.show()