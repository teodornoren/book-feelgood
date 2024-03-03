import pytest
from datetime import datetime, timedelta
from book_feelgood.book import (
    Feelgood_Activity,
    _wait_for_time,
    # _activities_to_book,
)


@pytest.fixture
def fa_fixture():
    fa = Feelgood_Activity(url="haha.se", name="Badminton", start="16:00")

    fa.start_time = 123123123123123123
    return fa


def test_feelgood_activity_init(fa_fixture):
    assert fa_fixture.url == "haha.se"
    assert fa_fixture.name == "Badminton"
    assert fa_fixture.start == "16:00"
    assert fa_fixture.start_time == 123123123123123123


def test_activities_to_book():
    # urls = {}
    # yml_acts = {}
    # feelgood_activities = {}
    pass


def test_wait_for_time_positive():
    now = datetime.now()
    now = now.replace(microsecond=0)
    future = now + timedelta(seconds=2)
    _wait_for_time(future.hour, future.minute, future.second)
    assert datetime.now().replace(microsecond=0) == future


def test_wait_for_time_negative():
    now = datetime.now()
    now = now.replace(microsecond=0)
    _wait_for_time(now.hour, now.minute, now.second - 1)
