"""
MSMD Assignment 2026/2027 - Project 9, Task 3
Compares Task 2's simulated minimum safe distance (read from
outputs/task2_results.json -- NOT hardcoded) with the geometric "critical
distance of give-way start" of Hashimoto & Okushima (1990).

    m_h_ij = D_ij / sin(theta),   D_ij = (B_i + B_j) / 2
"""

import json
import numpy as np
import matplotlib.pyplot as plt

import ship_data as sd


def hashimoto_okushima_head_on(D_ij, theta_deg):
    return D_ij / np.sin(np.radians(theta_deg))


if __name__ == "__main__":
    with open("outputs/task2_results.json") as f:
        task2 = json.load(f)

    D_ij = (sd.VESSEL1["B"] + sd.VESSEL2["B"]) / 2.0
    m_h_20 = hashimoto_okushima_head_on(D_ij, 20.0)
    m_h_30 = hashimoto_okushima_head_on(D_ij, 30.0)

    D_colreg_m = task2["COLREG-COLREG"]["D_min_m"]
    D_blind_m = task2["Blind-Blind"]["D_min_m"]

    print(f"Collision diameter D_ij = {D_ij:.1f} m")
    print(f"Hashimoto & Okushima, theta=20deg: {m_h_20:.1f} m")
    print(f"Hashimoto & Okushima, theta=30deg: {m_h_30:.1f} m")
    print(f"Task 2 COLREG-COLREG (from outputs/task2_results.json): {D_colreg_m:.1f} m")
    print(f"Task 2 Blind-Blind (reference only): {D_blind_m:.1f} m")
    print(f"Ratio (Task2 / Hashimoto theta=20): {D_colreg_m / m_h_20:.1f}x")

    labels = ["Hashimoto & Okushima\n(theta=20 deg)", "Hashimoto & Okushima\n(theta=30 deg)",
              "Task 2 simulation\n(COLREG-COLREG)", "Task 2 simulation\n(Blind-Blind, ref. only)"]
    values = [m_h_20, m_h_30, D_colreg_m, D_blind_m]
    colors = ["tab:green", "tab:green", "tab:blue", "lightsteelblue"]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    bars = ax.bar(labels, values, color=colors)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 20, f"{v:.0f} m",
                 ha="center", va="bottom", fontsize=10)
    ax.set_ylabel("Distance (m)")
    ax.set_title("Head-on encounter (KCS vs KVLCC2): minimum safe distance\n"
                  "geometric formula vs. dynamic simulation")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig("figures/task3_comparison.png", dpi=150)

    results = {
        "D_ij_m": D_ij, "theta_20_m": m_h_20, "theta_30_m": m_h_30,
        "task2_colreg_colreg_m": D_colreg_m, "task2_blind_blind_m": D_blind_m,
        "ratio_task2_over_hashimoto20": D_colreg_m / m_h_20,
    }
    with open("outputs/task3_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved figures/task3_comparison.png, outputs/task3_results.json")
