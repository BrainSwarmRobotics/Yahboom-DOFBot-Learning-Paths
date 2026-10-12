#!/usr/bin/env python3
# =============================================================================
# joint_state_subscriber.py
#
# Practical Session 2, Exercise A, Python version.
#
# This is the same exercise as src/joint_state_subscriber.cpp. Do it in
# whichever language you are more comfortable with. Reading both side by side
# is worthwhile: the concepts are identical and only the syntax differs.
#
# HOW TO USE THIS FILE
#   Every place you have to write something is marked FILL_IN_<n>.
#   Search the file for "FILL_IN" to find them all.
#
#   This file does NOT run as given. That is deliberate. Python will stop at
#   the first blank you left behind and name it, for example:
#
#     ImportError: cannot import name 'FILL_IN_1' from 'sensor_msgs.msg'
#     NameError: name 'FILL_IN_3_TOPIC_NAME' is not defined
#
#   so the error will tell you which blank you still owe it. Unlike C++, which
#   reports every blank at build time, Python only finds them one at a time as
#   it reaches them, so expect to run the node several times.
#
# THE BLANKS
#   FILL_IN_1  the message type to import
#   FILL_IN_2  the message type, passed to create_subscription
#   FILL_IN_3  the topic name, as a quoted string
#   FILL_IN_4  the queue depth
#   FILL_IN_5  the field holding the joint names
#   FILL_IN_6  the field holding the joint positions
#   FILL_IN_7  the two values to print
#
# FINDING THE ANSWERS YOURSELF
#   Do not guess, ask the robot. With the arm running:
#
#     ros2 topic list                       which topics exist
#     ros2 topic info /the_topic_you_want   what type it carries
#     ros2 interface show <that type>       what fields are inside it
#     ros2 topic echo /the_topic_you_want   see real values go past
#
#   Those four commands are all you need. Note how the type name is written
#   differently in the two places you will use it:
#
#     ros2 interface show   sensor_msgs/msg/JointState   (slashes)
#     Python import         from sensor_msgs.msg import JointState
#
#   The msg part of the path becomes .msg, and the type name itself does not
#   change at all. That is the whole rule.
#
# WHEN IT RUNS
#   Once it runs and prints, make these three changes in order:
#     TODO 1  Print only the one joint you care about, not all of them.
#     TODO 2  Warn when that joint moves outside a range you choose.
#     TODO 3  Change the topic name to something that does not exist and watch
#             the node go quiet, to prove to yourself that a subscriber only
#             ever hears the topic it asked for. Then change it back.
#
# Build:  cd ~/dofbot_ws && colcon build --packages-select dofbot_practice
# Source: source ~/dofbot_ws/install/setup.bash
# Run:    ros2 run dofbot_practice joint_state_subscriber.py
#
# Note the .py on the end of the run command. That is the installed file name.
# The C++ node for the same job installs without an extension, so the two
# never collide and you can run both at once.
# =============================================================================

import rclpy
from rclpy.node import Node

# FILL_IN_1: import the message type this topic carries. The package name
# gains a .msg, and the type name is written exactly as ros2 interface show
# prints it. So geometry_msgs/msg/Twist is imported as
# "from geometry_msgs.msg import Twist". Work out the one you need the same way.
from sensor_msgs.msg import FILL_IN_1


class JointStateSubscriber(Node):
    def __init__(self):
        super().__init__('joint_state_subscriber')   # as ros2 node list shows it

        # create_subscription(MessageType, topic, callback, queue_depth).
        #
        # FILL_IN_2: the message type you imported above, by name and with no
        #            quotes around it
        # FILL_IN_3: the topic name in quotes, exactly as ros2 topic list
        #            prints it, leading slash included
        # FILL_IN_4: the queue depth, which is how many messages rclpy will
        #            hold for you if your callback is slower than the
        #            publisher. Any small number works; 10 is a normal start.
        self.subscription = self.create_subscription(
            FILL_IN_2,
            FILL_IN_3_TOPIC_NAME,
            self.on_joint_state,
            FILL_IN_4_QUEUE_DEPTH)

        self.get_logger().info('Listening for joint states')

    # Called once per message that arrives. Never block in here: ROS 2 cannot
    # deliver the next message until this function returns.
    def on_joint_state(self, msg):
        # The message carries parallel arrays: the name at index i belongs to
        # the position at index i. Run "ros2 interface show" on the type to see
        # what those two fields are called.
        #
        # FILL_IN_5: the field holding the joint names
        # FILL_IN_6: the field holding the joint positions
        #
        # Take the smaller of the two lengths rather than trusting either one.
        # A publisher is allowed to send names with no positions, and your node
        # must not crash when it does.
        count = min(len(msg.FILL_IN_5), len(msg.FILL_IN_6))

        for i in range(count):
            # TODO 1: skip every joint except the one you picked, for example
            #         if msg.FILL_IN_5[i] != 'joint1': continue

            # TODO 2: compare this position against a limit of your own and
            #         call self.get_logger().warn(...) when it is exceeded.

            # FILL_IN_7: pass the name and the position for this index, in
            #            that order. The format string expects two values.
            self.get_logger().info(
                '{:<10} {:7.3f} rad'.format(FILL_IN_7))


def main(args=None):
    rclpy.init(args=args)
    node = JointStateSubscriber()
    try:
        # spin() blocks and pumps callbacks until you press Ctrl and C.
        # Without it the node exists but never hears anything.
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
