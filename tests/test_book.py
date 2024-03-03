import pytest
from datetime import datetime, timedelta
from book_feelgood.book import (
    Feelgood_Activity,
    _wait_for_time,
    _activities_to_book,
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
    urls = {
        "base_url": "https://dummy.com/",
        "home": "users/start",
        "schema": "schema",
        "participate": "w_booking/activities/participate/",
        "list": "w_booking/activities/list",
    }
    yml_acts = [
        {
            "name": "Boka",
            "time": "09:00",
            "day": "Saturday",
            "start_time": "09:00",
        },
        {
            "name": "Boka",
            "time": "09:00",
            "day": "Saturday",
            "start_time": "09:30",
        },
    ]
    feelgood_activities = {
        "activities": [
            {
                "ActivityType": {
                    "name": "Boka sporthallen 30min",
                    "bookable_times": True,
                    "bookable_time_every": "30",
                    "bookable_lengths": "30",
                    "bookable_simultaneously": False,
                    "bookable_block_user_times": False,
                    "use_bookable_time_every_start": False,
                    "booking_try_it_text": "",
                    "late_book_minutes": "30",
                    "late_unbook_minutes": "5",
                    "days_in_future_book": "6",
                    "multiple_participants": False,
                    "using_resources": False,
                    "booking_many_try_it": False,
                    "modified": "2023-01-02 15:52:20",
                    "bookings_visible_public": False,
                    "question_active": False,
                    "question_mandatory": False,
                    "question_label": None,
                    "use_parent_type_resource": False,
                    "id": "618a65cd-4144-4ddc-85fa-002c0a10050f",
                    "has_sub_types": "0",
                },
                "Activity": {
                    "id": "cool_id",
                    "start": "2024-03-09 09:00:00",
                },
            }
        ],
    }
    result = _activities_to_book(urls, yml_acts, feelgood_activities)
    expected_url = (
        "https://dummy.com/w_booking/activities/" "participate/cool_id"
    )
    expected_name = "Boka sporthallen 30min"
    expected_start = "2024-03-09 09:00:00"
    expected_start_time = "09:00"
    expected_fa_1 = Feelgood_Activity(
        expected_url, expected_name, expected_start, expected_start_time
    )

    assert result[0] == expected_fa_1


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
