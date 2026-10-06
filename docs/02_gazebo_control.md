# Task02｜Gazebo + TurtleBot3 控制

## 目标
实现：
```text
键盘/代码 → /cmd_vel → Gazebo 小车运动 → /odom 改变
```

## 1. 安装
```bash
sudo apt update
sudo apt install -y ros-humble-turtlebot3 ros-humble-turtlebot3-gazebo ros-humble-teleop-twist-keyboard
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
source ~/.bashrc
```

## 2. 启动仿真
终端 A：
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

## 3. 键盘遥控
终端 B：
```bash
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```

## 4. 观察速度与里程计
终端 C：
```bash
ros2 topic echo /cmd_vel
```
终端 D：
```bash
ros2 topic echo /odom
```

## 5. 自己的控制节点
```bash
cd ~/rdk_study_ws
source install/setup.bash
ros2 run rdk_study_control square_driver
```
观察小车自动前进、转向。

## 必须理解
- linear.x > 0：前进
- angular.z > 0：左转
- /cmd_vel 是命令
- /odom 是状态估计

TurtleBot3 是差速车；正式 Ackermann 赛车不能原地旋转，后续迁移时要换运动学/控制器。

## 验收
1. 键盘控制成功
2. /cmd_vel 有数据
3. /odom 随运动变化
4. square_driver 能驱动车辆
5. 能解释命令与反馈
