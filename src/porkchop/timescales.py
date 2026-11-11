"""Day 1: epoch and time-scale handling. Write this before any physics.

The rules this module enforces:
  * Inputs a human types (config dates, CelesTrak OMM `EPOCH`) are UTC.
  * Everything that touches ephemerides or Lambert is TDB. Horizons vector tables are TDB;
    JPL's mdesign grid uses MJD.
  * Time of flight is a difference of two TDB instants, in seconds.

In 2027, TT - UTC = 69.184 s (37 leap seconds + 32.184 s), and TDB - TT is a +/- 1.7 ms wobble.
Mixing UTC and TDB moves Earth ~2,000 km along its orbit (69 s x 29.8 km/s). That's small for a
porkchop, but it would fail the 1 km propagation acceptance check.

Use astropy.time.Time. Don't hand-roll leap seconds.
"""
from astropy.time import Time


def utc_iso_to_tdb(iso_utc: str) -> Time:
    """'2027-01-01T00:00:00' (UTC) -> astropy Time in the TDB scale.

    Hint: build the Time with scale='utc', then convert it. One line.
    """
    raise NotImplementedError


def mjd_tdb(t: Time) -> float:
    """Modified Julian Date of `t` in TDB. MJD = JD - 2400000.5 (JPL mdesign's convention)."""
    raise NotImplementedError


def tof_seconds(t_dep: Time, t_arr: Time) -> float:
    """Time of flight in seconds between two instants, measured in TDB.

    Positive if t_arr is after t_dep. Make sure this works even if a caller hands you UTC Times.
    """
    raise NotImplementedError
