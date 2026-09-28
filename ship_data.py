"""
MSMD Assignment 2026/2027 - Project 9
ship_data.py - Vessel principal characteristics and Nomoto model parameters.

This is the SINGLE SOURCE OF TRUTH for vessel data, imported by every other
script (task1, task2, task4). Change a value here and re-run everything
downstream to propagate it.

============================================================================
IMPORTANT: Nomoto time constant T
============================================================================
Lotovskyi & Teixeira (2023) -- the paper the assignment cites for Task 1's
Nomoto model -- sample T from a triangular distribution "based on the
vessel's length and type" attributed to Silveira et al. (2016), but only
give the actual Tri(70, 100, 130) s numbers for their OWN 330 m case-study
cargo ship (their Table 1). The Silveira et al. (2016) paper itself
("Probabilistic modelling of evasive manoeuvring actions to avoid
collisions", MARTECH 2016 conference proceedings) is a paywalled conference
chapter with no accessible full text, and is not in this project's
reference set.

Rather than reuse a single generic T=100s placeholder for both KCS and
KVLCC2 (as earlier drafts of this work did), T is derived here using the
standard non-dimensionalisation from ship manoeuvring theory: the Nomoto
time constant scales with a ship's own length-over-speed ratio,

    T' = T * V / L   (approximately constant across similar ship types)

Using the ONE real data point available -- the reference paper's own
worked example (L=330 m, V=15 kn, T=100 s, their Table 1 / Figure 4) -- to
fix T', then applying that same T' to KCS and KVLCC2's own L and V gives a
distinct, physically grounded T for each vessel instead of one shared
placeholder. This is a standard, defensible naval-architecture scaling
approach; it is not the actual Silveira et al. (2016) table, and should be
replaced with the real table if it becomes available.
"""

import numpy as np

KN_TO_MS = 0.514444

# ---------------------------------------------------------------------
# Reference case (Lotovskyi & Teixeira 2023's own worked example, used
# ONLY to derive the non-dimensional T' scaling factor)
# ---------------------------------------------------------------------
REF_LPP = 330.0
REF_V0_KN = 15.0
REF_T = 100.0  # s, most-likely value of their Tri(70, 100, 130)

T_PRIME = REF_T * (REF_V0_KN * KN_TO_MS) / REF_LPP  # non-dimensional, ~2.338

# ---------------------------------------------------------------------
# Project 9 vessels (assignment Tables 1 and 3)
# ---------------------------------------------------------------------
VESSEL1_BASE = {"name": "KCS", "Lpp": 230.0, "B": 32.2, "V0_kn": 24.0, "turn_side": "port"}
VESSEL2_BASE = {"name": "KVLCC2", "Lpp": 320.0, "B": 58.0, "V0_kn": 15.5, "turn_side": "starboard"}

RUDDER_MAX_DEG = 35.0
RUDDER_RATE = 2.33          # deg/s
V_ST_OVER_V0 = 0.65         # midpoint of U(0.6, 0.7), Lotovskyi & Teixeira (2023) Eq. 9
HEADING_TARGET_DEG = 720.0  # Task 1 turning circle target


def nomoto_params(ship_base):
    """Compute K, T, K_beta, beta_ST for a vessel, given its Lpp and V0.

    T is derived from the length/speed scaling described in the module
    docstring (NOT a shared placeholder). K, K_beta, beta_ST follow
    Lotovskyi & Teixeira (2023) Eqs. 8, 9, 15 and the equation following
    their Eq. 9, exactly as validated in Tasks 1-2.
    """
    Lpp = ship_base["Lpp"]
    V0 = ship_base["V0_kn"] * KN_TO_MS
    R = 2.0 * Lpp                          # steady turning radius, SNAME (1989)
    delta_R = np.radians(RUDDER_MAX_DEG)

    V_STD_35 = V0 * V_ST_OVER_V0
    K = V_STD_35 / (delta_R * R)

    C_Vred_35 = 1.0 - V_ST_OVER_V0
    beta_lo = 18.0 * (Lpp / R)
    beta_hi = 22.5 * (Lpp / R) + 1.45
    beta_ST = np.radians(0.5 * (beta_lo + beta_hi))
    K_beta = beta_ST / delta_R

    T = T_PRIME * Lpp / V0   # <-- corrected per-vessel T (see module docstring)

    ship = dict(ship_base)
    ship.update(V0=V0, R=R, K=K, T=T, K_beta=K_beta, beta_ST=beta_ST, C_Vred_35=C_Vred_35)
    return ship


VESSEL1 = nomoto_params(VESSEL1_BASE)
VESSEL2 = nomoto_params(VESSEL2_BASE)

if __name__ == "__main__":
    import json
    print(f"T' (non-dimensional, from reference ship) = {T_PRIME:.4f}\n")
    out = {"T_prime": T_PRIME, "reference": {"Lpp": REF_LPP, "V0_kn": REF_V0_KN, "T": REF_T}}
    for key, v in (("VESSEL1", VESSEL1), ("VESSEL2", VESSEL2)):
        print(f"{v['name']}: Lpp={v['Lpp']} m, V0={v['V0_kn']} kn "
              f"({v['V0']:.3f} m/s), R={v['R']:.1f} m")
        print(f"  K       = {v['K']:.6f} 1/s")
        print(f"  T       = {v['T']:.2f} s   <-- corrected (was 100 s placeholder for both)")
        print(f"  K_beta  = {v['K_beta']:.4f}")
        print(f"  beta_ST = {np.degrees(v['beta_ST']):.2f} deg")
        print()
        out[key] = {k: (float(val) if isinstance(val, (int, float, np.floating)) else val)
                    for k, val in v.items()}
        out[key]["beta_ST_deg"] = float(np.degrees(v["beta_ST"]))

    import os
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/ship_data.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Saved outputs/ship_data.json")

