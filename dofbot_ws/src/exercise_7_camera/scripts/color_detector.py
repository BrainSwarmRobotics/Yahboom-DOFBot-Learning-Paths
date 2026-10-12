#!/usr/bin/env python3
"""Exercise 7: find the coloured blocks in the arm camera's picture.

Subscribes to the arm camera, finds red, yellow, green and blue blocks with
HSV colour thresholds, and publishes the colours of the blocks in the middle
of the picture, top to bottom, on /block_colors (std_msgs/String), e.g.
"yellow,red,green,blue". Every 2 s it also saves the picture with the blocks
marked to ~/dofbot_ws/src/snapshots/detections.png.

Run (simulator):  ros2 run exercise_7_camera color_detector.py
Run (real arm):   ros2 run exercise_7_camera color_detector.py --ros-args -p image_topic:=/usb_cam/image_raw/compressed
"""
import os
import time

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import String

# HSV ranges (OpenCV: hue 0-180, saturation and value 0-255). Red needs two
# ranges because its hue wraps around 0.
COLOR_RANGES = {
    'red': [((0, 120, 70), (8, 255, 255)), ((170, 120, 70), (180, 255, 255))],
    'yellow': [((20, 120, 100), (35, 255, 255))],
    'green': [((40, 80, 50), (85, 255, 255))],
    'blue': [((95, 120, 50), (130, 255, 255))],
}
MIN_AREA = 400  # pixels; smaller blobs are noise
DRAW_COLORS = {'red': (0, 0, 255), 'yellow': (0, 255, 255), 'green': (0, 200, 0), 'blue': (255, 0, 0)}
SNAPSHOT = os.path.expanduser('~/dofbot_ws/src/snapshots/detections.png')


def find_blocks(bgr):
    """Return a list of (color, x, y, w, h) for every coloured blob in the picture."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    blocks = []
    for color, ranges in COLOR_RANGES.items():
        mask = np.zeros(hsv.shape[:2], np.uint8)
        for low, high in ranges:
            mask |= cv2.inRange(hsv, np.array(low), np.array(high))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))  # remove specks
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) >= MIN_AREA:
                blocks.append((color, *cv2.boundingRect(contour)))
    return blocks


def middle_column(blocks, width):
    """Blocks whose centre is in the middle third of the picture, top to bottom."""
    middle = [b for b in blocks if width / 3 < b[1] + b[3] / 2 < 2 * width / 3]
    return sorted(middle, key=lambda b: b[2] + b[4] / 2)


class ColorDetector(Node):
    def __init__(self):
        super().__init__('color_detector')
        self.declare_parameter('image_topic', '/camera/image_raw')
        topic = self.get_parameter('image_topic').value

        self.bridge = CvBridge()
        self.last_colors = None
        self.last_processed = 0.0
        self.last_saved = 0.0
        self.publisher_ = self.create_publisher(String, '/block_colors', 10)

        # Compressed pictures (JPEG) are ~20x smaller: use them over the internet.
        if topic.endswith('/compressed'):
            self.create_subscription(CompressedImage, topic, self.on_compressed, qos_profile_sensor_data)
        else:
            self.create_subscription(Image, topic, self.on_image, qos_profile_sensor_data)
        self.get_logger().info(f'Looking for blocks on {topic}')

    def on_image(self, msg):
        self.process(self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8'))

    def on_compressed(self, msg):
        self.process(cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR))

    def process(self, bgr):
        now = time.monotonic()
        if now - self.last_processed < 0.2:  # 5 pictures a second is plenty
            return
        self.last_processed = now

        blocks = find_blocks(bgr)
        stack = middle_column(blocks, bgr.shape[1])
        colors = [b[0] for b in stack]

        self.publisher_.publish(String(data=','.join(colors)))
        if colors != self.last_colors:
            self.get_logger().info(f'Blocks in the middle, top to bottom: {colors or "none"}')
            self.last_colors = colors

        if now - self.last_saved > 2.0:
            self.last_saved = now
            self.save_annotated(bgr, blocks, stack)

    def save_annotated(self, bgr, blocks, stack):
        picture = bgr.copy()
        height, width = picture.shape[:2]
        for x in (width // 3, 2 * width // 3):  # the middle third
            cv2.line(picture, (x, 0), (x, height), (200, 200, 200), 1)
        for color, x, y, w, h in blocks:
            thickness = 3 if (color, x, y, w, h) in stack else 1
            cv2.rectangle(picture, (x, y), (x + w, y + h), DRAW_COLORS[color], thickness)
            cv2.putText(picture, color, (x, max(y - 6, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        DRAW_COLORS[color], 1, cv2.LINE_AA)
        os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
        cv2.imwrite(SNAPSHOT, picture)


def main(args=None):
    rclpy.init(args=args)
    node = ColorDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
