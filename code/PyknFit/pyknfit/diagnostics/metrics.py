import numpy as np

def mse(y_true, y_pred):

    return np.mean((y_true - y_pred) ** 2)


def r_squared(y_true, y_pred):

    ss_res = np.sum((y_true - y_pred) ** 2)

    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

    return 1 - (ss_res / ss_tot)


def aic(loglikelihood, k):

    return 2 * k - 2 * loglikelihood


def bic(loglikelihood, k, n):

    return k * np.log(n) - 2 * loglikelihood
