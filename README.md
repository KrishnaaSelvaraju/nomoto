# MSMD Assignment 2026/2027 - Project 9 (KCS vs KVLCC2)

Tasks 1-4 for the head-on encounter (COLREG-COLREG and Blind-Blind
scenarios), fully self-contained and reproducible: every number in the
final report is read from this pipeline's own output files, not typed in
by hand.

## What changed from the earlier version

The Nomoto time constant **T** previously used the same placeholder
(100 s) for both KCS and KVLCC2, because the paper this assignment cites
for Task 1 (Lotovskyi & Teixeira, 2023) attributes its T-distribution to
Silveira et al. (2016) -- a paywalled 2016 conference chapter that isn't
available. This version instead derives a **distinct, physically
grounded T for each vessel** using the standard ship-manoeuvring
length/speed scaling `T' = T*V/L` (see `ship_data.py`'s docstring for the
full derivation and the caveat that this should be swapped for the real
Silveira et al. (2016) table if it ever becomes available).

Everything downstream (Task 1 turning circle, Task 2 minimum safe
distances, Task 4 Monte Carlo) now uses these corrected, vessel-specific
T values automatically.

## Setup

```bash
# Python dependencies
pip install -r requirements.txt

# Report generation (Word doc) dependencies
npm install docx

# For PDF conversion (optional but the assignment wants both Word + PDF)
# -- install LibreOffice if not already present, e.g.:
#    sudo apt-get install libreoffice        (Debian/Ubuntu)
#    brew install --cask libreoffice          (macOS)

# For the MP4 animations in Tasks 1-2, ffmpeg must be installed:
#    sudo apt-get install ffmpeg
```

## Running everything

```bash
chmod +x run_all.sh
./run_all.sh              # full run, N=10000 Monte Carlo (assignment default)
```

For a quick sanity check before committing to the full run (~a few
minutes, mostly Task 4's Blind-Blind Monte Carlo, which has to search
harder for the small fraction of near-zero-rudder draws):

```bash
./run_all.sh --quick      # N=500, finishes in under a minute
```

Or run each step individually:

```bash
python3 ship_data.py              # prints + saves corrected K/T/etc for both vessels
python3 task1_turning_circle.py   # KCS turning circle: plot + MP4 + results JSON
python3 task2_encounter.py        # both head-on scenarios: plots + MP4s + Excel + JSON
python3 task3_hashimoto.py        # geometric comparison (reads Task 2's real results)
python3 task4_run.py --n 10000    # Monte Carlo: plots + raw CSV + JSON
node build_report.js              # assembles the Word report from all the above JSON
soffice --headless --convert-to pdf MSMD_Project9_Report_Tasks1-4.docx
```

## File map

| File | Purpose |
|---|---|
| `ship_data.py` | **Single source of truth** for vessel data and the corrected Nomoto K/T/K_beta/beta_ST. Everything else imports this. |
| `engine.py` | Shared single-vessel Nomoto stepper + SAT collision check + the minimum-safe-distance search (used by Tasks 1-2). |
| `task1_turning_circle.py` | Task 1: KCS 720 degree turning circle. |
| `task2_encounter.py` | Task 2: head-on COLREG-COLREG and Blind-Blind minimum safe distance, data tables, MP4s. |
| `task4_mc_engine.py` | Vectorised (numpy-batched) version of the same search algorithm, for running N=10000 trials in ~minutes instead of ~28 minutes per scenario. |
| `task4_run.py` | Task 4: runs the Monte Carlo, saves plots + raw sample CSVs. |
| `task3_hashimoto.py` | Task 3: Hashimoto & Okushima (1990) geometric comparison -- reads Task 2's *actual* results from JSON, not hardcoded numbers. |
| `build_report.js` | Assembles `MSMD_Project9_Report_Tasks1-4.docx` from every task's `outputs/*.json` and `figures/*.png`. Run this last. |
| `run_all.sh` | Runs the whole pipeline in order. |

## Outputs

- `outputs/*.json` -- machine-readable results per task (also what the report reads)
- `outputs/task2_headon_*_data.xlsx` -- full per-timestep data tables (Task 2)
- `outputs/task4_*_raw_sample.csv` -- full 10,000-row Monte Carlo sample per scenario (Task 4)
- `figures/*.png`, `figures/*.mp4` -- all plots and animations
- `MSMD_Project9_Report_Tasks1-4.docx` / `.pdf` -- the assembled report

## Still open (see report Section 6 for details)

- T is a scaling-law estimate, not the real Silveira et al. (2016) table
- MMG-vs-Nomoto-only for solo submissions needs confirming with course staff
- Task 2 doesn't yet have the "cruise straight, then trigger at minimum safe
  distance" demo version (current version starts the rudder at t=0, which
  is correct for *finding* the minimum safe distance, but not a full
  approach-and-react demonstration)
- Task 4's Blind-Blind censoring cap (~6 nm) affects the reported tail
  statistics -- revisit if a tighter bound is needed
