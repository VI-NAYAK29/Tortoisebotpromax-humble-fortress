import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    slam_pkg = get_package_share_directory('tortoisebotpromax_slam')
    desc_pkg  = get_package_share_directory('tortoisebotpromax_description')

    slam_params  = os.path.join(slam_pkg, 'config', 'slam_toolbox_params.yaml')
    rviz_config  = os.path.join(desc_pkg, 'rviz', 'simulation.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock — must be true when running in Gazebo'
        ),

        # ── SLAM Toolbox async node ───────────────────────────────────────
        # async = processes scans asynchronously so it never blocks the
        # ROS2 executor. Better for simulation where scan timing can be
        # irregular. Subscribes to /scan, publishes /map and map->odom TF.
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            parameters=[
                slam_params,
                # Override use_sim_time from launch argument so it can be
                # set at launch time rather than hardcoded in the yaml
                {'use_sim_time': use_sim_time},
            ],
            remappings=[
                ('scan', '/scan'),
            ],
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
