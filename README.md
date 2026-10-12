# 🦾 Yahboom DOFBOT ROS 2 Learning Paths

Hands-on learning paths for **ROS 2 Humble** with the **Yahboom DOFBOT**, a 5-joint robot arm with a gripper and a camera, on the **AnyBot** platform.

There are two paths, and the second builds on the first:

| Path | Where it runs | What you do |
|---|---|---|
| **Part 1 - Simulation** | Your preview session, any time | Learn ROS 2 on a simulated DOFBOT: topics, nodes, messages, services, actions, C++, the camera, and a pick-and-place capstone |
| **Part 2 - Real Hardware** | A booked session on the real arm | Connect to the real DOFBOT and run what you built in simulation on real servos and a real camera, safely |

The simulator uses the same controllers, topics and actions as the real arm, so code written in Part 1 runs on the robot in Part 2 without changes.

---

## 🧠 Part 1 - Simulation

| Module | Topic |
|---|---|
| 0 | Understanding the picture: AnyBot, the DOFBOT, how the paths work |
| 1 | Linux command line essentials |
| 2 | Start the simulator, watch it, move it with ready-made commands |
| 3 | Make the arm move from the command line (topics, the gripper action) |
| 4 | ROS 2 architecture: nodes, topics, messages, services, actions |
| 5 | Your workspace and your first package |
| 6 | Your first node: a publisher that makes the arm wave |
| 7 | Reading the arm: a subscriber for joint states |
| 8 | Custom messages: an arm pose in degrees |
| 9 | Services: move to a pose by name |
| 10 | Actions: pick up a block and put it down |
| 11 | Your first C++ node |
| 12 | The camera: finding coloured blocks with OpenCV |
| 13 | Capstone: sort the blocks by colour |

## 🦾 Part 2 - Real Hardware

| Module | Topic |
|---|---|
| 0 | From simulation to the real arm: what changes, safety rules |
| 1 | Connecting to the real DOFBOT |
| 2 | Safety and first moves |
| 3 | Joint states and servo angles |
| 4 | Running your nodes on the real arm |
| 5 | The real camera |
| 6 | Capstone on the real arm |

---

## 📁 Repository layout

```
Part 1 - Simulation/      learning path modules (markdown), shown in the AnyBot console
Part 2 - Real Hardware/   learning path modules (markdown)
assets/                   images used by the modules
Docs/                     feedback and issue sheets
dofbot_ws/src/            ROS 2 packages, copied into every student's workspace (~/dofbot_ws/src)
  dofbot_lab/               the simulator with an overview camera, snapshots, block reset, stop
  exercise_1_publisher/     reference solutions, one package per module...
  exercise_2_subscriber/
  exercise_3_custom_message/
  exercise_4_service/
  exercise_5_action/
  exercise_6_cpp/
  exercise_7_camera/
  exercise_8_block_sorter/
  Practical_Session_2/      handouts and the dofbot_practice package for the practical sessions
```

The AnyBot console shows every top-level folder that contains `.md` files as a learning path, and lists its modules by the number at the start of each file name (`0_...`, `1_...`, `10_...`). Images are referenced as `../assets/...`. The console renders the modules with Python-Markdown, so keep a blank line before every list, table and code block, and write each paragraph on one line (line breaks are kept).

The `dofbot_ws` folder is also how the platform recognises this repository's workspace name: it is seeded into each user's `workspaces/<id>/dofbot_ws/src` and mounted at `/home/user/dofbot_ws/src`. The copy happens once, the first time a student's console starts, so changes made here later reach only students whose workspace is created after the change.

## 🛠️ Requirements

Students need only a laptop and a web browser. Everything else is in the AnyBot console:

- ROS 2 Humble, Ignition Gazebo Fortress and the DOFBOT simulation packages (`dofbot_description`, `dofbot_gazebo`, `dofbot_bringup`, `dofbot_moveit_config`), in the `dofbot/theia-humble` image
- for Part 2, a booked session: the console joins the robot's Husarnet network, and `/home/project/fastdds_hnet_client.xml` points ROS 2 at the robot's discovery server (hostname `dofbot`)

The real DOFBOT runs ROS 2 Humble in the `dofbot_humble` container on its Raspberry Pi 5, with the same `arm_controller`, `gripper_controller` and `joint_state_broadcaster` as the simulator, plus MoveIt 2 and the USB camera (`/usb_cam/image_raw`).

## ✅ Testing the packages

```bash
cd ~/dofbot_ws
colcon build --packages-select dofbot_lab exercise_1_publisher exercise_2_subscriber \
  exercise_3_custom_message exercise_4_service exercise_5_action exercise_6_cpp \
  exercise_7_camera exercise_8_block_sorter
source install/setup.bash
ros2 launch dofbot_lab sim.launch.py               # terminal 1
ros2 run exercise_8_block_sorter block_sorter.py   # terminal 2: the whole capstone
```

`Practical_Session_2/dofbot_practice` does not build until its Exercise A blanks are filled in, on purpose, so build the other packages by name as above.
