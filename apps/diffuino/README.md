# Diffuino

Diffuino runs a class-conditioned binary-weight MNIST diffusion model on the
Arduino UNO Q. The Qualcomm Linux processor performs ONNX inference and streams
8×13 grayscale frames over Bridge RPC; the STM32 refreshes the onboard matrix.

## UNO Q

```bash
cd ~/monodiffuse
git pull --ff-only
source .venv/bin/activate
python -m pip install -r apps/diffuino/requirements.txt
```

Open `apps/diffuino` in Arduino App Lab and run it once to compile and flash
`sketch/sketch.ino`. Then generate a requested digit from the repository root:

```bash
python -m apps.diffuino.python.main --digit 7 --steps 50 --seed 0
```

Use `--digit random` for a randomly selected class and `--no-matrix` to benchmark
inference without Bridge. The final 28×28 image is saved under
`apps/diffuino/output/latest.png`.

## Training workstation

```bash
venv/bin/python -m apps.diffuino.train_conditional --epochs 12
venv/bin/python -m apps.diffuino.export_onnx
```

The ONNX export materializes the learned one-bit convolution weights into
ordinary floating-point convolution tensors because ONNX Runtime does not use a
packed XNOR kernel. The trained representation is binary-weight, but this first
deployment does not claim binary arithmetic acceleration.
