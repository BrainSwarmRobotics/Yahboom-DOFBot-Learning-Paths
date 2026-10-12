cmake_minimum_required(VERSION 3.8)
project(exercise_3_custom_message)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Turn the interface file(s) into Python and C++ code (msg/ArmPose.msg).
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ArmPose.msg"
)
ament_export_dependencies(rosidl_default_runtime)

# Install the Python nodes so that "ros2 run exercise_3_custom_message <file>" finds them.
install(PROGRAMS
  scripts/pose_commander.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
