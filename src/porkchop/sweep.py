"""Day 3-4: the porkchop sweep. Lambert at every (launch date, time of flight) pair.

BEFORE CODING: draw the grid on paper. A small one: 4 launch dates across, 3 TOFs down.

              dep[0]   dep[1]   dep[2]   dep[3]      <- columns  j  (m = 4)
    tof[0]  [  .        .        .        .   ]
    tof[1]  [  .        .        .        .   ]      <- rows     i  (n = 3)
    tof[2]  [  .        .        .        .   ]

    Each dot = one Lambert solve: leave Earth at dep[j], arrive at the target at dep[j] + tof[i].
    The array is shape (n, m) = (len(tof), len(dep)), i.e. ROWS = TOF, COLS = launch date.

Why this convention: it's JPL mdesign's (n x m, m = len(dep_date)). Your grid minus JPL's grid is
then one subtraction with no transposes. matplotlib's contourf(dep, tof, Z) also expects Z with
shape (len(tof), len(dep)).

Preallocate, then fill:
    vinf_dep = np.full((n, m), np.nan)      # NaN = "not computed / failed", so it shows up as a hole
    for i, tof in enumerate(tof_days):
        for j, dep in enumerate(dep_mjd):
            ... vinf_dep[i, j] = ...
Two plain for-loops are fine. ~50k solves is seconds to a minute. Vectorize later, if ever.

Rendezvous (Day 8-9): arrival dV = |v2_lambert - v_target| = v_inf_arr. Departure:
v_inf_dep = v1_lambert - v_earth, C3 = |v_inf_dep|^2.
"""
import numpy as np

from .constants import MU_SUN, SECONDS_PER_DAY
from . import lambert

# For each flight time and each launch date, find Earth at launch and the asteroid at arrival, 
# solve Lambert between them, and record how fast you arrive at the asteroid, each relative to the body
def porkchop_grid(dep_mjd, tof_days, earth_state, target_state, mu: float = MU_SUN) -> dict:
    """Sweep Lambert over the grid.

    Args:
        dep_mjd: launch dates, MJD (TDB), shape (m,)
        tof_days: times of flight, days, shape (n,)
        earth_state, target_state: callables  f(mjd_tdb) -> (r_km[3], v_kms[3]), heliocentric ecliptic
        mu: central-body GM (Sun)

    Returns dict of arrays, all with leading shape (n, m):
        'vinf_dep' (km/s), 'vinf_arr' (km/s), 'c3' (km^2/s^2), 'vinf_dep_vec' (n, m, 3), ecliptic frame, 
        'n_revs' (n, m): 0 or 1, which revolution count won
    """
    n, m = len(tof_days), len(dep_mjd)

    # Preallocate: one empty (n, m) "sheet" per quantity, filled with NaN = "not computed yet"
    vinf_dep = np.full((n, m), np.nan)
    vinf_arr = np.full((n, m), np.nan)  # same shape
    vinf_dep_vec = np.full((n, m, 3), np.nan)   # a 3-vector at every grid point
    n_revs = np.full((n, m), -1)                # which revolution count won at each point (-1 = none yet)

    for i, tof in enumerate(tof_days):                  # rows
        for j, dep in enumerate(dep_mjd):               # columns
            r1, v_earth = earth_state(dep)
            r2, v_target = target_state(dep + tof)                       # the asteroid's state at ARRIVAL

            dt = tof * SECONDS_PER_DAY
            candidates = [lambert.solve(mu, r1, r2, dt)] + lambert.solve_multirev(mu, r1, r2, dt, revs=1)
            revs_of = [0] + [1] * (len(candidates) - 1)     # label each candidate with its rev count

            best_total = np.inf
            for (v1, v2), k in zip(candidates, revs_of):    # walks both lists side by side, so each pass gives you one solution and its label together
                vd = v1 - v_earth                           # departure v-infinity vector
                total = np.linalg.norm(vd) + np.linalg.norm(v2 - v_target)
                if total < best_total:                      # NaN < anything is False, so failed solves are skipped
                    best_total = total
                    vinf_dep_vec[i, j] = vd
                    vinf_dep[i, j] = np.linalg.norm(vd)
                    vinf_arr[i, j] = np.linalg.norm(v2 - v_target)
                    n_revs[i, j] = k

    return {"vinf_dep": vinf_dep, "vinf_arr": vinf_arr, "c3": vinf_dep**2, 
            "vinf_dep_vec": vinf_dep_vec, "n_revs": n_revs}
