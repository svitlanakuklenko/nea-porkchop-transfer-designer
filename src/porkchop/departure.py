"""Day 5: the parking-orbit layer. This is what makes "origin" change the answer.

Two effects:
  1. Burn size. A deeper potential well costs more:  dV = sqrt(C3 + 2 mu/r) - sqrt(mu/r)
  2. Geometry. The departure asymptote has a declination delta (measured from Earth's EQUATOR).
     From a circular orbit of inclination i, a coplanar burn reaches |delta| <= i for prograde
     orbits, or |delta| <= 180 - i for retrograde ones (SSO is retrograde, i ~ 97-98 deg).
     GEO (i ~ 0) can only send you out along the equator without a plane change.

FRAME TRAP: Horizons heliocentric vectors default to the ECLIPTIC J2000 frame. Declination is
measured in the EQUATORIAL frame. Rotate v_inf about +x by the obliquity before taking the
declination. Getting this wrong gives answers that are plausible but off by up to ~23 deg.
"""
import numpy as np

from .constants import MU_EARTH, OBLIQUITY_J2000_DEG


def dv_from_circular(c3: float, r_park: float, mu: float = MU_EARTH) -> float:
    """Impulsive burn (km/s) from a circular orbit of radius r_park (km) to a hyperbola with this C3 (km^2/s^2)."""
    raise NotImplementedError


def ecliptic_to_equatorial(vec_ecl: np.ndarray) -> np.ndarray:
    """Rotate a vector from ecliptic J2000 to equatorial J2000 (rotation about +x by the obliquity).

    Sanity check before coding: where should ecliptic +x land? What should the ecliptic north pole
    (+z) look like in equatorial coordinates? Sketch it.
    """
    raise NotImplementedError


def declination_deg(vec_eq: np.ndarray) -> float:
    """Declination (deg) of an equatorial-frame vector: the angle above the equatorial plane."""
    raise NotImplementedError


def max_reachable_declination_deg(inc_deg: float) -> float:
    """Largest |declination| a coplanar departure can reach from a circular orbit of inclination inc_deg."""
    raise NotImplementedError
