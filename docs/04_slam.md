# Task04｜SLAM Toolbox 建图

## 比赛对应

正式比赛中的自主移动，离不开“机器人在哪里”和“周围环境是什么样”。  
本 Task 主线统一使用 **SLAM Toolbox**，这样与 RDK X5 官方机器人开发文档的教学路线保持一致。

---

## 1. 安装

```bash
sudo apt update
sudo apt install -y \
  ros-humble-slam-toolbox \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-gazebo
```

---

## 2. 启动 Gazebo

终端 A：

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

成功现象：

- Gazebo 打开；
- TurtleBot3 出现在场景中；
- /scan、/odom、/tf 等话题存在。

检查：

```bash
ros2 topic list | grep -E "/scan|/odom|/tf"
```

---

## 3. 启动 SLAM Toolbox

终端 B：

```bash
source /opt/ros/humble/setup.bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
```

说明：

- online_async_launch.py：在线异步建图；
- use_sim_time:=true：使用 Gazebo 仿真时间；
- SLAM Toolbox 会使用 /scan、TF、里程计等信息建立 /map。

检查：

```bash
ros2 topic echo /map --once
```

如果能看到 OccupancyGrid，说明地图话题已经建立。

---

## 4. 启动 RViz2

终端 C：

```bash
rviz2
```

配置：

1. Fixed Frame 选择 `map`
2. Add → Map → Topic 选择 `/map`
3. Add → LaserScan → Topic 选择 `/scan`
4. Add → TF
5. Add → RobotModel

此时应能看到：

```text
LaserScan
   ↓
SLAM Toolbox
   ↓
/map
   ↓
RViz
```

---

## 5. 遥控机器人探索

终端 D：

```bash
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```

建议：

- 线速度先低一些；
- 转弯不要猛转；
- 墙角要覆盖；
- 尽量回到走过的位置形成闭环；
- 不要只在一个小区域原地绕圈。

---

## 6. 保存地图

创建目录：

```bash
mkdir -p ~/maps
```

保存：

```bash
ros2 run nav2_map_server map_saver_cli \
  -f ~/maps/rdk_study_map \
  --ros-args -p use_sim_time:=true
```

检查：

```bash
ls -lh ~/maps
```

应得到：

```text
rdk_study_map.pgm
rdk_study_map.yaml
```

---

## 7. 如何判断地图质量

好地图：

- 墙体连续；
- 重影少；
- 拐角明显；
- 地图没有整体撕裂。

坏地图：

- 一面墙变成两三面平行墙；
- 地图突然旋转/扭曲；
- 小车位置明显跳变；
- 大量墙体错位。

---

## 8. 为什么不再把 Cartographer 当主线

Cartographer 也可以用于 TurtleBot3 建图，但本仓库主线统一使用 SLAM Toolbox，原因是：

1. 更贴合当前 RDK X5 官方机器人开发路线；
2. 新人只学一条主线，避免“README 说 SLAM Toolbox、实际却跑 Cartographer”的混乱；
3. 后续 Nav2 与 ROS2 Humble 学习更统一。

Cartographer 可以作为扩展学习，不作为 Task04 必做内容。

---

## 验收

提交：

- `rdk_study_map.pgm`
- `rdk_study_map.yaml`
- RViz 建图截图
- TF 树
- 一段 30–60 秒建图视频

并回答：

1. /scan 提供什么？
2. /odom 提供什么？
3. 为什么 TF 错了 SLAM 会失败？
4. 为什么速度太快更容易出现地图重影？
5. 什么叫闭环？
