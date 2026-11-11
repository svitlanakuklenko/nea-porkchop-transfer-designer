# Parking lot

New ideas land here the day they appear, **never in scope**. Revisit after `v1.0` is tagged.

- **Lunar-flyby departure**: DeepSpace-2's real profile ("slingshot around the moon" off IM-3's trajectory). An SDSU friend built a MATLAB version; a Python v2 could reuse this engine for the heliocentric leg.
- **Candidate ranking**: sweep several M/X-type NEAs and rank them by minimum ΔV vs launch date (AstroForge-style target selection from a candidate list).
- **Plane-change penalty** instead of a reachable/unreachable flag when |δ| exceeds what the inclination allows: combined burn at periapsis, ΔV = √(v_c² + v_p² − 2·v_c·v_p·cos Δ).
- **Parking-orbit timing**: RAAN / time-of-day alignment with the departure asymptote, plus J2 precession during the coast.
- **Multi-rev Lambert and Earth flybys**: how OSIRIS-REx and Hayabusa2 actually did it.
- **Low-thrust porkchop** (JPL's API dropped its low-thrust data in v1.2; see arXiv 2508.02920).
- **SPICE path**: spiceypy + DE440 kernels instead of Horizons queries.
- **GMAT cross-check** of the chosen trajectory.
- **Attitude-at-arrival sim**: moved to Mini-project B (SpartanSat sizing notebook), if that happens.
