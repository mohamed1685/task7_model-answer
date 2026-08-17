from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='individual_task_pkg',
            executable='turtle_control',
            arguments=[],
            output='screen',
            parameters=[
                {'velocity_topic': '/turtle1/cmd_vel',
                'dominant_colour_topic': '/dominant_color',
                'colour_topic': '/turtle1/color_sensor'}
            ]
        ),
         Node(
            package='turtlesim',
            executable='turtlesim_node',
            arguments=[],
            output='screen'
        )
    ])