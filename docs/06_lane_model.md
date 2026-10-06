# Task06｜巡线 ResNet18：从零数据到 ONNX

## 目标

即使队长没有提供任何额外数据，也能完整走通：

```text
生成数据
  ↓
训练 ResNet18
  ↓
验证集评估
  ↓
导出 ONNX
  ↓
PyTorch ↔ ONNX 一致性检查
  ↓
独立 test 评估
```

> 本仓库生成的合成数据只用于**跑通工具链**，不能代表正式比赛模型效果。  
> 真正比赛时必须换成真实赛道数据重新训练和评估。

---

## 1. 创建 Python 环境

```bash
cd ~/RDK-study/vision

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -U pip
pip install -r requirements.txt
```

检查：

```bash
python - <<'PY'
import torch, torchvision, onnx, onnxruntime
print("torch:", torch.__version__)
print("torchvision:", torchvision.__version__)
print("onnx:", onnx.__version__)
print("onnxruntime:", onnxruntime.__version__)
PY
```

---

## 2. 自动生成学习用数据

```bash
python generate_lane_dataset.py
```

生成：

```text
vision/data/
├── train/
├── val/
├── test/
├── train.csv
├── val.csv
└── test.csv
```

其中标签 `x` 表示赛道目标点的横坐标。

---

## 3. 检查一张样本

桌面 Ubuntu 可运行：

```bash
python - <<'PY'
import cv2
from pathlib import Path

p = next(Path("data/train").glob("*.jpg"))
im = cv2.imread(str(p))

print("file:", p)
print("shape:", im.shape)

cv2.imshow("sample", im)
cv2.waitKey(0)
cv2.destroyAllWindows()
PY
```

如果是没有 GUI 的 SSH/WSL 环境，不要使用 imshow，可改成：

```bash
python - <<'PY'
import cv2
from pathlib import Path

p = next(Path("data/train").glob("*.jpg"))
im = cv2.imread(str(p))
print("file:", p)
print("shape:", im.shape)
print("mean:", im.mean())
PY
```

---

## 4. 训练 ResNet18

```bash
python train_resnet18.py --epochs 5 --batch-size 32 --seed 42
```

成功后生成：

```text
lane_resnet18.pt
train_meta.json
```

训练日志至少应该看到：

```text
train_loss=...
val_mae_px=...
```

关注：

- train_loss 是否下降；
- val_mae_px 是否整体下降；
- 不要只看最后一次训练 loss。

---

## 5. 为什么固定随机种子

本仓库默认：

```text
seed = 42
```

目的是：

- 方便不同队员比较；
- 更容易复现；
- 出问题时更容易定位。

固定种子不代表完全位级一致，GPU/CUDA 某些算子仍可能存在小差异。

---

## 6. 导出 ONNX

```bash
python export_onnx.py
```

输出：

```text
lane_resnet18.onnx
```

本仓库显式：

- opset = 11；
- dynamo = False；
- 输入 = `images [1,3,224,224]`；
- 输出 = `x_norm [1,1]`。

这样是为了减少新旧 PyTorch 导出器差异对 X5 教学链路的影响。

---

## 7. PyTorch ↔ ONNX 一致性检查

运行：

```bash
python verify_onnx.py
```

现在脚本会同时做两件事：

### A. 测 ONNX 在 test 上的误差

输出：

```text
ONNX test MAE(px)
ONNX test P90(px)
ONNX test P95(px)
```

### B. 比较 PyTorch 与 ONNX 数值

输出：

```text
PyTorch-vs-ONNX mean_abs_diff
PyTorch-vs-ONNX max_abs_diff
```

正常应最后看到：

```text
PASS: PyTorch and ONNX outputs are consistent.
```

如果最大归一化输出差异 > 1e-4，脚本会直接失败。

**此时不要继续做 PTQ。**

---

## 8. 为什么必须做独立 test

如果 train / val / test 使用高度相似的相邻视频帧，模型可能“看起来很准”，实际只是数据泄漏。

真实比赛数据应优先按：

```text
视频
场景
采集轮次
```

进行划分，而不是把所有图片随机 shuffle 后再拆。

---

## 9. 正式比赛要换成什么数据

真实赛道至少包含：

- 直线；
- 左弯；
- 右弯；
- 光照变化；
- 阴影；
- 模糊；
- 不同曝光；
- 地面纹理；
- 摄像头畸变；
- 不同车辆速度。

合成数据只能证明：

> 训练代码、ONNX 导出和推理链路能跑通。

不能证明：

> 模型可以直接参加比赛。

---

## 10. 和正式巡线 ROS2 功能的关系

以后正式 RDK 侧应形成：

```text
Camera
  ↓
ROS2 Image
  ↓
BPU / ResNet18
  ↓
Track Point
  ↓
ROS2 Topic
  ↓
Controller
```

不要把：

- 摄像头
- 模型
- 控制
- 状态机

全部写进同一个 Python 文件。

---

## 验收

提交：

- 训练日志；
- `lane_resnet18.pt`；
- `train_meta.json`；
- `lane_resnet18.onnx`；
- test MAE / P90 / P95；
- PyTorch vs ONNX 最大差异；
- 一页失败分析。

必须回答：

1. train / val / test 各做什么？
2. 为什么要固定随机种子？
3. 为什么 ONNX 导出后还要和 PyTorch 比较？
4. 为什么合成数据不能代表比赛效果？
5. 为什么不能把相邻视频帧随机拆到 train 和 test？
