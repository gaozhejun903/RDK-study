# Task03｜TF、Odom 与 LaserScan

## 1. 启动 TurtleBot3
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

## 2. 检查关键话题
```bash
ros2 topic list | sort
```
重点：
```text
/cmd_vel
/odom
/scan
/tf
/tf_static
```

## 3. 雷达
```bash
ros2 topic echo /scan --once
```
理解 angle_min、angle_max、range_min、range_max、ranges[]。

## 4. TF
```bash
sudo apt install -y ros-humble-tf2-tools
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo odom base_footprint
```

典型链：
```text
map → odom → base_footprint/base_link → base_scan
```

## 5. RViz2
```bash
rviz2
```
Fixed Frame 设为 odom，添加 RobotModel、TF、LaserScan、Odometry。

## 验收
- /scan 有合法 ranges
- /odom 随运动变化
- RViz 能看到雷达
- 能生成 TF 树
- 能解释 map/odom/base_link/base_scan
