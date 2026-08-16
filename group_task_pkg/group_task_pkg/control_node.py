import time
import numpy as np

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool

from custom_actions.action import MovementX
from custom_actions.action import MovementYaw


class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')
        self._movement_x_client = ActionClient(self, MovementX, 'movement_x')
        self._movement_yaw_client = ActionClient(self, MovementYaw, 'movement_yaw')
        self.cli = self.create_client(SetBool, 'toggle_walls_1_2')
        self.wall_status = False

    def execute_movement_yaw(self, angle, speed):
        goal_msg = MovementYaw.Goal()
        goal_msg.angle = angle
        goal_msg.angular_speed = speed

        self.get_logger().info(f'Sending movement_yaw goal: angle={angle}, speed={speed}')
        self._movement_yaw_client.wait_for_server()

        # Step 1: Send goal and wait for server acceptance
        send_goal_future = self._movement_yaw_client.send_goal_async(
            goal_msg, feedback_callback=self.movement_yaw_feedback_callback
        )
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().info('MovementYaw goal was rejected by server.')
            return None

        # Step 2: Wait for actual completion of movement
        get_result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, get_result_future)
        return get_result_future.result()

    def execute_movement_x(self, distance, speed):
        goal_msg = MovementX.Goal()
        goal_msg.distance = distance
        goal_msg.speed = speed

        self.get_logger().info(f'Sending movement_x goal: distance={distance}, speed={speed}')
        self._movement_x_client.wait_for_server()

        # Step 1: Send goal and wait for server acceptance
        send_goal_future = self._movement_x_client.send_goal_async(
            goal_msg, feedback_callback=self.movement_x_feedback_callback
        )
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().info('MovementX goal was rejected by server.')
            return None

        # Step 2: Wait for actual completion of movement
        get_result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, get_result_future)
        return get_result_future.result()

    def movement_x_feedback_callback(self, feedback_msg):   
        feedback = feedback_msg.feedback
        self.get_logger().info(f'MovementX Feedback: Remaining distance: {feedback.remaining_distance:.2f} meters')

    def movement_yaw_feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'MovementYaw Feedback: Remaining angle: {feedback.remaining_angle:.2f} radians')

    def toggle_walls(self):
        req = SetBool.Request()
        req.data = not self.wall_status

        self.get_logger().info(f'Sending toggle_walls request: enable={req.data}')
        self.cli.wait_for_service()
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            self.wall_status = req.data  # Update internal state on success
            self.get_logger().info(f'Toggle walls success: {future.result().message}')


def main(args=None):
    rclpy.init(args=args)
    ctrl_node = ControlNode()

    # Sequential execution: each call blocks until completion
    ctrl_node.execute_movement_yaw(angle=np.pi/2, speed=0.5)
    ctrl_node.toggle_walls()    

    ctrl_node.execute_movement_x(distance=1.0, speed=1.0)
    ctrl_node.toggle_walls()
    ctrl_node.execute_movement_x(distance=1.0, speed=1.0)
    ctrl_node.execute_movement_yaw(angle=-np.pi/2, speed=0.5)
    ctrl_node.execute_movement_x(distance=5.0, speed=5.0)




    ctrl_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()