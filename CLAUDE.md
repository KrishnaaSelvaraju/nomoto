# CLAUDE.md - MSMD Project 9 (KCS vs KVLCC2), Tasks 1-4

## Context
MSc Naval Architecture assignment "Modelling and Safety of Maritime Traffic" (2026-2027).
Solo student, Project 9: Vessel 1 = KCS, Vessel 2 = KVLCC2, HEAD-ON encounter only,
scenarios COLREG-COLREG and Blind-Blind. Nomoto first-order model ONLY (no MMG - to be
confirmed in writing with course staff). Python for simulation, Word + PDF report.
Assignment spec and reference papers are in `reference/`.

## State of the code (already built and tested at small N)
- `ship_data.py`: single source of truth for vessel data. T is DERIVED per vessel via
  T' = T*V/L scaling from the reference paper's worked example (L=330, V=15kn, T=100s),
  because Silveira et al. (2016) (the paper Lotovskyi & Teixeira 2023 cite for the T table)
  is unavailable. KCS T~43.6 s, KVLCC2 T~93.8 s.
- `engine.py`: Nomoto stepper (Lotovskyi & Teixeira 2023 Eqs 4-17), SAT collision check,
  min-safe-distance search (D0=(Lpp1+Lpp2)/2, increment=0.25*min(Lpp), rudder starts t=0).
- `task1_turning_circle.py`, `task2_encounter.py`, `task3_hashimoto.py`,
  `task4_mc_engine.py` (numpy-vectorised), `task4_run.py`, `build_report.js`, `run_all.sh`.
- Coordinate convention: origin (0,0), heading 0 = +y, positive rudder = starboard (psi grows).

## What to do
1. `pip install -r requirements.txt && npm install docx` (also need ffmpeg + libreoffice).
2. `./run_all.sh --quick` to sanity check, then `./run_all.sh` for the real N=10000 run
   (no tool time limit here, so no chunking needed).
3. Review outputs/*.json, figures/, and the generated report. Sanity-check that results
   are physically sensible (COLREG-COLREG D_min < Blind-Blind; Task 1 numbers reasonable).
4. Known caveats to keep in the report: T is a scaling estimate; Blind-Blind Monte Carlo
   has a censored fraction (0.3% at N=10000) still unresolved at the search cap (11,200 m,
   ~6.05 nm). A trial that hits the sim time limit without collision counts as safe only
   if the steady turning circles can never touch (engine.steady_turn_circles_disjoint);
   vectorised vs scalar engines can differ by one search increment at boundary cases.

## Open items / possible improvements
- Task 2 "cruise straight then trigger turn at min safe distance" demo not built.
- Task 1 real-vs-simulated comparison against SIMMAN/ITTC data for KCS not done
  (assignment asks to compare with official lab data; only Nomoto sim exists).
- Task 5 (collision probability in Lisbon-Madeira canal) and Task 6 (domain-based timely
  avoidance, sector D) are NOT started.
- Report title page needs student name/number; submission zip naming: MSMD_2026_09_<Name>.
