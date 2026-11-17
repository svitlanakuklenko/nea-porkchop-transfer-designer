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
    """State after dt seconds. Universal-variable Kepler propagation (Curtis Alg. 3.3 + 3.4).
    Returns (r, v), km and km/s, shape (3,) each."""
    R0 = np.linalg.norm(r0)                 # capital = magnitude (yesterday's lesson)
    V0 = np.linalg.norm(v0)

    vr0 = np.dot(r0, v0)/R0                 # radial speed: component of v0 along r0
    alpha = 2/R0 - (V0**2)/mu               # 1/a: 2/R0 - V0^2/mu (>0 ellipse, <0 hyperbola)
    sqmu = np.sqrt(mu)

    # Solve the universal Kepler equation F(chi) = 0 with Newton's method
    chi = sqmu * abs(alpha) * dt            # Curtis's starting guess
    for _ in range(100):
        z = alpha * chi**2
        C, S = stumpff_c(z), stumpff_s(z)
        F = (R0*vr0)/sqmu * chi**2*C + (1-alpha*R0)*chi**3*S + R0*chi - sqmu * dt
        dFdx = (R0*vr0)/sqmu * chi * (1-z*S) + (1-alpha*R0) * chi**2 * C + R0
        step = F/dFdx
        chi -= step
        if abs(step) < 1e-12 * max(1.0, abs(chi)):
            break

    # Lagrange coefficients and the new state
    z = alpha * chi**2
    C, S = stumpff_c(z), stumpff_s(z)
    f = 1 - (chi**2/R0)*C
    g = dt - (chi**3/sqmu)*S
    r = f*r0 + g*v0                         # vector
    R = np.linalg.norm(r)
    fdot = (sqmu/(R*R0)) * (z*chi*S - chi)  # Recall that z = alpha*chi^2, so z*chi*S = alpha*chi^3*S
    gdot = 1 - (chi**2/R)*C
    v = fdot*r0 + gdot*v0                   # vector
    return r, v


def specific_energy(mu: float, r: np.ndarray, v: np.ndarray) -> float:
    """epsilon = v^2/2 - mu/|r|, km^2/s^2."""
    return np.dot(v, v) / 2 - mu / np.linalg.norm(r)
