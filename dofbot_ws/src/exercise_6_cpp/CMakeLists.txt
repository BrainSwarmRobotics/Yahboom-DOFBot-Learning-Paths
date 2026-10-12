cmake_minimum_required(VERSION 3.8)
project(exercise_6_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

# One executable per node: the name here is the name after "ros2 run exercise_6_cpp".
add_executable(joint_monitor src/joint_monitor.cpp)
ament_target_dependencies(joint_monitor rclcpp sensor_msgs)

# Compiled programs are installed with install(TARGETS ...).
install(TARGETS
  joint_monitor
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
