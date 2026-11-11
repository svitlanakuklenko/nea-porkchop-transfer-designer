"""Day 3. Acceptance criterion: textbook cases to 4+ significant figures; propagated arrival within 1 km."""
import numpy as np
import pytest

from porkchop import lambert, twobody

MU_CURTIS = 398600.0          # Curtis uses this rounded value in Ex. 5.2
MU_VALLADO = 398600.4418


def test_curtis_example_5_2():
    r1 = np.array([5000.0, 10000.0, 2100.0])
    r2 = np.array([-14600.0, 2500.0, 7000.0])
    v1, v2 = lambert.solve(MU_CURTIS, r1, r2, 3600.0)
    np.testing.assert_allclose(v1, [-5.9925, 1.9254, 3.2456], rtol=1e-4)
    np.testing.assert_allclose(v2, [-3.3125, -4.1966, -0.38529], rtol=1e-4)


def test_vallado_example_7_5():
    r1 = np.array([15945.34, 0.0, 0.0])
    r2 = np.array([12214.83899, 10249.46731, 0.0])
    v1, v2 = lambert.solve(MU_VALLADO, r1, r2, 76 * 60.0)
    np.testing.assert_allclose(v1[:2], [2.058913, 2.915965], rtol=1e-5)
    np.testing.assert_allclose(v2[:2], [-3.451565, 0.910315], rtol=1e-5)


def test_quarter_circle_closed_form():
    # 90 deg along a circular orbit in a quarter period: v1 must be the circular velocity.
    R = 7000.0
    tof = 0.25 * 2 * np.pi * np.sqrt(R**3 / MU_VALLADO)
    v1, v2 = lambert.solve(MU_VALLADO, np.array([R, 0, 0.0]), np.array([0, R, 0.0]), tof)
    vc = np.sqrt(MU_VALLADO / R)
    np.testing.assert_allclose(v1, [0, vc, 0], atol=1e-9 * vc * 1e3)
    np.testing.assert_allclose(v2, [-vc, 0, 0], atol=1e-9 * vc * 1e3)


def test_propagated_solution_hits_r2():
    r1 = np.array([5000.0, 10000.0, 2100.0])
    r2 = np.array([-14600.0, 2500.0, 7000.0])
    v1, _ = lambert.solve(MU_CURTIS, r1, r2, 3600.0)
    r_end, _ = twobody.propagate(MU_CURTIS, r1, v1, 3600.0)
    assert np.linalg.norm(r_end - r2) < 1.0   # km


def test_cross_check_against_lamberthub_heliocentric():
    lamberthub = pytest.importorskip("lamberthub")
    mu_sun = 1.32712440041279419e11
    au = 149597870.7
    r1 = np.array([1.0 * au, 0.0, 0.0])
    r2 = au * np.array([-0.9, 0.9, 0.05])      # ~135 deg transfer, slightly out of plane
    tof = 200 * 86400.0
    v1, v2 = lambert.solve(mu_sun, r1, r2, tof)
    v1_ref, v2_ref = lamberthub.izzo2015(mu_sun, r1, r2, tof)
    np.testing.assert_allclose(v1, v1_ref, rtol=1e-6)
    np.testing.assert_allclose(v2, v2_ref, rtol=1e-6)
