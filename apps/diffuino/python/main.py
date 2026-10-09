"""Generate a requested MNIST digit and stream denoising frames to UNO Q."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
from PIL import Image

try:
    from .frame import board_bytes, state_to_matrix
    from .runtime import DiffusionSampler
except ImportError:  # App Lab executes python/main.py as a script.
    from frame import board_bytes, state_to_matrix
    from runtime import DiffusionSampler


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--sampler", choices=("ddpm", "ddim"), default="ddpm")
    result.add_argument("--steps", type=int, default=1000, help="DDPM requires 1000; DDIM may use fewer")
    result.add_argument("--seed", type=int, default=11)
    result.add_argument("--threads", type=int, default=4)
    result.add_argument("--frame-every", type=int, default=20)
    result.add_argument("--frame-delay", type=float, default=0.0)
    result.add_argument("--brightness-levels", type=int, default=8)
    result.add_argument("--no-matrix", action="store_true")
    result.add_argument(
        "--model",
        type=Path,
        default=ROOT / "models" / "mnist_unconditional_w1a32.onnx",
    )
    result.add_argument("--output", type=Path, default=ROOT / "output" / "latest.png")
    return result


def save_image(state: np.ndarray, path: Path) -> None:
    pixels = np.clip((state.squeeze() + 1.0) * 127.5, 0, 255).astype(np.uint8)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(pixels, mode="L").save(path)


def run(args: argparse.Namespace) -> None:
    if not args.model.exists():
        raise SystemExit(f"model not found: {args.model}; pull or export it first")
    sampler = DiffusionSampler(args.model, threads=args.threads)
    display_context = None
    if not args.no_matrix:
        try:
            from .display import MatrixDisplay
        except ImportError:
            from display import MatrixDisplay

        display_context = MatrixDisplay()

    emitted = 0
    started = time.perf_counter()

    def generate(display=None):
        nonlocal emitted

        def on_frame(position: int, timestep: int, state: np.ndarray) -> None:
            nonlocal emitted
            frame = state_to_matrix(state, levels=args.brightness_levels)
            if display is not None:
                display.draw(board_bytes(frame))
            emitted += 1
            print(f"frame={emitted:03d} step={position:03d}/{args.steps} t={timestep:03d}")
            if args.frame_delay:
                time.sleep(args.frame_delay)

        return sampler.sample(
            sampling_steps=args.steps,
            seed=args.seed,
            sampler=args.sampler,
            callback=on_frame,
            frame_every=args.frame_every,
        )

    if display_context is None:
        final = generate()
    else:
        with display_context as display:
            final = generate(display)

    elapsed = time.perf_counter() - started
    save_image(final, args.output)
    print(
        f"done seed={args.seed} sampler={args.sampler} steps={args.steps} "
        f"frames={emitted} seconds={elapsed:.3f} output={args.output}"
    )


if __name__ == "__main__":
    run(parser().parse_args())
