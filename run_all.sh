#!/bin/bash
# MSMD Assignment 2026/2027 - Project 9
# Runs the full pipeline: Tasks 1-4 + report generation.
#
# USAGE:
#   ./run_all.sh              # full N=10000 Monte Carlo (assignment default)
#   ./run_all.sh --quick      # N=500 for a fast end-to-end sanity check
#
# Expect the full run to take several minutes, almost all of it in Task 4's
# Blind-Blind Monte Carlo (the censored/near-zero-rudder trials are the
# slow part). Task 1-3 finish in seconds.

set -e  # stop on first error

N=10000
if [ "$1" == "--quick" ]; then
    N=500
    echo ">>> QUICK MODE: N=$N (for sanity-checking the pipeline, not for the final report)"
fi

mkdir -p outputs figures

echo ""
echo "=== [0/5] Vessel data and corrected Nomoto T ==="
python3 ship_data.py

echo ""
echo "=== [1/5] Task 1 - KCS turning circle ==="
python3 task1_turning_circle.py

echo ""
echo "=== [2/5] Task 2 - Head-on encounters (COLREG-COLREG, Blind-Blind) ==="
python3 task2_encounter.py

echo ""
echo "=== [3/5] Task 3 - Hashimoto & Okushima comparison ==="
python3 task3_hashimoto.py

echo ""
echo "=== [4/5] Task 4 - Monte Carlo (N=$N per scenario) ==="
python3 task4_run.py --n $N

echo ""
echo "=== [5/5] Building report (Word + PDF) ==="
node build_report.js

# Convert to PDF if LibreOffice is available (assignment requires both formats)
if command -v soffice &> /dev/null; then
    soffice --headless --convert-to pdf MSMD_Project9_Report_Tasks1-4.docx
    echo "Also saved MSMD_Project9_Report_Tasks1-4.pdf"
else
    echo "NOTE: LibreOffice (soffice) not found -- only the .docx was created."
    echo "      Open the .docx in Word and 'Save As PDF' to get the PDF the"
    echo "      assignment requires, or install LibreOffice and re-run."
fi

echo ""
echo "=== DONE ==="
echo "Report:  MSMD_Project9_Report_Tasks1-4.docx / .pdf"
echo "Figures: figures/"
echo "Data:    outputs/ (JSON results, Excel tables, CSV raw samples)"
