import pytest

from source.parse import parse_day


def test_parse_days():
    # Test int to string
    assert parse_day(1) == 'Monday'
    assert parse_day(2) == 'Tuesday'
    assert parse_day(3) == 'Wednesday'
    assert parse_day(4) == 'Thursday'
    assert parse_day(5) == 'Friday'
    assert parse_day(6) == 'Saturday'
    assert parse_day(7) == 'Sunday'
    # Test string to int
    assert parse_day('Monday') == 1
    assert parse_day('Tuesday') == 2
    assert parse_day('Wednesday') == 3
    assert parse_day('Thursday') == 4
    assert parse_day('Friday') == 5
    assert parse_day('Saturday') == 6
    assert parse_day('Sunday') == 7
    random_text = 'Blabal'
    # parse_days turns all input into lower()
    random_text = random_text.lower()
    with pytest.raises(
        ValueError,
        match=f"Could not parse input as a day: str: {random_text}"
    ):
        assert parse_day(random_text.lower()) == ValueError
