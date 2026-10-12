#!/usr/bin/env python3
"""Exercise 1: make the DOFBOT wave (a publisher with a timer).

Every 2.5 seconds this node publishes the next pose of a wave on
/arm_controller/joint_trajectory: straight up, then the base turns left and
right three times with the wrist bent, then straight up again.

Run:  ros2 run exercise_1_publisher wave_node.py
"""
import rclpy
from builtin_interfaces.msg import Duration
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# The five arm joints, from the base up. The order must match the numbers in each pose.
JOINTS = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']

# Poses in radians. 0 on every joint = the arm straight up.
HOME = [0.0, 0.0, 0.0, 0.0, 0.0]
WAVE_LEFT = [0.5, 0.0, -0.3, -0.6, 0.0]    # base turned left, elbow and wrist bent forward
WAVE_RIGHT = [-0.5, 0.0, -0.3, -0.6, 0.0]  # base turned right

POSES = [HOME] + [WAVE_LEFT, WAVE_RIGHT] * 3 + [HOME]

MOVE_TIME = 2.0  # seconds the arm takes to reach each pose
PERIOD = 2.5     # seconds between two commands (a little longer than MOVE_TIME)


class WaveNode(Node):
    def __init__(self):
        super().__init__('wave_node')

        # Publisher: sends JointTrajectory messages to the arm controller.
        self.publisher_ = self.create_publisher(
            JointTrajectory, '/arm_controller/joint_trajectory', 10)

        # Timer: calls timer_callback every PERIOD seconds.
        self.timer = self.create_timer(PERIOD, self.timer_callback)

        self.step = 0  # index of the next pose in POSES

    def timer_callback(self):
        # A message published before the controller has connected is lost.
        if self.publisher_.get_subscription_count() == 0:
            self.get_logger().warn('Waiting for the arm controller to connect...')
            return

        if self.step == len(POSES):
            self.get_logger().info('Done waving. Press Ctrl+C to exit.')
            self.timer.cancel()
            return

        # One trajectory with a single point: "be at these positions MOVE_TIME s from now".
        point = JointTrajectoryPoint()
        point.positions = POSES[self.step]
        point.time_from_start = Duration(sec=int(MOVE_TIME), nanosec=int(MOVE_TIME % 1 * 1e9))

        msg = JointTrajectory()
        msg.joint_names = JOINTS
        msg.points = [point]

        self.publisher_.publish(msg)
        self.get_logger().info(f'Pose {self.step + 1}/{len(POSES)}: {POSES[self.step]}')
        self.step += 1


def main(args=None):
    rclpy.init(args=args)
    node = WaveNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
