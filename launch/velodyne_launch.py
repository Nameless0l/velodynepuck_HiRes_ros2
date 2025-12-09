#!/usr/bin/env python3
"""
Launch file for Velodyne VLP-16 LiDAR driver
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """
    Generate launch description for Velodyne VLP-16 LiDAR
    """
    
    # Declare launch arguments
    device_ip_arg = DeclareLaunchArgument(
        'device_ip',
        default_value='192.168.1.201',
        description='IP address of the Velodyne device'
    )
    
    frame_id_arg = DeclareLaunchArgument(
        'frame_id',
        default_value='velodyne',
        description='Frame ID for the point cloud'
    )
    
    model_arg = DeclareLaunchArgument(
        'model',
        default_value='VLP16HiRes',
        description='Velodyne model (VLP16, VLP16HiRes, VLP32C, HDL32E, HDL64E)'
    )
    
    rpm_arg = DeclareLaunchArgument(
        'rpm',
        default_value='600.0',
        description='Motor RPM'
    )
    
    pcap_arg = DeclareLaunchArgument(
        'pcap',
        default_value='',
        description='Path to PCAP file (leave empty for live data)'
    )
    
    port_arg = DeclareLaunchArgument(
        'port',
        default_value='2368',
        description='UDP port for Velodyne packets'
    )
    
    # Velodyne driver node
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
    
    # Velodyne transform node (converts packets to point cloud)
    velodyne_transform_node = Node(
        package='velodyne_pointcloud',
        executable='velodyne_transform_node',
        name='velodyne_transform',
        output='screen',
        parameters=[{
            'model': LaunchConfiguration('model'),
            'calibration': '',
            'min_range': 0.9,
            'max_range': 130.0,
            'view_direction': 0.0,
            'view_width': 6.283185307179586,  # 2*pi
        }]
    )
    
    # Velodyne laserscan node (converts point cloud to 2D laser scan)
    velodyne_laserscan_node = Node(
        package='velodyne_laserscan',
        executable='velodyne_laserscan_node',
        name='velodyne_laserscan',
        output='screen',
        parameters=[{
            'ring': 10,
            'resolution': 0.007,
        }],
        remappings=[
            ('velodyne_points', 'velodyne_points'),
        ]
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
