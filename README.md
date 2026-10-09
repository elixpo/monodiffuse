# MonoDiffuse

MonoDiffuse is a controlled study of one-bit-weight diffusion training. The main
question is narrow: when zero-shot one-bit post-training quantization fails, how
much can be recovered by optimizing with binary weights in the forward pass?

The current study compares parameter-compatible variants of one small residual
U-Net:

- FP32 training;
- native W1A32 training from random initialization;
- zero-shot W1A32 post-training quantization (PTQ);
- FP32-initialized W1A32 quantization-aware training (QAT); and
- a W1A1 core whose boundary, normalization, time-conditioning, scaling, and
  residual operations remain floating point.

Every condition uses the same optimizer, training budget, diffusion schedule, and
ancestral 1,000-step sampler. Results are repeated over training seeds 0, 1, and 2.

## Current finding

On MNIST, the best native W1A32 condition substantially outperforms zero-shot PTQ,
but it does **not** match the FP32 baseline. Domain-feature Fréchet distance is
`46.33 ± 17.24` for native uncentered/pre-activation W1A32, versus
`1314.20 ± 314.96` for matched PTQ and `3.15 ± 0.38` for FP32.

The experiments also reject two claims from an earlier draft:

- mean-centering does not reduce trained latent-to-binary angular error and hurts
  the strongest pre-activation condition; and
- peak classifier confidence is not a valid quality score here, because clamped
  Gaussian noise receives mean confidence `1.000`.

The full metric suite therefore reports domain-feature Fréchet and kernel
distances, density, coverage, and class-prior Jensen--Shannon divergence, with
real--real and Gaussian-noise controls. CIFAR-10 is included as a natural-image
stress test rather than presented as a competitive benchmark.

## Reproduce the study

Install the pinned environment:

```bash
python -m venv venv
venv/bin/pip install -r requirements.txt
```

Run the tests:

```bash
venv/bin/python -m pytest -q
```

Train all MNIST conditions with three independent seeds:

```bash
venv/bin/python -m experiments.v1_binary_study.train suite \
  --dataset mnist --seeds 0,1,2 --epochs 12 \
  --batch-size 256 --base-channels 16
```

Evaluate with the exact ancestral sampler:

```bash
venv/bin/python -m experiments.v1_binary_study.evaluate suite \
  --dataset mnist --encoder-epochs 10 --eval-samples 2000 \
  --eval-batch-size 256 --sampler ddpm
```

Export physically packed binary inference weights:

```bash
venv/bin/python -m experiments.v1_binary_study.export \
  artifacts/v1_binary_study/mnist/native_uncentered_pre/seed_0/checkpoint.pt
```

The representative packed tensor payload is 121,316 bytes, versus 875,972 bytes
for the FP32 state (7.22×). This is a storage measurement. The project does not yet
implement packed XNOR convolution kernels and makes no measured latency or energy
claim.

## Repository map

- `experiments/v1_binary_study/`: matched models, training, evaluation, export,
  tests, and exact commands;
- `artifacts/v1_binary_study/`: per-seed checkpoints, hashes, histories, metrics,
  controls, summaries, and sample grids;
- `paper/v0_mnist/paper.tex`: the paper source; and
- `experiments/v0_mnist/`: archived exploratory scripts and figures, not the
  source of the controlled-study results.

## License

[MIT](LICENSE)
