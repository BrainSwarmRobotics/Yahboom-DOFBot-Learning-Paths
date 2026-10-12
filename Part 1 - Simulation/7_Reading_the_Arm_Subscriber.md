# 👀 Reading the Arm: Your First Subscriber

📍 **Level:** Beginner
📚 **Topic:** Subscribers, callbacks, and the JointState message

------

## 🧠 Why Read the Arm?

Your wave node sends commands and hopes for the best. Real robot programs also **listen**: where is the arm now? Did it get there? Is a joint near the end of its travel?

The arm publishes where every joint is on `/joint_states`, about 100 times a second. In this module you write a node that **subscribes** to it and prints the joints in degrees, once a second, with a warning when a joint is close to its limit.

```
joint_state_broadcaster --(/joint_states, 100 times a second)--> joint_monitor --> your terminal
```

------

## 📦 The Message You Will Read

```
ros2 interface show sensor_msgs/msg/JointState
```

| Field | Type | Meaning |
|---|---|---|
| `name` | list of strings | The joint names |
| `position` | list of numbers | Each joint's angle in radians (the gripper: metres) |
| `velocity` | list of numbers | How fast each joint moves |
| `effort` | list of numbers | The force on each joint |

`name[i]` belongs to `position[i]`. Never assume the order: the DOFBOT's `/joint_states` lists `joint2` first. Always match by name.

------

## 📄 Step 1: Create the File

Create `my_dofbot/scripts/joint_monitor.py`:

```
#!/usr/bin/env python3
"""Print the arm's joint angles in degrees once a second, and warn near the limits."""
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

# Joint names as /joint_states reports them, with a friendly name and the
# limits of travel in degrees (0 = straight up).
JOINTS = [
    # name        label       min    max
    ('joint1', 'base', -90.0, 90.0),
    ('joint2', 'shoulder', -90.0, 90.0),
    ('joint3', 'elbow', -90.0, 90.0),
    ('joint4', 'wrist', -90.0, 90.0),
    ('joint5', 'roll', -90.0, 180.0),
]
WARN_MARGIN = 5.0  # degrees from a limit


class JointMonitor(Node):
    def __init__(self):
        super().__init__('joint_monitor')
        self.positions = {}  # joint name -> latest position (rad, or m for the gripper)

        # Subscriber: on_joint_states runs every time a JointState message arrives.
        self.subscription = self.create_subscription(
            JointState, '/joint_states', self.on_joint_states, 10)

        # Print from a timer, not from the callback: /joint_states arrives many
        # times a second, far too fast to read.
        self.timer = self.create_timer(1.0, self.print_joints)

    def on_joint_states(self, msg):
        # name[i] belongs to position[i]. Match by name: the order is not guaranteed.
        for name, position in zip(msg.name, msg.position):
            self.positions[name] = position

    def print_joints(self):
        if not self.positions:
            self.get_logger().info('No /joint_states yet. Is the simulator (or robot) running?')
            return

        parts = []
        for name, label, low, high in JOINTS:
            if name not in self.positions:
                continue
            degrees = math.degrees(self.positions[name])
            parts.append(f'{label} {degrees:6.1f}')
            if degrees < low + WARN_MARGIN or degrees > high - WARN_MARGIN:
                self.get_logger().warn(f'{label} ({name}) is near the end of its travel: {degrees:.1f} deg')

        if 'finger_left_joint' in self.positions:
            parts.append(f'gripper {self.positions["finger_left_joint"] * 1000:4.1f} mm')

        self.get_logger().info(' | '.join(parts))


def main(args=None):
    rclpy.init(args=args)
    node = JointMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

------

## 🧠 Step 2: Understand the Code

### 📥 The subscriber

```
self.subscription = self.create_subscription(
    JointState, '/joint_states', self.on_joint_states, 10)
```

Four things: the **message type**, the **topic**, the **callback** (the function to call for every message), and the queue size.

### 📞 The callback

```
def on_joint_states(self, msg):
    for name, position in zip(msg.name, msg.position):
        self.positions[name] = position
