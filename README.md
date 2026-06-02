<h1 align="center">MonoDiffuse</h1>

<p align="center">
  <b>How far can a 1-bit neural network go at making pictures?</b>
</p>

<p align="center">
  <img src="results/comparison_grid.png" width="640" alt="1-bit vs 16-bit comparison"/><br/>
  <em>Phase 0 — Top: full-precision model · Bottom: 1-bit model. The shapes survive.</em>
</p>

---

## What this is

Most AI image generators run on big, high-precision numbers. MonoDiffuse asks the opposite
question: **what happens if you shrink the network down to a single bit?**

We're pushing a 1-bit model — the smallest a network can possibly get — to its physical limit as
an image generator that paints a picture out of pure random noise. It's a research project, built
in two phases:

| Phase | The question | Status |
|------|--------------|--------|
| **Phase 0** | Can a 1-bit model learn the *shape* of real images without falling apart? | ✅ Done |
| **Phase 1 — MonoDiffuse** | Take it all the way: a fully 1-bit, color-image generator that's fast to run. | 🚧 In progress |

---

## What we found so far (Phase 0)

We compared a normal full-precision generator against a 1-bit version on handwritten digits.
The short version: **the tiny model gives up beauty, but keeps the meaning.**

- **It doesn't just memorize.** The 1-bit model copies *less* from its training data — being small
  actually keeps it honest.
- **It keeps the variety.** No collapse into repeating the same few images.
- **It loses fine texture.** Results look more like clean stencils than photographs.
- **But it stays readable.** People (and a classifier) can still tell exactly what each image is —
  almost as easily as with the full-precision model.

There's also a fun quirk in how the two models "morph" one image into another: the big model
*cross-fades* shapes, while the 1-bit model *bends and curls* them like reshaping a solid object.

---

## Where it's going (Phase 1 · MonoDiffuse)

Phase 1 takes the idea to its extreme and aims for **color** images, with three goals:

1. **Make everything 1-bit**, not just part of the network.
2. **Start from pure random noise** and let the model build a real picture out of it.
3. **Keep it fast** — a lightweight "compressor" (a VAE) lets the model run quickly.

The bet: each piece of this has been tried separately before, but never all together. If it works,
it's one of the smallest image generators ever built — and a clear answer to *how far you can push
a single bit.*


---

## Try it

```bash
pip install -r requirements.txt

# Reproduce the Phase 0 benchmark (trains both models, scores them)
python experiments/v0_mnist/rigorous_bench_trainer.py

# Generate samples from a saved model
python checkpoints/model_tester.py
```

Phase 1 lives in the `monodiffuse/` package and is under active construction.

---

## Credits

- **Phase 0 (1-bit diffusion study)** — original work by [**@nihal-gazi**](https://github.com/nihal-gazi).
- **Phase 1 (MonoDiffuse)** — ongoing research building on that foundation.

## License

[MIT](LICENSE) — free for academic and commercial use with attribution.
