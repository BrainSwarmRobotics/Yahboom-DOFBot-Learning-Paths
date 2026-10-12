#!/usr/bin/env python3
"""Exercise 3: move the arm with your own message type.

Listens on /arm_pose for ArmPose messages (degrees, easy for people) and turns
each one into a JointTrajectory (radians, what the arm controller needs).

Run:   ros2 run exercise_3_custom_message pose_commander.py
Send:  ros2 topic pub --once /arm_pose exercise_3_custom_message/msg/ArmPose \
         "{base: 30.0, shoulder: -20.0, elbow: -30.0, wrist: -40.0, roll: 0.0, seconds: 2.0}"
"""
import math

import rclpy
from builtin_interfaces.msg import Duration
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from exercise_3_custom_message.msg import ArmPose

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']
LIMITS_DEG = [(-90, 90), (-90, 90), (-90, 90), (-90, 90), (-90, 180)]
MIN_SECONDS = 1.0  # never rush the arm


class PoseCommander(Node):
    def __init__(self):
        super().__init__('pose_commander')
        self.subscription = self.create_subscription(ArmPose, '/arm_pose', self.on_arm_pose, 10)
        self.publisher_ = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.get_logger().info('Waiting for ArmPose messages on /arm_pose')

    def on_arm_pose(self, pose):
        requested = [pose.base, pose.shoulder, pose.elbow, pose.wrist, pose.roll]

        # Keep every joint inside its travel, and say so when we had to.
        degrees = []
        for name, value, (low, high) in zip(JOINTS, requested, LIMITS_DEG):
            clamped = min(max(value, low), high)
            if clamped != value:
                self.get_logger().warn(f'{name}: {value:.0f} deg is out of range, using {clamped:.0f}')
            degrees.append(clamped)

        seconds = max(pose.seconds, MIN_SECONDS)

        point = JointTrajectoryPoint()
        point.positions = [math.radians(d) for d in degrees]
        point.time_from_start = Duration(sec=int(seconds), nanosec=int(seconds % 1 * 1e9))

        msg = JointTrajectory()
        msg.joint_names = JOINTS
        msg.points = [point]
        self.publisher_.publish(msg)
        self.get_logger().info(f'Moving to {degrees} deg in {seconds:.1f} s')


def main(args=None):
    rclpy.init(args=args)
    node = PoseCommander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
