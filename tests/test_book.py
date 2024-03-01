import pytest
from book_feelgood.book import Feelgood_Activity


@pytest.fixture
def fa_fixture():
    fa = Feelgood_Activity(
        url="haha.se",
        name="Badminton",
        start="16:00",
        start_time=123123123123123123,
    )
    return fa


def test_feelgood_activity_init(fa_fixture):
    assert fa_fixture.url == "haha.se"
    assert fa_fixture.name == "Badminton"
    assert fa_fixture.start == "16:00"
    assert fa_fixture.start_time == 123123123123123123
