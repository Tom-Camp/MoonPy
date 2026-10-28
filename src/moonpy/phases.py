import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Final

PHASE_NAMES: Final = (
    "New Moon",
    "Waxing Crescent",
    "First Quarter",
    "Waxing Gibbous",
    "Full Moon",
    "Waning Gibbous",
    "Third Quarter",
    "Waning Crescent",
)
SYNODIC_MONTH: Final = 29.530588853
REFERENCE_NEW_MOON: Final = datetime(2000, 1, 6, 18, 14, tzinfo=UTC)
# Countdowns within this many days (one second) after an event snap to 0, so
# floating-point error at the exact instant doesn't report a full cycle.
PHASE_TOLERANCE: Final = 1 / 86400


@dataclass(frozen=True)
class MoonPhase:
    """
    Calculate the phase of the moon for now or a given datetime.
    :param when: Timezone-aware datetime to calculate the phase for. Defaults to now.
    :raises TypeError: If ``when`` is naive.
    """

    when: datetime = field(default_factory=lambda: datetime.now(UTC))
    age: float = field(init=False)
    """Days since the last new moon, in ``[0, SYNODIC_MONTH)``."""

    def __post_init__(self) -> None:
        if self.when.utcoffset() is None:
            raise TypeError("when must be a timezone-aware datetime")
        elapsed_days = (self.when - REFERENCE_NEW_MOON).total_seconds() / 86400
        object.__setattr__(self, "age", elapsed_days % SYNODIC_MONTH)

    @property
    def cycle_fraction(self) -> float:
        """Position in the cycle: 0.0 = new, 0.5 = full."""
        return self.age / SYNODIC_MONTH

    @property
    def illumination(self) -> float:
        """Fraction of the visible disc that is lit, from 0 to 1."""
        return (1 - math.cos(2 * math.pi * self.cycle_fraction)) / 2

    @property
    def days_since_new(self) -> float:
        """Alias for ``age``."""
        return self.age

    @property
    def days_to_full(self) -> float:
        """Days until the next full moon; 0 at full moon."""
        days = (SYNODIC_MONTH / 2 - self.age) % SYNODIC_MONTH
        return 0.0 if days > SYNODIC_MONTH - PHASE_TOLERANCE else days

    @property
    def days_to_new(self) -> float:
        """Days until the next new moon; 0 at new moon."""
        days = SYNODIC_MONTH - self.age
        return 0.0 if days > SYNODIC_MONTH - PHASE_TOLERANCE else days

    @property
    def name(self) -> str:
        """The nearest of the eight ``PHASE_NAMES``."""
        return PHASE_NAMES[int(self.cycle_fraction * 8 + 0.5) % 8]
