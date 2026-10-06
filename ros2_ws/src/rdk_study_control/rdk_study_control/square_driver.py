import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class SquareDriver(Node):
    def __init__(self):
        super().__init__("square_driver")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.phase = 0
        self.ticks = 0
        self.timer = self.create_timer(0.1, self.step)

    def step(self):
        msg = Twist()

        # 30 ticks = 3 s forward, 15 ticks = 1.5 s rotate.
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

    def safe_stop(self):
        stop = Twist()
        # Publish several zero commands so a transient DDS loss is less likely
        # to leave the simulated/real chassis executing the previous command.
        for _ in range(5):
            self.pub.publish(stop)
            time.sleep(0.03)


def main():
    rclpy.init()
    node = SquareDriver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.safe_stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
