import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SquareDriver(Node):
    def __init__(self):
        super().__init__('square_driver')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.phase = 0
        self.ticks = 0
        self.timer = self.create_timer(0.1, self.step)

    def step(self):
        msg = Twist()
        if self.phase % 2 == 0:
            msg.linear.x = 0.15
            limit = 30
        else:
            msg.angular.z = 0.55
            limit = 15
        self.pub.publish(msg)
        self.ticks += 1
        if self.ticks >= limit:
            self.ticks = 0
            self.phase = (self.phase + 1) % 8

def main():
    rclpy.init()
    node = SquareDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.pub.publish(Twist())
    node.destroy_node()
    rclpy.shutdown()
