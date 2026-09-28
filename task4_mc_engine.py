"""
MSMD Assignment 2026/2027 - Project 9, Task 4
Vectorized Monte Carlo minimum-safe-distance engine (same algorithm as
engine.py, batched across all N trials at once with numpy so N=10000 runs
in ~1-2 minutes instead of ~28). Uses each vessel's own corrected T from
ship_data.py (not a shared placeholder).
"""

import numpy as np
import ship_data as sd

DT = 0.5
MAX_SIM_TIME = 900.0
MAX_ROUNDS = 100
STAGNATION_PATIENCE = 30

D0 = (sd.VESSEL1["Lpp"] + sd.VESSEL2["Lpp"]) / 2.0
INCREMENT = 0.25 * min(sd.VESSEL1["Lpp"], sd.VESSEL2["Lpp"])


def rect_corners_vec(cx, cy, psi, Lpp, B):
    hl, hb = Lpp / 2.0, B / 2.0
    f = np.stack([np.sin(psi), np.cos(psi)], axis=-1)
    r = np.stack([np.cos(psi), -np.sin(psi)], axis=-1)
    center = np.stack([cx, cy], axis=-1)
    corners = [center + s1 * hl * f + s2 * hb * r for s1 in (1, -1) for s2 in (1, -1)]
    return np.stack(corners, axis=1)


def axes_of_vec(corners):
    axes = []
    for i in range(2):
        edge = corners[:, i + 1, :] - corners[:, i, :]
        normal = np.stack([-edge[:, 1], edge[:, 0]], axis=-1)
        norm = np.linalg.norm(normal, axis=-1, keepdims=True)
        norm = np.where(norm < 1e-9, 1e-9, norm)
        axes.append(normal / norm)
    return axes


def sat_overlap_vec(corners1, corners2):
    axes = axes_of_vec(corners1) + axes_of_vec(corners2)
    overlap = np.ones(corners1.shape[0], dtype=bool)
    for axis in axes:
        p1 = np.einsum("nij,nj->ni", corners1, axis)
        p2 = np.einsum("nij,nj->ni", corners2, axis)
        sep = (p1.max(axis=1) < p2.min(axis=1)) | (p2.max(axis=1) < p1.min(axis=1))
        overlap &= ~sep
    return overlap


def sample_rudder(n, scenario, rng):
    if scenario == "COLREG-COLREG":
        d1 = np.round(rng.triangular(1.0, 15.0, 35.0, size=n))
        d2 = np.round(rng.triangular(1.0, 15.0, 35.0, size=n))
        return d1, d2  # both positive -> both starboard
    elif scenario == "Blind-Blind":
        d1 = np.round(rng.uniform(-35.0, 35.0, size=n))
        d2 = np.round(rng.uniform(-35.0, 35.0, size=n))
        return d1, d2
    else:
        raise ValueError(scenario)


