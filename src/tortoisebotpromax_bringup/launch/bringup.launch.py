import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    gui = LaunchConfiguration('gui')

    description_pkg = get_package_share_directory('tortoisebotpromax_description')
    gazebo_pkg      = get_package_share_directory('tortoisebotpromax_gazebo')

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, 'launch', 'ignition_sim.launch.py')
        ),
        launch_arguments={'gui': gui}.items()
    )

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(description_pkg, 'launch', 'rviz.launch.py')
        ),
        launch_arguments={
            'rvizconfig': os.path.join(
                description_pkg, 'rviz', 'simulation.rviz'
            )
        }.items()
    )

    return LaunchDescription([

        # Force software rendering — reduces GPU pressure on VM
        SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'),

        DeclareLaunchArgument(
            'gui',
            default_value='true',
            description='Run Gazebo with GUI'
        ),

        simulation,
        rviz,
    ])
