"""Two-body propagation: the independent check on every Lambert answer.

Two good routes:
  * Universal-variable Kepler propagation (Curtis Algorithm 3.4): exact up to Newton tolerance;
    energy conservation comes almost for free.
  * scipy.integrate.solve_ivp on r'' = -mu r / |r|^3 with method='DOP853', rtol=atol~1e-12.
    This one is more transferable to Project 1, but to hit 1e-10 energy you must tighten the tolerances.

Either passes the tests. Pick one and write in BUILD_LOG why.
"""
import numpy as np

# Stumpff helper function C(z)
def stumpff_c(z: float) -> float:
    if z > 1e-8:
        return (1 - np.cos(np.sqrt(z))) / z
    elif z < -1e-8:
        return (np.cosh(np.sqrt(-z)) - 1) / (-z)
    else:
        return 1/2      # the formulas divide by ~0 here, so use the limit value

# Stumpff helper function S(z)
def stumpff_s(z: float) -> float:
    if z > 1e-8:
        return (np.sqrt(z) - np.sin(np.sqrt(z))) / (np.sqrt(z))**3
    elif z < -1e-8:
        return (np.sinh(np.sqrt(-z)) - np.sqrt(-z)) / (-np.sqrt(-z))**3
    else:
        return 1/6      # the formulas divide by ~0 here, so use the limit value

def propagate(mu: float, r0: np.ndarray, v0: np.ndarray, dt: float):
    """State after dt seconds. Returns (r, v), km and km/s, shape (3,) each."""
    raise NotImplementedError


def specific_energy(mu: float, r: np.ndarray, v: np.ndarray) -> float:
    """epsilon = v^2/2 - mu/|r|, km^2/s^2."""
    raise NotImplementedError
