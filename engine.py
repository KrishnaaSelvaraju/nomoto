"""
MSMD Assignment 2026/2027 - Project 9
engine.py - Shared first-order Nomoto stepping + Separating Axis Theorem
collision engine, used by task1_turning_circle.py and task2_encounter.py.

Model equations follow Lotovskyi & Teixeira (2023), Eqs. 4-17, validated in
Task 1 against that paper's own worked example (advance/tactical
diameter/turning radius matched within ~0.1-4%).

Coordinate convention: origin (0,0), heading psi=0 means travelling along
+y (i.e. at zero rudder, the ship/rudder are parallel to the y-axis).
Positive rudder = turn to STARBOARD (increases psi); negative = PORT.
"""

import numpy as np

import ship_data as sd


class VesselState:
    """Single-vessel Nomoto state, stepped with a pure open-loop rudder
    command (no PID/PD control anywhere)."""

    def __init__(self, ship, x0, y0, psi0_deg, delta_target_deg):
        self.ship = ship
        self.x, self.y = x0, y0
        self.psi = np.radians(psi0_deg)
        self.r = 0.0
        self.beta = 0.0
        self.V = ship["V0"]
        self.delta_target = np.radians(delta_target_deg)  # signed: + = starboard

    def step(self, t, dt):
        ship = self.ship
        delta = np.sign(self.delta_target) * min(abs(self.delta_target),
                                                   np.radians(sd.RUDDER_RATE) * t)

        self.r += ((ship["K"] * delta - self.r) / ship["T"]) * dt
        self.beta += ((ship["K_beta"] * delta - self.beta) / ship["T"]) * dt
        self.psi += self.r * dt

        C_Vred_delta = (abs(delta) / np.radians(sd.RUDDER_MAX_DEG)) * ship["C_Vred_35"]
        if abs(ship["beta_ST"]) > 1e-9:
            V = ship["V0"] * (1.0 - C_Vred_delta *
                               (np.tan(self.beta) ** 2) / (np.tan(ship["beta_ST"]) ** 2))
        else:
            V = ship["V0"]
        self.V = max(V, 0.1 * ship["V0"])

        cog = self.psi - self.beta
        d = self.V * dt
        self.x += d * np.sin(cog)
        self.y += d * np.cos(cog)
        return np.degrees(delta)

    def corners(self):
        return rect_corners(self.x, self.y, self.psi, self.ship["Lpp"], self.ship["B"])

    def centroid(self):
        return np.array([self.x, self.y])


def rect_corners(cx, cy, psi, Lpp, B):
    hl, hb = Lpp / 2.0, B / 2.0
    f = np.array([np.sin(psi), np.cos(psi)])
    r = np.array([np.cos(psi), -np.sin(psi)])
    center = np.array([cx, cy])
    return np.array([center + s1 * hl * f + s2 * hb * r
                      for s1 in (1, -1) for s2 in (1, -1)])


def sat_overlap(corners1, corners2):
    def axes_of(corners):
        axes = []
        for i in range(2):
            edge = corners[i + 1] - corners[i]
            normal = np.array([-edge[1], edge[0]])
            n = np.linalg.norm(normal)
            if n > 1e-9:
                axes.append(normal / n)
        return axes

    for axis in axes_of(corners1) + axes_of(corners2):
        p1, p2 = corners1 @ axis, corners2 @ axis
        if p1.max() < p2.min() or p2.max() < p1.min():
            return False
    return True


def collision_check(corners1, corners2, centroid1, centroid2, D_initial):
    if sat_overlap(corners1, corners2):
        return 1  # collision
    if np.linalg.norm(centroid2 - centroid1) > D_initial:
        return 0  # confirmed safe / diverging past starting separation
    return 2  # inconclusive, keep going


def find_minimum_safe_distance(delta1_target_deg, delta2_target_deg,
                                dt=0.5, max_sim_time=900.0, max_trials=300,
                                verbose=True):
    """Head-on encounter: Vessel1 at (0,0) heading north, Vessel2 at (0,D)
    heading south, closing. Increases D until SAT shows no collision and
    the vessels end up farther apart than their starting separation."""
    D = (sd.VESSEL1["Lpp"] + sd.VESSEL2["Lpp"]) / 2.0
    increment = 0.25 * min(sd.VESSEL1["Lpp"], sd.VESSEL2["Lpp"])

    trial = 0
    while trial < max_trials:
        trial += 1
        s1 = VesselState(sd.VESSEL1, 0.0, 0.0, 0.0, delta1_target_deg)
        s2 = VesselState(sd.VESSEL2, 0.0, D, 180.0, delta2_target_deg)

        cols = ["t", "x", "y", "c1x", "c1y", "c2x", "c2y", "c3x", "c3y", "c4x", "c4y",
                "r_deg_s", "psi_deg", "beta_deg", "V_ms", "delta_deg", "D_trial"]
        rows1, rows2 = [], []
        t = 0.0
        status = 2
        while t < max_sim_time:
            d1 = s1.step(t, dt)
            d2 = s2.step(t, dt)
            t += dt

            c1, c2 = s1.corners(), s2.corners()
            rows1.append([t, s1.x, s1.y, *c1.flatten(), np.degrees(s1.r),
                          np.degrees(s1.psi), np.degrees(s1.beta), s1.V, d1, D])
            rows2.append([t, s2.x, s2.y, *c2.flatten(), np.degrees(s2.r),
                          np.degrees(s2.psi), np.degrees(s2.beta), s2.V, d2, D])

            status = collision_check(c1, c2, s1.centroid(), s2.centroid(), D)
            if status in (0, 1):
                break

        if verbose:
            print(f"  trial {trial}: D = {D:8.1f} m -> "
                  f"{'COLLISION' if status == 1 else 'SAFE'} at t = {t:.1f} s")

        if status == 0:
            return D, np.array(rows1), np.array(rows2), cols
        D += increment

    raise RuntimeError("Search did not converge within max_trials.")
