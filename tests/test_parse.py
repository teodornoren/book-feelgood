import pytest

from book_feelgood.parse import (
    parse_day,
    splash,
    load_config,
    read_yaml,
    # initialize_parser,
)


def test_parse_day_all():
    # Test int to string
    assert parse_day(1) == "Monday"
    assert parse_day(2) == "Tuesday"
    assert parse_day(3) == "Wednesday"
    assert parse_day(4) == "Thursday"
    assert parse_day(5) == "Friday"
    assert parse_day(6) == "Saturday"
    assert parse_day(7) == "Sunday"
    # Test string to int
    assert parse_day("Monday") == 1
    assert parse_day("Tuesday") == 2
    assert parse_day("Wednesday") == 3
    assert parse_day("Thursday") == 4
    assert parse_day("Friday") == 5
    assert parse_day("Saturday") == 6
    assert parse_day("Sunday") == 7


def test_parse_day_str_value_error():
    random_text = "Blabal"
    # parse_days turns all input into lower()
    random_text = random_text.lower()
    with pytest.raises(
        ValueError, match=f"Could not parse input as a day: str: {random_text}"
    ):
        parse_day(random_text.lower())


def test_parse_day_int_value_error():
    random_number = 77
    with pytest.raises(
        ValueError,
        match=f"Could not parse input as a day: int: {random_number}",
    ):
        parse_day(random_number)


def test_splash():
    splash()


def test_load_config():
    settings, urls, config = load_config()
    assert bool(settings) is True
    assert bool(urls) is True
    assert bool(config) is True


def test_load_unexisting_yml():
    with pytest.raises(Exception):
        read_yaml("config/dummy.yml")


# def test_initialize_parser_help(capsys):
#     try:
#         initialize_parser()
#     except SystemExit:
#         pass
#     output = capsys.readouterr().out
#     print(output)
#     assert "-usr USERNAME -pw PASSWORD" in output
