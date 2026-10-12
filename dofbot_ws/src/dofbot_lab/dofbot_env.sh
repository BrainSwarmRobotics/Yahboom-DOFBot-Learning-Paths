# dofbot_env.sh: terminal setup for the DOFBOT learning paths.
#
# Add it to your ~/.bashrc once (Simulation path, module 2):
#
#   echo 'source ~/dofbot_ws/src/dofbot_lab/dofbot_env.sh' >> ~/.bashrc
#
# Every new terminal then
#   * loads your workspace (~/dofbot_ws/install/setup.bash), once it has been built;
#   * talks to the simulator or to the real robot, whichever you chose last,
#     and says which at the start of the prompt: (sim) or (ROBOT).
#
# Commands:
#   use_sim     talk to the simulated DOFBOT in your own console
#   use_robot   talk to the real DOFBOT (only during a booked session)
#   stop_sim    stop every simulator process in this console (when Ctrl+C left some behind)

DOFBOT_ROBOT_HOST=dofbot                                   # the robot's name on the lab network
DOFBOT_ROBOT_PROFILE=/home/project/fastdds_hnet_client.xml # how to find the robot's ROS 2 nodes
DOFBOT_TARGET_FILE="$HOME/.dofbot_target"                  # remembers sim/robot for new terminals

_dofbot_set_sim() {
    unset FASTRTPS_DEFAULT_PROFILES_FILE
    export ROS_LOCALHOST_ONLY=1      # ROS 2 traffic stays inside this console
    export DOFBOT_TARGET=sim
}

_dofbot_set_robot() {
    export FASTRTPS_DEFAULT_PROFILES_FILE="$DOFBOT_ROBOT_PROFILE"
    export ROS_LOCALHOST_ONLY=0
    export DOFBOT_TARGET=robot
}

_dofbot_robot_reachable() {
    [ -f "$DOFBOT_ROBOT_PROFILE" ] && getent hosts "$DOFBOT_ROBOT_HOST" >/dev/null 2>&1
}

use_sim() {
    _dofbot_set_sim
    echo sim > "$DOFBOT_TARGET_FILE"
    ros2 daemon stop >/dev/null 2>&1   # it restarts by itself with the new setting
    echo "This terminal now talks to the SIMULATED DOFBOT (new terminals too)."
}

use_robot() {
    if ! _dofbot_robot_reachable; then
        echo "The real DOFBOT is not reachable from this console."
        echo "It is connected only during a booked session. If you are in one, wait a minute and"
        echo "try again; if it still fails, tell your instructor."
        return 1
    fi
    _dofbot_set_robot
    echo robot > "$DOFBOT_TARGET_FILE"
    ros2 daemon stop >/dev/null 2>&1
    echo "This terminal now talks to the REAL DOFBOT (new terminals too)."
    echo "Your commands move real hardware: watch the arm."
}

stop_sim() {
    pkill -INT -f "ros2 launch dofbot_lab" && sleep 3
    pkill -f "ign gazebo"
    pkill -f "ros_gz_bridge/parameter_bridge"
    pkill -f "robot_state_publisher/robot_state_publisher"
    pkill -f "controller_manager/spawner"
    ros2 daemon stop >/dev/null 2>&1
    echo "Simulator stopped. Start it again with: ros2 launch dofbot_lab sim.launch.py"
}

# Your workspace, once it has been built.
if [ -f "$HOME/dofbot_ws/install/setup.bash" ]; then
    source "$HOME/dofbot_ws/install/setup.bash"
fi

# Use the last choice; fall back to the simulator when the robot isn't connected.
if [ "$(cat "$DOFBOT_TARGET_FILE" 2>/dev/null)" = robot ] && _dofbot_robot_reachable; then
    _dofbot_set_robot
else
    _dofbot_set_sim
fi

_dofbot_prompt() {
    if [ "$DOFBOT_TARGET" = robot ]; then printf '(ROBOT) '; else printf '(sim) '; fi
}
case "$PS1" in
    *_dofbot_prompt*) ;;
    *) PS1='$(_dofbot_prompt)'"$PS1" ;;
esac
