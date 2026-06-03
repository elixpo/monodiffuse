# P1 — Logic-Gate Diffusion: feasibility test

**The one question this answers:** can a *differentiable logic-gate network* — a model whose
hidden compute is boolean gates, no arithmetic — act as a diffusion denoiser well enough to
generate recognizable images from pure noise?

If **yes**, the "arithmetic-free diffusion" paper is viable and we scale to CIFAR-10 (P3).
If **no**, we learned it in a few days and fall back to the co-designed binary-UNet plan.

## What's here

| File | Role |
|---|---|
| [model.py](model.py) | Minimal differentiable logic-gate layers (16 relaxed boolean gates per neuron) + a `LogicDenoiser` that predicts clean bits from noisy bits + a binary timestep code. |
| [diffusion.py](diffusion.py) | Bernoulli bit-flip diffusion: forward flips bits toward a uniform random bitstring; closed-form Bernoulli reverse posterior; ancestral sampler. |
| [train.py](train.py) | Trains on binarized MNIST, saves sample grids, prints the go/no-go report. |

**Why Bernoulli (not Gaussian) diffusion here:** logic gates natively output *bits*. A diffusion
process whose state and target are bits is the gate network's natural home — it removes the
hardest viability risk (squeezing precise continuous outputs out of gates).

**Why our own logic layers (not the official `difflogic` CUDA package):** zero build step, runs on
CPU or GPU. If P1 passes, swap in the official kernels for speed before scaling.

## Run

```bash
pip install torch torchvision          # if not already present
python experiments/p1_logicdiff/train.py --quick    # ~minutes: verify it runs end to end
python experiments/p1_logicdiff/train.py            # the real feasibility run
```

Sample grids are written to `results/p1_samples_epXXX.png`. MNIST downloads to `data/` (gitignored).

## Go / No-Go criterion

**PASS** if both hold:
1. **Denoising works** — `x0`-prediction accuracy at low noise (small `t`) is **> 0.9**
   (printed in the report). This says the gate network learned the reverse process.
2. **Generation works** — the final `results/p1_samples_*.png` grid shows **visibly digit-like**
   shapes (not noise, not a uniform blob), with a pixel-on rate near the data's ~0.13.

**Watch the soft-vs-hard gap** in the report: `soft` uses the trained gate *mixture*; `hard` uses
the single argmax gate (true arithmetic-free inference). A large gap = the DLGN **discretization
gap**, the main thing P2 must close (mitigation: the "Mind the Gap" method, arXiv 2506.07500).

## If it passes / fails

- **PASS →** P2: proper architecture (multi-resolution gate blocks, better t-conditioning,
  close the discretization gap), then P3: CIFAR-10 (3-channel, via bit-planes or a binary latent).
- **FAIL →** diagnose: is it denoising-but-not-generating (sampler/schedule), or not denoising at
  all (capacity/training)? If gates fundamentally can't denoise, pivot to the binary-UNet plan.
