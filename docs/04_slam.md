# Task04｜SLAM 建图

## 1. 安装
```bash
sudo apt update
sudo apt install -y ros-humble-slam-toolbox ros-humble-navigation2 ros-humble-nav2-bringup
```

## 2. 启动仿真
终端 A：
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

## 3. 第一次建图
为降低新人门槛，先用 TurtleBot3 常见可运行的 Cartographer 路线：
```bash
sudo apt install -y ros-humble-turtlebot3-cartographer
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

后续再尝试 slam_toolbox，理解两者的输入都依赖 /scan、/odom、TF。

## 4. 遥控探索
```bash
ros2 run turtlebot3_teleop teleop_keyboard
```
原则：慢速、少猛转、覆盖拐角、尽量回到走过的位置形成闭环。

## 5. 保存地图
```bash
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/rdk_study_map
ls ~/maps
```
应得到 .pgm 和 .yaml。

## 判断地图质量
好地图：墙连续、重影少、拐角清楚。
坏地图：双墙、扭曲、机器人跳变、大空洞。

## 验收
提交 map.pgm、map.yaml、建图截图、TF 树，并回答 /scan、/odom、闭环各自作用。
