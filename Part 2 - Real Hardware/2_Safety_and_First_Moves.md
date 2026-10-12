# 🛡️ Safety and First Moves

📍 **Level:** Intermediate
📚 **Topic:** A safety routine for real hardware, stopping the arm, and your first real movements

------

## 🧠 Why a Routine?

On the simulator you could try anything. On the real arm, a wrong number can push the gripper into the table or sweep the blocks off the mat. You can't undo it, and the next student has to live with it.

A short routine, done every time, prevents almost every accident.

------

## ✅ The Routine (every time you run something)

```
1. PROMPT   does it say (ROBOT)?            -> you are about to move real hardware
2. WATCH    is the Robot Video Feed open?   -> you will see what happens
3. STOP     is a second terminal ready?      -> ros2 run dofbot_lab stop_arm.py
4. STATE    where is the arm now?            -> ros2 run dofbot_bringup dofbot_cmd state
5. SLOW     first time with a pose? 3 s or more
```

------

## 🛑 Step 1: Learn to Stop the Arm

Practise stopping **before** you need to. There are two tools:

| Tool | What it stops |
|---|---|
| `Ctrl + C` in the terminal of your node | Your **node**: it sends nothing more |
| `ros2 run dofbot_lab stop_arm.py` | The **arm**: it freezes where it is, even in the middle of a move |

The arm keeps following the last trajectory it received even after your node has stopped. That is why you need both: `Ctrl + C` first (so nothing new arrives), then `stop_arm.py` (so the current move ends).

Try it. Open two terminals, both `(ROBOT)`. In terminal A, send a **slow** move to the ready pose (8 seconds):

```
ros2 run dofbot_bringup dofbot_cmd -t 8 ready
```

While the arm is moving, in terminal B:

```
ros2 run dofbot_lab stop_arm.py
```

```
[INFO] [stop_arm]: Arm stopped: holding joint1=-0.79, joint2=+0.30, joint3=-0.40, joint4=-0.41, joint5=+0.00 rad
```

(Your numbers will differ.) The arm stops halfway. (`dofbot_cmd` in terminal A reports that its move was aborted. That's expected.)

------

## 🦾 Step 2: First Moves with a Known Tool

`dofbot_cmd` moves to poses that are known to be safe. Use it for your first moves, slowly:

```
ros2 run dofbot_bringup dofbot_cmd state
ros2 run dofbot_bringup dofbot_cmd -t 3 ready
```

Watch the video feed: the arm unfolds into Yahboom's start pose, camera looking at the mat. Then:

```
ros2 run dofbot_bringup dofbot_cmd -t 3 home
ros2 run dofbot_bringup dofbot_cmd open
ros2 run dofbot_bringup dofbot_cmd close
ros2 run dofbot_bringup dofbot_cmd open
ros2 run dofbot_bringup dofbot_cmd -t 3 ready
```

Compare with the simulator. The motion is the same, but you will notice:

- the real servos move a little less smoothly
- the real arm stops close to the pose, but not exactly on it (`state` still shows the exact angles: module 3 explains why)
- the gripper sounds different when it closes on nothing and when it closes on a block

------

## 📡 Step 3: One Joint, from the Command Line

The same command as in Part 1, module 3, but small and slow. From `ready`, turn the base a little to the left:

```
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{joint_names: [joint1], points: [{positions: [0.3], time_from_start: {sec: 3}}]}"
```

And back:

```
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{joint_names: [joint1], points: [{positions: [0.0], time_from_start: {sec: 3}}]}"
```

Only `joint1` is named, so only the base moves: the controller accepts trajectories for some of its joints and holds the others still.

------

## 📐 Step 4: Know Where the Table Is

The arm stands on the table, so some angles drive the gripper into it. A simple rule, worked out from the arm's dimensions:

**Add up how far the shoulder (`joint2`), elbow (`joint3`) and wrist (`joint4`) are bent from straight, ignoring the sign.**

| Total bend | Lowest the gripper can get |
|---|---|
| up to 90° (1.5 rad) | more than 12 cm above the table: safe anywhere |
| about 100° (1.8 rad) | about 6 cm: close to the top of the block stack |
| 115° (2.0 rad) or more | can reach the table |

| Pose | Total bend | Safe? |
|---|---|---|
| `[0, 0, 0, 0, 0]` (home) | 0° | ✅ |
| `[0.5, -0.5, -0.5, -0.5, 0]` | 86° | ✅ |
| `[0, -0.7, -0.7, -0.7, 0]` | 120° | ⚠️ gripper about 10 cm above the table, in front of the stack |
| `[0, -0.9, -0.9, -0.9, 0]` | 155° | ❌ gripper into the table |

The `ready` pose (bend 220°) and the pick-and-place poses go far beyond 90° **on purpose**: they were measured to end just above the mat. Use measured poses like those as they are, and treat anything new beyond 90° with care: try it in the simulator first.

`Moving one joint on its own from home is always safe: the gripper stays at least 10 cm above the table.`

------

## ⚠️ Never Do This on the Real Arm

| Don't | Why |
|---|---|
| `time_from_start` under 1 second | Sudden jumps strain the servos and can shake the arm off its target |
| Two nodes commanding the arm at once | They fight; the arm jerks between their targets |
| Run a node you haven't tested in simulation | The simulator exists so the real arm never sees your bugs |
| Squeeze harder than `max_effort: 10.0` | The gripper servo can overheat holding a block too hard |
| Leave the arm in an unusual pose at the end | End every session with `dofbot_cmd ready` |

------

## 🎯 What You Learned

- A five-step routine before every run: prompt, watch, stop, state, slow
- `Ctrl + C` stops your node; `stop_arm.py` stops the arm
- `dofbot_cmd` gives safe known poses; the command line moves single joints
- A rule of thumb for the table: total bend up to 90° is safe

------

## 🚀 What's Next?

The real arm reports itself slightly differently from the simulator. Next: real joint states, and the servo angles behind them.
