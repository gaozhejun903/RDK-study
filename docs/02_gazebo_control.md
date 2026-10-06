# Task02｜Gazebo + TurtleBot3 控制

## 目标

实现：

```text
键盘/代码 → /cmd_vel → Gazebo 小车运动 → /odom 改变
```

---

## 1. 安装 TurtleBot3

优先使用 apt：

```bash
sudo apt update
sudo apt install -y \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-gazebo \
  ros-humble-teleop-twist-keyboard
```

设置型号：

```bash
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
source ~/.bashrc
echo $TURTLEBOT3_MODEL
```

应输出：

```text
burger
```

---

## 2. 如果 apt 找不到 turtlebot3_gazebo

先确认已经：

```bash
source /opt/ros/humble/setup.bash
sudo apt update
apt-cache search ros-humble-turtlebot3
```

如果你的镜像源或发行包没有对应仿真包，可以走源码安装：

```bash
mkdir -p ~/turtlebot3_ws/src
cd ~/turtlebot3_ws/src

git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git

cd ~/turtlebot3_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

如果走源码路线，建议写入：

```bash
echo "source ~/turtlebot3_ws/install/setup.bash" >> ~/.bashrc
```

---

## 3. 启动仿真

终端 A：

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

成功现象：

- Gazebo 打开；
- 世界中出现 TurtleBot3；
- 不应持续刷严重 error。

---

## 4. 键盘遥控

终端 B：

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```

按终端提示控制车辆。

---

## 5. 观察 /cmd_vel

终端 C：

```bash
ros2 topic echo /cmd_vel
```

你应该看到：

```text
linear:
  x: ...
angular:
  z: ...
```

---

## 6. 观察 /odom

终端 D：

```bash
ros2 topic echo /odom
```

移动小车时：

- position.x / y 改变；
- orientation 改变；
- twist 中速度改变。

---

## 7. 用自己的节点控制小车

确保 Task01 的示例包已经复制到：

```text
~/rdk_study_ws/src/rdk_study_control
```

重新编译：

```bash
cd ~/rdk_study_ws
colcon build --symlink-install
source install/setup.bash
```

启动：

```bash
ros2 run rdk_study_control square_driver
```

观察小车自动执行：

```text
前进
→ 左转
→ 前进
→ 左转
→ ...
```

按 Ctrl+C 后，小车应收到停止指令。

---

## 8. 必须理解 /cmd_vel

对 TurtleBot3：

```text
linear.x  > 0：前进
linear.x  < 0：后退
angular.z > 0：左转
angular.z < 0：右转
```

注意：

TurtleBot3 是**差速车**，可以近似原地旋转。

正式比赛若使用 Ackermann 结构：

- 不能把原地旋转当正常能力；
- 后续需要使用 Ackermann 运动学/控制器；
- 但 ROS2、/odom、TF、导航等基础概念仍然通用。

---

## 验收

必须完成：

1. 键盘控制小车；
2. /cmd_vel 有数据；
3. /odom 随车辆运动改变；
4. square_driver 能控制 Gazebo 小车；
5. Ctrl+C 后车辆停止；
6. 能解释“控制命令”和“状态反馈”的区别。

---

## 常见错误

### package 'turtlebot3_gazebo' not found

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash  # 仅源码安装时
ros2 pkg list | grep turtlebot3
```

### Gazebo 卡顿/黑屏

```bash
sudo apt install -y mesa-utils
glxinfo | grep "OpenGL renderer"
```

虚拟机图形性能通常明显弱于双系统。

### 车不动但 /cmd_vel 有数据

检查：

```bash
ros2 topic info /cmd_vel
ros2 node list
```

确认 Gazebo 控制插件已经订阅对应速度话题。
