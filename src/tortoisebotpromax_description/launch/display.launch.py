import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_share = FindPackageShare(
        'tortoisebotpromax_description'
    ).find('tortoisebotpromax_description')

    model_path = os.path.join(pkg_share, 'urdf', 'tortoisebotpromax_sim.xacro')

    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('model')]),
        value_type=str
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),

        DeclareLaunchArgument(
            'model',
            default_value=model_path
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'robot_description': robot_description}
            ],
            output='screen'
        )
    ])
