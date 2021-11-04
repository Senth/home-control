import pytest
from mockito import ANY, spy2, unstub, verify
from tealprint import TealPrint

from .controller import _diff


@pytest.mark.parametrize(
    "name,start,end,percentage,expected",
    [
        ("should be start when at 0 percent", 10, 50, 0, 10.0),
        ("should be at end when at 100 percent", 10, 50, 1, 50.0),
        ("should be halfway when at 50 percent", 10, 20, 0.5, 15.0),
    ],
)
def test_diff(name, start, end, percentage, expected):
    print(name)

    actual = _diff(start, end, percentage)
    assert expected == actual


@pytest.mark.parametrize(
    "name,percentage",
    [
        ("lower out of bounds", -0.01),
        ("upper out of bounds", 1.01),
    ],
)
def test_diff_when_out_of_bounds(name, percentage):
    print(name)
    start = 1

    spy2(TealPrint.error)

    actual = _diff(start, 2, percentage)
    assert start == actual

    verify(TealPrint).error(ANY)
    unstub()
