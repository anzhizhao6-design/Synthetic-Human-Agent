"""Cursor movement.

Drop-in replacements for the teammate's `human_curve_move` and
`human_move_and_click`, with the same signatures, so you can paste these over
the ones in his file (or `from andie.cursor import human_curve_move, human_move_and_click`).

Upgrades over the current version:
  - TRUE cubic Bezier path (his version is piecewise-linear waypoints), so the
    arc is smooth and never kinks.
  - Variable speed along the path (ease-in / ease-out) => slow start, faster
    middle, slow approach, like a real hand. Fitts's-law-style: farther targets
    take proportionally longer.
  - Occasional overshoot then correction (humans overshoot ~1 in 5 moves).
  - Sub-pixel jitter and a final aim micro-correction.

Why this helps scoring: Human Entropy & Timing (30%) rewards natural, varied
motion rather than linear teleports. Clicks land where recognition.py says a
REAL element is, not random screen points.
"""
from __future__ import annotations

import math
import random
import time

try:
    import pyautogui  # type: ignore
    pyautogui.PAUSE = 0.0
    pyautogui.FAILSAFE = True
except Exception:  # pragma: no cover - lets this import off-Windows
    pyautogui = None

_rng = random.Random()


def _cubic_bezier(p0, p1, p2, p3, t):
    mt = 1 - t
    x = (mt**3) * p0[0] + 3 * (mt**2) * t * p1[0] + 3 * mt * (t**2) * p2[0] + (t**3) * p3[0]
    y = (mt**3) * p0[1] + 3 * (mt**2) * t * p1[1] + 3 * mt * (t**2) * p2[1] + (t**3) * p3[1]
    return x, y


def _ease(t):
    # ease-in-out: smootherstep. Gives slow-fast-slow velocity.
    return t * t * t * (t * (t * 6 - 15) + 10)


def _control_points(x0, y0, x1, y1):
    """Two control points offset perpendicular to the straight line, so the
    path bows out like a hand sweep. Offset scales with distance (capped)."""
    dist = math.hypot(x1 - x0, y1 - y0)
    # perpendicular unit vector
    if dist < 1:
        return (x0, y0), (x1, y1)
    px, py = -(y1 - y0) / dist, (x1 - x0) / dist
    amp = min(max(dist * _rng.uniform(0.08, 0.22), 15), 120)
    # control points at ~1/3 and ~2/3 along, pushed to one side (random side)
    side = _rng.choice((-1, 1))
    c1 = (x0 + (x1 - x0) / 3 + px * amp * side * _rng.uniform(0.6, 1.0),
          y0 + (y1 - y0) / 3 + py * amp * side * _rng.uniform(0.6, 1.0))
    c2 = (x0 + 2 * (x1 - x0) / 3 + px * amp * side * _rng.uniform(0.3, 0.8),
          y0 + 2 * (y1 - y0) / 3 + py * amp * side * _rng.uniform(0.3, 0.8))
    return c1, c2


def _travel(x0, y0, x1, y1):
    """Move the cursor along one smooth Bezier arc with variable speed."""
    if pyautogui is None:
        return
    dist = math.hypot(x1 - x0, y1 - y0)
    # Fitts-ish total time: base + log of distance, with jitter
    total = _rng.uniform(0.25, 0.5) + 0.0006 * dist + 0.12 * math.log2(1 + dist / 40)
    steps = max(12, int(dist / 12))
    c1, c2 = _control_points(x0, y0, x1, y1)
    prev_t = 0.0
    for i in range(1, steps + 1):
        t = _ease(i / steps)
        x, y = _cubic_bezier((x0, y0), c1, c2, (x1, y1), t)
        # tiny sub-pixel tremor
        x += _rng.uniform(-0.6, 0.6)
        y += _rng.uniform(-0.6, 0.6)
        pyautogui.moveTo(int(round(x)), int(round(y)), duration=0)
        dt = (t - prev_t) * total
        if dt > 0:
            time.sleep(min(dt, 0.08))
        prev_t = t


def human_curve_move(start_x, start_y, end_x, end_y):
    """Drop-in replacement. Smooth Bezier move with occasional overshoot."""
    if pyautogui is None:
        return
    # ~20% of moves overshoot slightly, then correct — very human.
    if _rng.random() < 0.20:
        over = 1.0 + _rng.uniform(0.04, 0.12)
        ox = int(start_x + (end_x - start_x) * over)
        oy = int(start_y + (end_y - start_y) * over)
        _travel(start_x, start_y, ox, oy)
        time.sleep(_rng.uniform(0.05, 0.15))
        _travel(ox, oy, end_x, end_y)
    else:
        _travel(start_x, start_y, end_x, end_y)
    # final aim micro-corrections (humans nudge onto the target)
    for _ in range(_rng.randint(1, 3)):
        pyautogui.moveRel(_rng.randint(-3, 3), _rng.randint(-3, 3),
                          duration=_rng.uniform(0.08, 0.2))


def human_move_and_click(x, y, button="left"):
    """Drop-in replacement. Curve to (x,y) with a human aim offset, then click."""
    if pyautogui is None:
        return
    sx, sy = pyautogui.position()
    tx = x + _rng.randint(-4, 4)          # humans don't hit the exact center
    ty = y + _rng.randint(-4, 4)
    human_curve_move(sx, sy, tx, ty)
    time.sleep(_rng.uniform(0.12, 0.4))   # pause before the click
    pyautogui.click(button=button)
    time.sleep(_rng.uniform(0.1, 0.3))
