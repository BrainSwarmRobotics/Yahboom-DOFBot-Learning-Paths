# 🐧 Linux Command Line Essentials

📍 **Level:** Absolute beginner
📚 **Topic:** The terminal commands you need for this course

------

## 🧠 Why the Terminal?

Your console runs **Linux**, like almost every robot. In robotics, nearly everything is done by typing commands in a **terminal**: building code, starting the robot, looking at its data, sending it commands.

You don't need to learn all of Linux. The tables below are everything this course uses. Come back to this page whenever a command looks unfamiliar.

`Tip: press Tab while typing a file name, folder name or command and the terminal completes it for you. It saves typing and avoids spelling mistakes.`

------

## 🟢 Beginner Commands (you will use these every day)

| Command | What it does | Example |
|---|---|---|
| `pwd` | Shows which folder you are in | `pwd` |
| `ls` | Lists the files and folders here | `ls` |
| `ls -l` | Lists them with details (size, date, permissions) | `ls -l` |
| `cd <folder>` | Moves into a folder | `cd ~/dofbot_ws` |
| `cd ..` | Moves up one folder | `cd ..` |
| `cd ~` | Goes to your home folder (`/home/user`) | `cd ~` |
| `mkdir -p <folder>` | Creates a folder (and any missing parents) | `mkdir -p scripts` |
| `touch <file>` | Creates an empty file | `touch wave_node.py` |
| `cat <file>` | Prints a file in the terminal | `cat package.xml` |
| `cp <from> <to>` | Copies a file | `cp a.py b.py` |
| `mv <from> <to>` | Moves or renames a file | `mv old.py new.py` |
| `rm <file>` | Deletes a file (there is no recycle bin!) | `rm test.py` |
| `clear` | Clears the terminal screen | `clear` |

`~` is short for your home folder, `/home/user`. So `~/dofbot_ws` means `/home/user/dofbot_ws`.

------

## ⌨️ Keys You Need

| Key | What it does |
|---|---|
| `Tab` | Completes a command or file name |
| `↑` / `↓` | Brings back the commands you typed before |
| `Ctrl + C` | **Stops the program running in this terminal.** This is how you stop a node, the simulator, or a command that keeps publishing |
| `Ctrl + Shift + V` | Pastes into the terminal |

------

## 🟡 ROS 2 Commands (the course workflow)

| Command | What it does | Example |
|---|---|---|
| `colcon build --packages-select <pkg>` | Builds one package of your workspace | `colcon build --packages-select my_dofbot` |
| `source install/setup.bash` | Tells this terminal about what you just built | `source install/setup.bash` |
| `ros2 pkg create` | Creates a new package | `ros2 pkg create --build-type ament_cmake my_dofbot` |
| `ros2 run <pkg> <program>` | Starts a program (a node) | `ros2 run dofbot_bringup dofbot_cmd state` |
| `ros2 launch <pkg> <file>` | Starts several programs at once | `ros2 launch dofbot_lab sim.launch.py` |
| `ros2 node list` | Lists the running nodes | `ros2 node list` |
| `ros2 topic list` | Lists the topics | `ros2 topic list` |
| `ros2 topic echo <topic>` | Prints the messages on a topic as they arrive | `ros2 topic echo /joint_states` |
| `ros2 topic info <topic>` | Shows a topic's type and who uses it | `ros2 topic info /joint_states` |
| `ros2 topic hz <topic>` | Measures how often a topic is published | `ros2 topic hz /joint_states` |
| `ros2 interface show <type>` | Shows the fields of a message type | `ros2 interface show sensor_msgs/msg/JointState` |

------

## 🔴 Advanced Commands (sending commands and debugging)

| Command | What it does | Example |
|---|---|---|
| `ros2 topic pub --once <topic> <type> "<data>"` | Publishes one message | moves the arm in module 3 |
| `ros2 service list` / `call` | Lists services / calls one | `ros2 service list` |
| `ros2 action list` / `send_goal` | Lists actions / sends a goal | `ros2 action list` |
| `ros2 control list_controllers` | Shows the robot's controllers and whether they are active | `ros2 control list_controllers` |
| `chmod +x <file>` | Makes a file executable (needed for Python nodes) | `chmod +x scripts/wave_node.py` |
| `grep <text> <file>` | Finds text in a file | `grep joint1 wave_node.py` |
| `history` | Shows the commands you typed | `history` |

------

## 🚀 The Most Important Ones

| Command | Why it matters |
|---|---|
| `cd`, `ls` | Find your way around |
| `colcon build --packages-select ...` | Turn your code into something ROS 2 can run |
| `source install/setup.bash` | Make the terminal see what you built |
| `ros2 run ...` | Run your programs |
| `ros2 topic list` / `echo` | See what the robot is saying |
| `Ctrl + C` | Stop whatever is running |

------

## 🚀 What's Next?

Next you will start the DOFBOT simulator and make the arm move.
