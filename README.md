# Yahboom DofBot — Learning Paths

Content repo for the Yahboom DofBot (6-DOF arm).

`dofbot_ws/src` is the ROS 2 workspace seeded into each user's
`workspaces/<id>/dofbot_ws/src` and mounted at `/home/user/dofbot_ws/src`.
It is intentionally empty for now — the directory's existence is what makes
`_find_workspace_dir_name()` resolve this robot to `dofbot_ws` instead of the
default `mentorpi_ws`. Drop packages in here as they are written.
