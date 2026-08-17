from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='individual_task_pkg',
            executable='turtle_control',
            arguments=[],
            output='screen'
        ),
         Node(
            package='turtlesim',
            executable='turtlesim_node',
            arguments=[],
            output='screen'
        )
    ])