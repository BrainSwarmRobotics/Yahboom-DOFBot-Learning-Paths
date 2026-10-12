#!/usr/bin/env python3
"""Freeze the arm where it is right now.

    ros2 run dofbot_lab stop_arm.py

Sends the arm controller a new trajectory whose only point is the current
position. That replaces whatever the arm was doing (a long trajectory from the
terminal, a running action), so the arm stops and holds.

It cannot stop a node that keeps sending new commands: stop that node first
with Ctrl+C in its terminal, then run this.
"""
import sys

import rclpy
from builtin_interfaces.msg import Duration
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

ARM_JOINTS = ["joint1", "joint2", "joint3", "joint4", "joint5"]


def main():
    rclpy.init()
    node = Node("stop_arm")
    latest = {}

    def on_joint_states(msg):
        latest.update(zip(msg.name, msg.position))

    node.create_subscription(JointState, "/joint_states", on_joint_states, 10)
    publisher = node.create_publisher(JointTrajectory, "/arm_controller/joint_trajectory", 10)

    # Wait for the arm's position and for the controller to be listening.
    for _ in range(100):
        rclpy.spin_once(node, timeout_sec=0.1)
        if all(j in latest for j in ARM_JOINTS) and publisher.get_subscription_count() > 0:
            break
    else:
        node.get_logger().error("No /joint_states or no arm controller. Is the simulator (or robot) running?")
        rclpy.try_shutdown()
        return 1

    hold = JointTrajectory()
    hold.joint_names = ARM_JOINTS
    hold.points = [JointTrajectoryPoint(positions=[latest[j] for j in ARM_JOINTS],
                                        time_from_start=Duration(sec=0, nanosec=300_000_000))]
    publisher.publish(hold)
    node.get_logger().info("Arm stopped: holding " +
                           ", ".join(f"{j}={latest[j]:+.2f}" for j in ARM_JOINTS) + " rad")
    rclpy.spin_once(node, timeout_sec=0.5)  # let the message go out before exiting
    node.destroy_node()
    rclpy.try_shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
