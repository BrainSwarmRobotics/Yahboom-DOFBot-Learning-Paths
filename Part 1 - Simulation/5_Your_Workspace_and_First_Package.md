# 📦 Your Workspace and Your First Package

📍 **Level:** Beginner
📚 **Topic:** Workspaces, packages, building with colcon, and running your own program with `ros2 run`

------

## 🧠 Goal

You will:

- Understand what a **workspace** and a **package** are
- Create your own package, `my_dofbot`, where all your programs for this path will live
- Write a tiny ROS 2 program and run it the ROS 2 way, with `ros2 run`

You don't need the simulator for this module, but it does no harm to leave it running.

------

## 📁 1. The Workspace

A **workspace** is a folder that holds your ROS 2 code. Yours already exists: `~/dofbot_ws`.

```
cd ~/dofbot_ws
ls
```

```
build  install  log  src
```

| Folder | What is in it | Do you edit it? |
|---|---|---|
| `src` | The **source code**: your packages. This is what the file explorer shows | ✅ Yes, all your work goes here |
| `build` | Temporary files made while building | ❌ No |
| `install` | The **finished result** that ROS 2 actually runs | ❌ No |
| `log` | A record of every build; look here when one fails | ❌ No |

`build`, `install` and `log` were created when you built `dofbot_lab` in module 2. You can delete them at any time; the next build makes them again.

------

## 📦 2. What Is a Package?

A **package** is a folder of code with a name, a list of what it needs, and instructions for building it. It is the unit ROS 2 understands: you build packages and you run programs **from** packages.

```
dofbot_ws/
└── src/
    ├── dofbot_lab/              <- a package
    ├── exercise_1_publisher/    <- another package
    └── my_dofbot/               <- yours, created now
```

------

## 🏗️ 3. Create Your Package

Packages are created inside `src`:

```
cd ~/dofbot_ws/src
ros2 pkg create --build-type ament_cmake my_dofbot
```

```
going to create a new package
package name: my_dofbot
destination directory: /home/user/dofbot_ws/src
package format: 3
version: 0.0.0
...
creating folder ./my_dofbot
creating ./my_dofbot/package.xml
creating source and include folder
creating folder ./my_dofbot/src
creating folder ./my_dofbot/include/my_dofbot
creating ./my_dofbot/CMakeLists.txt
```

`--build-type ament_cmake` creates a package built with CMake. It can hold Python programs (this path), C++ programs (module 11) and your own message types (module 8), all in one package.

Your package now appears in the file explorer:

```
my_dofbot/
├── CMakeLists.txt
├── include/my_dofbot/
├── package.xml
└── src/
```

| File | What it controls |
|---|---|
| `package.xml` | The package's name, version, maintainer, and which other packages it needs |
| `CMakeLists.txt` | How the package is built, and **what gets installed** so that `ros2 run` can find it |
| `src/`, `include/` | For C++ code (module 11) |

------

## ✍️ 4. Write a Tiny Program

Python programs go in a `scripts` folder:

```
mkdir -p ~/dofbot_ws/src/my_dofbot/scripts
```

In the file explorer, right-click `my_dofbot/scripts`, choose **New File**, name it `hello_dofbot.py`, and paste:

```
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node


def main():
    rclpy.init()                         # start ROS 2 for this program
    node = Node('hello_dofbot')          # create a node with a name
    node.get_logger().info('Hello, DOFBOT!')
    node.destroy_node()
    rclpy.shutdown()                     # stop ROS 2 for this program


if __name__ == '__main__':
    main()
```

The first line (`#!/usr/bin/env python3`) tells Linux to run this file with Python. Save with `Ctrl + S` if auto-save is off.

Make it executable, and run it the ordinary way:

```
cd ~/dofbot_ws/src/my_dofbot
chmod +x scripts/hello_dofbot.py
python3 scripts/hello_dofbot.py
```

```
[INFO] [1712345678.123456789] [hello_dofbot]: Hello, DOFBOT!
```

It works, but only because you pointed `python3` straight at the file. ROS 2 itself doesn't know about it yet.

------

## ⚙️ 5. Make It Run with `ros2 run`

`ros2 run my_dofbot hello_dofbot.py` only finds programs that were **installed** into the workspace's `install` folder. You tell CMake to install your script by adding this block to `CMakeLists.txt`, **above** the last line, `ament_package()`:

```
install(PROGRAMS
  scripts/hello_dofbot.py
  DESTINATION lib/${PROJECT_NAME}
)
```

Your `CMakeLists.txt` now ends like this:

```
install(PROGRAMS
  scripts/hello_dofbot.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
```

Then **build**, **source** and **run**:

```
cd ~/dofbot_ws
colcon build --packages-select my_dofbot
source install/setup.bash
ros2 run my_dofbot hello_dofbot.py
```

```
Starting >>> my_dofbot
Finished <<< my_dofbot [1.2s]

Summary: 1 package finished [1.5s]
[INFO] [1712345690.987654321] [hello_dofbot]: Hello, DOFBOT!
```

🎉 You built your first package and ran your first ROS 2 program.

------

## 🧠 6. Build, Source, Run

| Step | Command | What it does |
|---|---|---|
| **Build** | `colcon build --packages-select my_dofbot` | Copies and compiles your package into `install/` |
| **Source** | `source install/setup.bash` | Tells **this terminal** what is in `install/` |
| **Run** | `ros2 run my_dofbot hello_dofbot.py` | Starts the installed program |

You repeat these three every time you change your code:

```
Edit -> Save -> Build -> Source -> Run
```

### Why `--packages-select`?

`colcon build` on its own builds **every** package in `src`. That takes longer, and the `Practical_Session_2` starter package is designed **not** to build until you fill in its exercise. Always build the package you are working on by name:

```
colcon build --packages-select my_dofbot
```

### Why source?

Each terminal has its own environment. New terminals load your workspace automatically (you set that up in module 2), but a terminal that was **already open** during a build doesn't see what was just built until you run `source install/setup.bash` in it.

------

## ⚠️ Common Mistakes

| Problem | Cause and fix |
|---|---|
| `Package 'my_dofbot' not found` | You haven't sourced since building: `source install/setup.bash` |
| `No executable found` | The script isn't in the `install(PROGRAMS ...)` block, or you didn't rebuild after adding it |
| The program runs with `python3` but not with `ros2 run`: `Permission denied` | You forgot `chmod +x` on the script |
| Changes to your code have no effect | You didn't rebuild, or rebuilt but didn't source |
| `colcon build` run inside `src` | Always build from the workspace folder, `~/dofbot_ws`. If `build`, `install` and `log` folders appeared inside `src`, delete them |
| You edited a file in `install/` or `build/` | Those are copies and get overwritten. Edit only in `src/` |

------

## 🎯 What You Learned

- A **workspace** (`~/dofbot_ws`) holds **packages** in `src`
- `ros2 pkg create --build-type ament_cmake` creates a package
- Python programs need `#!/usr/bin/env python3`, `chmod +x` and an `install(PROGRAMS ...)` entry
- The cycle is **build → source → run**

------

## 🚀 What's Next?

`hello_dofbot` says hello and exits. In the next module, your node keeps running and makes the arm **wave**.
