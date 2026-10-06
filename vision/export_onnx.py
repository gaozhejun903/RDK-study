from pathlib import Path

import onnx
import torch

from model import build_model

BASE = Path(__file__).resolve().parent
PT = BASE / "lane_resnet18.pt"
OUT = BASE / "lane_resnet18.onnx"

if not PT.exists():
    raise FileNotFoundError(f"Missing {PT}. Train the model first.")

model = build_model()
model.load_state_dict(torch.load(PT, map_location="cpu"))
model.eval()

dummy = torch.randn(1, 3, 224, 224, dtype=torch.float32)

torch.onnx.export(
    model,
    dummy,
    OUT,
    input_names=["images"],
    output_names=["x_norm"],
    opset_version=11,
    do_constant_folding=True,
    dynamo=False,
)

onnx_model = onnx.load(str(OUT))
onnx.checker.check_model(onnx_model)

print(f"ONNX OK: {OUT}")
print("input : images [1,3,224,224] float32")
print("output: x_norm [1,1] float32, bounded to [0,1]")
print("opset :", onnx_model.opset_import[0].version)
