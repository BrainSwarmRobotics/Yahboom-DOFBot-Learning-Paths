cmake_minimum_required(VERSION 3.8)
project(exercise_7_camera)

find_package(ament_cmake REQUIRED)

# Install the Python nodes so that "ros2 run exercise_7_camera <file>" finds them.
install(PROGRAMS
  scripts/color_detector.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
