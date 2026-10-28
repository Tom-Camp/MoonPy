from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime

PHASE_NAMES: list = [
    "New Moon",
    "Waxing Crescent",
    "First Quarter",
    "Waxing Gibbous",
    "Full Moon",
    "Waning Gibbous",
    "Third Quarter",
    "Waning Crescent",
]
SYNODIC_MONTH: float = 29.530588853
REFERENCE_NEW_MOON: datetime = datetime(2000, 1, 6, 18, 14, tzinfo=UTC)
PHASE_TOLERANCE: float = 1 / 86400


@dataclass(frozen=True)
class MoonPy:
    """
    Calculate the phase of the moon for today or a given date.
    :param when: Date to calculate phase for.
    :param age: Age of the moon.
    """

    when: datetime = field(default_factory=lambda: datetime.now(UTC))
    age: float = field(init=False)

    def __post_init__(self):
        elapsed_days = (self.when - REFERENCE_NEW_MOON).total_seconds() / 86400
        object.__setattr__(self, "when", self.when)
        object.__setattr__(self, "age", elapsed_days % SYNODIC_MONTH)

    @property
    def cycle_fraction(self) -> float:
        """0.0 = new, 0.5 = full."""
        return self.age / SYNODIC_MONTH

    @property
    def illumination(self) -> float:
        return (1 - math.cos(2 * math.pi * self.cycle_fraction)) / 2

    @property
    def days_since_new(self) -> float:
        return self.age

    @property
    def days_to_full(self) -> float:
        days = (SYNODIC_MONTH / 2 - self.age) % SYNODIC_MONTH
        return 0.0 if days > SYNODIC_MONTH - PHASE_TOLERANCE else days

    @property
    def days_to_new(self) -> float:
        days = SYNODIC_MONTH - self.age
        return 0.0 if days > SYNODIC_MONTH - PHASE_TOLERANCE else days

    @property
    def name(self) -> str:
        return PHASE_NAMES[int(self.cycle_fraction * 8 + 0.5) % 8]
