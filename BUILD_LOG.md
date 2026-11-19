# Build log

Dated entries.

---

## #0 · 2026-11-10 · Kickoff: front sheet + first hand calcs

**Did:**
- [x] Front sheet drafted and moved to a Google Doc (question, figures F1–F3, acceptance criteria, schedule)
- [x] Hand-estimate sheet: LEO departure row (C3 = 0 / 10 / 20 → 3.18 / 3.63 / 4.06 km/s)
- [ ] Figures F1–F3 sketched on paper
- Cleaned up GitHub profile (bio, pins, made the PSA course-notes repo private)

**Surprised me:**
- How rusty I was on the departure-burn derivation. The key is C3 = 2ε, so v_p = √(C3 + 2μ/r).
- ΔV grows *slower* than C3: 0→10 cost 0.45 km/s, 10→20 only 0.43 km/s (square root + Oberth).

**Notes:**
"Before writing any code I hand-calculated the numbers it should produce, so every output had a sanity check from day one."

---

## #1 · 2026-11-11 · Hand estimates done, repo live, first code

**Did:**
- [x] GEO departure row (C3 = 0 / 10 / 20 → 1.27 / 2.30 / 3.16 km/s)
- [x] Heliocentric sanity numbers: Earth 29.78 km/s; Hohmann 1.0 → 1.2 AU gives v∞ 1.32 / 1.27 km/s, TOF ≈ 211 days
- [x] Repo on GitHub (`nea-porkchop-transfer-designer`), first commit
- [x] venv + `pytest` running; baseline = all tests fail with `NotImplementedError`
- [x] `timescales.py` implemented; **3/3 time-scale tests pass**
- Decided: no `dev` branch for now, solo project commits to `main`

**Surprised me:**
- **GEO "looks" cheaper but isn't.** Departure from GEO is 2.30 vs 3.63 km/s at C3 = 10, but getting to GEO costs ~3.85 km/s. Only cheaper if a rideshare already paid for it.
- **Heliocentric v∞ (~1.3 km/s) is tiny next to Earth escape (~3.2 km/s).** Most of the cost of reaching a near-Earth asteroid is leaving Earth.
- **Saw the 69.184 s TDB − UTC offset directly** in astropy (`t.tdb` → 00:01:09.184). Earth moves ~2,000 km in that time.
- **Python:** an expression on its own line inside a function does nothing. Assign it or `return` it. The `>>>` prompt hides this because it prints everything.
- Git setup lessons: GitHub needs browser sign-in, not a password; my Desktop lives in a OneDrive folder.

**Notes:**
"The first code I wrote was time-scale handling, because mixing UTC and TDB silently moves Earth by thousands of kilometers. That failure wouldn't crash; it'd just be wrong."

---

## #2 · 2026-11-13 · Target selection

**Did:**
- [x] Queried SBDB for NEOs with measured spectral types (327) → 48 X-complex / M candidates
- [x] Filtered by albedo (E / M / P split), orbit similarity to Earth, condition code, size
- [x] Compared 2022 OB5 vs 1989 ML in JPL's Small-Body Mission Design tool (2027 launches)
- [x] **Target: 2022 OB5.** Set in `config/mission.yaml`

| | 2022 OB5 | 1989 ML |
|---|---|---|
| Best 2027 launch | 2027-01-02 (JPL Id 76) | 2027-10-08 |
| TOF | 430 d | 700 d |
| C3 / v∞ dep / v∞ arr | 1.77 / 1.3 / 0.7 | 0.99 / 1.0 / 3.4 |
| **Total from LEO** | **3.96 km/s** | 6.62 km/s |
| Arrival burn (spacecraft pays) | 0.7 km/s | 3.4 km/s |
| Composition | unmeasured ("M-type?") | measured X-type |
| Size | ~3–13 m, ~1.5-min spin | ~0.4 km |

