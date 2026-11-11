# Front sheet: Porkchop & Transfer Designer (warm-up)

Filled in **before any physics code**. Items marked ✏️ are yours to fill in by hand on Day 1–2. Everything else is a draft for you to accept, edit or cut.

---

## 1. The question (one sentence)

> For a rideshare that leaves a real Earth parking orbit in 2027, what does a ballistic rendezvous with **[target NEA]** cost in ΔV, and how much does a launch slip change that cost?

Why it fits now: AstroForge's DeepSpace-2 is assembled, waiting on Intuitive Machines' IM-3 (now NET Q1 2027, after slipping from 2025 and then 2026). AstroForge picks the target from about 28 candidate metal asteroids close to launch. A launch-date-dependent ΔV map is the tool that kind of decision runs on. *(Status re-verified Nov 10, 2026. Check it again before you publish the writeup.)*

## 2. Money figures (sketch these by hand first ✏️)

| # | Figure | What it proves |
|---|--------|----------------|
| **F1** | **Porkchop:** total rendezvous ΔV (departure from parking orbit + arrival match) over launch date × time of flight, minimum marked, region the origin can't reach (declination) hatched | The engine works on real ephemeris, and the origin choice changes the answer |
| **F2** | **Launch-slip curve:** minimum total ΔV vs launch date, one line per origin (ISS-like LEO, SSO, GEO) | The "what does a 1-month slip cost?" answer. Comes straight out of F1's grid |
| **F3** | **Validation residual:** your departure v∞ grid minus JPL's for the same target and grid, as a contour | You reproduced a published case and can explain the difference |

Anything that doesn't feed F1–F3 goes to `PARKING_LOT.md`.

## 3. Hand-estimate sheet ✏️ (one page, pencil, before code)

Every code output gets compared against these. Use μ⊕ = 398600.4418 km³/s², R⊕ = 6378.137 km.

**Departure burn from a circular parking orbit:** ΔV = √(C3 + 2μ/r) − √(μ/r)

| Origin | r (km) | v_circ (km/s) | ΔV at C3 = 0 | ΔV at C3 = 10 | ΔV at C3 = 20 |
|---|---|---|---|---|---|
| ISS-like LEO (~400 km alt) | ✏️ | ✏️ | ✏️ | ✏️ | ✏️ |
| GEO | ✏️ | ✏️ | ✏️ | ✏️ | ✏️ |

Relation checks (answer *before* filling the table, then check yourself against it):
- ✏️ At C3 = 0, what is ΔV as a multiple of v_circ? (There's a closed form.)
- ✏️ If C3 doubles from 10 to 20, does the LEO ΔV double? Grow by more or less than it did going from 0 to 10? Why?
- ✏️ For the same C3, is GEO departure cheaper or pricier than LEO? Does that mean GEO is the "better" origin? (Hint: who paid to get to GEO?)

**Heliocentric sanity numbers:**
- ✏️ Earth's orbital speed (km/s), from √(μ☉ / 1 AU)
- ✏️ Hohmann Earth (1.0 AU) → a 1.2 AU circular orbit: v∞ at departure and at arrival, and the TOF in days. Your NEA's numbers should sit in the same tens-of-percent neighborhood if its orbit is Earth-like.
- ✏️ Typical v∞ range for accessible NEAs (look at the JPL list query in §5 once you pick a target)

**The cheapest alternative:** ✏️ in one line, what would a mission designer do *instead* of a direct ballistic transfer? (Earth flyby? Lunar flyby? Low thrust?) What's your rough guess at its ΔV?

## 4. Acceptance criteria (pass/fail)

- [ ] Lambert solver matches Curtis Ex. 5.2 and Vallado Ex. 7-5 to 4+ significant figures *(tests written)*
- [ ] Propagating each Lambert solution lands within 1 km of the target position *(test written for the textbook case; spot-check 5 grid points on the real case)*
- [ ] Two-body propagation conserves specific energy to ~1e-10 relative *(test written)*
- [ ] Departure v∞ grid matches JPL Mission Design within ✏️ ___ km/s over the region where v∞ < ✏️ ___ km/s, **or** every difference is explained
- [ ] Departure declination matches JPL `decl_dep` within ✏️ ___ deg at the same points
- [ ] Changing the origin in `config/mission.yaml` changes F1 and F2, with no code edits

## 5. Reproduce one published case first

**Primary: JPL Small-Body Mission Design API, map mode** (`mdesign.api`, Mode M). For a given asteroid it returns a porkchop grid over launch date (MJD) × time of flight (days), with `vinf_dep`, `vinf_arr` and `decl_dep` as **2-D arrays of shape (n_tof, n_dep)**. Same domain, same quantities, same axes, so validation is a literal array subtraction. `decl_dep` also validates your Day-5 declination check.

- Docs: https://ssd-api.jpl.nasa.gov/doc/mdesign.html
- Undocumented: JPL doesn't name its Lambert solver or ephemeris. Expect small differences, and explain them (EMB vs Earth center? ephemeris version? time scale?).
- Grid cap: 1.5 M points. `step` must be one of 1, 2, 5, 10, 15, 20, 30 days.

**Fallback** (if the JPL diff is unexplainable): Burke, Falck & McGuire, *Interplanetary Mission Design Handbook: Earth-to-Mars Mission Opportunities 2026 to 2045*, NASA/TM-2010-216764. Its 2026 Mars window is open this month.

**Target choice ✏️** (Day 1–2):
- Shortlist accessible NEOs: `https://ssd-api.jpl.nasa.gov/mdesign.api?lim=50&crit=3&year=2027&sb-group=neo` (sorted by total ΔV)
- Check spectral class in SBDB (M or X type ≈ metal-rich candidate)
- 2022 OB5 is AstroForge's publicly known Odin target, which ties the case study tightly. Your SDSU friend used QN266; pick something different unless you deliberately want to compare.

## 6. Unit tests per model (3 each)

| Model | Residual ≈ 0 | Conserved quantity | Known / closed-form case |
|---|---|---|---|
| Lambert | propagated r(t₂) − r₂ | — (uses two-body below) | Curtis 5.2, Vallado 7-5, quarter-circle |
| Two-body propagator | one period returns to start | specific energy, \|h\| | circular orbit period |
| Departure | ecliptic→equatorial round-trip | — | C3 = 0 → (√2−1)·v_circ; GEO mean motion → 42164 km |
| Sweep | grid[i,j] equals a direct solve at (tof[i], dep[j]) | — | shape is (n_tof, n_dep) |

## 7. Parking lot → `PARKING_LOT.md`

## 8. Red-team day (Day 12–13). Seed list of assumptions to attack:

1. Patched conics: Earth's SOI and the target's gravity are ignored.
2. Zero-revolution Lambert only; no multi-rev, no flybys.
3. Instantaneous, impulsive burns at the parking-orbit periapsis.
4. Parking orbit treated as circular at its mean-motion semi-major axis; RAAN timing and J2 precession ignored.
5. Ephemeris source and frame (ecliptic J2000, TDB), with Earth = body 399, not the Earth–Moon barycenter (3).
6. Mid-course correction is a flat allowance, not computed.
7. ✏️ ask one person to attack three claims in the README.

## 9. AI rule

AI may scaffold code and attack results. Every AI-written explanation gets one independent check (a plot, a limiting case, a literature number) before it goes in the writeup.

## 10. Definition of done

Tagged `v1.0` · README with F1 or F2 at the top · one-page writeup · 3-minute spoken explanation (Grad Slam style) · LinkedIn post the week it ships.
