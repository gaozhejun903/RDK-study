# Task00｜Ubuntu、Git 与 ROS2 Humble 环境安装

## 目标
完成后能运行：
```bash
ros2 --help
python3 --version
git --version
```

## 1. 基础系统
推荐 Ubuntu 22.04 双系统。更新：
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget vim build-essential python3-pip python3-venv software-properties-common
```

## 2. 安装 ROS2 Humble
```bash
sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

sudo add-apt-repository universe
sudo apt update
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install -y ros-humble-desktop ros-dev-tools python3-colcon-common-extensions
```

自动 source：
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## 3. ROS2 通信测试
终端 A：
```bash
ros2 run demo_nodes_cpp talker
```
终端 B：
```bash
ros2 run demo_nodes_py listener
```
持续收到 Hello World 即成功。

## 4. 克隆本仓库
```bash
cd ~
git clone https://github.com/gaozhejun903/RDK-study.git
cd RDK-study
bash scripts/check_ros_env.sh
```

## 5. 创建学习工作空间
```bash
mkdir -p ~/rdk_study_ws/src
cp -r ~/RDK-study/ros2_ws/src/rdk_study_control ~/rdk_study_ws/src/
cd ~/rdk_study_ws
colcon build --symlink-install
source install/setup.bash
```

## 验收
- ros2 可执行
- talker/listener 通信正常
- colcon build 成功
- 能解释 source 的作用

## 常见错误
### ros2: command not found
```bash
source /opt/ros/humble/setup.bash
```
### package not found
```bash
source ~/rdk_study_ws/install/setup.bash
```
