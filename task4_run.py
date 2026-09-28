"""
MSMD Assignment 2026/2027 - Project 9, Task 4
Runs the full N=10000 Monte Carlo for both scenarios, saves the raw sample
(CSV, for anyone who wants the underlying data), plots, and a results JSON
consumed by build_report.js.

USAGE:
    python3 task4_run.py                  # N=10000 (assignment default)
    python3 task4_run.py --n 2000         # smaller N for a quick check
    python3 task4_run.py --seed-colreg 42 --seed-blind 43
"""

import argparse
import json
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import ship_data as sd
import task4_mc_engine as mc

NM = 1852.0


def plot_task4(D, censored, scenario_name, out_path, n_points=200, bins=40):
    D_nm = D / NM
    n = len(D_nm)
    n_cens = int(censored.sum())

    x_vals = np.linspace(D_nm.min(), D_nm.max(), n_points)
    p_coll = np.array([(D_nm > x).sum() / n for x in x_vals])

    fig, ax1 = plt.subplots(figsize=(8, 5.5))
    ax1.hist(D_nm, bins=bins, color="steelblue", alpha=0.65, edgecolor="white",
             label="Frequency (histogram)")
    ax1.set_xlabel("Minimum safe distance (nautical miles)")
    ax1.set_ylabel("Frequency", color="steelblue")
    ax1.tick_params(axis="y", labelcolor="steelblue")

    ax2 = ax1.twinx()
    ax2.plot(x_vals, p_coll, color="crimson", linewidth=2.2, label="P(collision)")
    ax2.set_ylabel("P(collision)", color="crimson")
    ax2.tick_params(axis="y", labelcolor="crimson")
    ax2.set_ylim(0, 1.05)

    title = f"Head-on, {scenario_name}: minimum safe distance (N={n})"
    if n_cens > 0:
        title += f"\n({n_cens} trials, {100*n_cens/n:.1f}%, censored at search cap)"
    ax1.set_title(title)

    l1, lab1 = ax1.get_legend_handles_labels()
    l2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lab1 + lab2, loc="upper right")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def run_and_save(n, scenario, seed, tag):
    print(f"=== {scenario} (N={n}, seed={seed}) ===")
    t0 = time.time()
    D, d1, d2, v1, v2, cens = mc.run_monte_carlo(n, scenario, seed=seed, verbose=True)
    dt = time.time() - t0
    print(f"Done in {dt:.1f}s. censored={cens.sum()} ({100*cens.sum()/n:.1f}%)")

    # raw sample, for full transparency / anyone who wants to re-analyse it
    df = pd.DataFrame({
        "delta1_deg": d1, "delta2_deg": d2,
        "V1_kn": v1, "V2_kn": v2,
        "min_safe_distance_m": D, "censored": cens,
    })
    df.to_csv(f"outputs/task4_{tag}_raw_sample.csv", index=False)

    plot_task4(D, cens, scenario, f"figures/task4_{tag}.png")

    stats = {
        "scenario": scenario, "N": int(n), "seed": seed,
        "censored_count": int(cens.sum()), "censored_pct": float(100 * cens.sum() / n),
        "min_nm": float(D.min() / NM), "max_nm": float(D.max() / NM),
        "mean_nm": float(D.mean() / NM), "median_nm": float(np.median(D) / NM),
        # distance at which the search stopped for still-unresolved trials
        "search_stop_m": float(D[cens].max()) if cens.any() else None,
        "search_cap_m": float(mc.D0 + mc.MAX_ROUNDS * mc.INCREMENT),
        "runtime_s": dt,
    }
    return stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--seed-colreg", type=int, default=42)
    ap.add_argument("--seed-blind", type=int, default=43)
    args = ap.parse_args()

    results = {}
    results["COLREG-COLREG"] = run_and_save(args.n, "COLREG-COLREG", args.seed_colreg, "colreg_colreg")
    results["Blind-Blind"] = run_and_save(args.n, "Blind-Blind", args.seed_blind, "blind_blind")

    with open("outputs/task4_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved outputs/task4_results.json, figures/task4_*.png, outputs/task4_*_raw_sample.csv")