```

You never call `on_joint_states` yourself. ROS 2 calls it, with the message as `msg`, every time one arrives (100 times a second). It only stores the latest position of each joint in a dictionary, keyed by name. `zip` walks the two lists side by side: the first name with the first position, and so on.

`Keep callbacks short. While a callback runs, the node can't handle anything else.`

### ⏱️ Printing from a timer

The timer runs `print_joints` once a second and prints whatever was stored last. **The callback collects, the timer acts**: a pattern you will use often.

### 📐 Radians to degrees

```
degrees = math.degrees(self.positions[name])
```

ROS 2 uses radians; people read degrees more easily. `math.degrees(1.5708)` is `90.0`.

------

## ⚙️ Step 3: Install, Build, Run

Add `scripts/joint_monitor.py` to `install(PROGRAMS ...)` in `CMakeLists.txt`, then:

```
chmod +x ~/dofbot_ws/src/my_dofbot/scripts/joint_monitor.py
cd ~/dofbot_ws
colcon build --packages-select my_dofbot
source install/setup.bash
ros2 run my_dofbot joint_monitor.py
```

```
[INFO] [joint_monitor]: base    0.0 | shoulder    0.0 | elbow    0.0 | wrist    0.0 | roll    0.0 | gripper 30.0 mm
[INFO] [joint_monitor]: base    0.0 | shoulder    0.0 | elbow    0.0 | wrist    0.0 | roll    0.0 | gripper 30.0 mm
```

Leave it running. In another terminal, move the arm and watch the numbers change:

```
ros2 run dofbot_bringup dofbot_cmd ready
```

```
[WARN] [joint_monitor]: elbow (joint3) is near the end of its travel: -90.0 deg
[WARN] [joint_monitor]: wrist (joint4) is near the end of its travel: -90.0 deg
[INFO] [joint_monitor]: base    0.0 | shoulder   40.0 | elbow  -90.0 | wrist  -90.0 | roll    0.0 | gripper 32.5 mm
```

The `ready` pose bends the elbow and wrist all the way: your monitor noticed.

Now run your wave node from module 6 at the same time, and watch the base swing between +28.6° and -28.6° (0.5 rad).

`Stuck? Compare with exercise_2_subscriber/scripts/joint_monitor.py, or build and run it: colcon build --packages-select exercise_2_subscriber, source, ros2 run exercise_2_subscriber joint_monitor.py`

------

## 🔄 What Just Happened

```
your wave node --(/arm_controller/joint_trajectory)--> arm_controller --> arm moves
                                                                               |
your joint monitor <--(/joint_states)-- joint_state_broadcaster <--------------+
```

You now have both halves of a robot program: **acting** (publisher) and **sensing** (subscriber).

------

## 🧪 Try It Yourself

### 🟢 Easy

- Print only the base joint
- Print twice a second instead of once

### 🟡 Medium

- Also print each joint's velocity (`msg.velocity`, in rad/s). Careful: on some robots `velocity` is empty. Check its length first.
- Print `MOVING` while any joint moves faster than 0.01 rad/s, and `STILL` otherwise

### 🔴 Challenge

- Change the topic name to `/joint_state` (one letter missing) and run it. What happens? Why is that dangerous? (Nothing complains: a subscriber to a topic nobody publishes simply waits forever. Always check names with `ros2 topic list`.)

------

## ⚠️ Common Mistakes

| Problem | Cause |
|---|---|
| `No /joint_states yet` forever | Simulator not running, or a typo in the topic name |
| `KeyError: 'joint1'` | You read `self.positions['joint1']` before any message arrived. Check `if name in self.positions` first |
| Printing inside the callback floods the terminal | It runs 100 times a second. Store in the callback, print from a timer |
| Wrong joint shown | You indexed by number (`msg.position[0]`) instead of matching names |

------

## 🎯 What You Learned

- A **subscriber** calls your **callback** for every message on a topic
- `JointState` holds parallel lists: `name[i]` goes with `position[i]`
- Store data in the callback, act on it from a timer
- Radians to degrees with `math.degrees`

------

## 🚀 What's Next?

`[0.5, 0.0, -0.3, -0.6, 0.0]` is not a friendly way to describe a pose. Next you will design your **own message type** that describes an arm pose the way people think about it.
