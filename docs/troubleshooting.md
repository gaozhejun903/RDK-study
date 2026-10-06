# Troubleshooting｜统一排错方法

## 第一原则：不要一报错就重装

按照顺序查：

1. **复制完整报错**
2. 确认当前命令在哪个终端执行
3. 确认 ROS source
4. 确认 package 是否安装
5. 确认 topic/node 是否存在
6. 确认 TF
7. 最后才考虑重装

## ROS package not found
```bash
source /opt/ros/humble/setup.bash
source ~/rdk_study_ws/install/setup.bash
ros2 pkg list | grep 包名
```

## Topic 没数据
```bash
ros2 topic list
ros2 topic info /topic_name
ros2 topic hz /topic_name
```
先确认有没有 Publisher。

## Gazebo 卡顿
```bash
glxinfo | grep "OpenGL renderer"
```
检查显卡/OpenGL。虚拟机通常性能更差。

## RViz No transform
先看：
```bash
ros2 run tf2_tools view_frames
```
再查具体 frame：
```bash
ros2 run tf2_ros tf2_echo frame_a frame_b
```

## Nav2 车不动
先看：
```bash
ros2 topic echo /cmd_vel
```
- 有速度：继续查底盘/仿真控制
- 没速度：查 Nav2 状态、定位、costmap、planner/controller

## Python 缺包
确认是不是在正确 venv：
```bash
which python
python -m pip list
```

## 提问模板
向学长/AI 提问时必须带：
```text
系统：Ubuntu 22.04
ROS：Humble
正在做：TaskXX
执行命令：
完整报错：
我已经尝试：
期望结果：
实际结果：
```
不要只发一句“为什么运行不了”。
