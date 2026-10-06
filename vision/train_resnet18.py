from pathlib import Path
import csv
import argparse
import json
import random

import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image

from model import build_model

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
SEED = 42


def set_seed(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class LaneDataset(Dataset):
    def __init__(self, split):
        self.dir = DATA / split
        csv_path = DATA / f"{split}.csv"

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Missing {csv_path}. Run: python generate_lane_dataset.py"
            )

        with open(csv_path, encoding="utf-8") as f:
            self.rows = list(csv.DictReader(f))

        self.tf = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225],
            ),
        ])

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        row = self.rows[i]
        img = Image.open(self.dir / row["filename"]).convert("RGB")
        x_norm = float(row["x"]) / 639.0

        return (
            self.tf(img),
            torch.tensor([x_norm], dtype=torch.float32),
        )


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    errors = []

    for images, targets in loader:
        preds = model(images.to(device)).cpu()
        errors.extend((preds - targets).abs().flatten().tolist())

    if not errors:
        raise RuntimeError("Validation set is empty.")

    return sum(errors) / len(errors) * 639.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    set_seed(args.seed)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={device} seed={args.seed}")

    generator = torch.Generator()
    generator.manual_seed(args.seed)

    train_loader = DataLoader(
        LaneDataset("train"),
        batch_size=args.batch_size,
        shuffle=True,
        generator=generator,
    )

    val_loader = DataLoader(
        LaneDataset("val"),
        batch_size=args.batch_size,
        shuffle=False,
    )

    model = build_model().to(device)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-3,
    )

    loss_fn = nn.SmoothL1Loss()
    best_mae = float("inf")

    for epoch in range(1, args.epochs + 1):
        model.train()

        train_loss_sum = 0.0
        train_count = 0

        for images, targets in train_loader:
            images = images.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()

            preds = model(images)
            loss = loss_fn(preds, targets)

            loss.backward()
            optimizer.step()

            train_loss_sum += loss.item() * images.size(0)
            train_count += images.size(0)

        val_mae_px = evaluate(
            model,
            val_loader,
            device,
        )

        mean_train_loss = train_loss_sum / max(
            train_count,
            1,
        )

        print(
            f"epoch={epoch} "
            f"train_loss={mean_train_loss:.6f} "
            f"val_mae_px={val_mae_px:.3f}"
        )

        if val_mae_px < best_mae:
            best_mae = val_mae_px
            torch.save(
                model.state_dict(),
                BASE / "lane_resnet18.pt",
            )

    meta = {
        "seed": args.seed,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "best_val_mae_px": best_mae,
        "input_shape": [1, 3, 224, 224],
        "output": "x_norm in [0,1]",
        "normalization_mean": [
            0.485,
            0.456,
            0.406,
        ],
        "normalization_std": [
            0.229,
            0.224,
            0.225,
        ],
    }

    (BASE / "train_meta.json").write_text(
        json.dumps(
            meta,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"best val MAE(px): {best_mae:.3f}")
    print(f"saved: {BASE / 'lane_resnet18.pt'}")
    print(f"saved: {BASE / 'train_meta.json'}")


if __name__ == "__main__":
    main()
