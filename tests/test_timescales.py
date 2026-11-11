"""Day 1. Make these pass before anything else."""
import pytest
from astropy.time import Time

from porkchop.timescales import mjd_tdb, tof_seconds, utc_iso_to_tdb


def test_tdb_minus_utc_in_2027():
    # TT - UTC = 69.184 s since the 2017 leap second; TDB - TT is within +/- 2 ms.
    t_utc = Time("2027-01-01T00:00:00", scale="utc")
    t_tdb = utc_iso_to_tdb("2027-01-01T00:00:00")
    assert t_tdb.scale == "tdb"
    assert (t_tdb - t_utc).sec == pytest.approx(0.0, abs=1e-6)          # same instant...
    offset_s = (t_tdb.jd1 - t_utc.jd1 + t_tdb.jd2 - t_utc.jd2) * 86400.0  # ...different label
    assert offset_s == pytest.approx(69.184, abs=0.002)


def test_mjd_convention_matches_jpl():
    t = Time(2461406.5, format="jd", scale="tdb")
    assert mjd_tdb(t) == pytest.approx(61406.0, abs=1e-9)


def test_tof_is_tdb_seconds_even_from_utc_inputs():
    a = Time("2027-01-01T00:00:00", scale="utc")
    b = Time("2027-01-11T00:00:00", scale="utc")
    assert tof_seconds(a, b) == pytest.approx(10 * 86400.0, abs=1e-3)
    assert tof_seconds(b, a) < 0
