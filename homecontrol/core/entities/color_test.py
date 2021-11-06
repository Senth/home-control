import pytest

from .color import Color


def color(x: float = 0.25, y: float = 0.5, saturation: int = 25, hue: int = 26, temperature: int = 300) -> Color:
    color = Color()
    color.x = x
    color.y = y
    color.saturation = saturation
    color.hue = hue
    color.temperature = temperature
    return color


def test_equality() -> None:
    a = color()
    b = color()

    assert a == b


@pytest.mark.parametrize(
    "c",
    [
        [color(x=0.5)],
        [color(y=0.65)],
        [color(saturation=34)],
        [color(hue=31)],
        [color(temperature=268)],
    ],
)
def test_not_equal(c: Color) -> None:
    default = color()
    assert default != c
