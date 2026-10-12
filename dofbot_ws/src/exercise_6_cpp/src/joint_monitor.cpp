// Exercise 6: the joint monitor from Exercise 2, written in C++.
//
// Subscribes to /joint_states and, once a second, prints every arm joint in
// degrees (gripper in millimetres) and warns when a joint is close to the end
// of its travel.
//
// Build: cd ~/dofbot_ws && colcon build --packages-select exercise_6_cpp
// Run:   ros2 run exercise_6_cpp joint_monitor

#include <chrono>
#include <cmath>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joint_state.hpp"

using namespace std::chrono_literals;

struct JointInfo
{
  std::string name;   // as /joint_states reports it
  std::string label;  // for people
  double min_deg;
  double max_deg;
};

// 0 degrees = straight up.
const std::vector<JointInfo> JOINTS = {
  {"joint1", "base", -90.0, 90.0},
  {"joint2", "shoulder", -90.0, 90.0},
  {"joint3", "elbow", -90.0, 90.0},
  {"joint4", "wrist", -90.0, 90.0},
  {"joint5", "roll", -90.0, 180.0},
};
const double WARN_MARGIN = 5.0;  // degrees from a limit

class JointMonitor : public rclcpp::Node
{
public:
  JointMonitor()
  : Node("joint_monitor")
  {
    // Subscriber: on_joint_states runs every time a JointState message arrives.
    subscription_ = create_subscription<sensor_msgs::msg::JointState>(
      "/joint_states", 10,
      std::bind(&JointMonitor::on_joint_states, this, std::placeholders::_1));

    // Timer: print once a second.
    timer_ = create_wall_timer(1s, std::bind(&JointMonitor::print_joints, this));
  }

private:
  void on_joint_states(const sensor_msgs::msg::JointState::SharedPtr msg)
  {
    // name[i] belongs to position[i]. Match by name: the order is not guaranteed.
    const size_t count = std::min(msg->name.size(), msg->position.size());
    for (size_t i = 0; i < count; ++i) {
      positions_[msg->name[i]] = msg->position[i];
    }
  }

  void print_joints()
  {
    if (positions_.empty()) {
      RCLCPP_INFO(get_logger(), "No /joint_states yet. Is the simulator (or robot) running?");
      return;
    }

    std::string line;
    for (const auto & joint : JOINTS) {
      auto found = positions_.find(joint.name);
      if (found == positions_.end()) {
        continue;
      }
      const double degrees = found->second * 180.0 / M_PI;
      char part[40];
      std::snprintf(part, sizeof(part), "%s %6.1f | ", joint.label.c_str(), degrees);
      line += part;
      if (degrees < joint.min_deg + WARN_MARGIN || degrees > joint.max_deg - WARN_MARGIN) {
        RCLCPP_WARN(
          get_logger(), "%s (%s) is near the end of its travel: %.1f deg",
          joint.label.c_str(), joint.name.c_str(), degrees);
      }
    }

    auto gripper = positions_.find("finger_left_joint");
    if (gripper != positions_.end()) {
      char part[40];
      std::snprintf(part, sizeof(part), "gripper %4.1f mm", gripper->second * 1000.0);
      line += part;
    }
    RCLCPP_INFO(get_logger(), "%s", line.c_str());
  }

  std::map<std::string, double> positions_;  // joint name -> latest position
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr subscription_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<JointMonitor>());
  rclcpp::shutdown();
  return 0;
}
