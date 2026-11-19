import numpy as np
import matplotlib.pyplot as plt
from porkchop.data_sources import fetch_horizons_vectors, state_interpolator
from porkchop.sweep import porkchop_grid
from porkchop import lambert
from lamberthub import izzo2015
from porkchop.constants import MU_SUN, SECONDS_PER_DAY

earth = state_interpolator(*fetch_horizons_vectors("399", "2026-12-31", "2029-06-30"))
ob5 = state_interpolator(*fetch_horizons_vectors("2022 OB5", "2026-12-31", "2029-06-30"))

dep = np.arange(61406, 61406 + 365, 5)      # 2027-01-01 → 2027-12-31, every 5 days (MJD TDB)
tof = np.arange(30, 501, 5)                 # 30 → 500 days
grid = porkchop_grid(dep, tof, earth, ob5)

total = grid["vinf_dep"] + grid["vinf_arr"]  # JPL's "total ΔV" for apples-to-apples comparison
plt.contourf(dep, tof, total, levels=np.arange(0, 8.5, 0.5))
plt.colorbar(label="v∞ dep + v∞ arr (km/s)")
plt.plot(61407, 430, "r*", markersize=12, label="JPL Id 76")
plt.xlabel("Launch date (MJD TDB)"); plt.ylabel("Time of flight (days)")
plt.title("2022 OB5 — first raw porkchop"); plt.legend()
plt.savefig("figures/first_porkchop.png", dpi=150)
plt.show()

r1, ve = earth(61407)                       # JPL Id 76: launch 2027-01-02
r2, vt = ob5(61407 + 430)                   # arrive 430 days later
dt = 430 * SECONDS_PER_DAY
v1, v2 = lambert.solve(MU_SUN, r1, r2, dt)
print("mine, 0-rev:", np.linalg.norm(v1 - ve), np.linalg.norm(v2 - vt))

for low in (True, False):                   # a 1-rev transfer has two solutions
    v1, v2 = izzo2015(MU_SUN, r1, r2, dt, M=1, low_path=low)
    print(f"Izzo1-rev (low_path={low}):", np.linalg.norm(v1 - ve), np.linalg.norm(v2 - vt))

print("NaN grid points:", np.isnan(total).sum(), "of", total.size)

i = np.where(tof == 430) [0][0]             # row for TOF = 430 days; finds which row holds 430 days
j = np.where(dep == 61406)[0][0]            # column for 2027-01-01 (nearest grid date to JPL's 01-02)
print("At JPL Id 76:", total[i, j], "km/s, revs =", grid["n_revs"][i, j])

# Finds the smallest value while ignoring NaNs, but it reports the position as if the grid were one long list.
# np.unravel_index converts that back to (row, column); useful whenever you need "where is the minimum" on a 2D grid
k = np.unravel_index(np.nanargmin(total), total.shape)
print("Grid minimum:", total[k], "km/s at launch MJD", dep[k[1]],
      "TOF", tof[k[0]], "d, revs =", grid["n_revs"][k])
print("C3:", grid["c3"][i, j], "v_inf dep/arr:", grid["vinf_dep"][i, j], grid["vinf_arr"][i, j])
