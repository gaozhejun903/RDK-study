import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

class NumberPublisher(Node):
    def __init__(self):
        super().__init__('number_publisher')
        self.pub = self.create_publisher(Int32, '/number', 10)
        self.n = 0
        self.timer = self.create_timer(0.5, self.tick)

    def tick(self):
        msg = Int32()
        msg.data = self.n
        self.pub.publish(msg)
        self.get_logger().info(f'publish: {self.n}')
        self.n += 1

def main():
    rclpy.init()
    node = NumberPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
