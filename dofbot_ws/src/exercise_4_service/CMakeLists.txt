cmake_minimum_required(VERSION 3.8)
project(exercise_4_service)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Turn the interface file(s) into Python and C++ code (srv/MoveToNamedPose.srv).
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/MoveToNamedPose.srv"
)
ament_export_dependencies(rosidl_default_runtime)

# Install the Python nodes so that "ros2 run exercise_4_service <file>" finds them.
install(PROGRAMS
  scripts/named_pose_server.py
  scripts/named_pose_client.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
