import pytest
from loguru import logger

from book_feelgood.book import Feelgood_Activity


@pytest.fixture
def caplog(caplog):
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def fa_fixture():
    fa = Feelgood_Activity(url="haha.se", name="Badminton", start="16:00")

    fa.start_time = 123123123123123123
    return fa
