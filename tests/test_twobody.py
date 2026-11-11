"""Acceptance criterion: specific energy conserved to ~1e-10 relative."""
import numpy as np
import pytest

from porkchop import twobody

MU = 398600.4418


def _ellipse():
    # perigee 7000 km, e ~ 0.3
    r0 = np.array([7000.0, 0.0, 0.0])
    v0 = np.array([0.0, np.sqrt(MU / 7000.0 * 1.3), 0.5])
    return r0, v0


def test_one_period_returns_to_start():
    r0, v0 = _ellipse()
    eps = twobody.specific_energy(MU, r0, v0)
    a = -MU / (2 * eps)
    T = 2 * np.pi * np.sqrt(a**3 / MU)
    r, v = twobody.propagate(MU, r0, v0, T)
    assert np.linalg.norm(r - r0) < 1e-3          # km
    assert np.linalg.norm(v - v0) < 1e-6          # km/s


def test_energy_conserved():
    r0, v0 = _ellipse()
    e0 = twobody.specific_energy(MU, r0, v0)
    r, v = twobody.propagate(MU, r0, v0, 3 * 86400.0)
    assert abs((twobody.specific_energy(MU, r, v) - e0) / e0) < 1e-10


def test_angular_momentum_conserved():
    r0, v0 = _ellipse()
    h0 = np.cross(r0, v0)
    r, v = twobody.propagate(MU, r0, v0, 12345.0)
    np.testing.assert_allclose(np.cross(r, v), h0, rtol=1e-9)


def test_specific_energy_circular():
    r = 7000.0
    assert twobody.specific_energy(MU, np.array([r, 0, 0.0]), np.array([0, np.sqrt(MU / r), 0])) == pytest.approx(-MU / (2 * r))
