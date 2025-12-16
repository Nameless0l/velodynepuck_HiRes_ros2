#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    calibration_file = os.path.join(
        get_package_share_directory('velodyne_pointcloud'),
        'params', 'VLP16_hires_db.yaml'
    )

    device_ip_arg = DeclareLaunchArgument('device_ip', default_value='192.168.1.201')
    frame_id_arg = DeclareLaunchArgument('frame_id', default_value='velodyne')
    model_arg = DeclareLaunchArgument('model', default_value='VLP16')
    rpm_arg = DeclareLaunchArgument('rpm', default_value='600.0')
    pcap_arg = DeclareLaunchArgument('pcap', default_value='')
    port_arg = DeclareLaunchArgument('port', default_value='2368')

    velodyne_driver_node = Node(
        package='velodyne_driver',
        executable='velodyne_driver_node',
        name='velodyne_driver',
        output='screen',
        parameters=[{
            'device_ip': LaunchConfiguration('device_ip'),
            'frame_id': LaunchConfiguration('frame_id'),
            'model': LaunchConfiguration('model'),
            'rpm': LaunchConfiguration('rpm'),
            'pcap': LaunchConfiguration('pcap'),
            'port': LaunchConfiguration('port'),
        }]
    )

    velodyne_transform_node = Node(
        package='velodyne_pointcloud',
        executable='velodyne_transform_node',
        name='velodyne_transform',
        output='screen',
        parameters=[{
            'model': LaunchConfiguration('model'),
            'calibration': calibration_file,
            'min_range': 0.4,
            'max_range': 130.0,
            'view_direction': 0.0,
            'view_width': 6.283185307179586,
        }]
    )

    velodyne_laserscan_node = Node(
        package='velodyne_laserscan',
        executable='velodyne_laserscan_node',
        name='velodyne_laserscan',
        output='screen',
        parameters=[{
            'ring': 8,
            'resolution': 0.007,
        }],
        remappings=[('velodyne_points', 'velodyne_points')]
    )

    return LaunchDescription([
        device_ip_arg,
        frame_id_arg,
        model_arg,
        rpm_arg,
        pcap_arg,
        port_arg,
        velodyne_driver_node,
        velodyne_transform_node,
        velodyne_laserscan_node,
    ])
