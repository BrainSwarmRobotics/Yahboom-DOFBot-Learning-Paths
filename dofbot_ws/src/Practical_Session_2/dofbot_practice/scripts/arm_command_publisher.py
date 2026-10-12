#!/usr/bin/env python3
# =============================================================================
# arm_command_publisher.py
#
# Practical Session 2, Exercise B, Python version.
#
# This is the same node as src/arm_command_publisher.cpp, written in Python.
# As given it holds every joint at 0.0 rad, which is safe and boring on
# purpose: run it first, confirm the subscriber from Exercise A sees no
# movement, then start changing it.
#
# WHAT YOU WILL CHANGE (see the TODO markers below):
#   TODO 1  Put real angles in point.positions so one joint moves.
#   TODO 2  Change time_from_start and watch the arm move faster or slower.
#   TODO 3  Alternate between two poses so the arm sweeps back and forth.
#
# SAFETY: keep your first angles small, under about 0.5 rad from the current
# pose, and keep a hand near the power switch. Watch the real arm, not the
# screen, the first time you run a new target.
#
# Build:  cd ~/dofbot_ws && colcon build --packages-select dofbot_practice
# Source: source ~/dofbot_ws/install/setup.bash
# Run:    ros2 run dofbot_practice arm_command_publisher.py
# =============================================================================

import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class ArmCommandPublisher(Node):
    def __init__(self):
        super().__init__('arm_command_publisher')

        self.publisher = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',   # confirm with: ros2 topic list
            10)

        # A publisher on its own sends nothing. Something has to call publish().
        # Here a timer does it twice a second.
        self.timer = self.create_timer(
            0.5,                                  # TODO 2: try 2.0
            self.publish_once)

        # TODO 3: keep a flag here, flip it in publish_once, and choose between
        #         two different position lists so the arm sweeps.
        self.toggle = False

        self.get_logger().info(
            'Publishing to /arm_controller/joint_trajectory')

    def publish_once(self):
        message = JointTrajectory()

        # The names must match what the arm actually reports. If you are
        # unsure, run: ros2 topic echo /joint_states --once
        message.joint_names = [
            'joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']

        point = JointTrajectoryPoint()

        # TODO 1: replace these with your own angles, in radians, one per joint
        #         above and in the same order. Start by moving ONE joint a little.
        point.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # How long the arm should take to arrive. Too short is a jerk, which
        # the controller may refuse or the hardware may not survive.
        point.time_from_start = Duration(sec=2, nanosec=0)

        message.points.append(point)
        self.publisher.publish(message)

        self.get_logger().info(
            'Sent a trajectory with {} joints'.format(len(message.joint_names)))


def main(args=None):
    rclpy.init(args=args)
    node = ArmCommandPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
