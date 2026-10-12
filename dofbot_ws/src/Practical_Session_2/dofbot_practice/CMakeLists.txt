cmake_minimum_required(VERSION 3.8)
project(dofbot_practice)

# ROS 2 Humble targets C++17.
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# ---------------------------------------------------------------------------
# 1. Find every package this one builds against.
#    Each of these has a matching <depend> line in package.xml. If you add a
#    message type, you add it in BOTH files or the build fails.
# ---------------------------------------------------------------------------
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED)

# ---------------------------------------------------------------------------
# 2. Declare one executable per node.
#    add_executable() names the program; ament_target_dependencies() tells it
#    which ROS libraries to link. The name in add_executable is the name you
#    type after "ros2 run dofbot_practice".
# ---------------------------------------------------------------------------
add_executable(joint_state_subscriber src/joint_state_subscriber.cpp)
ament_target_dependencies(joint_state_subscriber rclcpp sensor_msgs)

add_executable(arm_command_publisher src/arm_command_publisher.cpp)
ament_target_dependencies(arm_command_publisher rclcpp trajectory_msgs)

# ---------------------------------------------------------------------------
# 3. Install the executables into the package's lib directory.
#    This is the step that makes "ros2 run" able to find them. Skip it and the
#    build still succeeds, but ros2 run reports "No executable found", which is
#    the single most common mistake in this session.
#
#    TODO: when you add a third node, add its add_executable and
#    ament_target_dependencies above, then add its name to this list.
# ---------------------------------------------------------------------------
install(TARGETS
  joint_state_subscriber
  arm_command_publisher
  DESTINATION lib/${PROJECT_NAME}
)

# ---------------------------------------------------------------------------
# 4. Install the Python nodes.
#    This is the SAME idea as step 3 and a different CMake command, and the
#    difference is worth understanding rather than memorising:
#
#      install(TARGETS ...)   for things CMake COMPILED. It knows where the
#                             binary ended up, so you name the target.
#      install(PROGRAMS ...)  for files that are already runnable as they are.
#                             CMake just copies them, so you name the path.
#
#    Both land in the same place, lib/${PROJECT_NAME}, which is the only
#    directory ros2 run looks in. This is the install(PROGRAMS ...) block you
#    met in Session 1, unchanged.
#
#    The Python files keep their .py extension when installed, so they do not
#    collide with the compiled nodes of the same job and you can run both:
#      ros2 run dofbot_practice joint_state_subscriber       (C++)
#      ros2 run dofbot_practice joint_state_subscriber.py    (Python)
#
#    The files must also be executable in the source tree (chmod +x) and start
#    with a #!/usr/bin/env python3 line, or they install but will not run.
#
#    TODO: when you add a fourth node in Python, add its path to this list.
# ---------------------------------------------------------------------------
install(PROGRAMS
  scripts/joint_state_subscriber.py
  scripts/arm_command_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

# Launch files, if you add any, are installed separately.
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
  OPTIONAL
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
