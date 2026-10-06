# RDK-study｜地瓜智能车新人自学仓库

> 面向：几乎没有 ROS2 基础、暂时没有 RDK X5 / 实体小车，但需要为地瓜智能车比赛做准备的队员。  
> 目标：只看本仓库，从零完成 **ROS2 控制 → Gazebo 仿真 → SLAM 建图 → Nav2 导航 → 巡线模型训练 → ONNX → RDK X5 PTQ 量化 → 综合联调**。

---

## 0. 为什么这样学

正式比赛的软件链路可以抽象为：

```text
传感器/摄像头
      ↓
   ROS2 数据
      ↓
 感知 / 定位
      ↓
 路径规划 / 决策
      ↓
    /cmd_vel
      ↓
      底盘
```

目前没有实体 RDK X5 和小车，所以先在 PC 上完成 80% 以上的软件能力：

1. 用 TurtleBot3 + Gazebo 代替真实小车；
2. 用 ROS2 Humble 学习 Topic、Service、TF、/cmd_vel、/odom；
3. 用 SLAM Toolbox 建图；
4. 用 Nav2 做目标点导航和避障；
5. 用仓库自带脚本生成一个“无需额外数据”的巡线玩具数据集；
6. 训练 ResNet18 并导出 ONNX；
7. 在 OpenExplorer 中完成 X5 PTQ / BIN 编译；
8. 最后把导航、视觉和控制串起来。

等拿到 RDK X5 后，主要替换：
- Gazebo → 真实底盘；
- 仿真 /scan、/odom → 真实雷达和里程计；
- ONNX Runtime → X5 BPU / BIN；
- 上层 ROS2 结构尽量不变。

---

# 1. 学习路线

| 阶段 | 内容 | 是否需要 RDK X5 | 建议时间 |
|---|---|---:|---:|
| Task00 | Ubuntu / Git / ROS2 环境 | 否 | 0.5–1 天 |
| Task01 | ROS2 最小基础 | 否 | 1–2 天 |
| Task02 | Gazebo 小车控制 | 否 | 1–2 天 |
| Task03 | TF / Odom / LaserScan | 否 | 1 天 |
| Task04 | SLAM Toolbox 建图 | 否 | 1–2 天 |
| Task05 | Nav2 自主导航 | 否 | 1–2 天 |
| Task06 | 巡线模型训练 + ONNX | 否 | 2–4 天 |
| Task07 | RDK X5 OpenExplorer PTQ | 否（转换阶段） | 2–3 天 |
| Task08 | 综合任务与比赛迁移 | 否 | 2–3 天 |

建议严格按顺序做，不要跳 Task。

---

# 2. 环境基线

本仓库默认：

- Ubuntu 22.04
- ROS2 Humble
- Python 3.10
- Gazebo Classic（ROS2 Humble 常用组合）
- TurtleBot3 Burger
- SLAM Toolbox
- Nav2
- PyTorch / torchvision
- ONNX / ONNX Runtime
- Docker Engine
- RDK X5 OpenExplorer（PTQ 阶段）

> Windows 用户：ROS2 / Gazebo / RViz / SLAM 建议优先使用 Ubuntu 22.04 双系统。  
> WSL2 可以用于模型训练和 PTQ，但 Gazebo GUI、网络和图形加速更容易出现额外问题。

---

# 3. 从哪里开始

从这里开始：

👉 [Task00：环境安装](docs/00_environment.md)

完成后依次进入：

1. [Task01：ROS2 基础](docs/01_ros2_basics.md)
2. [Task02：Gazebo 小车控制](docs/02_gazebo_control.md)
3. [Task03：TF / Odom / LaserScan](docs/03_tf_odom_scan.md)
4. [Task04：SLAM 建图](docs/04_slam.md)
5. [Task05：Nav2 导航](docs/05_nav2.md)
6. [Task06：巡线模型训练与 ONNX](docs/06_lane_model.md)
7. [Task07：X5 PTQ 量化](docs/07_x5_ptq.md)
8. [Task08：综合任务](docs/08_final_project.md)

