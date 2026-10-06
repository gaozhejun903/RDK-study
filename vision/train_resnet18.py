from pathlib import Path
import csv
import argparse
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

class LaneDataset(Dataset):
    def __init__(self, split):
        self.dir = DATA / split
        with open(DATA / f"{split}.csv", encoding="utf-8") as f:
            self.rows = list(csv.DictReader(f))
        self.tf = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
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
    return sum(err)/len(err) * 639.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--batch-size", type=int, default=32)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    train = DataLoader(LaneDataset("train"), batch_size=args.batch_size, shuffle=True)
    val = DataLoader(LaneDataset("val"), batch_size=args.batch_size)

    model = build_model().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.SmoothL1Loss()

    best = 1e9
    for epoch in range(1, args.epochs + 1):
        model.train()
        for x, y in train:
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            loss = loss_fn(model(x), y)
            loss.backward()
            opt.step()
        mae = evaluate(model, val, device)
        print(f"epoch={epoch} val_mae_px={mae:.3f}")
        if mae < best:
            best = mae
            torch.save(model.state_dict(), BASE / "lane_resnet18.pt")
    print("best val MAE(px):", best)

if __name__ == "__main__":
    main()
