"""Shared deterministic aggregate-population curve for public activities."""

from __future__ import annotations

import math


def seeded_unit_pure(seed: int, stream: int) -> float:
    value = (int(seed) ^ (int(stream) * 0x9E3779B9)) & 0xFFFFFFFF
    value = (value * 1_664_525 + 1_013_904_223) & 0xFFFFFFFF
    return value / 0xFFFFFFFF


def _normalized_logistic(phase: float, midpoint: float, steepness: float) -> float:
    phase = max(0.0, min(1.0, float(phase)))

    def sigmoid(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-value))

    start = sigmoid(-steepness * midpoint)
    end = sigmoid(steepness * (1.0 - midpoint))
    current = sigmoid(steepness * (phase - midpoint))
    if end <= start:
        return phase
    return max(0.0, min(1.0, (current - start) / (end - start)))


def naturalized_population_target_bps_pure(
    *,
    phase: float,
    day_phase: float,
    seed: int,
    base_ceiling: float,
) -> int:
    """Return a monotonic aggregate public-population pressure target."""

    phase = max(0.0, min(1.0, float(phase)))
    jitter = (seeded_unit_pure(seed, 4) * 0.2) - 0.1
    natural_phase = max(
        0.0,
        min(1.0, phase + jitter * math.sin(math.pi * phase)),
    )
    midpoint = 0.5 + ((seeded_unit_pure(seed, 2) * 0.2) - 0.1)
    steepness = 8.0 * (0.85 + seeded_unit_pure(seed, 3) * 0.3)
    curve = _normalized_logistic(natural_phase, midpoint, steepness)

    day_envelope = 1.0 + 0.25 * math.sin(
        2.0 * math.pi * (float(day_phase) % 1.0)
    )
    seeded_ceiling = float(base_ceiling) * (
        0.8 + seeded_unit_pure(seed, 1) * 0.4
    )
    ceiling = seeded_ceiling * day_envelope
    return min(10_000, max(0, int(round(curve * ceiling * 10_000))))
