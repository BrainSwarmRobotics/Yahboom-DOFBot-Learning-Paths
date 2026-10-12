#!/usr/bin/env python3
"""Exercise 5: pick up a block and put it down somewhere else (action clients).

Uses the two actions of the DOFBOT's controllers:

  /arm_controller/follow_joint_trajectory   control_msgs/action/FollowJointTrajectory
  /gripper_controller/gripper_cmd           control_msgs/action/GripperCommand

and waits for each move to finish before starting the next one. Takes the top
block (yellow) off the stack on the centre square and puts it on the yellow
square.

Run:  ros2 run exercise_5_action pick_and_place.py
Reset the blocks afterwards (simulator):  ros2 run dofbot_lab reset_blocks.py
"""
import math

import rclpy
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory, GripperCommand
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']

# Poses as Yahboom's servo angles in degrees (90 = straight), servos 1-5.
# These are Yahboom's own poses for its colour mat, so they work on the real arm too.
READY = [90, 130, 0, 0, 90]
ABOVE_STACK = [90, 80, 50, 50, 270]
PICK_TOP = [90, 72, 49, 13, 270]       # gripper around the top block of a 4-block stack
PLACE_YELLOW = [65, 22, 64, 56, 270]   # gripper just above the yellow square
LIFT_YELLOW = [65, 90, 90, 90, 270]    # straight up over the yellow square

# Gripper opening: distance of each finger from the centre, in metres.
GRIPPER_OPEN = 0.0325   # fully open (servo 6 at 60 degrees)
GRIPPER_BLOCK = 0.0122  # closed on a 3 cm block (servo 6 at 135 degrees)


def servos_to_radians(servo_degrees):
    """Yahboom servo angle (0-180, 90 = straight) -> ROS joint angle in radians (0 = straight)."""
    return [math.radians(d - 90.0) for d in servo_degrees]


class PickAndPlace(Node):
    def __init__(self):
        super().__init__('pick_and_place')
        self.arm = ActionClient(self, FollowJointTrajectory, '/arm_controller/follow_joint_trajectory')
        self.gripper = ActionClient(self, GripperCommand, '/gripper_controller/gripper_cmd')
        self.last_progress = -1

    def wait_for_controllers(self):
        for client, name in [(self.arm, 'arm'), (self.gripper, 'gripper')]:
            if not client.wait_for_server(timeout_sec=10.0):
                self.get_logger().error(f'The {name} controller is not running. Is the simulator (or robot) on?')
                return False
        return True

    def run_goal(self, client, goal, feedback_callback=None):
        """Send a goal, wait until it is accepted, then wait for its result."""
        send_future = client.send_goal_async(goal, feedback_callback=feedback_callback)
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return None
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return result_future.result().result

    def move_arm(self, servo_degrees, seconds=1.5):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINTS
        point = JointTrajectoryPoint()
        point.positions = servos_to_radians(servo_degrees)
        point.time_from_start = Duration(sec=int(seconds), nanosec=int(seconds % 1 * 1e9))
        goal.trajectory.points = [point]

        self.goal_seconds = seconds
        self.last_progress = -1
        result = self.run_goal(self.arm, goal, self.on_arm_feedback)
        if result is None or result.error_code != FollowJointTrajectory.Result.SUCCESSFUL:
            self.get_logger().error(f'Arm move failed: {result.error_string if result else "rejected"}')
            return False
        return True

    def on_arm_feedback(self, feedback_msg):
        # Feedback arrives many times a second while the arm moves. Report every 25 %.
        elapsed = feedback_msg.feedback.desired.time_from_start
        progress = int(100 * (elapsed.sec + elapsed.nanosec / 1e9) / self.goal_seconds) // 25 * 25
        if progress != self.last_progress:
            self.last_progress = progress
            self.get_logger().info(f'  arm {min(progress, 100)} %')

    def set_gripper(self, opening):
        goal = GripperCommand.Goal()
        goal.command.position = opening
        goal.command.max_effort = 10.0
        result = self.run_goal(self.gripper, goal)
        # When the fingers stop on a block before reaching `opening`, the
        # controller reports stalled=True. That is what a good grasp looks like.
        return result is not None

    def run(self):
        # Each step is (what it does, the call that does it). lambda: delays the
        # call until the loop below reaches that step.
        steps = [
            ('open the gripper', lambda: self.set_gripper(GRIPPER_OPEN)),
            ('go to the ready pose', lambda: self.move_arm(READY, 2.0)),
            ('move above the stack', lambda: self.move_arm(ABOVE_STACK)),
            ('reach the top block', lambda: self.move_arm(PICK_TOP)),
            ('close the gripper on it', lambda: self.set_gripper(GRIPPER_BLOCK)),
            ('lift it', lambda: self.move_arm(ABOVE_STACK)),
            ('lower it onto the yellow square', lambda: self.move_arm(PLACE_YELLOW)),
            ('let go', lambda: self.set_gripper(GRIPPER_OPEN)),
            ('lift clear', lambda: self.move_arm(LIFT_YELLOW)),
            ('back to ready', lambda: self.move_arm(READY, 2.0)),
        ]
        for number, (what, action) in enumerate(steps, start=1):
            self.get_logger().info(f'Step {number}/{len(steps)}: {what}')
            if not action():
                self.get_logger().error('Stopping here.')
                return False
        self.get_logger().info('Done')
        return True


def main(args=None):
    rclpy.init(args=args)
    node = PickAndPlace()
    if node.wait_for_controllers():
        node.run()
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
