"""Dataset definitions shared by training and evaluation."""

from __future__ import annotations

from pathlib import Path

from torch.utils.data import DataLoader
from torchvision import datasets, transforms


DATASET_INFO = {
    "mnist": {"channels": 1, "classes": 10, "size": 28},
    "fashion_mnist": {"channels": 1, "classes": 10, "size": 28},
    "cifar10": {"channels": 3, "classes": 10, "size": 32},
}


def dataset(name: str, root: Path, train: bool, augment: bool = False):
    normalize = transforms.Lambda(lambda x: x.mul(2).sub(1))
    operations = []
    if augment and name == "cifar10":
        operations += [transforms.RandomHorizontalFlip(), transforms.RandomCrop(32, padding=4)]
    operations += [transforms.ToTensor(), normalize]
    transform = transforms.Compose(operations)
    cls = {
        "mnist": datasets.MNIST,
        "fashion_mnist": datasets.FashionMNIST,
        "cifar10": datasets.CIFAR10,
    }[name]
    return cls(root=root, train=train, download=True, transform=transform)


def loader(name: str, root: Path, train: bool, batch_size: int, workers: int, seed: int):
    import torch

    generator = torch.Generator().manual_seed(seed)
    return DataLoader(
        dataset(name, root, train, augment=train),
        batch_size=batch_size,
        shuffle=train,
        num_workers=workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=train,
        generator=generator,
        persistent_workers=workers > 0,
    )
