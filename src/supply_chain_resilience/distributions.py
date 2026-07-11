from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.random import Generator


class DistType(str, Enum):
    UNIFORM = "uniform"
    TRIANGULAR = "triangular"
    NORMAL_TRUNC = "normal_trunc"
    PERT = "pert"
    LOGNORMAL = "lognormal"


@dataclass(frozen=True)
class Distribution:
    kind: DistType = DistType.UNIFORM
    minimum: float = 0.0
    maximum: float = 0.5
    mode: float | None = None
    mean: float = 0.25
    scale: float = 0.12
    sigma: float = 0.8

    def validate(self) -> None:
        if self.maximum <= self.minimum:
            raise ValueError("maximum must be greater than minimum")
        if self.scale <= 0 or self.sigma <= 0:
            raise ValueError("scale and sigma must be positive")
        if self.mode is not None and not self.minimum <= self.mode <= self.maximum:
            raise ValueError("mode must be within distribution bounds")


def sample(rng: Generator, size: int, distribution: Distribution) -> np.ndarray:
    if size <= 0:
        raise ValueError("size must be positive")
    distribution.validate()
    lo, hi = distribution.minimum, distribution.maximum
    if distribution.kind == DistType.UNIFORM:
        values = rng.uniform(lo, hi, size=size)
    elif distribution.kind == DistType.TRIANGULAR:
        mode = distribution.mode if distribution.mode is not None else (lo + hi) / 2
        values = rng.triangular(lo, mode, hi, size=size)
    elif distribution.kind == DistType.NORMAL_TRUNC:
        values = np.clip(rng.normal(distribution.mean, distribution.scale, size=size), lo, hi)
    elif distribution.kind == DistType.PERT:
        mode = distribution.mode if distribution.mode is not None else distribution.mean
        alpha = 1 + 4 * (mode - lo) / (hi - lo)
        beta = 1 + 4 * (hi - mode) / (hi - lo)
        values = lo + rng.beta(alpha, beta, size=size) * (hi - lo)
    elif distribution.kind == DistType.LOGNORMAL:
        raw = rng.lognormal(mean=distribution.mean, sigma=distribution.sigma, size=size)
        values = np.clip(raw, lo, hi)
    else:  # pragma: no cover
        raise ValueError(f"unsupported distribution: {distribution.kind}")
    return values.astype(float)
