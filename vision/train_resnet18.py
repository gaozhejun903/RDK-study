from pathlib import Path
import csv
import argparse
import json
import random

import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image

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
        r = self.rows[i]
        img = Image.open(self.dir / r["filename"]).convert("RGB")
        x = float(r["x"]) / 639.0
        return self.tf(img), torch.tensor([x], dtype=torch.float32)


def build_model():
    m = models.resnet18(weights=None)
    m.fc = nn.Linear(m.fc.in_features, 1)
    return m


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    err = []
    for x, y in loader:
        pred = model(x.to(device)).cpu()
        err.extend((pred - y).abs().flatten().tolist())
    if not err:
        raise RuntimeError("Validation set is empty.")
    return sum(err) / len(err) * 639.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    set_seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={device} seed={args.seed}")

    generator = torch.Generator()
    generator.manual_seed(args.seed)

    train = DataLoader(
        LaneDataset("train"),
        batch_size=args.batch_size,
        shuffle=True,
        generator=generator,
    )
    val = DataLoader(
        LaneDataset("val"),
        batch_size=args.batch_size,
        shuffle=False,
    )

    model = build_model().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.SmoothL1Loss()

    best = float("inf")
    for epoch in range(1, args.epochs + 1):
        model.train()
        train_loss = 0.0
        count = 0
        for x, y in train:
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            pred = model(x)
            loss = loss_fn(pred, y)
            loss.backward()
            opt.step()
            train_loss += loss.item() * x.size(0)
            count += x.size(0)

        mae = evaluate(model, val, device)
        mean_train_loss = train_loss / max(count, 1)
        print(
            f"epoch={epoch} "
            f"train_loss={mean_train_loss:.6f} "
            f"val_mae_px={mae:.3f}"
        )

        if mae < best:
            best = mae
            torch.save(model.state_dict(), BASE / "lane_resnet18.pt")

    meta = {
        "seed": args.seed,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "best_val_mae_px": best,
        "input_shape": [1, 3, 224, 224],
        "normalization_mean": [0.485, 0.456, 0.406],
        "normalization_std": [0.229, 0.224, 0.225],
    }
    (BASE / "train_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"best val MAE(px): {best:.3f}")
    print(f"saved: {BASE / 'lane_resnet18.pt'}")
    print(f"saved: {BASE / 'train_meta.json'}")


if __name__ == "__main__":
    main()
