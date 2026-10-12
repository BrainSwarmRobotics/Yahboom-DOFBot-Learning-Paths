#!/usr/bin/env python3
"""Stack the blocks on the centre square again (simulator only).

    ros2 run dofbot_lab reset_blocks.py                       # yellow, red, green, blue (top first), as at the start
    ros2 run dofbot_lab reset_blocks.py --shuffle             # a random order
    ros2 run dofbot_lab reset_blocks.py blue red yellow green # your own order, top first
    ros2 run dofbot_lab reset_blocks.py red green             # a smaller stack; the other blocks go off the mat

Move the arm out of the way first (ros2 run dofbot_bringup dofbot_cmd home),
or it may knock the new stack over.
"""
import os
import random
import socket
import subprocess
import sys
import time

COLOURS = ["yellow", "red", "green", "blue"]   # the starting stack, top first
CENTRE = (0.0, 0.221)                          # the grey square on the mat (m, robot frame)
BLOCK = 0.03                                   # block size (m)
PARKING = [(0.60, -0.30), (0.66, -0.30), (0.72, -0.30), (0.78, -0.30)]  # far from the arm


def set_pose(name, x, y, z):
    """Teleport a model with Gazebo's set_pose service."""
    request = f'name: "{name}", position: {{x: {x}, y: {y}, z: {z}}}, orientation: {{w: 1}}'
    env = dict(os.environ, IGN_PARTITION="dofbot_" + socket.gethostname())  # see sim.launch.py
    result = subprocess.run(
        ["ign", "service", "-s", "/world/dofbot_world/set_pose",
         "--reqtype", "ignition.msgs.Pose", "--reptype", "ignition.msgs.Boolean",
         "--timeout", "3000", "--req", request],
        env=env, capture_output=True, text=True)
    return "data: true" in result.stdout


def main():
    args = [a.lower() for a in sys.argv[1:] if not a.startswith("--ros-args")]
    if "--shuffle" in args:
        order = random.sample(COLOURS, len(COLOURS))
    elif args:
        order = args
        if not set(order) <= set(COLOURS) or len(set(order)) != len(order):
            print(f"Give some of {', '.join(COLOURS)}, each at most once, top first.")
            return 1
    else:
        order = COLOURS

    # Park all blocks away from the mat first, so none is teleported into another.
    for colour, (x, y) in zip(COLOURS, PARKING):
        if not set_pose(f"block_{colour}", x, y, BLOCK / 2 + 0.001):
            print("The simulator did not answer. Is it running? (ros2 launch dofbot_lab sim.launch.py)")
            return 1
    time.sleep(0.5)

    # Then build the stack from the bottom up, letting each block settle.
    for level, colour in enumerate(reversed(order)):
        set_pose(f"block_{colour}", CENTRE[0], CENTRE[1], BLOCK / 2 + level * (BLOCK + 0.0005) + 0.0005)
        time.sleep(0.4)

    print("Stack on the centre square, top to bottom: " + ", ".join(order))
    left_out = [c for c in COLOURS if c not in order]
    if left_out:
        print("Off the mat: " + ", ".join(left_out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
