# Diffuino

Diffuino runs an unconditional binary-weight MNIST diffusion model on the
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
python -m apps.diffuino.python.main --seed 11
```

Each seed starts from different Gaussian noise and may resolve into any digit
from 0 through 9. Use `--no-matrix` to benchmark inference without Bridge. The
final 28×28 image is saved under
`apps/diffuino/output/latest.png`.

Seed 11 is the reproducible default because it forms a legible seven with the
selected seed-2 binary checkpoint. Pass any integer seed to explore other
uncontrolled outputs.

The paper-faithful default is the 1,000-step ancestral DDPM sampler. A reduced-step
DDIM mode is available for profiling, but the present binary checkpoint does not
produce reliable digits with the 50-step DDIM path and it is not used for the demo.

## Training workstation

```bash
venv/bin/python -m apps.diffuino.export_onnx
```

The default export uses the best verified native uncentered/pre-activation seed-2
checkpoint from the paper. It materializes the learned one-bit convolution weights into
ordinary floating-point convolution tensors because ONNX Runtime does not use a
packed XNOR kernel. The trained representation is binary-weight, but this first
deployment does not claim binary arithmetic acceleration.
