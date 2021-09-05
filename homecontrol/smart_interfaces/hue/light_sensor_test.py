import pytest

from .light_sensor import LightLevels, LightSensor


def light_sensor(name: LightLevels, level: int) -> LightSensor:
    ls = LightSensor(0, False)
    ls.level_name = name
    ls.light_level = level
    return ls


threshold = LightSensor._threshold


@pytest.mark.parametrize(
    "name, sensor, expected",
    [
        (
            "Should keep same level if not over threshold",
            light_sensor(LightLevels.fully_dark, LightLevels.fully_dark.value.max + threshold),
            LightLevels.fully_dark,
        ),
        (
            "Should change level if over threshold",
            light_sensor(LightLevels.fully_dark, LightLevels.fully_dark.value.max + threshold + 1),
            LightLevels.dark,
        ),
        (
            "Should keep same level if not below threshold",
            light_sensor(LightLevels.partially_light, LightLevels.partially_dark.value.max - threshold),
            LightLevels.partially_light,
        ),
        (
            "Should keep same level if not below threshold",
            light_sensor(LightLevels.partially_light, LightLevels.partially_dark.value.max - threshold - 1),
            LightLevels.partially_dark,
        ),
    ],
)
def test_update_light_level(name: str, sensor: LightSensor, expected: LightLevels):
    print(name)
    sensor.update_light_level()
    assert expected == sensor.level_name
