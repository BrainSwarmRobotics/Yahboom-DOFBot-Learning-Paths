# Practical Session 2

Material for the second practical session on the Yahboom DofBot manipulator.

## Contents

- `AnyBot-Practical-Session-1.pdf` Recap of session one: platform overview, the
  terminal, workspace and package creation, and making a Python script run with
  `ros2 run`.
- `AnyBot-Practical-Session-2.pdf` Instructions for this session: topics,
  message types, services, actions, publishers and subscribers, and the two
  exercises against the live arm.
- `dofbot_practice/` ROS 2 C++ package students build and modify.

## Package

Two exercises, each supplied in both C++ and Python, with the same numbered
markers in either language so students can pick a language or read the two side
by side.

Exercise A is a fill-in-the-blanks skeleton. Every line the student has to write
is marked `FILL_IN_<n>` with a comment saying what belongs there and which `ros2`
command will tell them, but never the answer itself. Those files do not build or
run until the blanks are filled, which is deliberate: each blank left behind
produces an error that names it. Exercise B runs as given, so students have one
working node to check their toolchain against before Exercise A fights back.

| Exercise | C++ | Python |
| --- | --- | --- |
| A: subscribe to `/joint_states` | `joint_state_subscriber` | `joint_state_subscriber.py` |
| B: publish a trajectory to move the arm | `arm_command_publisher` | `arm_command_publisher.py` |

The Python nodes keep their `.py` extension when installed, so they never
collide with the compiled nodes and both can run at once. `CMakeLists.txt`
installs the C++ nodes with `install(TARGETS ...)` and the Python ones with
`install(PROGRAMS ...)`, which is the Session 1 block unchanged.

```
cd ~/dofbot_ws
colcon build --packages-select dofbot_practice
source install/setup.bash
ros2 pkg executables dofbot_practice      # should list all four
ros2 run dofbot_practice joint_state_subscriber      # C++
ros2 run dofbot_practice joint_state_subscriber.py   # Python
```

This directory sits under `dofbot_ws/src`, so it is seeded into every DofBot
user's workspace automatically and `colcon` finds the package by recursive
scan. The PDFs ride along with it so students have the instructions inside the
same workspace they are working in.
