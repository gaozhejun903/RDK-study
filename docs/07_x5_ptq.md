# Task07｜RDK X5 OpenExplorer PTQ 量化

## 目标
理解并完成：
```text
FP32 ONNX → 模型检查 → 校准集 → PTQ → 定点模型 / BIN → 精度与性能检查
```

**这一阶段的转换工作可以在 x86-64 PC/Docker 完成，不要求手边有 X5。**
真正的 BPU 运行与摄像头接入等拿到 X5 后再做。

## 1. 先理解三个概念

### ONNX
跨框架模型格式，是 PC 训练和部署工具链之间的桥梁。

### PTQ
Post Training Quantization。训练结束后，用代表性校准数据估计量化范围，将浮点网络转换为更适合 BPU 的定点模型。

### calibration dataset
不是训练集。它不做梯度更新，而是让量化工具看到“真实输入通常长什么样”。

## 2. X5 关键参数
RDK X5 对应的 march 为：
```text
bayes-e
```

## 3. 准备模型
使用 Task06：
```text
vision/lane_resnet18.onnx
```

先在 Python 中检查：
```bash
cd ~/RDK-study/vision
source .venv/bin/activate
python - <<'PY'
import onnx
m=onnx.load("lane_resnet18.onnx")
onnx.checker.check_model(m)
print("ONNX OK")
for x in m.graph.input: print("input:", x.name)
for x in m.graph.output: print("output:", x.name)
PY
```

## 4. 安装 OpenExplorer
OpenExplorer 版本会更新，**不要从本教程复制一个永久固定的下载链接**。进入 D-Robotics 官方 OpenExplorer 文档，选择与 X5 SDK/比赛环境匹配的版本，并优先使用官方 Docker 镜像/安装说明。

官方入口：
https://developer.d-robotics.cc/oe_x5_doc/

安装完成后记录：
- OpenExplorer 版本
- Docker 镜像 tag
- hb_mapper/hb_model_info 版本
- march=bayes-e

这些必须写进报告，避免队友环境不同无法复现。

## 5. 做 64–100 张校准样本
首次练习可从合成 train/val 选 64 张；正式比赛要换真实数据。

原则：
- 覆盖直线/左右弯
- 覆盖亮暗
- 覆盖赛道偏左/居中/偏右
- 不要只挑“最好看”的图片
- test 集不要拿去做校准

你可以先：
```bash
mkdir -p ptq/calibration
python - <<'PY'
from pathlib import Path
import shutil
src=list((Path("data/train")).glob("*.jpg"))[:64]
dst=Path("ptq/calibration"); dst.mkdir(parents=True,exist_ok=True)
for p in src: shutil.copy2(p,dst/p.name)
print(len(src))
PY
```

## 6. 理解 config.yaml
OpenExplorer 不同版本字段可能略有区别，因此以你安装版本官方示例为准。至少要能解释：
- model_parameters
- input_parameters
- calibration_parameters
- compiler_parameters
- march / target

不要只会复制 yaml。

## 7. Checker
在 OpenExplorer 环境中，先运行模型检查。常见工具链会提供 hb_mapper checker/等价检查命令。

目标：
- ONNX 能解析
- 输入 shape 正确
- 算子支持情况明确
- 无意外 CPU fallback（如工具报告支持查看）
- march 正确

## 8. PTQ 与编译
按照你安装版本的官方 quick start 执行 makertbin/convert/compile 流程，最终保留：
- float ONNX
- quantized ONNX / intermediate artifacts
- final BIN
- config.yaml
- checker log
- compiler log

## 9. 精度验证
**BIN 生成不等于完成。**

至少比较 float ONNX 与量化模型在同一 test 上：
- Mean 坐标漂移
- P95 漂移
- test MAE 变化
- NaN/Inf
- 模型大小

## 10. 静态工具
若当前版本提供，运行并保存：
```text
hb_model_info
hb_perf
hb_verifier
```
或官方文档中等价工具。

## 11. 拿到 X5 后
再补：
```text
BIN → X5
摄像头/NV12 → BPU
BPU输出 → ROS2 Topic
Foxglove/RViz验证
控制节点订阅结果
```

## 验收
必须能回答：
1. PTQ 与 QAT 区别？
2. calibration data 为什么不能全用 test？
3. 为什么 X5 需要 bayes-e？
4. 为什么 ONNX 能运行还要转换 BIN？
5. 为什么量化后必须重新做任务精度测试？
