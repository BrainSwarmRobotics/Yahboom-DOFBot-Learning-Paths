# 🚀 Running Your Nodes on the Real Arm

📍 **Level:** Intermediate
📚 **Topic:** Running the publisher, subscriber, custom message, service and action nodes from Part 1 on real hardware

------

## 🧠 Same Code, Real Arm

Every node you wrote in Part 1 talks only to `/arm_controller`, `/gripper_controller` and `/joint_states`. The real DOFBOT has exactly those, so the nodes run **without changes**. You only switch the terminal with `use_robot`.

`Build everything before your slot, in your preview session: cd ~/dofbot_ws && colcon build --packages-select my_dofbot my_dofbot_cpp. If your own package isn't ready, use the exercise_* packages, the same programs. Build them too: colcon build --packages-select exercise_1_publisher exercise_2_subscriber exercise_3_custom_message exercise_4_service exercise_5_action`

| Part 1 module | Your node | Reference |
|---|---|---|
| 6 | `my_dofbot wave_node.py` | `exercise_1_publisher wave_node.py` |
| 7 | `my_dofbot joint_monitor.py` | `exercise_2_subscriber joint_monitor.py` |
| 8 | `my_dofbot pose_commander.py` | `exercise_3_custom_message pose_commander.py` |
| 9 | `my_dofbot named_pose_server.py` / `named_pose_client.py` | `exercise_4_service ...` |
| 10 | `my_dofbot pick_and_place.py` | `exercise_5_action pick_and_place.py` |

------

## 🖥️ Set Up Your Terminals

Use three terminals, all showing `(ROBOT)`:

| Terminal | Runs |
|---|---|
| A | Your joint monitor: a live view of the joints, the whole time |
| B | The node you are testing |
| C | Ready for `ros2 run dofbot_lab stop_arm.py` |

In terminal A:

```
ros2 run my_dofbot joint_monitor.py
```

Keep the Robot Video Feed visible next to it.

------

## 👋 1. The Wave (publisher)

The wave starts by moving to `home`. Move there slowly yourself first, so the node's first move is short:

```
ros2 run dofbot_bringup dofbot_cmd -t 3 home
ros2 run my_dofbot wave_node.py
```

Watch the video feed and terminal A. The base swings between +28.6° and -28.6°, exactly as in the simulator. When it prints `Done waving`, press `Ctrl + C`.

`Notice: if the wave had started from the far side of the table, its first 2-second move would have been large and fast. On the real arm, always know where a node's first move goes, and start from a pose close to it.`

------

## 🧩 2. The Pose Commander (custom message)

Terminal B:

```
ros2 run my_dofbot pose_commander.py
```

Terminal C (it is only a `topic pub`, so it's fine to use the stop terminal for it):

```
ros2 topic pub --once /arm_pose my_dofbot/msg/ArmPose "{base: 30.0, shoulder: -20.0, elbow: -30.0, wrist: -40.0, roll: 0.0, seconds: 3.0}"
```

Total bend: 20 + 30 + 40 = 90°: safely above the table (module 2). Then back:

```
ros2 topic pub --once /arm_pose my_dofbot/msg/ArmPose "{seconds: 3.0}"
```

All fields default to 0: straight up.

Your node's limits now protect real hardware. Try `{base: 120.0, seconds: 3.0}` and check that the base stops at 90°.

------

## 🙋 3. The Named-Pose Service

Terminal B:

```
ros2 run my_dofbot named_pose_server.py
```

Terminal C, one at a time, watching each move:

```
ros2 run my_dofbot named_pose_client.py ready 3.0
ros2 run my_dofbot named_pose_client.py look 3.0
ros2 run my_dofbot named_pose_client.py left 3.0
ros2 run my_dofbot named_pose_client.py right 3.0
ros2 run my_dofbot named_pose_client.py ready 3.0
```

In the `look` pose, the camera points at the block stack. You will use it in the next module.

------

## 🎯 4. Pick and Place (actions)

`pick_and_place.py` takes the top block off the stack and leaves it on the yellow square: it **changes the table**. Run it only if the stack is on the mat (check the video feed) and your instructor allows it; otherwise go straight to module 5. Afterwards, tell your instructor the table needs resetting.

```
ros2 run my_dofbot pick_and_place.py
```

Watch every step. If the gripper is about to hit something, `Ctrl + C` in terminal B, then `stop_arm.py` in terminal C.

### What is different on the real arm

| | Simulator | Real DOFBOT |
|---|---|---|
| Gripper result with a block | `stalled: true`, `reached_goal: false` | `reached_goal: true`: the driver reports the commanded position (module 3) |
| Grasp | Exact | The block may sit a few millimetres off-centre in the fingers |
| Move timing | As commanded | As commanded, except that the driver limits each servo to 150°/s |
| A failed grasp | Visible in the gripper result | Visible **only on the video feed** |

Putting the block back on the stack with the arm is harder than taking it off (Part 1, module 13 explains why), so leave that to your instructor unless they ask you to try. If you do, write the reverse program (pick at `PLACE_YELLOW`, place at `PICK_TOP`) and test it in the simulator first.

------

## ⏱️ 5. Make the Most of Your Slot

| Do | Don't |
|---|---|
| Keep a list of the exact commands you will run | Edit code during your slot |
| Run each program once, watch, then decide | Run the same failing thing again and again |
| Note what differs from the simulator: that is the lesson | Assume it worked because the terminal says so |
| End with `dofbot_cmd -t 3 ready`, then `use_sim` | Leave a node running |

------

## 🧪 Try It Yourself

### 🟢 Easy

- Run the C++ joint monitor (`my_dofbot_cpp joint_monitor`) next to the Python one. Same output?

### 🟡 Medium

- Measure the delay: in one terminal `ros2 topic echo /joint_states --field header.stamp`, in another publish a move, and compare the time you pressed Enter with the stamp when the joints start changing.

### 🔴 Challenge

- Run your wave with `MOVE_TIME = 1.0` and `PERIOD = 1.2`, in the simulator and on the real arm. Do they keep up the same way?

------

## 🎯 What You Learned

- Part 1 nodes run unchanged on the real arm
- On real hardware: know where the first move goes, keep a stop terminal ready, watch the video
- What the real arm reports about its gripper, and what it can't

------

## 🚀 What's Next?

The real camera: compressed pictures over the internet, real light, and tuning your colour detector.
