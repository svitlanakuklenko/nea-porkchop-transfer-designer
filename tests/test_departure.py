"""Day 5. Limiting cases + the numbers on your hand-estimate sheet."""
import numpy as np
import pytest

from porkchop.constants import MU_EARTH, R_EARTH
from porkchop.data_sources import parking_orbit_from_omm
from porkchop.departure import (declination_deg, dv_from_circular, ecliptic_to_equatorial,
                                max_reachable_declination_deg)

R_LEO = R_EARTH + 400.0
R_GEO = R_EARTH + 35786.0


def test_c3_zero_is_escape_burn():
    vc = np.sqrt(MU_EARTH / R_LEO)
    assert dv_from_circular(0.0, R_LEO) == pytest.approx((np.sqrt(2) - 1) * vc, rel=1e-12)


def test_leo_and_geo_reference_values():
    # Check these against YOUR hand-estimate sheet before trusting them.
    assert dv_from_circular(10.0, R_LEO) == pytest.approx(3.628, abs=1e-3)
    assert dv_from_circular(10.0, R_GEO) == pytest.approx(2.302, abs=1e-3)


def test_dv_grows_slower_than_c3():
    d0, d10, d20 = (dv_from_circular(c, R_LEO) for c in (0.0, 10.0, 20.0))
    assert d0 < d10 < d20
    assert (d20 - d10) < (d10 - d0)      # concave: each extra 10 km^2/s^2 costs less


def test_frame_rotation():
    x = ecliptic_to_equatorial(np.array([1.0, 0, 0]))
    np.testing.assert_allclose(x, [1, 0, 0], atol=1e-15)            # vernal equinox is shared
    pole = ecliptic_to_equatorial(np.array([0, 0, 1.0]))
    assert declination_deg(pole) == pytest.approx(90 - 23.439281, abs=1e-6)
    # June solstice: the Sun sits at ecliptic longitude 90 deg (+y) and declination +23.44 deg.
    # This catches a rotation applied with the wrong sign (the pole check above can't).
    solstice = ecliptic_to_equatorial(np.array([0, 1.0, 0]))
    assert declination_deg(solstice) == pytest.approx(+23.439281, abs=1e-6)
    v = np.array([0.3, -1.2, 0.7])
    assert np.linalg.norm(ecliptic_to_equatorial(v)) == pytest.approx(np.linalg.norm(v))


def test_declination_basic():
    assert declination_deg(np.array([1.0, 0, 0])) == pytest.approx(0.0)
    assert declination_deg(np.array([0, 0, 2.0])) == pytest.approx(90.0)
    assert declination_deg(np.array([1.0, 0, -1.0])) == pytest.approx(-45.0)


@pytest.mark.parametrize("inc, expected", [(51.64, 51.64), (97.5, 82.5), (0.05, 0.05), (90.0, 90.0)])
def test_reachable_declination(inc, expected):
    assert max_reachable_declination_deg(inc) == pytest.approx(expected)


def test_geo_mean_motion_gives_geo_radius():
    omm = {"OBJECT_NAME": "TEST", "EPOCH": "2026-11-10T00:00:00", "MEAN_MOTION": 1.00273791,
           "ECCENTRICITY": 0.0001, "INCLINATION": 0.05}
    orbit = parking_orbit_from_omm(omm)
    assert orbit["a_km"] == pytest.approx(42164.2, abs=1.0)
    assert orbit["inc_deg"] == pytest.approx(0.05)
