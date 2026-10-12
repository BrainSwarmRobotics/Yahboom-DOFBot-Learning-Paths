// =============================================================================
// arm_command_publisher.cpp
//
// Practical Session 2, Exercise B: drive the arm.
//
// This node publishes a joint trajectory on a timer. As given it holds every
// joint at 0.0 rad, which is safe and boring on purpose: run it first, confirm
// the subscriber from Exercise A sees no movement, then start changing it.
//
// WHAT YOU WILL CHANGE (see the TODO markers below):
//   TODO 1  Put real angles in target_positions so one joint moves.
//   TODO 2  Change time_from_start and watch the arm move faster or slower.
//   TODO 3  Alternate between two poses so the arm sweeps back and forth.
//
// SAFETY: keep your first angles small, under about 0.5 rad from the current
// pose, and keep a hand near the power switch. Watch the real arm, not the
// screen, the first time you run a new target.
//
// Build:  cd ~/dofbot_ws && colcon build --packages-select dofbot_practice
// Source: source ~/dofbot_ws/install/setup.bash
// Run:    ros2 run dofbot_practice arm_command_publisher
// =============================================================================

#include <chrono>
#include <memory>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "trajectory_msgs/msg/joint_trajectory.hpp"
#include "trajectory_msgs/msg/joint_trajectory_point.hpp"

using namespace std::chrono_literals;

class ArmCommandPublisher : public rclcpp::Node
{
public:
  ArmCommandPublisher()
  : Node("arm_command_publisher")
  {
    publisher_ = this->create_publisher<trajectory_msgs::msg::JointTrajectory>(
      "/arm_controller/joint_trajectory",               // confirm with: ros2 topic list
      10);

    // A publisher on its own sends nothing. Something has to call publish().
    // Here a wall timer does it twice a second.
    timer_ = this->create_wall_timer(
      500ms,                                            // TODO 2: try 2000ms
      std::bind(&ArmCommandPublisher::publish_once, this));

    RCLCPP_INFO(this->get_logger(), "Publishing to /arm_controller/joint_trajectory");
  }

private:
  void publish_once()
  {
    auto message = trajectory_msgs::msg::JointTrajectory();

    // The names must match what the arm actually reports. If you are unsure,
    // run: ros2 topic echo /joint_states --once
    message.joint_names = {"joint1", "joint2", "joint3", "joint4", "joint5", "joint6"};

    auto point = trajectory_msgs::msg::JointTrajectoryPoint();

    // TODO 1: replace these with your own angles, in radians, one per joint
    //         above and in the same order. Start by moving ONE joint a little.
    point.positions = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

    // How long the arm should take to arrive. Too short is a jerk, which the
    // controller may refuse or the hardware may not survive.
    point.time_from_start = rclcpp::Duration::from_seconds(2.0);

    // TODO 3: keep a bool member, flip it here, and choose between two
    //         different position vectors so the arm sweeps.

    message.points.push_back(point);
    publisher_->publish(message);

    RCLCPP_INFO(this->get_logger(), "Sent a trajectory with %zu joints",
                message.joint_names.size());
  }

  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ArmCommandPublisher>());
  rclcpp::shutdown();
  return 0;
}
