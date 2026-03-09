# TortoisebotProMax — ROS2 Humble + Ignition Fortress Simulation

![ROS2](https://img.shields.io/badge/ROS2-Humble-blue?style=for-the-badge&logo=ros)
![Gazebo](https://img.shields.io/badge/Gazebo-Ignition%20Fortress-orange?style=for-the-badge)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-purple?style=for-the-badge&logo=ubuntu)
![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)

This repository contains the simulation stack for **TortoisebotProMax** running on **ROS2 Humble** with **Ignition Gazebo Fortress**. It includes full differential drive simulation, LiDAR, depth camera, and RViz visualization — launchable from a single command.

---

## Table of Contents

- [1. Package Overview](#1-package-overview)
- [2. Prerequisites](#2-prerequisites)
- [3. Installation](#3-installation)
- [4. Running the Simulation](#4-running-the-simulation)
- [5. Controlling the Robot](#5-controlling-the-robot)
- [6. TF Tree](#6-tf-tree)
- [7. ROS2 Topics](#7-ros2-topics)
- [8. Package Structure](#8-package-structure)
- [9. Simulation Architecture — How It Works](#9-simulation-architecture--how-it-works)
- [10. Bug Fixes Applied](#10-bug-fixes-applied)
- [11. Robot Parameters](#11-robot-parameters)
- [12. VM / Low-End Hardware Tips](#12-vm--low-end-hardware-tips)

---

## 1. Package Overview

| Package | Description |
|---|---|
| `tortoisebotpromax_description` | URDF/Xacro robot model, meshes, RViz configs |
| `tortoisebotpromax_gazebo` | Ignition Gazebo world, spawn, and ROS bridges |
| `tortoisebotpromax_bringup` | Top-level launch files — single entry point |
| `tortoisebotpromax_slam` | Cartographer and SLAM Toolbox configs |
| `tortoisebotpromax_navigation` | Nav2 navigation stack configs and maps |
| `tortoisebotpromax_firmware` | Real robot firmware, sensors, MicroROS (not used in sim) |

---

## 2. Prerequisites

- **OS:** Ubuntu 22.04
- **ROS2:** Humble Hawksbill
- **Gazebo:** Ignition Fortress

Install ROS2 Humble: https://docs.ros.org/en/humble/Installation.html

Install Ignition Fortress:
```bash
sudo apt-get install ignition-fortress
```

Install ROS-Gazebo bridge packages:
```bash
sudo apt install ros-humble-ros-gz-bridge \
                 ros-humble-ros-gz-sim \
                 ros-humble-robot-state-publisher \
                 ros-humble-joint-state-publisher \
                 ros-humble-xacro \
                 ros-humble-rviz2
```

---

## 3. Installation

Clone the repository into your ROS2 workspace:

```bash
cd ~/tortoisebot_ws/
git clone https://github.com/VI-NAYAK29/Tortoisebotpromax-humble-fortress.git
```

Install any remaining dependencies:

```bash
cd ~/tortoisebot_ws
rosdep install --from-paths src --ignore-src -r -y
```

Build the workspace:

```bash
cd ~/tortoisebot_ws
colcon build
source install/setup.bash
```

---

## 4. Running the Simulation

Everything launches from a single command:

```bash
ros2 launch tortoisebotpromax_bringup bringup.launch.py
```

This starts:
- Ignition Gazebo Fortress with the room world
- Robot spawned via `/robot_description`
- `robot_state_publisher` with `use_sim_time: True`
- All ROS ↔ Ignition bridges (`/cmd_vel`, `/odom`, `/scan`, `/clock`, `/tf`)
- RViz2 with `simulation.rviz` config (fixed frame: `odom`)

To run headless (no Gazebo GUI — lighter on resources):

```bash
ros2 launch tortoisebotpromax_bringup bringup.launch.py gui:=false
```

---

## 5. Controlling the Robot

Open a second terminal and run teleop:

```bash
source ~/tortoisebot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Or publish a velocity command directly:

```bash
# Move forward
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.2}, angular: {z: 0.0}}'

# Turn in place
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.0}, angular: {z: 0.5}}'

# Stop
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.0}, angular: {z: 0.0}}'
```

---

## 6. TF Tree

After launching, the full TF tree should look like this:

```
odom
└── base_link
    ├── left_wheel_1
    ├── right_wheel_1
    ├── front_castor_1
    ├── back_castor_1
    ├── imu_link
    ├── camera_link
    │   └── camera_depth_link
    └── lidar_base_1
        └── lidar_1
```

Verify with:

```bash
ros2 run tf2_tools view_frames
```

The generated `frames.pdf` will be saved in your current directory.

---

## 7. ROS2 Topics

| Topic | Type | Direction | Description |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | ROS → Gazebo | Velocity commands |
| `/odom` | `nav_msgs/Odometry` | Gazebo → ROS | Robot odometry |
| `/scan` | `sensor_msgs/LaserScan` | Gazebo → ROS | LiDAR scan data |
| `/tf` | `tf2_msgs/TFMessage` | Gazebo → ROS | `odom → base_link` transform |
| `/tf_static` | `tf2_msgs/TFMessage` | RSP → ROS | All static link transforms |
| `/clock` | `rosgraph_msgs/Clock` | Gazebo → ROS | Simulation time |
| `/robot_description` | `std_msgs/String` | RSP → ROS | URDF robot model |
| `/joint_states` | `sensor_msgs/JointState` | RSP → ROS | Wheel joint positions |

---

## 8. Package Structure

```
src/
├── tortoisebotpromax_bringup/
│   └── launch/
│       ├── bringup.launch.py          ← Single entry point for simulation
│       └── autobringup.launch.py      ← Full autonomous stack (real robot)
│
├── tortoisebotpromax_description/
│   ├── urdf/
│   │   ├── tortoisebotpromax_sim.xacro   ← Simulation robot model
│   │   ├── tortoisebotpromax.gazebo      ← Gazebo plugins (DiffDrive, LiDAR, Camera)
│   │   ├── tortoisebotpromax.xacro       ← Real robot model
│   │   └── materials.xacro
│   ├── meshes/                           ← .dae mesh files
│   ├── rviz/
│   │   ├── simulation.rviz               ← RViz config for simulation (fixed frame: odom)
│   │   └── navigation.rviz
│   └── launch/
│       ├── display.launch.py
│       ├── rviz.launch.py
│       └── state_publisher.launch.py
│
├── tortoisebotpromax_gazebo/
│   ├── launch/
│   │   └── ignition_sim.launch.py     ← Gazebo + bridges + RSP
│   └── worlds/
│       └── room2.sdf                  ← Simulation world
│
├── tortoisebotpromax_slam/
│   ├── config/
│   └── launch/
│       ├── cartographer.launch.py
│       └── slam_toolbox.launch.py
│
└── tortoisebotpromax_navigation/
    ├── config/
    │   └── nav2_params.yaml
    ├── maps/
    └── launch/
        ├── navigation.launch.py
        └── map_saver.launch.py
```

---

## 9. Simulation Architecture — How It Works

### How the TF chain is built

The simulation relies on two separate systems working together to produce the full TF tree:

**1. `robot_state_publisher` → static transforms**

Reads the URDF (`tortoisebotpromax_sim.xacro`) and publishes all fixed joint transforms immediately on `/tf_static`. This covers every link except the dynamic `odom → base_link`.

```
base_link → lidar_base_1 → lidar_1
base_link → camera_link  → camera_depth_link
base_link → imu_link
base_link → left_wheel_1
base_link → right_wheel_1
base_link → front_castor_1
base_link → back_castor_1
```

**2. DiffDrive plugin → dynamic `odom → base_link` transform**

The `libignition-gazebo-diff-drive-system.so` plugin inside Ignition Gazebo computes odometry from wheel joint velocities and publishes the `odom → base_link` transform on the Ignition topic `/tf`. The `ros_gz_bridge` bridges this into ROS2's `/tf` topic.

```
Ignition DiffDrive plugin
    └── publishes on /tf (gz.msgs.Pose_V)
            └── ros_gz_bridge converts to tf2_msgs/TFMessage
                    └── ROS2 TF system receives odom → base_link
```

### Bridge configuration

```
/cmd_vel    geometry_msgs/Twist      ←→   gz.msgs.Twist       (bidirectional)
/odom       nav_msgs/Odometry        ←    gz.msgs.Odometry     (Gazebo → ROS)
/scan       sensor_msgs/LaserScan    ←    gz.msgs.LaserScan    (Gazebo → ROS)
/clock      rosgraph_msgs/Clock      ←    gz.msgs.Clock        (Gazebo → ROS)
/tf         tf2_msgs/TFMessage       ←    gz.msgs.Pose_V       (Gazebo → ROS)
```

---

## 10. Bug Fixes Applied

This section documents the issues found in the original codebase and how they were resolved.

### Bug 1 — `odom → base_link` TF never reached ROS2

**Symptom:** `ros2 run tf2_tools view_frames` showed no connection between `odom` and `base_link`. RViz showed "No transform from base_link to odom".

**Root cause:** The original bridge was listening to the wrong Ignition topic:

```python
# WRONG — this is the world pose of the model, not odometry TF
'/model/tortoisebotpromax/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V'
```

The `/model/tortoisebotpromax/tf` topic carries the robot's absolute pose in the simulation world frame — it is not the same as the `odom → base_link` odometry transform. Even though the message type bridged without errors, the data inside it was meaningless to ROS2's TF system for this purpose.

The actual `odom → base_link` transform is published by the DiffDrive plugin on a separate Ignition topic named `/tf`.

**Fix — two parts:**

Part 1: Added `<tf_topic>/tf</tf_topic>` to the DiffDrive plugin in `tortoisebotpromax.gazebo` to explicitly set which Ignition topic it writes the TF to:

```xml
<plugin filename="libignition-gazebo-diff-drive-system.so"
        name="ignition::gazebo::systems::DiffDrive">
  ...
  <tf_topic>/tf</tf_topic>   <!-- added -->
  <publish_tf>true</publish_tf>
</plugin>
```

Part 2: Updated the bridge to listen to `/tf` instead:

```python
# CORRECT — the actual odom→base_link TF from the DiffDrive plugin
'/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V'
```

---

### Bug 2 — `robot_state_publisher` not launched in simulation

**Symptom:** Static TFs (`base_link → lidar`, `base_link → camera`, etc.) were intermittently missing or had TF timeout errors in RViz.

**Root cause:** `ignition_sim.launch.py` never started `robot_state_publisher`. The `bringup.launch.py` was including `display.launch.py` separately, but that file had incorrect path logic and was not passing `use_sim_time: True`, causing it to use wall clock time instead of the simulation clock. This caused TF expiry mismatches in RViz.

**Fix:** Moved `robot_state_publisher` directly into `ignition_sim.launch.py` with explicit parameters:

```python
Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    parameters=[{
        'use_sim_time': True,
        'robot_description': robot_description,
    }]
)
```

---

### Bug 3 — Lidar sensor used classic Gazebo `<ray>` format

**Symptom:** `/scan` topic received no data.

**Root cause:** The lidar sensor in `tortoisebotpromax.gazebo` used `<ray>` tags which is the format for classic Gazebo (ROS1). Ignition Fortress uses `<lidar>` tags. Also missing was an explicit `<topic>` tag so the bridge could find the scan data.

**Fix:**

```xml
<!-- BEFORE (classic Gazebo format — does not work in Ignition) -->
<ray>
  <scan>...</scan>
  <range>...</range>
</ray>

<!-- AFTER (Ignition Fortress format) -->
<lidar>
  <scan>...</scan>
  <range>...</range>
</lidar>
<topic>/scan</topic>
```

---

### Bug 4 — RViz fixed frame set to `map`

**Symptom:** RViz showed "Fixed Frame [map] does not exist" and refused to display the robot.

**Root cause:** `simulation.rviz` had `Fixed Frame: map`, which requires a running SLAM or localization node to publish a `map → odom` transform. For simulation-only mode with no SLAM, `odom` is the correct root frame.

**Fix:** Changed one line in `simulation.rviz`:

```yaml
# BEFORE
Fixed Frame: map

# AFTER
Fixed Frame: odom
```

Or via terminal:
```bash
sed -i 's/Fixed Frame: map/Fixed Frame: odom/' \
  ~/tortoisebot_ws/src/tortoisebotpromax_description/rviz/simulation.rviz
```

---

### Bug 5 — Wheel TFs (`left_wheel_1`, `right_wheel_1`) missing from TF tree

**Symptom:** RViz showed "No transform from left_wheel_1 to odom". The wheels stayed at their spawn position while the rest of the robot moved.

**Root cause:** `left_wheel_joint` and `right_wheel_joint` are `continuous` type joints in the URDF. `robot_state_publisher` only publishes TF for continuous joints when it receives `/joint_states` data containing those joint names. The joint state bridge from Ignition was not delivering data (confirmed by `ign topic -l | grep joint` returning nothing and `ros2 topic echo /joint_states` being empty). With no joint state data arriving, RSP never published the wheel TFs, so they disappeared from the tree.

**Fix:** Changed both wheel joints from `continuous` to `fixed` in `tortoisebotpromax_sim.xacro`. The DiffDrive plugin handles all wheel physics internally — it does not require the joints to be `continuous` in the URDF from a physics standpoint. Making them `fixed` means `robot_state_publisher` publishes their TFs immediately from the URDF without needing any `/joint_states` input, so the wheels are always present in the TF tree.

```xml
<!-- BEFORE -->
<joint name="right_wheel_joint" type="continuous">

<!-- AFTER -->
<joint name="right_wheel_joint" type="fixed">
```

> Note: The wheels will not visually spin in RViz since there is no joint state data, but the full robot model moves correctly as a rigid body following the `odom → base_link` transform.

---

## 11. Robot Parameters

| Parameter | Value |
|---|---|
| Wheel Type | Differential drive |
| Wheel Diameter | 0.12 m |
| Wheel Separation | 0.5 m (simulation) / 0.257 m (real) |
| Wheel Radius | 0.06 m |
| Robot Mass | 20.4 kg |
| LiDAR | YDLiDAR X4 Pro (simulated) — 720 samples, 360° |
| LiDAR Range | 0.2 m – 20 m |
| Camera | Intel RealSense D435i (simulated) — 640×480, 30 Hz |
| IMU | Onboard IMU link |
| Odometry Publish Rate | 50 Hz |

---

## 12. VM / Low-End Hardware Tips

If running inside a Virtual Machine or on hardware without a dedicated GPU, add the following to reduce rendering pressure:

**Option 1 — Set in terminal before launching (per session):**
```bash
export LIBGL_ALWAYS_SOFTWARE=1
ros2 launch tortoisebotpromax_bringup bringup.launch.py
```

**Option 2 — Add to `~/.bashrc` (permanent):**
```bash
echo 'export LIBGL_ALWAYS_SOFTWARE=1' >> ~/.bashrc
source ~/.bashrc
```

**Option 3 — Already built into `bringup.launch.py` via `SetEnvironmentVariable`** so it is applied automatically to all child processes without any manual steps.

Additional tips for VMs:
- Allocate at least 4 GB RAM and 4 CPU cores to the VM
- Enable 3D acceleration in VM display settings if available
- Run headless Gazebo (no GUI) to reduce load: `gui:=false`
- Lower the LiDAR sample count in `tortoisebotpromax.gazebo` from `720` to `360` if scan processing is slow

---

## Contributing

Pull requests are welcome. For major changes please open an issue first.

## License

Apache 2.0