---

# 4. 仓库结构

```text
RDK-study/
├── README.md
├── docs/
│   ├── 00_environment.md
│   ├── 01_ros2_basics.md
│   ├── 02_gazebo_control.md
│   ├── 03_tf_odom_scan.md
│   ├── 04_slam.md
│   ├── 05_nav2.md
│   ├── 06_lane_model.md
│   ├── 07_x5_ptq.md
│   ├── 08_final_project.md
│   └── troubleshooting.md
├── ros2_ws/
│   └── src/
│       └── rdk_study_control/
│           ├── package.xml
│           ├── setup.py
│           ├── setup.cfg
│           ├── resource/rdk_study_control
│           └── rdk_study_control/
│               ├── __init__.py
│               ├── number_publisher.py
│               ├── number_subscriber.py
│               └── square_driver.py
├── vision/
│   ├── requirements.txt
│   ├── generate_lane_dataset.py
│   ├── train_resnet18.py
│   ├── export_onnx.py
│   ├── verify_onnx.py
│   ├── prepare_x5_calibration.py
│   └── x5_ptq_config_template.yaml
└── scripts/
    ├── check_ros_env.sh
    └── check_topics.sh
```

---

# 5. 学习规则

每个 Task 都包含：

- **你要学什么**
- **为什么比赛需要**
- **完整操作步骤**
- **每条命令的作用**
- **成功时应该看到什么**
- **常见报错**
- **验收要求**
- **提交物**

不要只复制命令。每完成一个 Task，都要能回答文档末尾的“自测问题”。

---

# 6. 推荐统一提交方式

每个人 Fork 本仓库或建立自己的分支，例如：

```bash
git checkout -b study/你的名字-task01
```

完成后至少提交：

```text
report/
├── Task01.md
├── screenshots/
└── logs/
```

报告中记录：

1. 完成了什么；
2. 遇到什么报错；
3. 如何定位；
4. 如何解决；
5. 自己对这一 Task 的理解。

---

# 7. 与地瓜比赛的对应关系

| 学习内容 | 比赛中的意义 |
|---|---|
| ROS2 Topic / Node | 连接摄像头、雷达、视觉、导航、底盘 |
| /cmd_vel | 上层算法最终控制车辆 |
| /odom + TF | 定位、建图、导航的基础 |
| /scan | 激光雷达环境感知 |
| SLAM | 建立场地图 |
| Nav2 | 自主到达任务点、避障 |
| ResNet18 巡线 | 环道/赛道视觉感知 |
| ONNX | 模型部署中间格式 |
| X5 PTQ | 将 PC 浮点模型转换为 X5 可高效执行模型 |
| BIN / BPU | 最终板端推理 |

---

# 8. 参考官方资料

教程已经把关键操作写进本仓库，下面只作为进一步查阅：

- D-Robotics RDK 文档：https://developer.d-robotics.cc/
- X5 OpenExplorer 文档：https://developer.d-robotics.cc/oe_x5_doc/
- ROS2 Humble：https://docs.ros.org/en/humble/
- TurtleBot3：https://emanual.robotis.com/docs/en/platform/turtlebot3/
- Nav2：https://docs.nav2.org/

---

## 最终要求

学完本仓库后，你应该能独立回答并演示：

- ROS2 Node / Topic / Service 是什么？
- 如何通过 /cmd_vel 控制 Gazebo 中的小车？
- /odom、/scan、TF 分别是什么？
- 如何用 SLAM Toolbox 建出地图？
- 如何保存地图并用 Nav2 导航？
- 如何训练巡线 ResNet18 并导出 ONNX？
- 什么是 PTQ？为什么需要校准集？
- 为什么 X5 的 march 是 bayes-e？
- 如何把 PC 仿真链路迁移到 RDK X5 + 实车？

如果这些问题都能独立完成，你就已经具备进入真实 RDK X5 / 实车联调阶段的基础。
