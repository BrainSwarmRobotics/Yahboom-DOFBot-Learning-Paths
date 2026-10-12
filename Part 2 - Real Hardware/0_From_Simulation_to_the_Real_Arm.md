# 🦾 From Simulation to the Real Arm

📍 **Level:** Intermediate (you have finished Part 1)
📚 **Topic:** What stays the same, what changes, and how to use your time on the real DOFBOT

------

## 👋 Welcome to the Real Thing

In Part 1 you programmed a simulated DOFBOT. In this path you run the same programs on the **real DOFBOT** in our lab, from your browser.

The real arm is driven by the **same controllers**, with the **same topics, actions and joint names**, so your code runs unchanged. But a real robot is not a simulator. Servos have play and lag, the camera sees real light, a dropped block stays dropped, and nobody can press "restart" on the world.

This module tells you what to expect, and how to make the most of a short booked slot.

------

## ✅ What Stays the Same

| | Simulator | Real DOFBOT |
|---|---|---|
| Arm topic | `/arm_controller/joint_trajectory` | `/arm_controller/joint_trajectory` |
| Arm action | `/arm_controller/follow_joint_trajectory` | `/arm_controller/follow_joint_trajectory` |
| Gripper action | `/gripper_controller/gripper_cmd` | `/gripper_controller/gripper_cmd` |
| Joint states | `/joint_states` | `/joint_states` |
| Joint names | `joint1` ... `joint5`, `finger_left_joint` | the same |
| Controllers | `arm_controller`, `gripper_controller`, `joint_state_broadcaster` | the same |
| Your code | `my_dofbot`, `exercise_*` | the same, unchanged |

------

## ⚠️ What Changes

| | Simulator | Real DOFBOT |
|---|---|---|
| Where it runs | In your console | On a Raspberry Pi in our lab, reached over the internet |
| Camera topic | `/camera/image_raw` | `/usb_cam/image_raw`, and a compressed copy `/usb_cam/image_raw/compressed` (use this one) |
| Camera pictures | ~10 per second, perfect light | 30 per second, real light, shadows and reflections |
| Watching the arm | `snapshot.py` of the overview camera | The **Robot Video Feed** in your console |
| `/joint_states` | Simulated positions | Positions **calculated** from the commands, not measured (module 3) |
| Accuracy | Exact | A few millimetres of play; the arm sags slightly under its own weight |
| Mistakes | Restart the simulator | A knocked block stays knocked; a crash into the table is real |
| Reset the blocks | `reset_blocks.py` | Your instructor resets the table between slots: tell them what you changed |
| Time | Unlimited | Your booked slot (short) |
| Extra | | MoveIt 2 (motion planning) runs on the robot |

------

## ⏱️ How to Use a Booked Slot

A slot is short. Spend it **running** code, not writing it.

```
Before the slot (preview session, simulator):
    write the program -> test it in simulation until it works every time

During the slot (booked session, real arm):
    connect -> check the arm -> run your tested program -> watch -> stop -> disconnect
```

### 📋 Checklist before your slot

- [ ] Your program works in the simulator, several times in a row
- [ ] It is built and installed (`colcon build --packages-select ...`)
- [ ] You know the exact commands you will run (write them down)
- [ ] Every move in your program takes at least 1 second
- [ ] You have read module 2 (safety) of this path

------

## 🛡️ Safety Rules

These apply every time you are connected to the real arm.

1. **Watch the arm**, in the Robot Video Feed, every time you run something. Never run a command and look away.
2. **Know how to stop.** `Ctrl + C` stops your node. `ros2 run dofbot_lab stop_arm.py` freezes the arm where it is. Have a second terminal ready for it.
3. **Never rush the arm.** Every move takes at least 1 second; big moves 2 or more.
4. **Test new poses slowly.** The first time you send a pose, use 3 seconds or more.
5. **Mind the table.** Leaning the shoulder, elbow and wrist all far forward drives the gripper into the table.
6. **One program at a time.** Two nodes commanding the arm fight each other.
7. **Leave it tidy.** End with the arm in the `ready` pose, and tell your instructor if you moved any blocks.
8. **If something looks wrong, stop first, ask after.** A stopped arm is always safe.

------

## 🧭 This Path

| Module | What you do |
|---|---|
| 1 | Connect your console to the real DOFBOT |
| 2 | Safety and first moves |
| 3 | Joint states and servo angles: how the real arm reports itself |
| 4 | Run your Part 1 nodes on the real arm |
| 5 | The real camera: compressed pictures, real light, tuning colours |
| 6 | Capstone: sort the real blocks |

`Practical sessions: Practical Session 2 (in your workspace under Practical_Session_2) is the same idea in a class format: read the arm with a subscriber, then command it with a publisher, in one short slot.`

------

## 🚀 What's Next?

Book a slot (Part 1, module 0 shows how), and when it starts, connect your console to the robot.