**Surprised me:**
- **"X-type" ≠ metal.** The X complex splits by albedo: E (bright rock), M (metal candidate, ~0.1–0.3), P (dark).
- **The metric changes the ranking.** JPL's "total ΔV" (v∞ dep + v∞ arr) puts OB5 options 76 and 65 at 2.1 vs 2.7 km/s; from LEO they're 3.96 vs 3.99. Departure v∞ is cheap deep in Earth's well.
- **Cheapest rendezvous takes ~1 year,** much longer than DeepSpace-2's 3–9 months. Fits DS-2 being a lunar-assisted *flyby*.
- **White bands in the porkchop** at TOF ~200–230 and ~380–420 days: transfer angles near 180° / 360° where Lambert is singular. My own plot should show them too.
- **OB5's synodic period is ~26 years.** Its window is *now*, which is why Odin (2025) and DS-2 both target it.
- My hand estimate (4.53 km/s for an idealized 1.2 AU target) was in the right ballpark; real OB5 is lower because its orbit is more Earth-like.

**Notes:**
"The cheapest target wasn't the best-characterized one. 2022 OB5 costs 3.96 km/s from LEO versus 6.62 for 1989 ML, but it's 3–13 m and spinning every 90 seconds. Accessible doesn't mean exploitable."

**Next:** cache Horizons data (Earth = 399, 2022 OB5), then start Lambert.

---

## #3 · 2026-11-16 · Data cached + Lambert solver working
**Did:**
- [x] 'fetch_horizons_vectors': JPL Horizons → km, km/s → CSV cache in 'data/cache/' (cache-first: second run is instant)
- [x] Cached Earth ('399') and 2022 OB5, daily, 2026-12-31 → 2029-06-30 (913 rows each)
- [x] Stumpff functions C(z), S(z) in 'twobody.py', checked at z = 0, π², ±1e-9
- [x] 'lambert.solve': Curtis Algorithm 5.2 (universal variables), root found with 'brentq'
- [x] **4/5 Lambert tests pass**: Curtis 5.2, Vallado 7-5, quarter circle, lamberthub (Izzo) cross-check at heliocentric scale
- [ ] 'test_propagated_solution_hits_r2': waiting on 'twobody.propagate' (tomorrow)

**Data checks:**

| | Value | Expected | |
|---|---|---|---|
| Earth \|r\| on 2026-12-31 | 0.98336 AU | ~0.983 AU (perihelion is early Jan) | ✓ |
| Earth \|v\| on 2026-12-31 | 30.28 km/s | > 29.78 (faster at perihelion) | ✓ |
| OB5 min / max distance | 0.97033 / 1.08313 AU | q = 0.96990, Q = 1.08250 | ✓ (see below) |

**Surprised me:**
- **OB5 goes 0.0006 AU (~94,000 km) past its catalog Q.** SBDB elements are *osculating*: a two-body snapshot at one epoch. Horizons includes planetary perturbations (OB5 passes close to Earth) and a small non-gravitational push. My Lambert arcs are purely two-body, so this is red-team material.
- **Earth at perihelion is 30.28 km/s, not 29.78.** Kepler's second law, visible in my own cached data.
- **Vector vs magnitude:** I used 'r1*r2' (vectors) where Curtis means R1R2 (magnitudes). It would have turned A and y into arrays and broken everything silently. Lowercase = vector, capital = magnitude.
- **Read the grouping:** I wrote 'np.sqrt(mu * t)' for √μ·Δt. Also `t` didn't exist; the parameter is `tof`.
- **Retrograde branch was flipped.** No test covers it, so it would have hidden.

**Tooling lessons:**
- Two copies of 'scratch_fetch.py': I was editing one and running the other. Check the breadcrumb path at the top of the editor.
- 'NameError: AU_KM' → a file can only use what it imports. VS Vode's **Problems** panel flagged it before I ran anything.
- 'pip install -e .' makes 'from porkchop... import' work outside pytest. Added 'scratch_*.py' and '*.egg-info/' to '.gitignore'.

**Notes:**
"I wrote my own Lambert solver from Curtis's universal-variable method, validated it on two textbook cases and a closed-form case, then cross-checked it against Izzo's independent algorithm at heliocentric scale, the regime my porkchop actually runs in."

