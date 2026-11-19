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
from scipy.optimize import brentq, minimize_scalar
from .twobody import stumpff_c, stumpff_s

# ---------- shared helpers (Curtis Algorithm 5.2, split into pieces) ----------

def _geometry(r1, r2, prograde):
    """Steps 1-3: magnitudes, transfer angle (with the side picked by the cross product's z-component), and Curtis's constant A."""
    R1 = np.linalg.norm(r1)
    R2 = np.linalg.norm(r2)
    cos_dth = np.clip(np.dot(r1, r2) / (R1 * R2), -1.0, 1.0)        # clip guards against 1.0000000001
    cross_z = np.cross(r1, r2)[2]

    if prograde:
        dth = np.arccos(cos_dth) if cross_z >= 0 else 2*np.pi - np.arccos(cos_dth)
    else:
        dth = np.arccos(cos_dth) if cross_z < 0 else 2*np.pi - np.arccos(cos_dth)
    A = np.sin(dth) * np.sqrt((R1*R2) / (1 - np.cos(dth)))
    return R1, R2, A 

def _y(z, R1, R2, A):
    """Step 4: y(z)."""
    return R1 + R2 + A * (z*stumpff_s(z) - 1) / np.sqrt(stumpff_c(z))

def _tof_residual(z, R1, R2, A, mu, tof):
    """Step 5: F(z), zero at the right orbit (when this z's orbit takes exactly 'tof' seconds)."""
    yz = _y(z, R1, R2, A)
    if yz < 0:
        return np.inf               # y sits under a square root; treat this region as "infinitely long"    
    return (yz/stumpff_c(z))**1.5 * stumpff_s(z) + A * np.sqrt(yz) - np.sqrt(mu) * tof

def _velocities(z, r1, r2, R1, R2, A, mu):
    """Steps 7-8: Lagrange coefficients, then the two velocity vectors."""
    yz = _y(z, R1, R2, A)
    f = 1 - yz/R1
    g = A * np.sqrt(yz/mu)
    gdot = 1 - yz/R2
    v1 = (r2 - f*r1) / g
    v2 = (gdot*r2 - r1) / g
    return v1, v2

# ---------- public solvers ----------

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
    R1, R2, A = _geometry(r1, r2, prograde)
    resid = lambda z: _tof_residual(z, R1, R2, A, mu, tof)

    # Step 6 (zero-revolution): z between the y > 0 boundary and 4*pi^2
    z_high = 4 * np.pi**2 - 1e-6
    z_low = -4 * np.pi**2
    while _y(z_low, R1, R2, A) < 0 and z_low < z_high:      # y is under a square root, so it must be positive
        z_low += 0.1
    try:
        z = brentq(resid, z_low, z_high, xtol=1e-14, maxiter=500)
    except ValueError:                                      # no sign change: no solution in this bracket
        return nan3, nan3
    return _velocities(z, r1, r2, R1, R2, A, mu)

def solve_multirev(mu, r1, r2, tof, revs=1, prograde=True):
    """All 'revs' -revolution solutions (0 or 2 of them), as a list of (v1, v2).
    
    z lives in ((2*pi*revs)^2, (2*pi*(revs+1))^2). TOF -> infinity at both ends with a minimum
    between, so: find the minimum, then solve once on each side (Izzo's low / high path).
    """

    R1, R2, A = _geometry(r1, r2, prograde)
    resid = lambda z: _tof_residual(z, R1, R2, A, mu, tof)  # one-line unnamed function that turns the 6-input residual into a 1-input function that minimize_scalar and brentq need (same trick as defining F(z) inside solve)

    z_lo = (2*np.pi*revs)**2 + 1e-6
    z_hi = (2*np.pi*(revs + 1))**2 - 1e-6
    bottom = minimize_scalar(resid, bounds=(z_lo, z_hi), method="bounded")
    z_min = bottom.x                          # where the minimum is (the z at the bottom of the U; already stored that as z_min)
    if bottom.fun > 0:                        # Δt is shorter than the fastest 1-rev transfer; the fastest 1-rev transfer is still too slow → no solution
        return []                             # bottom.fun: the function's value there ("fun" is short for function value)

    solutions = []
    for a, b in ((z_lo, z_min), (z_min, z_hi)):                 # left side, then right side of the U
        z = brentq(resid, a, b, xtol=1e-14, maxiter=500)
        solutions.append(_velocities(z, r1, r2, R1, R2, A, mu))
    return solutions 