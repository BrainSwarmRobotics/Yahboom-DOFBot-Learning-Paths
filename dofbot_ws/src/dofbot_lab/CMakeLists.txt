cmake_minimum_required(VERSION 3.8)
project(dofbot_lab)

find_package(ament_cmake REQUIRED)

# Programs for "ros2 run dofbot_lab ..."
install(PROGRAMS
  scripts/snapshot.py
  scripts/stop_arm.py
  scripts/reset_blocks.py
  scripts/hsv_probe.py
  DESTINATION lib/${PROJECT_NAME}
)

# Simulator launch file, world and bridge config for "ros2 launch dofbot_lab sim.launch.py"
install(DIRECTORY
  launch
  worlds
  config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