**Next:** 'twobody.propagate' (Curtis Alg 3.4, reuses Stumpff) → last Lambert test + energy tests → first raw porkchop on the real OB5 grid.

---

## #4 · 2026-11-17 · Propagator, sweep, first porkchop and a real finding

**Did:**
- [x] `twobody.propagate`: universal-variable Kepler propagation (Curtis Alg. 3.3 + 3.4), Newton iteration on χ; `specific_energy`
- [x] **9/9 two-body + Lambert tests pass**, including `test_propagated_solution_hits_r2` (Lambert output really arrives at r₂, checked by an independent method)
- [x] `sweep.porkchop_grid`: Lambert over a (TOF × launch date) grid; **3/3 sweep tests pass** (shape and index order proven)
- [x] `state_interpolator`: exact row lookup in the daily cache (no interpolation needed)
- [x] **First raw porkchop** on real data: 2022 OB5, 2027 launches, TOF 30–500 d, 73 × 95 = 6,935 Lambert solves → `figures/first_porkchop.png`

**Compared with JPL (Small-Body Mission Design, same target and window):**

| Feature | Mine | JPL | |
|---|---|---|---|
| Lambert-singularity band edges | TOF ≈ 220 and ≈ 390–400 d | same | ✓ |
| Sep–Oct pocket (TOF ~330 d) | ~2.5–3 km/s | ~3 km/s | ✓ |
| Early Jan, TOF 355 d | ~2.5–3 km/s | 2.7 (Id 65) | ✓ |
| **TOF > ~400 d, incl. JPL's best (Id 76)** | **missing (white)** | **2.1 km/s** | ✗ |

**Diagnosis at JPL Id 76** (launch 2027-01-02, TOF 430 d):

| Solution | v∞ dep | v∞ arr |
|---|---|---|
| My solver, 0-rev | 38.5 | 39.2 km/s |
| Izzo, 1-rev, low path | **1.33** | **0.75** km/s |
| Izzo, 1-rev, high path | 30.6 | 31.1 km/s |
| JPL | 1.3 | 0.7 km/s |

→ **JPL's optimum is a one-revolution transfer.** OB5's orbit is ~1 year, so a 430-day trip goes ~420° around the Sun. A zero-rev solver can only find absurd high-energy loops there. NaN count = 0, so the white areas are real but off-scale, not solver failures.
→ Bonus: my cached ephemeris + Izzo reproduces JPL to ~0.05 km/s, which **validates data, time scales and frames**.

**Decision:** extend my own Lambert solver to 1 revolution (option b) rather than staying zero-rev or calling Izzo from `src/`. Derive it once by hand; in future projects I'd use a library solver (Izzo) and spend the time elsewhere. Costs ~1 day from the buffer → ship ≈ Dec 7.

