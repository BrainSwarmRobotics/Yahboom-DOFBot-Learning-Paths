#!/usr/bin/env python3
"""Exercise 4: call /move_to_named_pose from code (a service client).

Run:  ros2 run exercise_4_service named_pose_client.py ready
      ros2 run exercise_4_service named_pose_client.py home 3.0
"""
import sys

import rclpy
from rclpy.node import Node

from exercise_4_service.srv import MoveToNamedPose


def main():
    args = rclpy.utilities.remove_ros_args(sys.argv)[1:]
    if not args:
        print('Usage: ros2 run exercise_4_service named_pose_client.py <pose name> [seconds]')
        return 1

    rclpy.init()
    node = Node('named_pose_client')
    client = node.create_client(MoveToNamedPose, '/move_to_named_pose')

    if not client.wait_for_service(timeout_sec=5.0):
        node.get_logger().error('/move_to_named_pose is not available. Start named_pose_server.py first.')
        rclpy.try_shutdown()
        return 1

    request = MoveToNamedPose.Request()
    request.name = args[0]
    request.seconds = float(args[1]) if len(args) > 1 else 2.0

    future = client.call_async(request)             # send the request...
    rclpy.spin_until_future_complete(node, future)  # ...and wait for the answer
    response = future.result()

    if response.success:
        node.get_logger().info(response.message)
    else:
        node.get_logger().error(response.message)

    node.destroy_node()
    rclpy.try_shutdown()
    return 0 if response.success else 1


if __name__ == '__main__':
    sys.exit(main())
