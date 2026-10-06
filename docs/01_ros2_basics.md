# Task01｜ROS2 基础：Node、Topic、Service

## 比赛对应
摄像头、雷达、巡线、导航、决策、底盘通常拆成独立 Node，通过 Topic / Service / Action 协作。

## 1. 编译示例包
```bash
cd ~/rdk_study_ws
colcon build --symlink-install
source install/setup.bash
```

## 2. Publisher
终端 A：
```bash
ros2 run rdk_study_control number_publisher
```
终端 B：
```bash
ros2 topic list
ros2 topic echo /number
ros2 topic hz /number
ros2 topic info /number
```

## 3. Subscriber
终端 C：
```bash
ros2 run rdk_study_control number_subscriber
```

观察节点：
```bash
ros2 node list
ros2 node info /number_publisher
ros2 node info /number_subscriber
```

## 4. Service
```bash
sudo apt install -y ros-humble-turtlesim
ros2 run turtlesim turtlesim_node
```
新终端：
```bash
ros2 service list
ros2 service call /reset std_srvs/srv/Empty "{}"
```

## 必须理解
Topic：持续数据流，如 /image、/scan、/odom、/cmd_vel。
Service：一次请求一次响应，如 reset、保存配置。

## 验收
现场完成 topic list / echo / hz / node info，并回答：
1. Publisher 和 Subscriber 是否必须同时启动？
2. Topic 和 Service 的区别？
3. 为什么 /image 用 Topic？
