// =============================================================================
// joint_state_subscriber.cpp
//
// Practical Session 2, Exercise A: read the arm back.
//
// Your job is to write a node that subscribes to the topic the arm publishes
// its joint positions on, and prints them.
//
// HOW TO USE THIS FILE
//   Every place you have to write something is marked FILL_IN_<n>.
//   Search the file for "FILL_IN" to find them all.
//
//   This file does NOT compile as given. That is deliberate. A blank left in
//   place becomes a compiler error on that line, usually naming it:
//
//     error: 'FILL_IN_9' was not declared in this scope
//
//   Two things to expect while you work through it. The #include blank reports
//   itself differently, as "error: #include expects FILENAME", because the
//   preprocessor gives up before it ever sees the name. And one blank can
//   produce half a dozen errors at once, since the compiler keeps going after
//   it has lost its footing. So always read the FIRST error, fix that, and
//   rebuild. The rest usually vanish with it.
//
// THE BLANKS
//   FILL_IN_1  the header file that defines the message type
//   FILL_IN_2  the message type itself
//   FILL_IN_3  the topic name, as a quoted string
//   FILL_IN_4  the queue depth
//   FILL_IN_5  the message type again, in the callback signature
//   FILL_IN_6  the field holding the joint names
//   FILL_IN_7  the field holding the joint positions
//   FILL_IN_8  the two values to print
//   FILL_IN_9  the message type a third time, on the member variable
//
// FINDING THE ANSWERS YOURSELF
//   Do not guess, ask the robot. With the arm running:
//
//     ros2 topic list                       which topics exist
//     ros2 topic info /the_topic_you_want   what type it carries
//     ros2 interface show <that type>       what fields are inside it
//     ros2 topic echo /the_topic_you_want   see real values go past
//
//   Those four commands are all you need. Note how the type name is written
//   differently in the two places you will use it:
//
//     ros2 interface show   sensor_msgs/msg/JointState     (slashes)
//     C++ include           "sensor_msgs/msg/joint_state.hpp"   (lower_case)
//     C++ type              sensor_msgs::msg::JointState        (colons)
//
// WHEN IT RUNS
//   Once it builds and prints, make these three changes in order:
//     TODO 1  Print only the one joint you care about, not all of them.
//     TODO 2  Warn when that joint moves outside a range you choose.
//     TODO 3  Change the topic name to something that does not exist and watch
//             the node go quiet, to prove to yourself that a subscriber only
//             ever hears the topic it asked for. Then change it back.
//
// Build:  cd ~/dofbot_ws && colcon build --packages-select dofbot_practice
// Source: source ~/dofbot_ws/install/setup.bash
// Run:    ros2 run dofbot_practice joint_state_subscriber
// =============================================================================

#include <algorithm>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"

// FILL_IN_1: include the header that defines the message type this topic
// carries. The rule for turning a type name into a header path: the package
// name stays, the type name becomes lower_case_with_underscores, and the
// extension is .hpp. So geometry_msgs/msg/Twist lives in
// "geometry_msgs/msg/twist.hpp". Work out the one you need the same way.
#include FILL_IN_1

class JointStateSubscriber : public rclcpp::Node
{
public:
  JointStateSubscriber()
  : Node("joint_state_subscriber")   // the node name, as ros2 node list shows it
  {
    // create_subscription<MessageType>(topic, queue_depth, callback).
    //
    // FILL_IN_2: the message type, written with colons, for example
    //            some_package::msg::SomeType
    // FILL_IN_3: the topic name in double quotes, exactly as ros2 topic list
    //            prints it, leading slash included
    // FILL_IN_4: the queue depth, which is how many messages rclcpp will hold
    //            for you if your callback is slower than the publisher. Any
    //            small number works here; 10 is a normal starting value.
    subscription_ = this->create_subscription<FILL_IN_2>(
      FILL_IN_3_TOPIC_NAME,
      FILL_IN_4_QUEUE_DEPTH,
      std::bind(&JointStateSubscriber::on_joint_state, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "Listening for joint states");
  }

private:
  // Called once per message that arrives. Never block in here: ROS 2 cannot
  // deliver the next message until this function returns.
  //
  // FILL_IN_5: the same message type as FILL_IN_2. The ::SharedPtr suffix is
  //            already written for you, so you only need the type itself.
  void on_joint_state(const FILL_IN_5::SharedPtr msg)
  {
    // The message carries parallel arrays: the name at index i belongs to the
    // position at index i. Run "ros2 interface show" on the type to see what
    // those two fields are called.
    //
    // FILL_IN_6: the field holding the joint names
    // FILL_IN_7: the field holding the joint positions
    //
    // Take the smaller of the two lengths rather than trusting either one. A
    // publisher is allowed to send names with no positions, and your node must
    // not crash when it does.
    const size_t count = std::min(msg->FILL_IN_6.size(), msg->FILL_IN_7.size());

    for (size_t i = 0; i < count; ++i) {
      // TODO 1: skip every joint except the one you picked, for example
      //         if (msg->FILL_IN_6[i] != "joint1") { continue; }

      // TODO 2: compare this position against a limit of your own and use
      //         RCLCPP_WARN instead of RCLCPP_INFO when it is exceeded.

      // FILL_IN_8: pass the name and the position for this index. The format
      //            string already expects a C string and then a double, so the
      //            name needs .c_str() on the end of it.
      RCLCPP_INFO(
        this->get_logger(), "%-10s %7.3f rad",
        FILL_IN_8);
    }
  }

  // FILL_IN_9: the same message type once more. A subscription is typed, so
  //            the member that stores it has to name the type too.
  rclcpp::Subscription<FILL_IN_9>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  // spin() blocks and pumps callbacks until you press Ctrl and C. Without it
  // the node exists but never hears anything.
  rclcpp::spin(std::make_shared<JointStateSubscriber>());
  rclcpp::shutdown();
  return 0;
}
