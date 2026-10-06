from pathlib import Path
import csv
import random
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent / "data"
random.seed(42)
np.random.seed(42)

def make_sample(w=640, h=224):
    img = np.full((h, w, 3), 230, np.uint8)
    center = random.randint(140, w - 140)
    curve = random.uniform(-0.0015, 0.0015)
    thickness = random.randint(18, 32)
    for y in range(h):
        dy = y - h // 2
        x = int(center + curve * dy * dy)
        cv2.circle(img, (max(0, min(w - 1, x)), y), thickness, (30, 30, 30), -1)
    noise = np.random.normal(0, random.uniform(2, 10), img.shape).astype(np.float32)
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    if random.random() < 0.3:
        alpha = random.uniform(0.65, 1.25)
        img = np.clip(img.astype(np.float32) * alpha, 0, 255).astype(np.uint8)
    x_target = int(center + curve * (h - 1 - h // 2) ** 2)
    return img, max(0, min(w - 1, x_target))

def main():
    for split, n in [("train", 800), ("val", 160), ("test", 160)]:
        out = ROOT / split
        out.mkdir(parents=True, exist_ok=True)
        rows = []
        for i in range(n):
            img, x = make_sample()
            name = f"{split}_{i:05d}.jpg"
            cv2.imwrite(str(out / name), img)
            rows.append((name, x))
        with open(ROOT / f"{split}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["filename", "x"])
            w.writerows(rows)
        print(split, n)
    print("Dataset:", ROOT)

if __name__ == "__main__":
    main()
