# 📷 The Real Camera

📍 **Level:** Intermediate
📚 **Topic:** Image topics over the internet, compressed images, and tuning colour detection for real light

------

## 🧠 What Is Different

| | Simulator | Real DOFBOT |
|---|---|---|
| Topic | `/camera/image_raw` | `/usb_cam/image_raw` |
| Compressed copy | - | `/usb_cam/image_raw/compressed` (JPEG) |
| Pictures per second | ~10 | 30 |
| Light | Perfect, always the same | Lamps, daylight, shadows, reflections |
| Colours | Exactly the model's colours | Shifted by the light and the camera |

------

## 📶 Step 1: Why Compressed?

With your terminal on `(ROBOT)`, measure how much data each topic needs (`Ctrl + C` to stop):

```
ros2 topic bw /usb_cam/image_raw
```

```
Message size mean: 0.92 MB
```

```
ros2 topic bw /usb_cam/image_raw/compressed
```

```
Message size mean: 0.07 MB
```

A raw picture is almost **1 MB**; 30 of them a second is about **27 MB/s**, more than an internet connection carries comfortably. The compressed copy is about **13 times smaller**.

On the robot itself (where the camera node runs) raw pictures cost nothing. Across the internet, to your console, **always use `/usb_cam/image_raw/compressed`**. The tools and nodes in this course accept both: a topic ending in `/compressed` is decoded as JPEG.

------

## 📸 Step 2: Look Through the Real Camera

Point the camera at the stack with the `look` pose (the named-pose service from module 4, or `dofbot_cmd -t 3 servos 90 135 15 0 90`), then:

```
ros2 run dofbot_lab snapshot.py /usb_cam/image_raw/compressed
```

```
[INFO] [snapshot]: Saved /home/user/dofbot_ws/src/snapshots/usb_cam.png
```

Open `snapshots/usb_cam.png`. Compare it with the simulator's `camera.png` from the same pose: the blocks are in roughly the same place, but the colours, shadows and background are different.

------

## 🎨 Step 3: Run Your Colour Detector

The detector from Part 1, module 12, with one parameter changed:

```
ros2 run my_dofbot color_detector.py --ros-args -p image_topic:=/usb_cam/image_raw/compressed
```

```
[INFO] [color_detector]: Looking for blocks on /usb_cam/image_raw/compressed
[INFO] [color_detector]: Blocks in the middle, top to bottom: ['yellow', 'red', 'green', 'blue']
```

Open `snapshots/detections.png` (it updates every 2 seconds) to see what it found.

If the colours and their order match what you see, you're done. If not, read on.

------

## 🔧 Step 4: Tune the Colours

Typical problems under real light:

| You see | Likely cause |
|---|---|
| A block is missing | Its colour is outside your range: darker (V too low), or paler (S too low) |
| Yellow found as red, or the other way round | Warm lamps shift hues |
| Extra "blocks" | Something else in the picture has a similar colour (a cable, the mat's squares, a reflection) |
| A block found twice | A highlight splits it in two |

Measure the real colours instead of guessing. `hsv_probe.py` reads the HSV values inside a box of your snapshot. Find a box on one block in `usb_cam.png` (x, y = top-left corner in pixels; the picture is 640 × 480), then:

```
ros2 run dofbot_lab hsv_probe.py usb_cam.png 290 90 40 40
```

```
Box x=290 y=90 w=40 h=40 in /home/user/dofbot_ws/src/snapshots/usb_cam.png (640x480)
  H (hue)        typical    26   (10%..90%: 26..27)
  S (saturation) typical   169   (10%..90%: 165..169)
  V (value)      typical   154   (10%..90%: 154..219)
  Suggested range: ((21, 135, 124), (32, 255, 255))
Saved /home/user/dofbot_ws/src/snapshots/hsv_probe.png with the box drawn
```

(The numbers shown are from the simulator's yellow block; yours will differ.) Open `hsv_probe.png` to check the box is really on the block. Then put the suggested range into `COLOR_RANGES` in your `color_detector.py`, for that colour. Repeat for each colour, rebuild, and run the detector again.

`You can tune offline: a snapshot is just a file. Take snapshots of the real camera during your slot, and tune the ranges in your preview session afterwards.`

### Light-proof habits

- Keep **S** (saturation) minimums high enough to ignore the white mat and grey shadows, but low enough for the shaded sides of the blocks
- Keep **V** (value) minimums low: shadows mostly lower V
- Red needs both ends of the hue range (around 0 **and** around 180)
- Test with the arm in the **exact** pose you will use: the picture changes with the angle

------

## 🧪 Try It Yourself

### 🟢 Easy

- Measure the frame rate across the internet: `ros2 topic hz /usb_cam/image_raw/compressed`. Is it 30?

### 🟡 Medium

- Measure each colour with `hsv_probe.py` and compare with the simulator's ranges. Which colour moved the most?

### 🔴 Challenge

- Make the detector robust to small light changes: instead of fixed S and V minimums, scale them from the picture's average brightness.

------

## 🎯 What You Learned

- Raw images are too big for the internet: use `/compressed`
- `snapshot.py` and `color_detector.py` take the topic as an argument / parameter: no code changes between simulator and robot
- Real light changes colours; measure them with `hsv_probe.py` and tune `COLOR_RANGES`

------

## 🚀 What's Next?

The capstone, for real: read the real stack and sort the real blocks.
