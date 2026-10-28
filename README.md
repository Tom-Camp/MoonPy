# 🌝 MoonPy 🌚

A library for calculating the phases of the moon.

MoonPy has no runtime dependencies and requires Python 3.14 or later.

## Usage

```python
from datetime import UTC, datetime

from moonpy import MoonPy

moon = MoonPy()  # now
moon = MoonPy(datetime(2024, 1, 25, 17, 54, tzinfo=UTC))

moon.name  # 'Full Moon'
moon.illumination  # 0.999 (0 = dark, 1 = fully lit)
moon.age  # 14.40 days since the last new moon
moon.cycle_fraction  # 0.488 (0 = new, 0.5 = full)
moon.days_to_full  # 0.36
moon.days_to_new  # 15.13
```

The datetime must be timezone-aware; a naive datetime raises `TypeError`. Any timezone works, and `MoonPy()` with no
argument uses the current UTC time. `MoonPy` instances are immutable.

| Attribute        | Description                                                                            |
|------------------|----------------------------------------------------------------------------------------|
| `when`           | The datetime the phase was calculated for                                              |
| `age`            | Days since the last new moon, from 0 up to one synodic month (about 29.53 days)        |
| `days_since_new` | Same as `age`                                                                          |
| `cycle_fraction` | Position in the cycle: 0 = new, 0.25 = first quarter, 0.5 = full, 0.75 = third quarter |
| `illumination`   | Fraction of the visible disc that is lit, from 0 to 1                                  |
| `days_to_full`   | Days until the next full moon; 0 at full moon                                          |
| `days_to_new`    | Days until the next new moon; 0 at new moon                                            |
| `name`           | One of the eight phase names below                                                     |

`name` rounds the cycle to the nearest eighth: 🌑 New Moon, 🌒 Waxing Crescent, 🌓 First Quarter, 🌔 Waxing Gibbous, 🌕
Full Moon, 🌖 Waning Gibbous, 🌗 Third Quarter, 🌘 Waning Crescent.

## Accuracy

MoonPy uses the mean length of a lunar month (29.530588853 days) counted from a known new moon on 2000-01-06 18:14 UTC.
It is not an astronomical ephemeris: the real moon's orbit speeds up and slows down, so actual new and full moons can
fall up to about 14 hours from the times predicted here. That is accurate enough for phase names and illumination, but
not for exact event times. In the example above, the real full moon was at 17:54 UTC, while MoonPy places it about 9
hours later.

## Development

The project is managed with [uv](https://docs.astral.sh/uv/).

```sh
uv sync                     # install the package and dev tools
uv run pytest               # run the tests
uv run pytest --cov=moonpy  # with coverage
uv run mypy src             # type check
uv run ruff check --fix     # lint
uv run ruff format          # format
```

Git hooks run through [prek](https://github.com/j178/prek): `prek install`, then `prek run --all-files` to run them all.

## License

MIT. See [LICENSE](LICENSE).
