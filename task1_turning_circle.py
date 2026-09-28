"""
MSMD Assignment 2026/2027 - Project 9, Task 1
Turning manoeuvre simulation - KCS - first-order Nomoto model.
Uses the corrected, vessel-specific T from ship_data.py (see that module's
docstring for the derivation) instead of a shared 100 s placeholder.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon

import ship_data as sd
from engine import VesselState

DT = 0.2


def simulate_turning_circle():
    ship = sd.VESSEL1  # KCS
    sign = -1.0 if ship["turn_side"] == "starboard" else +1.0  # port -> psi grows
    delta_target = sign * sd.RUDDER_MAX_DEG

    s = VesselState(ship, 0.0, 0.0, 0.0, delta_target)
    heading_target = np.radians(sd.HEADING_TARGET_DEG)

    hist = {"t": [], "delta": [], "r": [], "psi_deg": [], "beta_deg": [], "x": [], "y": [], "V": []}
    t90 = t180 = None
    x90 = y90 = None

    t = 0.0
    while abs(s.psi) < heading_target:
        delta = s.step(t, DT)
        t += DT

        hist["t"].append(t)
        hist["delta"].append(delta)
        hist["r"].append(s.r)
        hist["psi_deg"].append(np.degrees(s.psi))
        hist["beta_deg"].append(np.degrees(s.beta))
        hist["x"].append(s.x)
        hist["y"].append(s.y)
        hist["V"].append(s.V)

        if t90 is None and abs(s.psi) >= np.radians(90):
            t90, x90, y90 = t, s.x, s.y
        if t180 is None and abs(s.psi) >= np.radians(180):
            t180 = t

    for k in hist:
        hist[k] = np.array(hist[k])

    advance = y90
    transfer = abs(x90)
    if t180 is not None:
        idx180 = np.argmax(np.abs(hist["psi_deg"]) >= 180)
        tactical_diameter = abs(hist["x"][idx180])
    else:
        tactical_diameter = None

    steady_mask = hist["t"] > 0.9 * hist["t"][-1]
    r_steady = np.mean(hist["r"][steady_mask])
    V_steady = np.mean(hist["V"][steady_mask])
    beta_steady = np.mean(hist["beta_deg"][steady_mask])
    idx_initial = min(int(2.0 / DT), len(hist["r"]) - 1)
    yaw_rate_initial = hist["r"][idx_initial]
    diameter_of_turn = 2 * V_steady / abs(r_steady)

    params = {
        "ship": ship["name"], "K": ship["K"], "T": ship["T"],
        "t90_s": t90, "t180_s": t180,
        "advance_m": advance, "advance_Lpp": advance / ship["Lpp"],
        "transfer_m": transfer, "transfer_Lpp": transfer / ship["Lpp"],
        "tactical_diameter_m": tactical_diameter,
        "tactical_diameter_Lpp": (tactical_diameter / ship["Lpp"]) if tactical_diameter else None,
        "diameter_of_turn_m": diameter_of_turn, "diameter_of_turn_Lpp": diameter_of_turn / ship["Lpp"],
        "yaw_rate_initial_deg_s": np.degrees(yaw_rate_initial),
        "yaw_rate_steady_deg_s": np.degrees(r_steady),
        "speed_steady_turn_kn": V_steady / sd.KN_TO_MS,
        "drift_angle_steady_deg": beta_steady,
    }
    return hist, params


def plot_turning_circle(hist, params, out_path):
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(hist["x"], hist["y"], color="tab:blue", label=f"{params['ship']} - Nomoto simulation")
    ax.plot(0, 0, "ko", markersize=5)
    ax.annotate("Rudder execute", (0, 0), textcoords="offset points", xytext=(8, -12), fontsize=9)
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    ax.set_title(f"{params['ship']} turning manoeuvre ({int(sd.HEADING_TARGET_DEG)} deg, "
                 f"T={params['T']:.1f}s)")
    ax.axis("equal"); ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def ship_polygon_local(length, beam):
    l2, b2 = length / 2.0, beam / 2.0
    return np.array([[0.0, l2], [b2, l2 * 0.6], [b2, -l2], [-b2, -l2], [-b2, l2 * 0.6]])


def animate_turning_circle(hist, ship_name, Lpp, B, out_path, fps=25, speed_up=15):
    step = max(1, int(round(speed_up / DT / fps)))
    idx = np.arange(0, len(hist["t"]), step)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(hist["x"], hist["y"], color="lightgray", linewidth=1.5, zorder=1)
    ax.plot(0, 0, "ko", markersize=5, zorder=2)
    track_line, = ax.plot([], [], color="tab:blue", linewidth=2, zorder=2)

    margin = 0.1 * max(hist["x"].max() - hist["x"].min(), hist["y"].max() - hist["y"].min(), 1.0)
    ax.set_xlim(hist["x"].min() - margin, hist["x"].max() + margin)
    ax.set_ylim(hist["y"].min() - margin, hist["y"].max() + margin)
    ax.set_aspect("equal"); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)"); ax.grid(alpha=0.3)
    title = ax.set_title("")

    local_poly = ship_polygon_local(Lpp, B)
    ship_patch = Polygon(local_poly, closed=True, facecolor="steelblue", edgecolor="black", zorder=3)
    ax.add_patch(ship_patch)

    def init():
        track_line.set_data([], [])
        ship_patch.set_xy(local_poly)
        return track_line, ship_patch, title

    def update(frame_i):
        i = idx[frame_i]
        track_line.set_data(hist["x"][:i + 1], hist["y"][:i + 1])
        psi = np.radians(hist["psi_deg"][i])
        c, s = np.cos(psi), np.sin(psi)
        rot = np.array([[c, s], [-s, c]])
        world_poly = local_poly @ rot.T + np.array([hist["x"][i], hist["y"][i]])
        ship_patch.set_xy(world_poly)
        title.set_text(f"{ship_name} turning manoeuvre - t = {hist['t'][i]:.0f} s, "
                        f"heading change = {hist['psi_deg'][i]:.0f} deg")
        return track_line, ship_patch, title

    ani = animation.FuncAnimation(fig, update, frames=len(idx), init_func=init, blit=False,
                                   interval=1000 / fps)
    writer = animation.FFMpegWriter(fps=fps, bitrate=2400)
    ani.save(out_path, writer=writer)
    plt.close(fig)


if __name__ == "__main__":
    hist, params = simulate_turning_circle()
    print(f"=== {params['ship']} turning circle (T={params['T']:.1f}s, corrected) ===")
    for k, v in params.items():
        print(f"  {k:28s}: {v}")

    plot_turning_circle(hist, params, "figures/task1_kcs_turning_circle.png")
    animate_turning_circle(hist, params["ship"], sd.VESSEL1["Lpp"], sd.VESSEL1["B"],
                            "figures/task1_kcs_turning_circle.mp4")

    with open("outputs/task1_results.json", "w") as f:
        json.dump(params, f, indent=2, default=lambda o: None if o is None else float(o))
    print("\nSaved figures/task1_kcs_turning_circle.png, .mp4, outputs/task1_results.json")
