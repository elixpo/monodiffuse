"""Dataset definitions shared by training and evaluation."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


DATASET_INFO = {
    "mnist": {"channels": 1, "classes": 10, "size": 28},
    "fashion_mnist": {"channels": 1, "classes": 10, "size": 28},
    "cifar10": {"channels": 3, "classes": 10, "size": 32},
}


class ParquetCIFAR10(Dataset):
    """CIFAR-10 reader for the University of Toronto Hugging Face mirror."""

    def __init__(self, path: Path, transform=None):
        try:
            import pyarrow.parquet as parquet
        except ImportError as error:
            raise RuntimeError("pyarrow is required to read the CIFAR-10 parquet mirror") from error
        table = parquet.read_table(path, columns=["img", "label"], memory_map=True)
        self.images = table["img"]
        self.labels = table["label"]
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        encoded = self.images[index].as_py()["bytes"]
        image = Image.open(io.BytesIO(encoded)).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return image, self.labels[index].as_py()


def dataset(name: str, root: Path, train: bool, augment: bool = False):
    normalize = transforms.Lambda(lambda x: x.mul(2).sub(1))
    operations = []
    if augment and name == "cifar10":
        operations += [transforms.RandomHorizontalFlip(), transforms.RandomCrop(32, padding=4)]
    operations += [transforms.ToTensor(), normalize]
    transform = transforms.Compose(operations)
    if name == "cifar10":
        parquet_path = root / f"cifar10-{'train' if train else 'test'}.parquet"
        if parquet_path.exists():
            return ParquetCIFAR10(parquet_path, transform=transform)
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
