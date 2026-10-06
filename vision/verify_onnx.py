from pathlib import Path
import csv
import numpy as np
import onnxruntime as ort
from PIL import Image
from torchvision import transforms

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
sess = ort.InferenceSession(str(BASE / "lane_resnet18.onnx"), providers=["CPUExecutionProvider"])
name = sess.get_inputs()[0].name

tf = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])

with open(DATA / "test.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

errors=[]
for r in rows:
    img = Image.open(DATA/"test"/r["filename"]).convert("RGB")
    x = tf(img).unsqueeze(0).numpy()
    p = float(sess.run(None, {name:x})[0].reshape(-1)[0]) * 639.0
    gt = float(r["x"])
    errors.append(abs(p-gt))

a=np.array(errors)
print(f"N={len(a)}")
print(f"MAE(px)={a.mean():.3f}")
print(f"P90(px)={np.percentile(a,90):.3f}")
print(f"P95(px)={np.percentile(a,95):.3f}")
