# ⚙️ Your First C++ Node

📍 **Level:** Intermediate
📚 **Topic:** C++ packages, rclcpp, compiling with CMake

------

## 🧠 1. Why C++?

So far you have used Python (`rclpy`). ROS 2 also has a C++ library, **rclcpp**. The controllers moving your arm, the camera drivers and MoveIt are all written in C++.

| | Python (`rclpy`) | C++ (`rclcpp`) |
|---|---|---|
| Writing code | Quick, short | Longer, stricter |
| Running code | Slower | Fast, predictable timing |
| Before running | Nothing to compile | Must be **compiled** |
| Used for | Scripts, tasks, prototypes | Controllers, drivers, anything fast or time-critical |

To compare the two directly, you will write the **joint monitor from module 7 again, in C++**: same topic, same output.

------

## 📦 2. Create a C++ Package

```
cd ~/dofbot_ws/src
ros2 pkg create my_dofbot_cpp --build-type ament_cmake --dependencies rclcpp sensor_msgs
```

`--dependencies rclcpp sensor_msgs` writes the two libraries you need into `package.xml` and `CMakeLists.txt` for you. Put the package name **before** `--dependencies`: everything after `--dependencies` is read as a dependency.

```
my_dofbot_cpp/
├── CMakeLists.txt
├── include/my_dofbot_cpp/
├── package.xml
└── src/              <- your .cpp files go here
```

------

## 🧩 3. The Code

Create `my_dofbot_cpp/src/joint_monitor.cpp`:

```
// Print the arm's joint angles in degrees once a second, and warn near the limits.
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
```

------

## 🧠 4. Python and C++ Side by Side

| Idea | Python | C++ |
|---|---|---|
| Import a message | `from sensor_msgs.msg import JointState` | `#include "sensor_msgs/msg/joint_state.hpp"` |
| The message type | `JointState` | `sensor_msgs::msg::JointState` |
| A node | `class JointMonitor(Node)` | `class JointMonitor : public rclcpp::Node` |
| Subscribe | `create_subscription(JointState, '/joint_states', self.cb, 10)` | `create_subscription<sensor_msgs::msg::JointState>("/joint_states", 10, std::bind(...))` |
| Timer | `create_timer(1.0, self.cb)` | `create_wall_timer(1s, std::bind(...))` |
| Log | `self.get_logger().info(f'...')` | `RCLCPP_INFO(get_logger(), "...", ...)` |
| Dictionary | `self.positions = {}` | `std::map<std::string, double> positions_` |
| Start | `rclpy.init()` ... `rclpy.spin(node)` | `rclcpp::init(argc, argv)` ... `rclcpp::spin(node)` |

The names follow a rule: the type `sensor_msgs/msg/JointState` becomes the header `sensor_msgs/msg/joint_state.hpp` (lower case with underscores) and the C++ type `sensor_msgs::msg::JointState`.

`std::bind(&JointMonitor::on_joint_states, this, std::placeholders::_1)` means: "call this object's on_joint_states, passing the message as the first argument". It is the C++ way of writing Python's `self.on_joint_states`.

------

## ⚙️ 5. Tell CMake to Compile It

A Python file is copied as it is; a C++ file must be **compiled** into a program. Open `my_dofbot_cpp/CMakeLists.txt`. `ros2 pkg create` already added the `find_package` lines for your dependencies. Add, **above** `ament_package()`:

```
add_executable(joint_monitor src/joint_monitor.cpp)
ament_target_dependencies(joint_monitor rclcpp sensor_msgs)

install(TARGETS
  joint_monitor
  DESTINATION lib/${PROJECT_NAME}
)
```

| Line | What it does |
|---|---|
| `add_executable(joint_monitor src/joint_monitor.cpp)` | Compile this file into a program called `joint_monitor` (the name you will give `ros2 run`) |
| `ament_target_dependencies(joint_monitor rclcpp sensor_msgs)` | Link it with the ROS 2 libraries it uses |
| `install(TARGETS ...)` | Install the compiled program so `ros2 run` finds it. For Python you used `install(PROGRAMS ...)` because there was nothing to compile |

------

## ▶️ 6. Build and Run

```
cd ~/dofbot_ws
colcon build --packages-select my_dofbot_cpp
source install/setup.bash
ros2 run my_dofbot_cpp joint_monitor
```

The build takes longer than for Python (20 to 30 seconds): the compiler is turning your code into machine instructions. Then:

```
[INFO] [joint_monitor]: base    0.0 | shoulder    0.0 | elbow    0.0 | wrist    0.0 | roll   -0.0 | gripper 30.0 mm
```

The same output as your Python monitor. Move the arm (`ros2 run dofbot_bringup dofbot_cmd ready`) and watch it change.

`Stuck? The finished package is exercise_6_cpp. Build it with colcon build --packages-select exercise_6_cpp, source, then ros2 run exercise_6_cpp joint_monitor`

------

## ⚠️ Common Mistakes

| Problem | Cause |
|---|---|
| `fatal error: sensor_msgs/msg/joint_state.hpp: No such file` | `sensor_msgs` missing from `find_package` / `ament_target_dependencies` |
| `undefined reference to ...` at the end of the build | `ament_target_dependencies` is missing a library |
| `No executable found` | `install(TARGETS ...)` missing, or a different name than in `add_executable` |
| Many errors at once | C++ reports a lot after the first mistake. **Fix the first error** and rebuild: the rest often disappear with it |
| Your code changes don't show | C++ must be rebuilt after every change (Python too, unless you change files in `install/`, which you shouldn't) |

------

## 🧪 Try It Yourself

### 🟢 Easy

- Print twice a second (`500ms`)

### 🟡 Medium

- Port the wave node from module 6 to C++: a `rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>` and a wall timer. Add `trajectory_msgs` to `package.xml`, `find_package` and `ament_target_dependencies`.

### 🔴 Challenge

- The `Practical_Session_2/dofbot_practice` package in your workspace contains a C++ joint state subscriber with blanks (`FILL_IN_1` ...). Fill them in from what you learned here and build it with `colcon build --packages-select dofbot_practice`.

------

## 🎯 What You Learned

- C++ nodes use `rclcpp`; the ideas are the same as in Python, the syntax differs
- A C++ program is compiled: `add_executable` + `ament_target_dependencies` + `install(TARGETS ...)`
- Message types map to headers (`joint_state.hpp`) and C++ types (`sensor_msgs::msg::JointState`) by a fixed rule

------

## 🚀 What's Next?

The arm can see. Next you will read its **camera** and find the coloured blocks with OpenCV.
