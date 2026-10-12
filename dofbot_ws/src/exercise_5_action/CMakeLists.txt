cmake_minimum_required(VERSION 3.8)
project(exercise_5_action)

find_package(ament_cmake REQUIRED)

# Install the Python nodes so that "ros2 run exercise_5_action <file>" finds them.
install(PROGRAMS
  scripts/pick_and_place.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
