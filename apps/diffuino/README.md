# Diffuino

Diffuino runs a class-conditioned MNIST diffusion model on the Arduino UNO Q.
The Qualcomm Linux processor performs ONNX inference and streams 8×13 grayscale
frames over Bridge RPC; the STM32 refreshes the onboard matrix. The reliable
interactive default is the FP32 teacher. Binary-weight checkpoints remain part
of the research workflow, but are deployed only after passing the same 10-class
matrix validation.

## UNO Q

```bash
cd ~/monodiffuse
git pull --ff-only
source .venv/bin/activate
python -m pip install -r apps/diffuino/requirements.txt
```

Open `apps/diffuino` in Arduino App Lab and run it once to compile and flash
`sketch/sketch.ino`. Then generate a requested digit from the repository root:

App Lab discovers user applications under `~/ArduinoApps`. From the UNO Q shell,
install or update this repository checkout with:

```bash
mkdir -p ~/ArduinoApps/diffuino
rsync -a ~/monodiffuse/apps/diffuino/ ~/ArduinoApps/diffuino/
arduino-app-cli app list
arduino-app-cli app start user:diffuino
```

The matrix briefly displays a border when the STM32 sketch boots. Diffusion
frames begin after the Linux container and Bridge RPC are ready. To inspect a
run that exits before displaying frames:

```bash
arduino-app-cli app ps
arduino-app-cli app logs user:diffuino --tail 200 --all
```

```bash
python -m apps.diffuino.python.main --seed 11
```

The default conditional FP32 deployment accepts `--digit 0` through `--digit 9`
and automatically selects a visually audited initial-noise seed for that class.
Pass `--seed` explicitly to explore other outputs. Use `--no-matrix` to benchmark
inference without Bridge. The
final 28×28 image is saved under
`apps/diffuino/output/latest.png`. Each run creates exactly one sample and then
prints a held-out MNIST classifier prediction so the terminal result can be
matched against the matrix. This prediction names the uncontrolled sample; it
is not a ground-truth label or a generative-quality metric.

The physical framebuffer is horizontal: 8 rows by 13 columns. Diffuino keeps
the digit square by centering an 8×8 image within those 13 columns.

The 8×8 digit conversion applies per-frame contrast stretching so thin MNIST
strokes reach the matrix's full grayscale range after downsampling.

The visually audited default seeds are `0:15`, `1:16`, `2:10`, `3:0`, `4:0`,
`5:0`, `6:12`, `7:4`, `8:10`, and `9:18`.

Screen candidate seeds on a workstation before running them on the board:

```bash
python -m apps.diffuino.screen_seeds --start 0 --count 50
# Recheck a shortlist at higher visual density:
python -m apps.diffuino.screen_seeds --seeds 11,12,30 --columns 3
```

This writes labeled 28×28 and exact quantized 8×8 matrix contact sheets plus a
CSV under `apps/diffuino/output/`.
The automatic `KEEP` filter combines classifier confidence with foreground-ink
and contrast checks; the contact sheet remains the final visual check.

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