**Surprised me:**
- The red-team assumption "zero-revolution Lambert only" hid the best answer *on my actual target*, found on day 4, not day 12.
- A 1-rev transfer has **two** solutions (Izzo's low / high path), and only one is cheap.

**Python lessons:**
- `r0*v0` multiplies component by component; the radial speed is `np.dot(r0, v0)`. "The truth value of an array is ambiguous" means a should-be-number is secretly an array; trace back to where it started.
- `np.abs(vector)` ≠ magnitude; use `np.linalg.norm`. (`np.norm` doesn't exist.)
- You can't use a variable before the line that creates it (`R` before `r`).
- **Loop variable vs whole array:** inside the loop use `tof` (one value), not `tof_days` (all 95).
- **Units per job:** dates in days (`dep + tof`), Lambert in seconds (`tof * SECONDS_PER_DAY`).
- **Testing:** `rtol` alone can never pass when the expected value is exactly 0; scale `atol` to the vector's magnitude. That test was AI-written; the independent check caught it.

**Notes:**
"My first porkchop matched JPL's structure but was missing its optimum. I hypothesized multi-revolution transfers, confirmed it against Izzo's solver, which reproduced JPL's best point to 0.05 km/s, and extended my own solver to one revolution."

**Next:** multi-rev extension. z ∈ (4π², 16π²); find the TOF minimum, solve on each side, validate against Izzo `M=1` (both paths); the sweep keeps the cheaper of 0-rev and 1-rev.

---

## #5 · 2026-11-18 · One-revolution Lambert: reproduced JPL's best mission

**Did:**
- [x] **Refactored `lambert.py`** into shared helpers (`_geometry`, `_y`, `_tof_residual`, `_velocities`). All 5 existing tests still pass, so nothing broke.
- [x] **`solve_multirev`**: one-revolution Lambert from the same Curtis equations; z ∈ (4π², 16π²)
- [x] **7/7 Lambert tests pass**: the new 1-rev test matches Izzo's low *and* high path; a too-short TOF correctly returns no solutions
- [x] **Sweep keeps the cheaper of 0-rev and 1-rev** at every grid point; new `n_revs` grid records which won
- [x] Porkchop now matches JPL's full structure, including the one-rev region above ~420 days

**Result: reproduced JPL's best 2027 mission to 2022 OB5**

| Launch 2027-01-01, TOF 430 d | Mine | JPL | |
|---|---|---|---|
| C3 | **1.6509** km²/s² | 1.65 | 0.05% |
| v∞ dep / arr | 1.285 / 0.782 km/s | 1.3 / 0.8 | ✓ (JPL rounds to 0.1) |
| v∞ dep + arr | 2.067 km/s | 2.1 | ✓ |
| Revolutions | 1 | – | |
| Grid minimum (6,935 points) | this same point | JPL's precomputed best (Id 76) | ✓ |

**How one revolution works:**
- Zero-rev: z < 4π², flight time rises steadily with z → **one** solution.
- One-rev: z ∈ (4π², 16π²), flight time → ∞ at both ends with a **minimum** between → a U-shaped curve.
  - Δt above the bottom of the U → **two** solutions (left side = Izzo's low path, right side = high path)
  - Δt below it → **none**. In my test geometry the bottom was ~391 days, which is why the missing region started at ~400 days.

**Surprised me:**
- The same Curtis equations handle one revolution; only the z range and the bracketing change. Izzo's "low / high path" are just the two sides of the U.
- A refactor felt risky until I realized the existing tests answer "did I break anything?" in 5 seconds.

**Python lessons:**
- **Refactor under tests:** move code into helpers, rerun the old tests *before* adding anything new.
- Helpers outside a function can't see its variables; they need them as explicit inputs.
- `lambda z: ...` turns a many-input function into the one-input form `brentq` and `minimize_scalar` need.
- `minimize_scalar` returns an object: `.x` = *where* the minimum is, `.fun` = the value there.
- Imports again: `minimize_scalar` undefined until added to the `from scipy.optimize import ...` line.
- "Replace" means delete the old lines. Leftover old code *after* new code silently overwrote the 1-rev results.
- `vinf_dep_vec` holds a vector, `vinf_dep` its magnitude. Don't store one where the other belongs.
- `zip(a, b)` walks two lists side by side; a running minimum starts at `np.inf`; `NaN < x` is always False, so failed solves skip themselves.
- `np.unravel_index(np.nanargmin(grid), grid.shape)` → (row, col) of a 2-D minimum.

**Notes:**
"My porkchop reproduces JPL's best 2027 mission to 2022 OB5, C3 1.651 vs their 1.65. Getting there meant extending my Lambert solver to one-revolution transfers after I found JPL's optimum was a 1-rev trajectory my zero-rev solver couldn't see."

**Next:** Day 5, the parking-orbit layer: departure ΔV from LEO / SSO / GEO and the declination reachability check (`departure.py` stubs + tests are ready). Then the full JPL grid comparison (Figure F3). Ship ≈ Dec 7.

---

## #6 · YYYY-MM-DD · Week 1 wrap (planned after Day 6–7)
