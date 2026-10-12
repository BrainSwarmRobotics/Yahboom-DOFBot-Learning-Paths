# A pose for the DOFBOT arm, in degrees. 0 on every joint = the arm straight up.
float64 base       # joint1: + turns left, - turns right       (-90 .. 90)
float64 shoulder   # joint2: - leans forward (towards the mat)  (-90 .. 90)
float64 elbow      # joint3: - bends forward                    (-90 .. 90)
float64 wrist      # joint4: - bends forward                    (-90 .. 90)
float64 roll       # joint5: turns the gripper                  (-90 .. 180)
float64 seconds    # how long the move should take
