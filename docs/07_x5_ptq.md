# Task07｜RDK X5 OpenExplorer PTQ 量化

## 目标

完成：

```text
FP32 ONNX
   ↓
Checker
   ↓
Calibration Data
   ↓
PTQ
   ↓
Quantized Model / BIN
   ↓
精度与性能检查
```

这一阶段的**模型转换**可以在 x86-64 PC / Docker 中完成，不要求手边有 RDK X5。  
真正的 BPU 实时推理、摄像头 NV12 接入、板端 ROS2/TROS 联调，等拿到 X5 后再做。

---

## 1. 前置条件

完成 Task06，并存在：

```text
vision/lane_resnet18.pt
vision/lane_resnet18.onnx
vision/data/
```

先执行：

```bash
cd ~/RDK-study/vision
source .venv/bin/activate
python verify_onnx.py
```

只有看到：

```text
PASS: PyTorch and ONNX outputs are consistent.
```

才继续 PTQ。

---

## 2. 理解 PTQ

PTQ = Post Training Quantization。

训练结束后，不再重新训练模型，而是使用一批代表性数据估计量化范围，把浮点模型转换为更适合 X5 BPU 的模型。

---

## 3. X5 关键参数

RDK X5 对应：

```text
march: bayes-e
```

不要把 X3/X5 的 march 混用。

---

## 4. OpenExplorer 安装

OpenExplorer 版本会随 SDK 更新，因此本仓库不写死永久下载地址。

官方入口：

https://developer.d-robotics.cc/oe_x5_doc/

建议：

- 使用官方 Docker；
- 记录镜像 tag；
- 记录 OpenExplorer 版本；
- 记录 hb_mapper / hb_model_info 版本。

---

## 5. 生成 PTQ 校准数据

本仓库已经提供：

```text
vision/prepare_x5_calibration.py
```

它会：

1. 从 train/val 中抽样；
2. 读取 RGB 图像；
3. Resize 到 224×224；
4. 转成 RGB；
5. 转成 CHW；
6. 保存为 float32 二进制；
7. **不在 Python 中做 mean/std normalize**。

原因：本仓库示例 YAML 会让 OpenExplorer 完成 mean/scale。  
这样可以避免 Python 和 YAML 两边重复归一化。

运行：

```bash
cd ~/RDK-study/vision
source .venv/bin/activate

python prepare_x5_calibration.py \
  --num-samples 64 \
  --output-dir ptq/calibration_rgb_f32
```

检查：

```bash
ls ptq/calibration_rgb_f32 | head
cat ptq/calibration_manifest.csv | head
```

---

## 6. 校准数据原则

正式比赛数据要覆盖：

- 直线；
- 左弯；
- 右弯；
- 亮光；
- 暗光；
- 赛道居左/居中/居右；
- 不同曝光；
- 不同速度采集画面。

不要：

- 全挑“最好看的图片”；
- 从 test 集选；
- 用完全重复的相邻帧凑数量。

建议 64–100 张起步。

---

## 7. YAML 模板

仓库提供：

```text
vision/x5_ptq_config_template.yaml
```

**注意：OpenExplorer 不同版本字段名可能略有差异。**  
因此模板用于“理解结构 + 快速起步”，最终以你安装版本的官方 sample config 为准。

模板里要重点理解：

- model_parameters
- input_parameters
- calibration_parameters
- compiler_parameters
- march
- input_layout
- input_type
- norm_type
- mean_value
- scale_value

本仓库训练预处理是：

```text
RGB
→ Resize(224,224)
→ /255
→ Normalize(mean,std)
```

因此模板把等价的 mean/std 通过 OpenExplorer 配置表达，而 Python 校准脚本只负责准备 RGB/CHW/float32 原始数值数据。

---

## 8. Checker

进入 OpenExplorer 环境后，先运行当前版本对应的 checker。

常见形式类似：

```bash
hb_mapper checker --model-type onnx --model lane_resnet18.onnx --march bayes-e
```

若你安装版本的命令参数不同，以：

```bash
hb_mapper checker --help
```

和官方文档为准。

目标：

- ONNX 能解析；
- 输入 shape 正确；
- 算子支持情况明确；
- march 正确；
- 无明显不支持算子。

---

## 9. PTQ / BIN 编译

按照安装版本官方 quick start 使用：

```text
checker
→ makertbin / convert
→ compiler
→ BIN
```

必须保留：

```text
lane_resnet18.onnx
quantized/intermediate model
model.bin
config.yaml
checker.log
compiler.log
```

---

## 10. 静态检查

如果当前版本提供以下工具：

```text
hb_model_info
hb_perf
hb_verifier
```

或官方等价工具，全部执行并保存日志。

---

## 11. 精度验证

BIN 生成成功 ≠ PTQ 成功。

至少比较：

- Float ONNX
- Quantized 模型

在相同 test 集上的：

- MAE
- Mean drift
- P95 drift
- NaN / Inf
- 模型大小

如果量化后明显变差，要优先检查：

1. 输入数据类型；
2. RGB/BGR；
3. HWC/CHW；
4. mean/std 是否重复；
5. /255 是否重复；
6. Resize 是否一致；
7. 校准集是否具有代表性。

---

## 12. 拿到 X5 后

再补：

```text
Camera / NV12
    ↓
X5 BPU
    ↓
BIN inference
    ↓
ROS2 Topic
    ↓
Decision / Control
```

---

## 验收

提交：

```text
ptq/
├── calibration_rgb_f32/
├── calibration_manifest.csv
├── x5_ptq_config.yaml
├── checker.log
├── compiler.log
└── model.bin
```

并回答：

1. PTQ 与 QAT 区别？
2. 为什么 calibration data 不能全用 test？
3. 为什么本仓库校准脚本不做 mean/std normalize？
4. YAML 里为什么还需要 mean/scale？
5. 为什么 X5 是 bayes-e？
6. 为什么 ONNX 能运行还要转换 BIN？
