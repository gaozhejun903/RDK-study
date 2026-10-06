from pathlib import Path
import argparse
import csv
import random

import cv2
import numpy as np

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"


def read_rows(split: str):
    csv_path = DATA / f"{split}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Missing {csv_path}. Run generate_lane_dataset.py first."
        )
    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [(split, r) for r in rows]


def preprocess_for_calibration(img_bgr: np.ndarray) -> np.ndarray:
    """
    Prepare calibration data for the repository's X5 PTQ template.

    IMPORTANT:
    - Resize to 224x224.
    - Convert BGR(OpenCV) -> RGB.
    - Convert HWC -> CHW.
    - Keep value range 0..255 as float32.
    - DO NOT divide by 255.
    - DO NOT apply ImageNet mean/std here.

    The PTQ YAML template is responsible for equivalent mean/scale handling.
    This prevents applying normalization twice.
    """
    img = cv2.resize(img_bgr, (224, 224), interpolation=cv2.INTER_LINEAR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    chw = np.transpose(img, (2, 0, 1)).astype(np.float32)
    return np.ascontiguousarray(chw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--num-samples", type=int, default=64)
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=BASE / "ptq" / "calibration_rgb_f32",
    )
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    candidates = read_rows("train") + read_rows("val")

    if args.num_samples <= 0:
        raise ValueError("--num-samples must be > 0")
    if args.num_samples > len(candidates):
        raise ValueError(
            f"Requested {args.num_samples} samples, "
            f"but only {len(candidates)} are available."
        )

    rng = random.Random(args.seed)
    selected = rng.sample(candidates, args.num_samples)

    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir.parent / "calibration_manifest.csv"

    manifest = []

    for index, (split, row) in enumerate(selected):
        image_path = DATA / split / row["filename"]
        img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if img is None:
            raise RuntimeError(f"Failed to read image: {image_path}")

        tensor = preprocess_for_calibration(img)
        out_name = f"{index:04d}_{Path(row['filename']).stem}.rgb_chw_f32.bin"
        out_path = out_dir / out_name
        tensor.tofile(out_path)

        manifest.append({
            "index": index,
            "split": split,
            "source": str(image_path.relative_to(BASE)),
            "output": str(out_path.relative_to(BASE)),
            "shape": "3x224x224",
            "dtype": "float32",
            "layout": "CHW",
            "color": "RGB",
            "value_range": "0..255",
        })

    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest[0].keys())
        writer.writeheader()
        writer.writerows(manifest)

    expected_bytes = 3 * 224 * 224 * 4
    first_file = next(out_dir.glob("*.bin"))
    actual_bytes = first_file.stat().st_size

    print(f"output_dir={out_dir}")
    print(f"manifest={manifest_path}")
    print(f"samples={len(manifest)}")
    print(f"expected_bytes_per_file={expected_bytes}")
    print(f"first_file_bytes={actual_bytes}")

    if actual_bytes != expected_bytes:
        raise RuntimeError(
            "Calibration binary size is wrong. "
            f"Expected {expected_bytes}, got {actual_bytes}."
        )

    print("PASS: calibration data generated successfully.")


if __name__ == "__main__":
    main()
