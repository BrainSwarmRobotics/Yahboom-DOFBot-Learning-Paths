# 🏆 Capstone on the Real Arm

📍 **Level:** Intermediate
📚 **Topic:** Running the block sorter on real hardware, safely

------

## 🎯 The Task

The same task as in Part 1, module 13, on the real DOFBOT:

1. Read the stack on the grey square with the real camera
2. Sort the blocks onto their colour squares

The program is the one you wrote in Part 1 (or `exercise_8_block_sorter`, built with `colcon build --packages-select exercise_8_block_sorter`), with two parameters changed. Your instructor rebuilds the stack between slots.

`Rebuilding the stack with the arm (restore:=true) was unreliable even in the simulator (Part 1, module 13). Use it on the real arm only if your instructor asks you to, and watch it closely.`

------

## 📋 Before Your Slot

In your preview session, in the simulator:

- [ ] Your `block_sorter.py` sorts a shuffled stack, several times in a row
- [ ] If you tuned colours in module 5, the new `COLOR_RANGES` are in your `block_sorter.py` too
- [ ] It is built (`colcon build --packages-select my_dofbot`)

------

## 🔍 Step 1: Check the Table

Connect (`use_robot`), open the Robot Video Feed, and look:

- Is the colour mat in front of the arm, with the four blocks stacked on the grey square?
- Is anything else on the mat?

If the stack is not there, or the mat looks different from the simulator, **don't run the sorter**: tell your instructor.

Then look through the arm's camera from the `look` pose:

```
ros2 run dofbot_bringup dofbot_cmd -t 3 ready
ros2 run dofbot_bringup dofbot_cmd -t 3 servos 90 135 15 0 90
ros2 run dofbot_lab snapshot.py /usb_cam/image_raw/compressed
```

Open `snapshots/usb_cam.png`: all four blocks should be in the middle third of the picture. Run your colour detector on it (module 5) and check that it reads the stack correctly.

------

## 🐢 Step 2: Check the Poses, Slowly

The poses in the sorter were computed for Yahboom's colour mat. On the real arm, check the first grasp by hand, slowly, before running everything. From `TRAVEL`, go over the top block and down to it:

```
ros2 run dofbot_bringup dofbot_cmd open
ros2 run dofbot_bringup dofbot_cmd -t 3 servos 90 80 50 50 270
ros2 run dofbot_bringup dofbot_cmd -t 3 servos 90 78 53 13 270
ros2 run dofbot_bringup dofbot_cmd -t 3 servos 90 72 49 14 270
```

These are `TRAVEL`, `STACK[4]['over']` and `STACK[4]['at']`. In the video feed, the open fingers should now be on both sides of the top block, without touching it. Then go back up without grasping:

```
ros2 run dofbot_bringup dofbot_cmd -t 3 servos 90 78 53 13 270
ros2 run dofbot_bringup dofbot_cmd -t 3 servos 90 80 50 50 270
```

If the fingers were not around the block, **stop here** and tell your instructor: the mat has moved, or the arm needs calibrating. A sorter that misses will knock the stack over.

------

## ▶️ Step 3: Run It

Two parameters differ from the simulator:

| Parameter | Value | Why |
|---|---|---|
| `image_topic` | `/usb_cam/image_raw/compressed` | The real camera, compressed for the internet (module 5) |
| `check_grasp` | `false` | The real gripper always reports that it reached its position, so a grasp can't be checked (module 3). You check it by watching |

Terminal B:

```
ros2 run my_dofbot block_sorter.py --ros-args -p image_topic:=/usb_cam/image_raw/compressed -p check_grasp:=false
```

Terminal C, ready:

```
ros2 run dofbot_lab stop_arm.py
```

**Watch the whole run.** It takes about a minute and a half.

```
[INFO] [block_sorter]: Looking at the stack
[INFO] [block_sorter]: Stack, top to bottom: ['yellow', 'red', 'green', 'blue']
[INFO] [block_sorter]: yellow: stack level 4 -> yellow square
[INFO] [block_sorter]: red: stack level 3 -> red square
[INFO] [block_sorter]: green: stack level 2 -> green square
[INFO] [block_sorter]: blue: stack level 1 -> blue square
[INFO] [block_sorter]: Done
```

------

## 🛑 If Something Goes Wrong

| You see | Do |
|---|---|
| The gripper is about to hit a block or the stack | `Ctrl + C` in terminal B, then `stop_arm.py` in terminal C |
| A block was dropped or missed | `Ctrl + C`. Don't try to fix it with more commands: tell your instructor |
| The program stopped with an error | Read the error; check the video feed; tell your instructor where the blocks are |
| The detector reads the stack wrongly | `Ctrl + C` before the first grasp. Re-tune the colours (module 5) |

------

## 🏁 Step 4: Finish

```
ros2 run dofbot_bringup dofbot_cmd -t 3 ready
use_sim
```

Check in the video feed that every block is on its square, and tell your instructor the table needs resetting.

------

## 📝 Reflect: Simulation vs Reality

Write down, for your report:

| Question | Simulator | Real arm |
|---|---|---|
| How long did a full run take? | | |
| Did the camera read the stack correctly the first time? | | |
| Were the blocks placed exactly on the squares? | | |
| (If you tried it) Did the stack rebuild? | | |
| What did you have to change between the two? | | |
| What could the real arm not tell you that the simulator could? | | |

The last row is the most important lesson of this path: a simulator tells you everything, a real robot only what its sensors measure. Good robot programs check the world, not just their own commands.

------

## 🎉 Congratulations

You have taken a robot program from an empty workspace to a real robot arm: topics, nodes, messages, services, actions, C++, a camera, and a complete pick-and-place task, first in simulation and then on hardware, safely.

### 🚀 Where to Go Next

- **MoveIt 2** runs on the real DOFBOT (`/move_action`, `/compute_ik`): plan motions to a position in space instead of joint angles
- **Better perception**: find the blocks anywhere on the mat (not only in the stack) and compute their positions from the camera
- **Closed loop**: use the camera to check every placement, and retry when a block is off its square. That is also the way to make rebuilding the stack reliable