def run_monte_carlo(n, scenario, seed=None, verbose=True):
    rng = np.random.default_rng(seed)
    delta1_deg, delta2_deg = sample_rudder(n, scenario, rng)
    V1_kn = rng.uniform(sd.VESSEL1_BASE["V0_kn"] - 2, sd.VESSEL1_BASE["V0_kn"] + 2, size=n)
    V2_kn = rng.uniform(sd.VESSEL2_BASE["V0_kn"] - 2, sd.VESSEL2_BASE["V0_kn"] + 2, size=n)
    V1_0 = V1_kn * sd.KN_TO_MS
    V2_0 = V2_kn * sd.KN_TO_MS

    delta_R = np.radians(sd.RUDDER_MAX_DEG)
    K1 = V1_0 * sd.V_ST_OVER_V0 / (delta_R * sd.VESSEL1["R"])
    K2 = V2_0 * sd.V_ST_OVER_V0 / (delta_R * sd.VESSEL2["R"])
    # NOTE: T is NOT re-derived per-trial speed here -- it uses each
    # vessel's fixed, corrected T from ship_data.py (T scales with the
    # vessel's nominal L/V0, not the per-trial sampled speed), matching
    # the assignment's statement that only rudder angle and approach
    # speed are Monte Carlo variables; T itself is a vessel property.
    T1, T2 = sd.VESSEL1["T"], sd.VESSEL2["T"]
    K_BETA1, K_BETA2 = sd.VESSEL1["K_beta"], sd.VESSEL2["K_beta"]
    BETA_ST1, BETA_ST2 = sd.VESSEL1["beta_ST"], sd.VESSEL2["beta_ST"]
    C_VRED_35 = sd.VESSEL1["C_Vred_35"]  # same for both (both use V_ST_OVER_V0=0.65)

    delta1_target = np.radians(delta1_deg)
    delta2_target = np.radians(delta2_deg)

    D = np.full(n, D0)
    final_D = np.full(n, np.nan)
    censored = np.zeros(n, dtype=bool)
    active = np.ones(n, dtype=bool)

    round_i = 0
    stagnant_rounds = 0
    prev_active_count = active.sum()
    while active.any() and round_i < MAX_ROUNDS:
        round_i += 1
        idx = np.where(active)[0]
        n_act = len(idx)

        r1 = np.zeros(n_act); beta1 = np.zeros(n_act); psi1 = np.zeros(n_act)
        x1 = np.zeros(n_act); y1 = np.zeros(n_act)
        r2 = np.zeros(n_act); beta2 = np.zeros(n_act); psi2 = np.full(n_act, np.pi)
        x2 = np.zeros(n_act); y2 = D[idx].copy()

        resolved = np.zeros(n_act, dtype=bool)
        status = np.full(n_act, 2)
        t = 0.0

        d1t = delta1_target[idx]; d2t = delta2_target[idx]
        k1 = K1[idx]; k2 = K2[idx]
        v1_0 = V1_0[idx]; v2_0 = V2_0[idx]

        while (not resolved.all()) and t < MAX_SIM_TIME:
            delta1 = np.sign(d1t) * np.minimum(np.abs(d1t), np.radians(sd.RUDDER_RATE) * t)
            r1 += ((k1 * delta1 - r1) / T1) * DT
            beta1 += ((K_BETA1 * delta1 - beta1) / T1) * DT
            psi1 += r1 * DT
            cvred1 = (np.abs(delta1) / delta_R) * C_VRED_35
            Vv1 = v1_0 * (1.0 - cvred1 * (np.tan(beta1) ** 2) / (np.tan(BETA_ST1) ** 2))
            Vv1 = np.maximum(Vv1, 0.1 * v1_0)
            cog1 = psi1 - beta1
            x1 += Vv1 * DT * np.sin(cog1)
            y1 += Vv1 * DT * np.cos(cog1)

            delta2 = np.sign(d2t) * np.minimum(np.abs(d2t), np.radians(sd.RUDDER_RATE) * t)
            r2 += ((k2 * delta2 - r2) / T2) * DT
            beta2 += ((K_BETA2 * delta2 - beta2) / T2) * DT
            psi2 += r2 * DT
            cvred2 = (np.abs(delta2) / delta_R) * C_VRED_35
            Vv2 = v2_0 * (1.0 - cvred2 * (np.tan(beta2) ** 2) / (np.tan(BETA_ST2) ** 2))
            Vv2 = np.maximum(Vv2, 0.1 * v2_0)
            cog2 = psi2 - beta2
            x2 += Vv2 * DT * np.sin(cog2)
            y2 += Vv2 * DT * np.cos(cog2)

            t += DT

            corners1 = rect_corners_vec(x1, y1, psi1, sd.VESSEL1["Lpp"], sd.VESSEL1["B"])
            corners2 = rect_corners_vec(x2, y2, psi2, sd.VESSEL2["Lpp"], sd.VESSEL2["B"])
            coll = sat_overlap_vec(corners1, corners2)
            dist = np.hypot(x2 - x1, y2 - y1)

            newly_coll = coll & (~resolved)
            newly_safe = (~coll) & (dist > D[idx]) & (~resolved)
            status[newly_coll] = 1
            status[newly_safe] = 0
            resolved |= newly_coll | newly_safe

        status[~resolved] = 1

        safe_local = status == 0
        idx_safe = idx[safe_local]
        final_D[idx_safe] = D[idx_safe]
        active[idx_safe] = False

        fail_local = status == 1
        idx_fail = idx[fail_local]
        D[idx_fail] += INCREMENT

        if verbose and round_i % 25 == 0:
            print(f"  round {round_i}: {active.sum()} / {n} trials still active")

        cur_active_count = active.sum()
        if cur_active_count < n:
            if cur_active_count == prev_active_count:
                stagnant_rounds += 1
            else:
                stagnant_rounds = 0
            prev_active_count = cur_active_count
        if stagnant_rounds >= STAGNATION_PATIENCE:
            if verbose:
                print(f"  round {round_i}: no progress for {STAGNATION_PATIENCE} rounds "
                      f"({cur_active_count} trials stuck) -- censoring and stopping search.")
            break

    if active.any():
        censored[active] = True
        final_D[active] = D[active]

    return final_D, delta1_deg, delta2_deg, V1_kn, V2_kn, censored
