#!/usr/bin/env python3
"""Measure the colour of part of a picture in HSV, to tune colour detection.

    ros2 run dofbot_lab hsv_probe.py                                   # middle of snapshots/usb_cam.png
    ros2 run dofbot_lab hsv_probe.py usb_cam.png 290 120 40 40         # a box: x y width height (pixels)
    ros2 run dofbot_lab hsv_probe.py camera.png 300 60 40 40           # a simulator snapshot

Pictures are looked up in ~/dofbot_ws/src/snapshots unless you give a full path.
Prints the typical H, S and V inside the box and suggests a range for
COLOR_RANGES, and saves hsv_probe.png with the box drawn, so you can check you
measured the right thing. Take the snapshot first with snapshot.py.
"""
import os
import sys

import cv2
import numpy as np

SNAPSHOT_DIR = os.path.expanduser("~/dofbot_ws/src/snapshots")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--ros-args")]
    name = args[0] if args else "usb_cam.png"
    path = name if os.path.isabs(name) or os.path.exists(name) else os.path.join(SNAPSHOT_DIR, name)
    picture = cv2.imread(path)
    if picture is None:
        print(f"Can't read {path}. Take a snapshot first, e.g.: "
              "ros2 run dofbot_lab snapshot.py /usb_cam/image_raw/compressed")
        return 1

    height, width = picture.shape[:2]
    if len(args) >= 5:
        x, y, w, h = (int(v) for v in args[1:5])
    else:
        w, h = 40, 40
        x, y = (width - w) // 2, (height - h) // 2
    x, y = max(0, min(x, width - 1)), max(0, min(y, height - 1))
    box = picture[y:y + h, x:x + w]

    hsv = cv2.cvtColor(box, cv2.COLOR_BGR2HSV).reshape(-1, 3).astype(float)
    low, mid, high = np.percentile(hsv, [10, 50, 90], axis=0)
    print(f"Box x={x} y={y} w={box.shape[1]} h={box.shape[0]} in {path} ({width}x{height})")
    print(f"  H (hue)        typical {mid[0]:5.0f}   (10%..90%: {low[0]:.0f}..{high[0]:.0f})")
    print(f"  S (saturation) typical {mid[1]:5.0f}   (10%..90%: {low[1]:.0f}..{high[1]:.0f})")
    print(f"  V (value)      typical {mid[2]:5.0f}   (10%..90%: {low[2]:.0f}..{high[2]:.0f})")
    if high[0] - low[0] > 40:
        print("  The hue varies a lot: the box covers more than one colour, or red (hue wraps at 180).")
    h_lo, h_hi = max(0, int(low[0]) - 5), min(180, int(high[0]) + 5)
    s_lo, v_lo = max(0, int(low[1]) - 30), max(0, int(low[2]) - 30)
    print(f"  Suggested range: (({h_lo}, {s_lo}, {v_lo}), ({h_hi}, 255, 255))")

    marked = picture.copy()
    cv2.rectangle(marked, (x, y), (x + box.shape[1], y + box.shape[0]), (255, 0, 255), 2)
    out = os.path.join(SNAPSHOT_DIR, "hsv_probe.png")
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    cv2.imwrite(out, marked)
    print(f"Saved {out} with the box drawn")
    return 0


if __name__ == "__main__":
    sys.exit(main())
