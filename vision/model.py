from torch import nn
from torchvision import models


def build_model():
    """
    ResNet18 regression model for normalized lane x coordinate.

    Output is constrained to [0, 1] with Sigmoid because the training target
    is x / 639. This prevents an unstable early training step from producing
    physically meaningless coordinates far outside the image.
    """
    model = models.resnet18(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(in_features, 1),
        nn.Sigmoid(),
    )
    return model
