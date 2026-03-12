include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,

  -- The frame the map is published in
  map_frame = "map",

  -- The frame Cartographer tracks internally for pose estimation.
  -- Use base_link (not odom) because we provide odometry separately below.
  tracking_frame = "base_link",

  -- The frame Cartographer publishes its pose in.
  -- base_link means it publishes map->base_link and lets odom->base_link
  -- come from the diff drive plugin via ros_gz_bridge.
  published_frame = "base_link",

  -- Odometry frame — must match what the diff drive plugin uses
  odom_frame = "odom",

  -- True = Cartographer generates the odom frame itself (pure lidar odometry).
  -- False = Cartographer uses the odom->base_link TF from the diff drive plugin.
  -- We set False because our diff drive plugin already publishes good odometry.
  -- This gives better results since wheel odometry constrains the SLAM solution.
  provide_odom_frame = false,

  -- Project 3D pose to 2D — required for a ground robot
  publish_frame_projected_to_2d = true,

  -- Use the /odom topic from the diff drive plugin as an odometry input.
  -- Significantly improves scan matching quality and map consistency.
  use_odometry = true,

  use_nav_sat = false,
  use_landmarks = false,

  -- One 2D laser scanner
  num_laser_scans = 1,
  num_multi_echo_laser_scans = 0,
  num_subdivisions_per_laser_scan = 1,
  num_point_clouds = 0,

  -- Timeouts — increase slightly for simulation where TF can be delayed
  lookup_transform_timeout_sec = 0.5,
  submap_publish_period_sec = 0.3,
  pose_publish_period_sec = 5e-3,
  trajectory_publish_period_sec = 30e-3,

  -- Sampling ratios — 1.0 means use every message
  rangefinder_sampling_ratio = 1.,
  odometry_sampling_ratio = 1.,
  fixed_frame_pose_sampling_ratio = 1.,
  imu_sampling_ratio = 1.,
  landmarks_sampling_ratio = 1.,
}

-- 2D SLAM only
MAP_BUILDER.use_trajectory_builder_2d = true

-- Range filter — match lidar sensor config in tortoisebotpromax.gazebo
-- min_range should be >= lidar <range><min> (0.2m)
-- max_range should be <= lidar <range><max> (20m) but 12m is practical indoors
TRAJECTORY_BUILDER_2D.min_range = 0.2
TRAJECTORY_BUILDER_2D.max_range = 12.0

-- Length assigned to rays that return no hit (just beyond max_range)
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 12.5

-- We have working wheel odometry so no need for IMU data
TRAJECTORY_BUILDER_2D.use_imu_data = false

-- Online correlative scan matching — tries to correct scan alignment
-- in real time before submitting to the pose graph.
-- Helps significantly when running in simulation with low-noise lidar.
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = true

-- How far to search for a better scan match (metres)
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.linear_search_window = 0.1

-- Cost weights — higher translation weight keeps position stable,
-- lower rotation weight allows heading to correct itself
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.translation_delta_cost_weight = 10.
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.rotation_delta_cost_weight = 1e-1

-- Only add a new scan to the submap if robot has rotated at least 0.2 degrees.
-- Prevents adding too many nearly-identical scans when robot is stationary.
TRAJECTORY_BUILDER_2D.motion_filter.max_angle_radians = math.rad(0.2)

-- Number of range data accumulated before inserting into submap.
-- 1 = insert every scan. Good for 10Hz lidar.
TRAJECTORY_BUILDER_2D.num_accumulated_range_data = 1

-- Pose graph optimization — how confident a loop closure match must be
-- before it is accepted. 0.65 is standard for a clean indoor environment.
POSE_GRAPH.constraint_builder.min_score = 0.65
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.65

-- Huber loss scale — controls outlier rejection in optimization.
-- Higher value = more tolerant of outliers.
POSE_GRAPH.optimization_problem.huber_scale = 1e2

-- Run global optimization every N nodes added to the pose graph.
-- 35 is a good balance between map quality and CPU usage.
POSE_GRAPH.optimize_every_n_nodes = 35

return options
