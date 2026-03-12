import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    slam_pkg = get_package_share_directory('tortoisebotpromax_slam')
    desc_pkg  = get_package_share_directory('tortoisebotpromax_description')

    config_dir       = os.path.join(slam_pkg, 'config')
    lua_basename     = 'lidar.lua'
    rviz_config      = os.path.join(desc_pkg, 'rviz', 'simulation.rviz')

    use_sim_time     = LaunchConfiguration('use_sim_time')
    resolution       = LaunchConfiguration('resolution')
    publish_period   = LaunchConfiguration('publish_period_sec')

    return LaunchDescription([

        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock — must be true when running in Gazebo'
        ),

        DeclareLaunchArgument(
            'resolution',
            default_value='0.05',
            description='Occupancy grid resolution in metres per cell'
        ),

        DeclareLaunchArgument(
            'publish_period_sec',
            default_value='1.0',
            description='How often the occupancy grid map is published (seconds)'
        ),

        # ── Cartographer SLAM node ────────────────────────────────────────
        # Subscribes to /scan and /odom, publishes map->odom TF and /map
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            arguments=[
                '-configuration_directory', config_dir,
                '-configuration_basename', lua_basename,
            ],
            parameters=[{'use_sim_time': use_sim_time}],
            remappings=[
                # Bridge publishes on /scan — Cartographer reads this
                ('scan', '/scan'),
                # Bridge publishes on /odom — Cartographer uses this
                # when use_odometry=true in lidar.lua
                ('odom', '/odom'),
            ],
            output='screen'
        ),

        # ── Occupancy grid publisher ──────────────────────────────────────
        # Converts Cartographer's internal submap representation into a
        # standard nav_msgs/OccupancyGrid on /map for RViz and Nav2
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            arguments=[
                '-resolution', resolution,
                '-publish_period_sec', publish_period,
            ],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        ),

        # ── RViz ─────────────────────────────────────────────────────────
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        ),

    ])
