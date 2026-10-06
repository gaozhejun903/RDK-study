from pathlib import Path
import csv

import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn
from torchvision import models, transforms
from PIL import Image

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
ONNX_PATH = BASE / "lane_resnet18.onnx"
PT_PATH = BASE / "lane_resnet18.pt"

if not ONNX_PATH.exists():
    raise FileNotFoundError(f"Missing {ONNX_PATH}. Run export_onnx.py first.")
if not PT_PATH.exists():
    raise FileNotFoundError(f"Missing {PT_PATH}. Train the model first.")

onnx.checker.check_model(onnx.load(str(ONNX_PATH)))

torch_model = models.resnet18(weights=None)
torch_model.fc = nn.Linear(torch_model.fc.in_features, 1)
torch_model.load_state_dict(torch.load(PT_PATH, map_location="cpu"))
torch_model.eval()

sess = ort.InferenceSession(
    str(ONNX_PATH),
    providers=["CPUExecutionProvider"],
)
input_name = sess.get_inputs()[0].name

tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225],
    ),
])

with open(DATA / "test.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise RuntimeError("Test set is empty.")

onnx_errors = []
pt_onnx_abs_diff = []

with torch.no_grad():
    for r in rows:
        img = Image.open(DATA / "test" / r["filename"]).convert("RGB")
        tensor = tf(img).unsqueeze(0)

        pt_norm = float(torch_model(tensor).reshape(-1)[0].item())
        onnx_norm = float(
            sess.run(None, {input_name: tensor.numpy()})[0].reshape(-1)[0]
        )

        gt_px = float(r["x"])
        onnx_px = onnx_norm * 639.0

        onnx_errors.append(abs(onnx_px - gt_px))
        pt_onnx_abs_diff.append(abs(pt_norm - onnx_norm))

err = np.asarray(onnx_errors, dtype=np.float64)
diff = np.asarray(pt_onnx_abs_diff, dtype=np.float64)

print(f"N={len(err)}")
print(f"ONNX test MAE(px)={err.mean():.3f}")
print(f"ONNX test P90(px)={np.percentile(err, 90):.3f}")
print(f"ONNX test P95(px)={np.percentile(err, 95):.3f}")
print(f"PyTorch-vs-ONNX mean_abs_diff(norm)={diff.mean():.8f}")
print(f"PyTorch-vs-ONNX max_abs_diff(norm)={diff.max():.8f}")
print(f"PyTorch-vs-ONNX max_abs_diff(px)={diff.max() * 639.0:.6f}")

if diff.max() > 1e-4:
    raise SystemExit(
        "FAIL: PyTorch/ONNX mismatch is larger than 1e-4. "
        "Do not continue to PTQ until this is fixed."
    )

print("PASS: PyTorch and ONNX outputs are consistent.")
