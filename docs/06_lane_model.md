# Task06｜巡线 ResNet18：从零数据到 ONNX

## 目标
即使队长没有给你任何数据，也能先完整走通：
```text
生成数据 → 训练 → 测试 → 导出 ONNX → ONNX Runtime 验证
```

这只是“工具链学习数据”。拿到真实比赛视频后必须重新采集和训练。

## 1. 建 Python 环境
```bash
cd ~/RDK-study/vision
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

如果有 NVIDIA GPU，需要自行安装与驱动匹配的 PyTorch CUDA 版本；没有 GPU 也可以用 CPU 完成本仓库小数据集。

## 2. 自动生成合成赛道
```bash
python generate_lane_dataset.py
```
会生成：
```text
vision/data/
├── train/
├── val/
├── test/
├── train.csv
├── val.csv
└── test.csv
```

标签 x 表示图像底部附近的赛道中心横坐标。

## 3. 看几张图片
```bash
python - <<'PY'
import cv2
from pathlib import Path
p=next((Path("data/train")).glob("*.jpg"))
im=cv2.imread(str(p))
print(p, im.shape)
cv2.imshow("sample", im)
cv2.waitKey(0)
PY
```

## 4. 训练 ResNet18
```bash
python train_resnet18.py --epochs 5 --batch-size 32
```
成功后生成：
```text
lane_resnet18.pt
```

观察 val_mae_px 是否下降。

## 5. 导出 ONNX
```bash
python export_onnx.py
```
生成：
```text
lane_resnet18.onnx
```

## 6. ONNX Runtime 测试
```bash
python verify_onnx.py
```
必须看到 MAE、P90、P95。

## 7. 为什么比赛不能只用合成数据
真实赛道存在：
- 光照变化
- 阴影
- 模糊
- 摄像头畸变
- 地面纹理
- 曝光
- 不同弯道

正式训练应按“视频级”划分 train/val/test，避免相邻帧泄漏。

## 8. 和比赛巡线功能包的关系
正式 RDK 侧可以将模型输出封装为 ROS2 Topic，让控制/决策节点订阅。推荐后续参考 racing_track_detection_resnet 的接口思想，而不是把推理和整车逻辑写在一个脚本里。

## 验收
提交：
- 训练日志
- lane_resnet18.pt
- lane_resnet18.onnx
- test MAE/P90/P95
- 解释为什么需要独立 test
