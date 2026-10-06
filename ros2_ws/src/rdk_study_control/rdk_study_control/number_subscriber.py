import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

class NumberSubscriber(Node):
    def __init__(self):
        super().__init__('number_subscriber')
        self.sub = self.create_subscription(Int32, '/number', self.cb, 10)

    def cb(self, msg):
        self.get_logger().info(f'receive: {msg.data}')

def main():
    rclpy.init()
    node = NumberSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
