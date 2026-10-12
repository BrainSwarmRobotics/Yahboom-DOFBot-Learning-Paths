#!/usr/bin/env python3
"""Save one picture from a camera topic as a PNG you can open in the editor.

    ros2 run dofbot_lab snapshot.py                         # simulator overview camera
    ros2 run dofbot_lab snapshot.py /camera/image_raw       # simulated arm camera
    ros2 run dofbot_lab snapshot.py /usb_cam/image_raw/compressed   # real arm camera

The picture is written to ~/dofbot_ws/src/snapshots/<name>.png (the name comes
from the topic, e.g. overview_camera.png). Click it in the file explorer to
look at it. Run the command again to take a new one.
"""
import os
import sys

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image

SNAPSHOT_DIR = os.path.expanduser("~/dofbot_ws/src/snapshots")


class Snapshot(Node):
    def __init__(self, topic):
        super().__init__("snapshot")
        self.topic = topic
        self.bridge = CvBridge()
        self.saved_path = None
        # Compressed pictures (JPEG) are much smaller: use them over the internet.
        if topic.endswith("/compressed"):
            self.create_subscription(CompressedImage, topic, self.on_compressed, qos_profile_sensor_data)
        else:
            self.create_subscription(Image, topic, self.on_image, qos_profile_sensor_data)
        self.get_logger().info(f"Waiting for a picture on {topic} ...")

    def on_image(self, msg):
        self.save(self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8"))

    def on_compressed(self, msg):
        self.save(cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR))

    def save(self, picture):
        if self.saved_path:
            return
        # /usb_cam/image_raw/compressed -> usb_cam.png, /overview_camera/image_raw -> overview_camera.png
        name = [part for part in self.topic.split("/") if part][0]
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        self.saved_path = os.path.join(SNAPSHOT_DIR, name + ".png")
        cv2.imwrite(self.saved_path, picture)


def main():
    args = rclpy.utilities.remove_ros_args(sys.argv)[1:]
    topic = args[0] if args else "/overview_camera/image_raw"

    rclpy.init()
    node = Snapshot(topic)
    deadline = node.get_clock().now().nanoseconds + 20e9
    while rclpy.ok() and node.saved_path is None and node.get_clock().now().nanoseconds < deadline:
        rclpy.spin_once(node, timeout_sec=0.5)

    if node.saved_path:
        node.get_logger().info(f"Saved {node.saved_path}")
        status = 0
    else:
        node.get_logger().error(
            f"No picture arrived on {topic} in 20 s. Is the simulator (or robot) running? "
            "Check the name with: ros2 topic list | grep image")
        status = 1
    node.destroy_node()
    rclpy.try_shutdown()
    return status


if __name__ == "__main__":
    sys.exit(main())
