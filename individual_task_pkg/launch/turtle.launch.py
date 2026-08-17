from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Launch arguments for individual_task_pkg parameters
    velocity_stamped_arg = DeclareLaunchArgument(
        'use_stamped_vel',
        default_value='False',
        description='Whether to use TwistStamped for velocity commands'
    )
    velocity_topic_arg = DeclareLaunchArgument(
        'velocity_topic',
        default_value='/turtle1/cmd_vel',
        description='Topic for turtle velocity commands'
    )
    dominant_colour_topic_arg = DeclareLaunchArgument(
        'dominant_colour_topic',
        default_value='/dominant_color',
        description='Topic for dominant color data'
    )
    colour_topic_arg = DeclareLaunchArgument(
        'colour_topic',
        default_value='/turtle1/color_sensor',
        description='Topic for turtle color sensor'
    )

    # Launch arguments for turtlesim_node parameters
    background_r_arg = DeclareLaunchArgument(
        'background_r',
        default_value='69',
        description='Red component of turtlesim background color (0-255)'
    )
    background_g_arg = DeclareLaunchArgument(
        'background_g',
        default_value='86',
        description='Green component of turtlesim background color (0-255)'
    )
    background_b_arg = DeclareLaunchArgument(
        'background_b',
        default_value='255',
        description='Blue component of turtlesim background color (0-255)'
    )

    return LaunchDescription([
        # Declare all launch arguments
        velocity_topic_arg,
        dominant_colour_topic_arg,
        colour_topic_arg,
        background_r_arg,
        background_g_arg,
        background_b_arg,
        velocity_stamped_arg,

        # Nodes
        Node(
            package='individual_task_pkg',
            executable='turtle_control',
            output='screen',
            parameters=[{
                'velocity_topic': LaunchConfiguration('velocity_topic'),
                'dominant_colour_topic': LaunchConfiguration('dominant_colour_topic'),
                'colour_topic': LaunchConfiguration('colour_topic'),
                'use_stamped_vel': LaunchConfiguration('use_stamped_vel'),
            }]
        ),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen',
            parameters=[{
                'background_r': LaunchConfiguration('background_r'),
                'background_g': LaunchConfiguration('background_g'),
                'background_b': LaunchConfiguration('background_b'),
            }]
        )
    ])