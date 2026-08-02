import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class ModeManager(Node):
    def __init__(self):
        super().__init__('mode_manager')
        self.mode = 'manual'  # default on startup

        self.pub_drone = self.create_publisher(Twist, '/model/quadrotor/cmd_vel', 10)

        self.create_subscription(String, '/control_mode', self.mode_cb, 10)
        self.create_subscription(Twist, '/cmd_vel_voice', self.voice_cb, 10)
        self.create_subscription(Twist, '/cmd_vel_manual', self.manual_cb, 10)

        self.get_logger().info('Mode manager started in MANUAL mode')

    def mode_cb(self, msg: String):
        if msg.data in ('voice', 'manual') and msg.data != self.mode:
            self.mode = msg.data
            self.get_logger().info(f'Switched to {self.mode.upper()} mode')

    def voice_cb(self, msg: Twist):
        if self.mode == 'voice':
            self.pub_drone.publish(msg)

    def manual_cb(self, msg: Twist):
        if self.mode == 'manual':
            self.pub_drone.publish(msg)

def main():
    rclpy.init()
    node = ModeManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()