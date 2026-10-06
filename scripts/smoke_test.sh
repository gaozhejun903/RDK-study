#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VISION="$ROOT/vision"

echo "=== RDK-study smoke test ==="
echo "repo: $ROOT"
python3 --version

cd "$VISION"

echo
echo "[1/6] Python syntax"
python3 -m compileall -q .

echo
echo "[2/6] Import dependencies"
python3 - <<'PY'
mods = [
    "torch",
    "torchvision",
    "numpy",
    "cv2",
    "onnx",
    "onnxruntime",
    "PIL",
]
for name in mods:
    mod = __import__(name)
    print(f"{name}: {getattr(mod, '__version__', 'OK')}")
PY

echo
echo "[3/6] Generate tiny dataset"
python3 generate_lane_dataset.py \
  --train-count 16 \
  --val-count 4 \
  --test-count 4 \
  --seed 42

test "$(find data/train -name '*.jpg' | wc -l)" -eq 16
test "$(find data/val   -name '*.jpg' | wc -l)" -eq 4
test "$(find data/test  -name '*.jpg' | wc -l)" -eq 4

echo
echo "[4/6] One-epoch CPU training"
CUDA_VISIBLE_DEVICES="" python3 train_resnet18.py \
  --epochs 1 \
  --batch-size 4 \
  --seed 42

test -s lane_resnet18.pt
test -s train_meta.json

echo
echo "[5/6] Export ONNX"
python3 export_onnx.py
test -s lane_resnet18.onnx

echo
echo "[6/6] Verify PyTorch <-> ONNX"
python3 verify_onnx.py

echo
echo "=== PASS: full vision smoke test completed ==="
