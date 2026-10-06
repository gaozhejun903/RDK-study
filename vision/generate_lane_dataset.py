from pathlib import Path
import argparse
import csv
import random

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent / "data"


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)


def make_sample(w=640, h=224):
    img = np.full((h, w, 3), 230, np.uint8)
    center = random.randint(140, w - 140)
    curve = random.uniform(-0.0015, 0.0015)
    thickness = random.randint(18, 32)

    for y in range(h):
        dy = y - h // 2
        x = int(center + curve * dy * dy)
        cv2.circle(
            img,
            (max(0, min(w - 1, x)), y),
            thickness,
            (30, 30, 30),
            -1,
        )

    noise = np.random.normal(
        0,
        random.uniform(2, 10),
        img.shape,
    ).astype(np.float32)
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    if random.random() < 0.3:
        alpha = random.uniform(0.65, 1.25)
        img = np.clip(img.astype(np.float32) * alpha, 0, 255).astype(np.uint8)

    x_target = int(center + curve * (h - 1 - h // 2) ** 2)
    return img, max(0, min(w - 1, x_target))


def write_split(split: str, count: int):
    out = ROOT / split
    out.mkdir(parents=True, exist_ok=True)

    # Remove stale generated images so a smoke-test dataset cannot silently
    # mix with an older, larger dataset.
    for old in out.glob("*.jpg"):
        old.unlink()

    rows = []
    for i in range(count):
        img, x = make_sample()
        name = f"{split}_{i:05d}.jpg"
        ok = cv2.imwrite(str(out / name), img)
        if not ok:
            raise RuntimeError(f"Failed to write {out / name}")
        rows.append((name, x))

    with open(ROOT / f"{split}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "x"])
        writer.writerows(rows)

    print(f"{split}: {count}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-count", type=int, default=800)
    ap.add_argument("--val-count", type=int, default=160)
    ap.add_argument("--test-count", type=int, default=160)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    for name, value in [
        ("train-count", args.train_count),
        ("val-count", args.val_count),
        ("test-count", args.test_count),
    ]:
        if value <= 0:
            raise ValueError(f"--{name} must be > 0")

    set_seed(args.seed)

    write_split("train", args.train_count)
    write_split("val", args.val_count)
    write_split("test", args.test_count)

    print("Dataset:", ROOT)


if __name__ == "__main__":
    main()
