import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist
from pynput import keyboard
from turtlesim.msg import Color


class TurtleControl(Node):
    def __init__(self):
        super().__init__('turtle_control')

        self.w_is_pressed = False
        self.a_is_pressed = False
        self.d_is_pressed = False
        self.s_is_pressed = False

        self.get_logger().info('Turtle control node has been started.')

        self.cmd_vel_publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.dominant_colour_publisher = self.create_publisher(String, '/dominant_colour', 10)
        self.colour_subscriber = self.create_subscription(Color, '/turtle1/color_sensor', self.colour_callback, 10)
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