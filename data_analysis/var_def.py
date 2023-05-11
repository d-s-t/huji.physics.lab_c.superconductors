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


def exp(x, y0, k, b, phi):
    return y0 * np.exp(k * x + phi) + b


def line(x, m, b):
    return x * m + b


def exp_heavy_line(x, y0, k, b0, phi, x0, m):
    return np.where(x < x0, exp(x, y0, k, b0, phi), line(x - x0, m, exp(x0, y0, k, b0, phi)))


FUNCTIONAL_RELATION = {"exp": exp, "line": line, "exp_heavy_line": exp_heavy_line}
