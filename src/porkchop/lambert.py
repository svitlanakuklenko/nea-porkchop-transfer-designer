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
from scipy.optimize import brentq

from .twobody import stumpff_c, stumpff_s


def solve(mu: float, r1: np.ndarray, r2: np.ndarray, tof: float, prograde: bool = True):
    """Velocities at r1 and r2 for a conic from r1 to r2 in `tof` seconds.
    Universal variables, Curtis Algorithm 5.2; root found with brentq.

    Args:
        mu: gravitational parameter, km^3/s^2
        r1, r2: position vectors, km, shape (3,)
        tof: time of flight, s (> 0)
        prograde: True picks the transfer whose angular momentum has +z (same sense as the planets)

    Returns:
        (v1, v2): km/s, each shape (3,). NaN arrays if the solver fails to converge.
    """
    nan3 = np.full(3, np.nan)

    # Step 1: magnitudes
    R1 = np.linalg.norm(r1)
    R2 = np.linalg.norm(r2)

    # Step 2: transfer angle, with the side picked by the cross product's z-component
    cos_dth = np.clip(np.dot(r1, r2) / (R1 * R2), -1.0, 1.0)    # clip guards against 1.0000000001
    cross_z = np.cross(r1, r2)[2]
    if prograde:
        dth = np.arccos(cos_dth) if cross_z >= 0 else 2*np.pi - np.arccos(cos_dth)
    else:
        dth = np.arccos(cos_dth) if cross_z < 0 else 2*np.pi - np.arccos(cos_dth)

    # Step 3: A, constant for this problem
    A = np.sin(dth) * np.sqrt((R1*R2)/(1-np.cos(dth))) 

    # Step 4: y(z)
    def y(z):
        return R1 + R2 + A * (z*stumpff_s(z) - 1) / np.sqrt(stumpff_c(z))

    # Step 5: F(z), zero at the right orbit (comes from Curtis's time-of-flight equation)
    def F(z):
        yz = y(z)
        return (yz/stumpff_c(z))**1.5 * stumpff_s(z) + A * np.sqrt(yz) - np.sqrt(mu) * tof

    # Step 6: bracket and solve (zero-revolution: z must stay below 4*pi^2)
    z_high = 4 * np.pi**2 - 1e-6
    z_low = -4 * np.pi**2
    while y(z_low) < 0 and z_low < z_high:              # y is under a square root, so it must be positive
        z_low += 0.1
    try:
        z = brentq(F, z_low, z_high, xtol=1e-14, maxiter=500)
    except ValueError:                                  # no sign change: no solution in this bracket
        return nan3, nan3

    # Step 7: Lagrange coefficients
    yz = y(z)
    f = 1-yz/R1
    g = A * np.sqrt(yz/mu)
    gdot = 1 - yz/R2

    # Step 8: velocities
    v1 = (r2 - f*r1)/g 
    v2 = (gdot*r2 - r1) / g
    return v1, v2
