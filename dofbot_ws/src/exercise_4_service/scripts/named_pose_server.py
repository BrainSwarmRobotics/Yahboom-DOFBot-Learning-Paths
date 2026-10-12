#!/usr/bin/env python3
"""Exercise 4: a service that moves the arm to a pose by name.

Offers /move_to_named_pose (exercise_4_service/srv/MoveToNamedPose). The
request names a pose; the server looks it up, sends it to the arm controller
and answers straight away.

Run:   ros2 run exercise_4_service named_pose_server.py
Call:  ros2 service call /move_to_named_pose exercise_4_service/srv/MoveToNamedPose "{name: ready, seconds: 2.0}"
"""
import rclpy
from builtin_interfaces.msg import Duration
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from exercise_4_service.srv import MoveToNamedPose

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']

# Named poses in radians (0 everywhere = straight up).
POSES = {
    'home': [0.0, 0.0, 0.0, 0.0, 0.0],             # straight up
    'ready': [0.0, 0.698, -1.571, -1.571, 0.0],    # camera looking at the mat (Yahboom's start pose)
    'look': [0.0, 0.785, -1.309, -1.571, 0.0],     # camera looking at the block stack
    'left': [1.2, -0.5, -0.6, -0.6, 0.0],          # leaning out to the left
    'right': [-1.2, -0.5, -0.6, -0.6, 0.0],        # leaning out to the right
}


class NamedPoseServer(Node):
    def __init__(self):
        super().__init__('named_pose_server')
        self.publisher_ = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.service = self.create_service(MoveToNamedPose, '/move_to_named_pose', self.handle_request)
        self.get_logger().info(f'Ready. Known poses: {", ".join(POSES)}')

    def handle_request(self, request, response):
        if request.name not in POSES:
            response.success = False
            response.message = f'Unknown pose "{request.name}". Known poses: {", ".join(POSES)}'
            self.get_logger().warn(response.message)
            return response

        seconds = max(request.seconds, 1.0)
        point = JointTrajectoryPoint()
        point.positions = POSES[request.name]
        point.time_from_start = Duration(sec=int(seconds), nanosec=int(seconds % 1 * 1e9))
        msg = JointTrajectory()
        msg.joint_names = JOINTS
        msg.points = [point]
        self.publisher_.publish(msg)

        response.success = True
        response.message = f'Moving to "{request.name}" in {seconds:.1f} s'
        self.get_logger().info(response.message)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = NamedPoseServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
