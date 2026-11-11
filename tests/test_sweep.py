"""Pins the array convention. If you transpose the grid by accident, these fail."""
import numpy as np
import pytest

from porkchop import lambert, sweep
from porkchop.constants import AU_KM, MU_SUN, SECONDS_PER_DAY


def _circular(radius_au, phase0_rad):
    """Fake ephemeris: circular, coplanar orbit. Returns f(mjd) -> (r, v)."""
    R = radius_au * AU_KM
    n = np.sqrt(MU_SUN / R**3)

    def state(mjd):
        th = phase0_rad + n * mjd * SECONDS_PER_DAY
        r = R * np.array([np.cos(th), np.sin(th), 0.0])
        v = R * n * np.array([-np.sin(th), np.cos(th), 0.0])
        return r, v

    return state


EARTH = _circular(1.0, 0.0)
TARGET = _circular(1.2, 0.9)
DEP = np.array([61406.0, 61416.0, 61426.0, 61436.0])   # m = 4
TOF = np.array([150.0, 200.0, 250.0])                  # n = 3


@pytest.fixture(scope="module")
def grid():
    return sweep.porkchop_grid(DEP, TOF, EARTH, TARGET)


def test_shape_rows_are_tof_cols_are_departure(grid):
    for key in ("vinf_dep", "vinf_arr", "c3"):
        assert grid[key].shape == (3, 4)
    assert grid["vinf_dep_vec"].shape == (3, 4, 3)


def test_entry_matches_direct_solve(grid):
    i, j = 2, 1                                   # tof = 250 d, departure = 61416
    r1, ve = EARTH(DEP[j])
    r2, vt = TARGET(DEP[j] + TOF[i])
    v1, v2 = lambert.solve(MU_SUN, r1, r2, TOF[i] * SECONDS_PER_DAY)
    assert grid["vinf_dep"][i, j] == pytest.approx(np.linalg.norm(v1 - ve))
    assert grid["vinf_arr"][i, j] == pytest.approx(np.linalg.norm(v2 - vt))
    assert grid["c3"][i, j] == pytest.approx(grid["vinf_dep"][i, j] ** 2)


def test_values_are_physical(grid):
    assert np.all(np.isfinite(grid["vinf_dep"]))
    assert np.all((grid["vinf_dep"] > 0) & (grid["vinf_dep"] < 30))   # km/s
