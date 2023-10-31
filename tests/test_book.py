import pytest
from book_feelgood.book import feelgood_activity


@pytest.fixture
def fa_fixture():
    fa = feelgood_activity(
        url="haha.se",
        name="Badminton",
        start="16:00"
    )
    return fa


def test_feelgood_activity_init(fa_fixture):
    assert fa_fixture.url == "haha.se"
