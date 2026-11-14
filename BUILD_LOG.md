# Build log

Dated entries. Each one: what I did, what surprised me, what I'd tell an interviewer.

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

**Interview line:**
"The cheapest target wasn't the best-characterized one. 2022 OB5 costs 3.96 km/s from LEO versus 6.62 for 1989 ML, but it's 3–13 m and spinning every 90 seconds. Accessible doesn't mean exploitable."

**Next:** cache Horizons data (Earth = 399, 2022 OB5), then start Lambert.

---

## #3 · YYYY-MM-DD · Week 1 wrap (planned after Day 6–7)
