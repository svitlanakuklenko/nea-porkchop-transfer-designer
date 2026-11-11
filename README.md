# Porkchop & Transfer Designer

**What does a ballistic rendezvous with a near-Earth asteroid cost from a real Earth parking orbit, and how much does a launch slip change it?**

> _[F1 or F2 goes here, the first thing a reader sees.]_

_[One result sentence with real numbers, e.g. "From an ISS-like orbit, the cheapest 2027 rendezvous with XXXX costs X.XX km/s total (launch YYYY-MM-DD, TOF NNN d); a 30-day slip adds X.XX km/s. From GEO, ..."]_

These are patched-conic, impulsive, two-body results for preliminary design, not a flight trajectory. See [assumptions](docs/ASSUMPTIONS.md) and [validation](docs/VALIDATION.md).

## What it does

- Pulls real parking orbits from CelesTrak (OMM/JSON) and real asteroid ephemerides from JPL (SBDB + Horizons)
- Sweeps a Lambert solver (written from scratch, cross-checked against `lamberthub`) over launch date × time of flight
- Converts departure C3 into burn ΔV from the selected parking orbit and flags departure directions the orbit's inclination can't reach
- Builds the rendezvous ΔV budget: departure + mid-course allowance + arrival match
- Validated against JPL's Small-Body Mission Design porkchop for the same target

## Quick start

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                      # all tests should pass before any figure is trusted
python -m porkchop.run config/mission.yaml   # (written in week 1)
```

Change the origin or target in `config/mission.yaml`. No code edits needed.

## Validation

_[Summary of the JPL comparison: max/median residual, where it disagrees, why.]_

## Layout

```
config/       mission.yaml: origin, target, launch window, grid step
src/porkchop/ timescales · data_sources · lambert · twobody · departure · sweep
tests/        textbook cases, conserved quantities, closed-form limits
data/cache/   downloaded ephemerides (git-ignored)
figures/      F1–F3
docs/         ASSUMPTIONS.md, VALIDATION.md, writeup
```

## References

- Curtis, *Orbital Mechanics for Engineering Students*, Ch. 5 & 8
- Vallado, *Fundamentals of Astrodynamics and Applications*, Ch. 7
- JPL SSD Small-Body Mission Design API: https://ssd-api.jpl.nasa.gov/doc/mdesign.html
- Burke, Falck & McGuire, NASA/TM-2010-216764 (Earth–Mars handbook, 2026–2045)
