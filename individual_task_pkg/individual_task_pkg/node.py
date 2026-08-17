import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist
from geometry_msgs.msg import TwistStamped

from pynput import keyboard
from turtlesim.msg import Color
from rclpy.parameter_event_handler import ParameterEventHandler

class TurtleControl(Node):
    def __init__(self):
        super().__init__('turtle_control')

        self.w_is_pressed = False
        self.a_is_pressed = False
        self.d_is_pressed = False
        self.s_is_pressed = False

        self.get_logger().info('Turtle control node has been started.')
        self.declare_parameter('velocity_topic', '/turtle1/cmd_vel')
        self.declare_parameter('dominant_colour_topic', '/dominant_colour')
        self.declare_parameter('colour_topic', '/turtle1/color_sensor')


        self.declare_parameter('use_stamped_vel', False)
        self.handler = ParameterEventHandler(self)
        self.callback_handle = self.handler.add_parameter_callback(
            parameter_name="use_stamped_vel",
            node_name="turtle_control",
            callback=self.on_use_stamped_vel_changed,
        )

        self.start_cmd_vel_publisher()
        self.dominant_colour_publisher = self.create_publisher(String, self.get_parameter('dominant_colour_topic').value, 10)
        self.colour_subscriber = self.create_subscription(Color, self.get_parameter('colour_topic').value, self.colour_callback, 10)
        self.timer = self.create_timer(0.2, self.timer_callback)

        self.dominant_colour = None
        
        # Register both press and release handlers
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def colour_callback(self, msg):
        #self.get_logger().info(f'Color detected: {msg}')
        colour_list = [msg.r, msg.g, msg.b]
        max_val = max(colour_list)
        if colour_list.count(max_val) > 1:
            self.dominant_colour = None
        else:
            max_index = colour_list.index(max_val)
            if max_index == 0:
                self.dominant_colour = 'red'
            elif max_index == 1:
                self.dominant_colour = 'green'
            elif max_index == 2:
                self.dominant_colour = 'blue'
       # self.get_logger().info(f'Dominant color: {self.dominant_colour}')

    def publish_cmd_vel(self, linear_x, angular_z):
        if self.get_parameter('use_stamped_vel').value:
            twist_msg = TwistStamped()
            twist_msg.header.stamp = self.get_clock().now().to_msg()  
            twist_msg.twist.linear.x = linear_x
            twist_msg.twist.angular.z = angular_z
            self.cmd_vel_publisher.publish(twist_msg)
        else:
            twist_msg = Twist()
            twist_msg.linear.x = linear_x
            twist_msg.angular.z = angular_z
            self.cmd_vel_publisher.publish(twist_msg)

    def publish_dominant_colour(self):
        if self.dominant_colour is not None:
            colour_msg = String()
            colour_msg.data = self.dominant_colour
            self.dominant_colour_publisher.publish(colour_msg)
        else:
            self.get_logger().warn('No dominant color detected yet.')

    def timer_callback(self):
        linear = 0.0
        angular = 0.0
        if not self.listener.is_alive():
            self.get_logger().error('Keyboard listener is not alive. Stopping the robot.')
        else:
            self.get_logger().info(f'Key status: W={self.w_is_pressed}, A={self.a_is_pressed}, D={self.d_is_pressed}, S={self.s_is_pressed}')

        if self.w_is_pressed:
            linear += 1.0
        if self.s_is_pressed:
            linear -= 1.0
        if self.a_is_pressed:
            angular += 1.0
        if self.d_is_pressed:
            angular -= 1.0

        self.publish_cmd_vel(linear, angular)
        self.publish_dominant_colour()

    def on_press(self, key):
        try:
            if key.char == 'w':
                self.w_is_pressed = True
            elif key.char == 'a':
                self.a_is_pressed = True
            elif key.char == 'd':
                self.d_is_pressed = True
            elif key.char == 's':
                self.s_is_pressed = True
        except AttributeError:
            pass  # Ignore special non-character keys safely

    def on_release(self, key):
        try:
            if key.char == 'w':
                self.w_is_pressed = False
            elif key.char == 'a':
                self.a_is_pressed = False
            elif key.char == 'd':
                self.d_is_pressed = False
            elif key.char == 's':
                self.s_is_pressed = False
        except AttributeError:
            pass
    def start_cmd_vel_publisher(self):
        if self.get_parameter('use_stamped_vel').value:
            self.cmd_vel_publisher = self.create_publisher(TwistStamped, self.get_parameter('velocity_topic').value, 10)
        else:
            self.cmd_vel_publisher = self.create_publisher(Twist, self.get_parameter('velocity_topic').value, 10)
    def on_use_stamped_vel_changed(self, event):
        self.get_logger().info(f"'use_stamped_vel' parameter changed to: {event}")
        # Stop the current publisher
        self.cmd_vel_publisher.destroy()
        # Start a new publisher based on the updated parameter value
        self.start_cmd_vel_publisher()


def main(args=None):
    rclpy.init(args=args)
    turtle_control_node = TurtleControl()
    try:
        rclpy.spin(turtle_control_node)
    except KeyboardInterrupt:
        pass
    finally:
        turtle_control_node.listener.stop()
        turtle_control_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()