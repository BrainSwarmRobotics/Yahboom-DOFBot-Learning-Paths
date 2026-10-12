#!/usr/bin/env python3
"""Exercise 2: read the arm's joint angles (a subscriber).

Subscribes to /joint_states and, once a second, prints every joint in degrees
(gripper in millimetres) and warns when a joint is close to the end of its
travel.

Run:  ros2 run exercise_2_subscriber joint_monitor.py
"""
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
