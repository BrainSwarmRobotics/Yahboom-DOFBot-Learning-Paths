#!/usr/bin/env python3
"""Exercise 8 (capstone): sort the stack of blocks by colour.

1. Look at the stack on the centre square with the arm camera and read the
   colours from top to bottom (the colour detection of Exercise 7).
2. Take the blocks off one by one, top first, and put each on the square of
   its own colour (the actions of Exercise 5).
3. With restore:=true, build the stack again afterwards, in the same order,
   so the next person finds the table as you did.

Run (simulator):  ros2 run exercise_8_block_sorter block_sorter.py
Run (real arm):   ros2 run exercise_8_block_sorter block_sorter.py --ros-args \
                    -p image_topic:=/usb_cam/image_raw/compressed -p check_grasp:=false
Reset (simulator): ros2 run dofbot_lab reset_blocks.py --shuffle
"""
import math
import time

import cv2
import numpy as np
import rclpy
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory, GripperCommand
from cv_bridge import CvBridge
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image
from trajectory_msgs.msg import JointTrajectoryPoint

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']

# --- Poses: Yahboom servo angles in degrees (90 = straight), servos 1-5 --------
READY = [90, 130, 0, 0, 90]
LOOK = [90, 135, 15, 0, 90]           # the camera sees the whole stack from the side
TRAVEL = [90, 80, 50, 50, 270]        # high above the stack: the way from one place to another

# Every place where a block can be has two poses:
#   'over': 3.5 cm straight above it, where the gripper comes down from and goes back up to
#   'at':   the gripper around the block, 2 mm above where the block rests
# Coming down vertically keeps the open fingers from pushing the block (or the
# stack) sideways, and letting go just above the surface keeps the block from
# dropping and tipping. The poses were worked out from Yahboom's poses for this
# mat with the arm's inverse kinematics.
STACK = {  # level 1 = the bottom of the stack on the centre square
    4: {'over': [90, 78, 53, 13, 270], 'at': [90, 72, 49, 14, 270]},
    3: {'over': [90, 76, 44, 17, 270], 'at': [90, 68, 41, 20, 270]},
    2: {'over': [90, 74, 32, 26, 270], 'at': [90, 63, 32, 30, 270]},
    1: {'over': [90, 65, 31, 30, 270], 'at': [90, 53, 32, 35, 270]},
}
SQUARES = {  # the four colour squares
    'yellow': {'over': [65, 34, 55, 55, 270], 'at': [65, 22, 60, 58, 270]},
    'red': {'over': [117, 35, 54, 55, 270], 'at': [117, 20, 66, 53, 270]},
    'green': {'over': [136, 76, 24, 20, 270], 'at': [136, 65, 20, 29, 270]},
    'blue': {'over': [44, 78, 21, 21, 270], 'at': [44, 65, 21, 27, 270]},
}
GRIPPER_OPEN = 0.0325    # m, servo 6 at 60 degrees
GRIPPER_BLOCK = 0.0122   # m, servo 6 at 135 degrees: squeezing a 3 cm block
GRIPPER_RESEAT = 0.019   # m, just open enough to let a block turn straight

# --- Colour detection (as in Exercise 7) ---------------------------------------
COLOR_RANGES = {
    'red': [((0, 120, 70), (8, 255, 255)), ((170, 120, 70), (180, 255, 255))],
    'yellow': [((20, 120, 100), (35, 255, 255))],
    'green': [((40, 80, 50), (85, 255, 255))],
    'blue': [((95, 120, 50), (130, 255, 255))],
}
MIN_AREA = 400


def find_blocks(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    blocks = []
    for color, ranges in COLOR_RANGES.items():
        mask = np.zeros(hsv.shape[:2], np.uint8)
        for low, high in ranges:
            mask |= cv2.inRange(hsv, np.array(low), np.array(high))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) >= MIN_AREA:
                blocks.append((color, *cv2.boundingRect(contour)))
    return blocks


def stack_colors(bgr):
    """Colours of the blocks in the middle third of the picture, top to bottom."""
    width = bgr.shape[1]
    middle = [b for b in find_blocks(bgr) if width / 3 < b[1] + b[3] / 2 < 2 * width / 3]
    return [b[0] for b in sorted(middle, key=lambda b: b[2] + b[4] / 2)]


def servos_to_radians(servo_degrees):
    return [math.radians(d - 90.0) for d in servo_degrees]


