"""DDPM training objective and deterministic DDIM evaluation sampler."""

from __future__ import annotations

import torch
from torch.nn import functional as F


class Diffusion:
    def __init__(self, steps: int = 1000, beta_start: float = 1e-4, beta_end: float = 0.02):
        self.steps = steps
        self.betas = torch.linspace(beta_start, beta_end, steps, dtype=torch.float32)
        self.alphas = 1.0 - self.betas
        self.alpha_bars = torch.cumprod(self.alphas, dim=0)

    def to(self, device: torch.device | str) -> "Diffusion":
        self.betas = self.betas.to(device)
        self.alphas = self.alphas.to(device)
        self.alpha_bars = self.alpha_bars.to(device)
        return self

    def training_loss(self, model, clean: torch.Tensor) -> torch.Tensor:
        t = torch.randint(0, self.steps, (clean.shape[0],), device=clean.device)
        noise = torch.randn_like(clean)
        alpha_bar = self.alpha_bars[t][:, None, None, None]
        noisy = alpha_bar.sqrt() * clean + (1 - alpha_bar).sqrt() * noise
        return F.mse_loss(model(noisy, t), noise)

    @torch.inference_mode()
    def sample(self, model, shape: tuple[int, ...], sampling_steps: int, generator=None) -> torch.Tensor:
        """Deterministic DDIM (eta=0), enabling paired noise across variants."""
        device = next(model.parameters()).device
        x = torch.randn(shape, device=device, generator=generator)
        schedule = torch.linspace(self.steps - 1, 0, sampling_steps, device=device).long()
        for index, t_value in enumerate(schedule):
            t = torch.full((shape[0],), int(t_value), device=device, dtype=torch.long)
            alpha_bar = self.alpha_bars[t_value]
            predicted_noise = model(x, t)
            predicted_clean = (x - (1 - alpha_bar).sqrt() * predicted_noise) / alpha_bar.sqrt()
            predicted_clean = predicted_clean.clamp(-1, 1)
            if index == len(schedule) - 1:
                x = predicted_clean
            else:
                next_alpha_bar = self.alpha_bars[schedule[index + 1]]
                x = next_alpha_bar.sqrt() * predicted_clean + (1 - next_alpha_bar).sqrt() * predicted_noise
        return x.clamp(-1, 1)
