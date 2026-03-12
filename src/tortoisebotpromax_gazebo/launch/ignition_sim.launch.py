import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.descriptions import ParameterValue

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    gui = LaunchConfiguration('gui')

    desc_pkg = FindPackageShare('tortoisebotpromax_description').find(
        'tortoisebotpromax_description'
    )

    gazebo_pkg = FindPackageShare('tortoisebotpromax_gazebo').find(
        'tortoisebotpromax_gazebo'
    )

    world = os.path.join(gazebo_pkg, 'worlds', 'room2.sdf')
    xacro_file = os.path.join(desc_pkg, 'urdf', 'tortoisebotpromax_sim.xacro')

    robot_description = ParameterValue(
        Command(['xacro', ' ', xacro_file]),
        value_type=str
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'gui',
            default_value='true'
        ),

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'robot_description': robot_description,
            }]
        ),

        # Start Ignition Gazebo
        ExecuteProcess(
            cmd=['ign', 'gazebo', '-r', world],
            condition=IfCondition(gui),
            output='screen'
        ),

        ExecuteProcess(
            cmd=['ign', 'gazebo', '-r', '-s', world],
            condition=UnlessCondition(gui),
            output='screen'
        ),

        # Spawn robot after Gazebo is ready
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package='ros_gz_sim',
                    executable='create',
                    arguments=[
                        '-name', 'tortoisebotpromax',
                        '-topic', 'robot_description',
                    ],
                    output='screen'
                )
            ]
        ),

        # Main ROS <-> Ignition bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge',
            arguments=[
                # Drive
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                # Odometry
                '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                # Clock
                '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',
                # TF — odom -> base_link from DiffDrive plugin
                '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
                # LiDAR
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                # IMU
                '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
                # Camera color image
                '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
                # Camera depth image
                '/camera/depth/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
                # Camera color info
                '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
                # Camera point cloud
                '/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            ],
            parameters=[{'use_sim_time': True}],
            output='screen'
        ),

        # Joint state bridge
        # Works now because JointStatePublisher system plugin is loaded
        # in tortoisebotpromax.gazebo — bridges wheel joint positions
        # into /joint_states so robot_state_publisher animates the wheels
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='joint_state_bridge',
            arguments=[
                '/world/default/model/tortoisebotpromax/joint_state'
                '[gz.msgs.Model',
            ],
            remappings=[
                (
                    '/world/default/model/tortoisebotpromax/joint_state',
                    '/joint_states',
                ),
            ],
            parameters=[{'use_sim_time': True}],
            output='screen'
        ),

    ])
