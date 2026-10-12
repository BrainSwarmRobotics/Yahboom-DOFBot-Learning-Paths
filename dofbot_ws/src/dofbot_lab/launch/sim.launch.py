"""Start the simulated DOFBOT for the learning path.

    ros2 launch dofbot_lab sim.launch.py              # no window: works in the browser console
    ros2 launch dofbot_lab sim.launch.py gui:=true    # Gazebo window + RViz (needs a desktop)

The same arm, controllers and colour mat as dofbot_gazebo's simulator (and as
the real DOFBOT), with these additions for the learning path:

  * an overview camera on /overview_camera/image_raw, so you can watch the
    arm without a desktop:  ros2 run dofbot_lab snapshot.py
  * the simulator stays private to your console, so it never mixes with
    another student's simulator or with the real robot;
  * the simulated joints can travel 0.02 rad past the servo range. A target
    exactly on Gazebo's joint limit (servo 0 or 180 degrees, which Yahboom's
    poses use) otherwise leaves that joint stuck there.
"""
import os
import re
import socket

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler,
                            SetEnvironmentVariable, UnsetEnvironmentVariable)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

LIMIT_MARGIN = {"revolute": 0.02, "prismatic": 0.001}  # rad, m


def widen_joint_limits(urdf):
    """Move every revolute/prismatic <limit> outwards by LIMIT_MARGIN."""
    def widen(joint):
        kind = re.search(r'<joint\b[^>]*\btype="(\w+)"', joint.group(0))  # ros2_control <joint>s have none
        if not kind or kind.group(1) not in LIMIT_MARGIN:
            return joint.group(0)
        margin = LIMIT_MARGIN[kind.group(1)]
        text = re.sub(r'lower="([-\d.e]+)"', lambda m: f'lower="{float(m.group(1)) - margin}"', joint.group(0))
        return re.sub(r'upper="([-\d.e]+)"', lambda m: f'upper="{float(m.group(1)) + margin}"', text)
    return re.sub(r"<joint\b.*?</joint>", widen, urdf, flags=re.S)


def simulator(context):
    lab = get_package_share_directory("dofbot_lab")
    gui = LaunchConfiguration("gui").perform(context) == "true"

    controllers = os.path.join(get_package_share_directory("dofbot_bringup"),
                               "config", "ros2_controllers.yaml")
    urdf = xacro.process_file(
        os.path.join(get_package_share_directory("dofbot_description"), "urdf", "dofbot.urdf.xacro"),
        mappings={"hardware": "gz", "controllers_file": controllers}).toxml()
    robot_description = widen_joint_limits(urdf)

    world = os.path.join(lab, "worlds", "dofbot_lab.sdf")
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")),
        launch_arguments={"gz_args": f"-r -v 2 {'' if gui else '-s '}{world}"}.items())

    spawn = Node(package="ros_gz_sim", executable="create", output="screen",
                 arguments=["-name", "dofbot", "-topic", "robot_description", "-z", "0.0"])

    def spawner(name):
        return Node(package="controller_manager", executable="spawner", output="screen",
                    arguments=[name, "--controller-manager", "/controller_manager"])

    joint_states = spawner("joint_state_broadcaster")

    return [
        gazebo,
        Node(package="robot_state_publisher", executable="robot_state_publisher", output="screen",
             parameters=[{"robot_description": robot_description, "use_sim_time": True}]),
        # Clock, the arm camera and the overview camera, Gazebo -> ROS.
        Node(package="ros_gz_bridge", executable="parameter_bridge", output="screen",
             parameters=[{"config_file": os.path.join(lab, "config", "bridge.yaml"),
                          "use_sim_time": True}]),
        spawn,
        # Controllers can only load once Gazebo has created the robot's controller manager.
        RegisterEventHandler(OnProcessExit(target_action=spawn, on_exit=[joint_states])),
        RegisterEventHandler(OnProcessExit(target_action=joint_states, on_exit=[
            spawner("arm_controller"), spawner("gripper_controller")])),
        Node(package="rviz2", executable="rviz2", condition=IfCondition(str(gui)),
             arguments=["-d", os.path.join(get_package_share_directory("dofbot_description"),
                                           "rviz", "dofbot.rviz")],
             parameters=[{"use_sim_time": True}]),
    ]


def generate_launch_description():
    # Gazebo finds package://dofbot_description/... meshes through this path.
    share_parent = os.path.dirname(get_package_share_directory("dofbot_description"))
    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="false",
                              description="true: open the Gazebo window and RViz (needs a desktop)"),
        # ROS 2 traffic stays inside this console (no robot, no other students).
        SetEnvironmentVariable("ROS_LOCALHOST_ONLY", "1"),
        UnsetEnvironmentVariable("FASTRTPS_DEFAULT_PROFILES_FILE"),
        # Gazebo's own messages too: a partition only this console uses.
        SetEnvironmentVariable("IGN_PARTITION", "dofbot_" + socket.gethostname()),
        AppendEnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", share_parent),
        OpaqueFunction(function=simulator),
    ])
