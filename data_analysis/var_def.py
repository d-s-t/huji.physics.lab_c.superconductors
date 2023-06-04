import numpy as np
import scipy.constants as const

AXIS_CHOICE = {"tmp": "Temperature(K)",
               "sv": "SampVolt(V)",
               "sc": "SampCurr(A)",
               "cc": "CoilCurr(A)",
               "h": "H"}

AXIS_TITLE = {"Temperature(K)": r"$ \text{Temperature} \left[ K \right] $",
              "SampVolt(V)": r"$ \text{Sample Voltage} \left[ V \right] $",
              "SampCurr(A)": r"$ \text{Sample Current} \left[ A \right] $",
              "CoilCurr(A)": r"$ \text{Coil Current} \left[ A \right] $",
              "H": r"$ \text{Applied Magnetic Field} \left[ G \right] $"}


def exp(x, y0, k, b):
    return y0 * np.exp(k * x) + b


def line(x, m, b):
    return x * m + b


def exp_heavy_line(x, y0, k, b0, x0, m):
    return np.where(x < x0, exp(x, y0, k, b0), line(x - x0, m, exp(x0, y0, k, b0)))


def ih_surface(x, i0, b0, v0, k, b1, x0, m1):
    return exp(x[:, 0], v0, 1 / i0, b0) * exp_heavy_line(x[:, 1], 1, k, b1, x0, m1)


def exp_surface(x, v0, k0, k1, b):
    return v0 * np.exp(k0 * x[:, 0] + k1 * x[:, 1]) + b


FUNCTIONAL_RELATION = {"exp": exp, "line": line, "exp_heavy_line": exp_heavy_line, "ih_surface": ih_surface,
                       "exp_surface": exp_surface}
