import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from geometry_msgs.msg import Twist

from custom_actions.action import MovementX
from custom_actions.action import MovementYaw
from nav_msgs.msg import Odometry
import numpy as np

from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from tf_transformations import euler_from_quaternion

class MovementNode(Node):
    def __init__(self):
        super().__init__('movement_server_node')
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)


        self.odom_subscriber = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        self.action_timeout = 10.0  # seconds

        self.callback_group = ReentrantCallbackGroup()

        self._movement_x_action_server = ActionServer(
            self,
            MovementX,
            'movement_x',
            self.execute_movement_x_callback,
            callback_group=self.callback_group

        )

        self._movement_yaw_action_server = ActionServer(
            self,
            MovementYaw,
            'movement_yaw',
            self.execute_movement_yaw_callback,
            callback_group=self.callback_group
        )

    def execute_movement_x_callback(self, goal_handle):
        self.get_logger().info('Executing movement in X direction...')
   
        distance =goal_handle.request.distance
        speed = goal_handle.request.speed
        action_timed_out = False
        # Set the result and mark the goal as succeeded
        goal_x = self.robot_x + distance*np.cos(self.robot_yaw)
        goal_y = self.robot_y + distance*np.sin(self.robot_yaw)
        start = time.time()
        self.get_logger().info(f'Goal position: x={goal_x}, y={goal_y}')

        while True:
            remaining_distance = np.sqrt((goal_x - self.robot_x)**2 + (goal_y - self.robot_y)**2)
            feedback = MovementX.Feedback()
            feedback.remaining_distance = float(remaining_distance)
            goal_handle.publish_feedback(feedback)
            #goal reached
            if (remaining_distance < 0.05):
                break
            #timeout
            if  (time.time() - start >= self.action_timeout):
                action_timed_out = True
                self.get_logger().warn('Movement action timed out!')
                break
            self.get_logger().info(f'Current position: x={self.robot_x}, y={self.robot_y}, yaw={self.robot_yaw}')


            self.publish_cmd_vel(speed,0.0,0.0)


        self.publish_cmd_vel(0.0,0.0,0.0)

        result = MovementX.Result()
        self.get_logger().info(f'type: {type(result)} Goal reached: {result}')
        if action_timed_out:
            result.goal_reached = False
            goal_handle.abort()
        else:
            result.goal_reached = True
            goal_handle.succeed()


        return result

    def execute_movement_yaw_callback(self, goal_handle):
        self.get_logger().info('Executing movement in Yaw direction...')

        angle = goal_handle.request.angle
        angular_speed = goal_handle.request.angular_speed

        action_timed_out = False

        # Save the yaw when the action started
        start_yaw = self.robot_yaw

        # Target yaw relative to starting orientation
        target_yaw = self.normalize_angle(start_yaw + angle)

        start = time.time()

        self.get_logger().info(
            f'Start yaw: {start_yaw}, '
            f'Target yaw: {target_yaw}'
        )

        while True:

            # Calculate shortest angular difference to target
            remaining_angle = self.normalize_angle(
                target_yaw - self.robot_yaw
            )
            feedback = MovementYaw.Feedback()
            feedback.remaining_angle = float(remaining_angle)
            goal_handle.publish_feedback(feedback)

            self.get_logger().info(
                f'Current yaw: {self.robot_yaw}, '
                f'Remaining angle: {remaining_angle}'
            )

            # Goal reached
            if abs(remaining_angle) <= 0.05:  # ~2.9 degrees
                break

            # Timeout
            if time.time() - start >= self.action_timeout:
                action_timed_out = True
                self.get_logger().warn('Yaw action timed out!')
                break

            # Rotate in the correct direction
            direction = np.sign(remaining_angle)

            self.publish_cmd_vel(
                0.0,
                0.0,
                direction * angular_speed
            )

        # Stop the robot
        self.publish_cmd_vel(0.0, 0.0, 0.0)

        result = MovementYaw.Result()

        if action_timed_out:
            result.goal_reached = False
            goal_handle.abort()
        else:
            result.goal_reached = True
            goal_handle.succeed()

        return result

    def normalize_angle(self, angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi

    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        #self.get_logger().error(f"Current position: x={self.robot_x}, y={self.robot_y}")
        quaternion = [msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w]
        _,_,self.robot_yaw= euler_from_quaternion(quaternion)

    def publish_cmd_vel(self, linear_x, linear_y, angular_z):
        twist = Twist()
        twist.linear.x = linear_x
        twist.linear.y = linear_y
        twist.angular.z = angular_z
        self.cmd_vel_publisher.publish(twist)
        self.get_logger().info(f'Published cmd_vel: linear.x={linear_x}, linear.y={linear_y}, angular.z={angular_z}')


def main():
    rclpy.init()
    movement_node = MovementNode()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(movement_node)
    try:
        executor.spin()
    finally:
        movement_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
