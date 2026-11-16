"""Day 1-2: real data in, cached to disk, never re-downloaded inside a sweep.

Pattern for every fetch:
    1. Check data/cache/<name>.json or .csv. If it's there, load it and return.
    2. Otherwise download it, save it to the cache, and return it.
    3. Log the download time (UTC) in what you save. Ephemerides and OMMs go stale.

Only `parking_orbit_from_omm` is pure math, so it's the only one with a unit test. The fetchers
get checked by eye in BUILD_LOG (print one record and compare it with the website).
"""
from pathlib import Path
from astroquery.jplhorizons import Horizons

import numpy as np

from .constants import AU_KM, MU_EARTH, SECONDS_PER_DAY

CACHE = Path(__file__).resolve().parents[2] / "data" / "cache"


def fetch_omm(catnr: int) -> dict:
    """CelesTrak GP record for one object, OMM in JSON.

    URL: https://celestrak.org/NORAD/elements/gp.php?CATNR={catnr}&FORMAT=json
    Set FORMAT explicitly. Returns a list with one dict. Fields you'll use: OBJECT_NAME, EPOCH (UTC),
    MEAN_MOTION (rev/day), ECCENTRICITY, INCLINATION (deg).
    """
    raise NotImplementedError


def parking_orbit_from_omm(omm: dict, mu: float = MU_EARTH) -> dict:
    """Turn an OMM record into what the departure layer needs.

    Returns {'name', 'epoch_utc', 'a_km', 'inc_deg', 'ecc'}.
    a comes from mean motion via Kepler's third law: n [rad/s] = MEAN_MOTION * 2*pi / 86400,
    a = (mu / n^2)^(1/3). (SGP4 "Kozai" vs "Brouwer" mean motion differ by ~km. Note it, ignore it.)
    """
    raise NotImplementedError


def fetch_sbdb(designation: str) -> dict:
    """Target metadata + osculating elements from JPL SBDB.

    API: https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=<designation>&phys-par=1
    (or astroquery.jplsbdb.SBDB.query). Save the spectral type (spec_B / spec_T), H, orbit class
    and orbit epoch.
    """
    raise NotImplementedError


def fetch_horizons_vectors(body_id: str, start_utc: str, stop_utc: str, step: str = "1d"):
    """
    Heliocentric ecliptic-J2000 state vectors from JPL Horizons (astroquery.jplhorizons).
    location='@sun'. Vector epochs come back in TDB. Store JD-TDB alongside x,y,z,vx,vy,vz.
    Returns arrays (jd_tdb[N], r_km[N,3], v_kms[N,3]).
    """

    # 1. Build a cache filename from the inputs (spaces in "2022 OB5" make awkward filenames)
    safe_id = body_id.replace(" ", "_")
    path = CACHE / f"horizons_{safe_id}_{start_utc}_{stop_utc}_{step}.csv"

    # 2. If we already downloaded it, load and return. No internet needed.
    if path.exists():
        data = np.loadtxt(path, delimiter=",", skiprows=1)  # shape (N, 7), skip header row
        jd_tdb = data[:, 0]     # column 0
        r_km = data [:, 1:4]   # column 1, 2, 3    (hint: a slice like a:b stops BEFORE b)
        v_kms = data[:, 4:7]   # columns 4, 5, 6
        return jd_tdb, r_km, v_kms

    # 3. Otherwise ask Horizons
    id_type = "smallbody" if not body_id.isdigit() else None    # Earth is '399'. '3' is the Earth-Moon BARYCENTER (~4,700 km off, ~12 m/s different). "399" is all digits >> a major body
    obj = Horizons(id=body_id, id_type=id_type, location="@sun",
                   epochs={"start": start_utc, "stop": stop_utc, "step": step})
    vec = obj.vectors(refplane="ecliptic")

    # 4. Pull columns out of the table and stack them side by side into (N, 3)
    jd_tdb = np.array(vec["datetime_jd"])
    r_au = np.column_stack([vec["x"], vec["y"], vec["z"]])
    v_aud = np.column_stack([vec["vx"], vec["vy"], vec["vz"]])

    # 5. Convert units: AU >> km, AU/day >> km/s
    r_km = r_au * AU_KM
    v_kms = v_aud * AU_KM / SECONDS_PER_DAY

    # 6. Save for next time: glue jd + r + v side by side into one (N, 7) table 
    CACHE.mkdir(parents = True, exist_ok = True)
    table = np.column_stack([jd_tdb, r_km, v_kms])
    np.savetxt(path, table, delimiter=",",
               header = "jd_tdb, x_km, y_km, z_km, vx_kms, vy_kms, vz_kms", comments="")
    return jd_tdb, r_km, v_kms


def fetch_jpl_porkchop(designation: str, mjd0: int, span: int, tof_min: int, tof_max: int, step: int) -> dict:
    """The published case: JPL mdesign.api Mode M.

    https://ssd-api.jpl.nasa.gov/mdesign.api?des=...&mjd0=...&span=...&tof-min=...&tof-max=...&step=...
    Returns dep_date (MJD, len m), tof (days, len n), and vinf_dep / vinf_arr / decl_dep as
    (n, m) arrays. Too many points comes back as HTTP 200 with an error IN the JSON, so check for it.
    """
    raise NotImplementedError


def state_interpolator(jd_tdb: np.ndarray, r: np.ndarray, v: np.ndarray):
    """Optional: callable (mjd_tdb) -> (r, v) from a cached daily table, for sweep.porkchop_grid.

    If your grid step is a whole number of days and the cache is daily, you can index exactly
    and skip interpolation entirely. Cheaper, and more correct.
    """
    raise NotImplementedError
