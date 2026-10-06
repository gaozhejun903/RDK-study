# Task08｜最终综合任务：模拟比赛软件链路

## 目标
把前三条主线连起来：
```text
ROS2 控制 + SLAM/Nav2 + 视觉模型
```

## Part A：导航
1. Gazebo 启动 TurtleBot3。
2. 加载 Task04 地图。
3. Nav2 定位。
4. 从 P 点发送到 Task Point。
5. 中途不得手动遥控。

记录：
- 成功/失败
- 时间
- 是否碰撞
- /cmd_vel
- /amcl_pose

## Part B：视觉
1. 启动 Task06 ONNX 推理。
2. 对一段/一批测试图输出赛道中心。
3. 把结果转换为一个统一结构：
```json
{"x": 320, "confidence": 1.0}
```
基础模型没有 confidence 时可先固定 1.0，之后升级模型。

## Part C：决策状态机
自己实现最小状态：
```text
INIT
  ↓
NAV_TO_TASK
  ↓
VISION_TASK
  ↓
RETURN
  ↓
FINISH
```

禁止把“到点以后直接退出”当完成。

## Part D：异常
至少模拟：
- 导航失败一次
- 视觉输入缺失一次
- 模型输出超范围一次

系统必须有安全处理，而不是崩溃。

## 为什么这样贴比赛
比赛机器人不是一个模型，而是：
```text
感知 → 定位 → 规划 → 决策 → 控制
```
任何一层失败都可能导致整车失败。

## 加分项
- 把状态机做成 ROS2 Node
- 使用 Action 发送导航目标
- 使用 Foxglove 查看状态
- 接入 racing_track_detection_resnet 思路
- 换 race-sim 做赛道仿真
- Ackermann 模型/Hybrid-A* 研究

## 最终提交
```text
report/final/
├── README.md
├── architecture.png
├── test_log.csv
├── screenshots/
└── demo.mp4
```

README 必须回答：
1. 每个 Node 做什么？
2. 每个 Topic 是什么？
3. 谁发布 /cmd_vel？
4. 视觉结果怎样影响决策？
5. 换成 RDK X5 后哪些模块替换，哪些不换？
