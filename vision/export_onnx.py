from pathlib import Path
import torch
from torch import nn
from torchvision import models

BASE = Path(__file__).resolve().parent

m = models.resnet18(weights=None)
m.fc = nn.Linear(m.fc.in_features, 1)
m.load_state_dict(torch.load(BASE / "lane_resnet18.pt", map_location="cpu"))
m.eval()

dummy = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    m, dummy, BASE / "lane_resnet18.onnx",
    input_names=["images"], output_names=["x_norm"],
    opset_version=11
)
print(BASE / "lane_resnet18.onnx")
