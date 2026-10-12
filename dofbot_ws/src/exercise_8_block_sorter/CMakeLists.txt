cmake_minimum_required(VERSION 3.8)
project(exercise_8_block_sorter)

find_package(ament_cmake REQUIRED)

# Install the Python nodes so that "ros2 run exercise_8_block_sorter <file>" finds them.
install(PROGRAMS
  scripts/block_sorter.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
