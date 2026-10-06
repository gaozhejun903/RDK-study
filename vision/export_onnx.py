from pathlib import Path

import onnx
import torch
from torch import nn
from torchvision import models

BASE = Path(__file__).resolve().parent
PT = BASE / "lane_resnet18.pt"
OUT = BASE / "lane_resnet18.onnx"

if not PT.exists():
    raise FileNotFoundError(f"Missing {PT}. Train the model first.")

m = models.resnet18(weights=None)
m.fc = nn.Linear(m.fc.in_features, 1)
m.load_state_dict(torch.load(PT, map_location="cpu"))
m.eval()

dummy = torch.randn(1, 3, 224, 224, dtype=torch.float32)

# Explicitly use the legacy exporter for this teaching repository.
# Reason: the X5 learning path intentionally targets a simple opset-11 graph.
# Newer PyTorch releases default to the dynamo exporter, whose behavior and
# dependencies change over time.
torch.onnx.export(
    m,
    dummy,
    OUT,
    input_names=["images"],
    output_names=["x_norm"],
    opset_version=11,
    do_constant_folding=True,
    dynamo=False,
)

model = onnx.load(str(OUT))
onnx.checker.check_model(model)

print(f"ONNX OK: {OUT}")
print("input : images [1,3,224,224] float32")
print("output: x_norm [1,1] float32")
print("opset :", model.opset_import[0].version)