class BlockSorter(Node):
    def __init__(self):
        super().__init__('block_sorter')
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('restore', False)
        self.declare_parameter('check_grasp', True)
        topic = self.get_parameter('image_topic').value

        self.arm = ActionClient(self, FollowJointTrajectory, '/arm_controller/follow_joint_trajectory')
        self.gripper = ActionClient(self, GripperCommand, '/gripper_controller/gripper_cmd')
        self.bridge = CvBridge()
        self.picture = None
        if topic.endswith('/compressed'):
            self.create_subscription(CompressedImage, topic, self.on_compressed, qos_profile_sensor_data)
        else:
            self.create_subscription(Image, topic, self.on_image, qos_profile_sensor_data)

    # --- camera ---------------------------------------------------------------
    def on_image(self, msg):
        self.picture = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    def on_compressed(self, msg):
        self.picture = cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR)

    def read_stack(self, timeout=15.0):
        """Wait until three pictures in a row show the same stack, and return it."""
        readings = []
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.picture = None
            while self.picture is None and time.monotonic() < deadline:
                rclpy.spin_once(self, timeout_sec=0.1)
            if self.picture is None:
                break
            readings.append(stack_colors(self.picture))
            if len(readings) >= 3 and readings[-1] == readings[-2] == readings[-3]:
                return readings[-1]
        self.get_logger().error('No steady picture of the stack. Is the camera running?')
        return None

    # --- arm and gripper (as in Exercise 5) -------------------------------------
    def run_goal(self, client, goal):
        send_future = client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()
        if not goal_handle.accepted:
            return None
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return result_future.result().result

    def move_arm(self, servo_degrees, seconds=1.5):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINTS
        goal.trajectory.points = [JointTrajectoryPoint(
            positions=servos_to_radians(servo_degrees),
            time_from_start=Duration(sec=int(seconds), nanosec=int(seconds % 1 * 1e9)))]
        result = self.run_goal(self.arm, goal)
        if result is None or result.error_code != FollowJointTrajectory.Result.SUCCESSFUL:
            self.get_logger().error(f'Arm move to {servo_degrees} failed')
            return False
        return True

    def set_gripper(self, opening):
        goal = GripperCommand.Goal()
        goal.command.position = opening
        goal.command.max_effort = 10.0
        return self.run_goal(self.gripper, goal)

    def open_gripper(self):
        return self.set_gripper(GRIPPER_OPEN) is not None

    def grasp(self):
        """Close on a block. In the simulator a block stops the fingers before they
        reach GRIPPER_BLOCK, so if they get there they closed on nothing. The real
        DOFBOT reports where its gripper should be, not where it is, so it always
        "gets there": turn the check off there with check_grasp:=false."""
        # Close, open a little, close again: a block that sits at a slight angle
        # is squared up by the first squeeze, so the second one holds it straight.
        if self.set_gripper(GRIPPER_BLOCK) is None or self.set_gripper(GRIPPER_RESEAT) is None:
            return False
        result = self.set_gripper(GRIPPER_BLOCK)
        if result is None:
            return False
        if self.get_parameter('check_grasp').value and result.reached_goal:
            self.get_logger().error('The gripper closed on nothing: the block is not where expected.')
            self.open_gripper()
            return False
        return True

    def carry(self, source, target):
        """Pick up the block at `source` and put it down at `target` (each a dict with 'over' and 'at')."""
        steps = [
            lambda: self.move_arm(source['over']),
            lambda: self.move_arm(source['at'], 1.0),    # straight down
            lambda: self.grasp(),
            lambda: self.move_arm(source['over'], 1.0),  # straight up
            lambda: self.move_arm(TRAVEL),
            lambda: self.move_arm(target['over']),
            lambda: self.move_arm(target['at'], 1.0),
            lambda: self.open_gripper(),
            lambda: self.move_arm(target['over'], 1.0),
            lambda: self.move_arm(TRAVEL),
        ]
        return all(step() for step in steps)  # all() stops at the first step that fails

    # --- the task -------------------------------------------------------------
    def run(self):
        log = self.get_logger()
        for client, name in [(self.arm, 'arm'), (self.gripper, 'gripper')]:
            if not client.wait_for_server(timeout_sec=10.0):
                log.error(f'The {name} controller is not running. Is the simulator (or robot) on?')
                return False

        log.info('Looking at the stack')
        if not (self.open_gripper() and self.move_arm(READY, 2.0) and self.move_arm(LOOK)):
            return False
        time.sleep(1.0)  # let the camera settle
        stack = self.read_stack()
        if not stack:
            return False
        if len(stack) > 4 or len(set(stack)) != len(stack):
            log.error(f'Expected up to 4 blocks of different colours, saw {stack}')
            return False
        log.info(f'Stack, top to bottom: {stack}')
        if not self.move_arm(TRAVEL):
            return False

        # Sort: the top block is at level len(stack), the bottom one at level 1.
        for index, color in enumerate(stack):
            level = len(stack) - index
            log.info(f'{color}: stack level {level} -> {color} square')
            if not self.carry(STACK[level], SQUARES[color]):
                return False

        if self.get_parameter('restore').value:
            log.info('Building the stack again')
            for level, color in enumerate(reversed(stack), start=1):
                log.info(f'{color}: {color} square -> stack level {level}')
                if not self.carry(SQUARES[color], STACK[level]):
                    return False

        self.move_arm(READY, 2.0)
        log.info('Done')
        return True


def main(args=None):
    rclpy.init(args=args)
    node = BlockSorter()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
