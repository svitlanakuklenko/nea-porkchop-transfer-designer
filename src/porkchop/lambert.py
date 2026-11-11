"""Day 3: your own Lambert solver. Zero-revolution, single solution.

Pick ONE method and cite it in the docstring:
  * Universal variables / Stumpff functions (Curtis Algorithm 5.2): easiest to derive by hand,
    and the one you can explain at a whiteboard.
  * Vallado's universal-variable bisection (Algorithm 58): the same family, more robust.
  * Izzo (2015): fastest and most robust, but harder to explain in an interview.

Recommendation: Curtis first. Make the tests pass. Only then decide whether robustness problems
on the real grid justify switching.

`lamberthub` (izzo2015, vallado2013, gooding1990) is your cross-check. Import it only in tests or
notebooks, never here. If this file imports it, the solver isn't yours.

Known edge cases to handle or flag (don't silently return garbage):
  * transfer angle near 180 deg: the transfer plane is undefined
  * no convergence (very short TOF on a long-way transfer, etc.): return NaNs, don't crash a 50k-point sweep
"""
import numpy as np


def solve(mu: float, r1: np.ndarray, r2: np.ndarray, tof: float, prograde: bool = True):
    """Velocities at r1 and r2 for a conic from r1 to r2 in `tof` seconds.

    Args:
        mu: gravitational parameter, km^3/s^2
        r1, r2: position vectors, km, shape (3,)
        tof: time of flight, s (> 0)
        prograde: True picks the transfer whose angular momentum has +z (same sense as the planets)

    Returns:
        (v1, v2): km/s, each shape (3,). NaN arrays if the solver fails to converge.
    """
    raise NotImplementedError
