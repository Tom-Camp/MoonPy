from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from moonpy import MoonPhase
from moonpy.phases import PHASE_NAMES, REFERENCE_NEW_MOON, SYNODIC_MONTH


def at_fraction(fraction: float) -> MoonPhase:
    """A MoonPhase at the given fraction of the cycle after the reference new moon."""
    return MoonPhase(REFERENCE_NEW_MOON + timedelta(days=SYNODIC_MONTH * fraction))


class TestAge:
    def test_reference_new_moon_has_zero_age(self):
        assert MoonPhase(REFERENCE_NEW_MOON).age == 0

    def test_age_is_days_since_reference(self):
        assert MoonPhase(REFERENCE_NEW_MOON + timedelta(days=3)).age == pytest.approx(3)

    def test_age_wraps_each_synodic_month(self):
        one = MoonPhase(datetime(2024, 6, 1, tzinfo=UTC))
        later = MoonPhase(one.when + timedelta(days=SYNODIC_MONTH * 12))
        assert later.age == pytest.approx(one.age, abs=1e-6)

    def test_dates_before_reference_give_non_negative_age(self):
        moon = MoonPhase(REFERENCE_NEW_MOON - timedelta(days=1))
        assert moon.age == pytest.approx(SYNODIC_MONTH - 1)

    @pytest.mark.parametrize("year", [1900, 1999, 2000, 2026, 2100])
    def test_age_within_one_cycle(self, year):
        age = MoonPhase(datetime(year, 3, 15, tzinfo=UTC)).age
        assert 0 <= age < SYNODIC_MONTH

    def test_days_since_new_equals_age(self):
        moon = at_fraction(0.3)
        assert moon.days_since_new == moon.age


class TestCycleFractionAndIllumination:
    @pytest.mark.parametrize(
        ("fraction", "illumination"),
        [(0, 0), (0.25, 0.5), (0.5, 1), (0.75, 0.5)],
    )
    def test_illumination_at_quarters(self, fraction, illumination):
        moon = at_fraction(fraction)
        assert moon.cycle_fraction == pytest.approx(fraction, abs=1e-9)
        assert moon.illumination == pytest.approx(illumination, abs=1e-9)

    @pytest.mark.parametrize("fraction", [i / 20 for i in range(20)])
    def test_illumination_bounded(self, fraction):
        assert 0 <= at_fraction(fraction).illumination <= 1

    def test_illumination_symmetric_around_full(self):
        assert at_fraction(0.3).illumination == pytest.approx(
            at_fraction(0.7).illumination
        )


class TestCountdowns:
    def test_days_to_full_at_full_is_zero(self):
        assert at_fraction(0.5).days_to_full == 0

    def test_days_to_full_just_after_full_counts_to_next_cycle(self):
        moon = MoonPhase(at_fraction(0.5).when + timedelta(hours=1))
        assert moon.days_to_full == pytest.approx(SYNODIC_MONTH - 1 / 24, abs=1e-6)

    def test_days_to_full_before_full(self):
        assert at_fraction(0.25).days_to_full == pytest.approx(SYNODIC_MONTH / 4)

    def test_days_to_full_just_before_full(self):
        moon = MoonPhase(at_fraction(0.5).when - timedelta(hours=1))
        assert moon.days_to_full == pytest.approx(1 / 24, abs=1e-6)

    def test_days_to_full_after_full_counts_to_next_cycle(self):
        assert at_fraction(0.75).days_to_full == pytest.approx(SYNODIC_MONTH * 0.75)

    def test_days_to_new_plus_age_is_one_cycle(self):
        moon = at_fraction(0.4)
        assert moon.days_to_new + moon.age == pytest.approx(SYNODIC_MONTH)

    def test_days_to_new_at_new_moon_is_zero(self):
        assert MoonPhase(REFERENCE_NEW_MOON).days_to_new == 0

    def test_days_to_new_just_after_new_counts_to_next_cycle(self):
        moon = MoonPhase(REFERENCE_NEW_MOON + timedelta(hours=1))
        assert moon.days_to_new == pytest.approx(SYNODIC_MONTH - 1 / 24, abs=1e-6)

    def test_days_to_new_just_before_new(self):
        moon = MoonPhase(REFERENCE_NEW_MOON - timedelta(hours=1))
        assert moon.days_to_new == pytest.approx(1 / 24, abs=1e-6)


class TestName:
    @pytest.mark.parametrize(("index", "name"), list(enumerate(PHASE_NAMES)))
    def test_name_at_each_eighth(self, index, name):
        assert at_fraction(index / 8).name == name

    @pytest.mark.parametrize(
        ("fraction", "name"),
        [
            (1 / 16 - 0.001, "New Moon"),
            (1 / 16 + 0.001, "Waxing Crescent"),
            (15 / 16 - 0.001, "Waning Crescent"),
            (15 / 16 + 0.001, "New Moon"),
        ],
    )
    def test_name_rounds_to_nearest_eighth(self, fraction, name):
        assert at_fraction(fraction).name == name

    @pytest.mark.parametrize(
        ("when", "name"),
        [
            (datetime(2024, 1, 25, 17, 54, tzinfo=UTC), "Full Moon"),
            (datetime(2024, 4, 8, 18, 21, tzinfo=UTC), "New Moon"),
            (datetime(2025, 3, 14, 6, 55, tzinfo=UTC), "Full Moon"),
            (datetime(2026, 2, 17, 12, 1, tzinfo=UTC), "New Moon"),
        ],
    )
    def test_known_dates(self, when, name):
        assert MoonPhase(when).name == name


class TestConstruction:
    def test_default_is_now_in_utc(self):
        before = datetime.now(UTC)
        moon = MoonPhase()
        after = datetime.now(UTC)
        assert before <= moon.when <= after
        assert moon.when.tzinfo is not None

    def test_non_utc_timezone_is_equivalent(self):
        when = datetime(2024, 6, 1, 12, tzinfo=UTC)
        eastern = when.astimezone(timezone(timedelta(hours=-5)))
        assert MoonPhase(eastern).age == pytest.approx(MoonPhase(when).age)

    def test_naive_datetime_rejected(self):
        with pytest.raises(TypeError):
            MoonPhase(datetime(2024, 6, 1))

    def test_age_is_not_an_init_argument(self):
        with pytest.raises(TypeError):
            MoonPhase(age=3)  # type: ignore[call-arg]

    def test_is_frozen(self):
        moon = MoonPhase(REFERENCE_NEW_MOON)
        with pytest.raises(FrozenInstanceError):
            moon.age = 5  # type: ignore[misc]

    def test_equal_for_same_instant(self):
        assert MoonPhase(REFERENCE_NEW_MOON) == MoonPhase(REFERENCE_NEW_MOON)
