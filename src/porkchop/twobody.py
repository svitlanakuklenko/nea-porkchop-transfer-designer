"""Two-body propagation: the independent check on every Lambert answer.

Two good routes:
  * Universal-variable Kepler propagation (Curtis Algorithm 3.4): exact up to Newton tolerance;
    energy conservation comes almost for free.
  * scipy.integrate.solve_ivp on r'' = -mu r / |r|^3 with method='DOP853', rtol=atol~1e-12.
    This one is more transferable to Project 1, but to hit 1e-10 energy you must tighten the tolerances.

Either passes the tests. Pick one and write in BUILD_LOG why.
"""
import numpy as np


def propagate(mu: float, r0: np.ndarray, v0: np.ndarray, dt: float):
    """State after dt seconds. Returns (r, v), km and km/s, shape (3,) each."""
    raise NotImplementedError


def specific_energy(mu: float, r: np.ndarray, v: np.ndarray) -> float:
    """epsilon = v^2/2 - mu/|r|, km^2/s^2."""
    raise NotImplementedError
