import os

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    gui       = LaunchConfiguration('gui')
    slam      = LaunchConfiguration('slam')
    slam_tool = LaunchConfiguration('slam_toolbox')

    description_pkg = get_package_share_directory('tortoisebotpromax_description')
    gazebo_pkg      = get_package_share_directory('tortoisebotpromax_gazebo')
    slam_pkg        = get_package_share_directory('tortoisebotpromax_slam')

    # Gazebo + all bridges + RSP
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, 'launch', 'ignition_sim.launch.py')
        ),
        launch_arguments={'gui': gui}.items()
    )

    # RViz — only when SLAM is OFF
    # When SLAM is ON the slam launch files open their own RViz
    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(description_pkg, 'launch', 'rviz.launch.py')
        ),
        launch_arguments={
            'rvizconfig': os.path.join(
                description_pkg, 'rviz', 'simulation.rviz'
            )
        }.items(),
        condition=UnlessCondition(slam)
    )

    # Cartographer — slam:=true  AND  slam_toolbox:=false
    cartographer = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_pkg, 'launch', 'cartographer.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items(),
        condition=IfCondition(
            PythonExpression([
                "'", slam, "' == 'true' and '", slam_tool, "' == 'false'"
            ])
        )
    )

    # SLAM Toolbox — slam:=true  AND  slam_toolbox:=true
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_pkg, 'launch', 'slam_toolbox.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items(),
        condition=IfCondition(
            PythonExpression([
                "'", slam, "' == 'true' and '", slam_tool, "' == 'true'"
            ])
        )
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'gui',
            default_value='true',
            description='Run Gazebo with GUI'
        ),

        DeclareLaunchArgument(
            'slam',
            default_value='false',
            description='Enable SLAM — true to start mapping'
        ),

        DeclareLaunchArgument(
            'slam_toolbox',
            default_value='false',
            description='false = Cartographer (default)  |  true = SLAM Toolbox'
        ),

        simulation,
        rviz,
        cartographer,
        slam_toolbox,
    ])
