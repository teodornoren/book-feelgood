from datetime import datetime, timedelta

import pytest
from requests.models import Response

from book_feelgood.book import (
    Feelgood_Activity,
    _get_simple_epoch,
    _match_yml_activity_to_remote,
    _parse_response,
    _return_matching_activities,
    _wait_for_time,
)


def test_feelgood_activity_init(fa_fixture):
    assert fa_fixture.url == "haha.se"
    assert fa_fixture.name == "Badminton"
    assert fa_fixture.start == "16:00"
    assert fa_fixture.start_time == 123123123123123123


@pytest.fixture
def future_date_fixture_1():
    return datetime(year=2024, month=3, day=10).date()


@pytest.fixture
def future_date_fixture_2():
    return datetime(year=2024, month=3, day=12).date()


@pytest.fixture
def activities_fixture():
    return {
        "activities": [
            {
                "name": "Boka",
                "time": "13:30",
                "day": "Monday",
                "start_time": "14:30",
            },
            {
                "name": "Boka",
                "time": "13:30",
                "day": "Monday",
                "start_time": "15:00",
            },
            {
                "name": "Boka",
                "time": "13:30",
                "day": "Monday",
                "start_time": "15:30",
            },
            {"name": "Badminton", "time": "15:00", "day": "Wednesday"},
            {"name": "Spinning", "time": "15:00", "day": "Friday"},
            {
                "name": "Boka",
                "time": "09:00",
                "day": "Sunday",
                "start_time": "09:00",
            },
            {
                "name": "Boka",
                "time": "09:00",
                "day": "Sunday",
                "start_time": "09:30",
            },
        ]
    }


@pytest.fixture
def matching_activity_fixture_1():
    return [
        {
            "day": "Sunday",
            "name": "Boka",
            "start_time": "09:00",
            "time": "09:00",
        },
        {
            "day": "Sunday",
            "name": "Boka",
            "start_time": "09:30",
            "time": "09:00",
        },
    ]


@pytest.fixture
def matching_activity_fixture_2():
    return []


@pytest.mark.parametrize(
    "activities, future_date, expected",
    [
        (
            "activities_fixture",
            "future_date_fixture_1",
            "matching_activity_fixture_1",
        ),
        (
            "activities_fixture",
            "future_date_fixture_2",
            "matching_activity_fixture_2",
        ),
    ],
)
def test_return_matching_activities(
    activities,
    future_date,
    expected,
    request,
):
    yml_acts = _return_matching_activities(
        request.getfixturevalue(activities),
        request.getfixturevalue(future_date),
    )
    assert yml_acts == request.getfixturevalue(expected)


def test_parse_response_success(caplog, fa_fixture):
    r = Response()
    r.status_code = 200
    r._content = b'{"result": "ok"}'
    _parse_response(r, fa_fixture)
    assert (
        "Successfully booked: Feelgood_Activity: "
        "Badminton, 16:00, 123123123123123123, haha.se" in caplog.text
    )


@pytest.mark.parametrize(
    "error_code, log_response",
    [
        (
            "ACTIVITY_FULL",
            "Activity is fully booked already:",
        ),
        (
            "ACTIVITY_BOOKING_TO_EARLY",
            "You are trying to book too soon:",
        ),
        ("USER_ALREADY_BOOKED", "You are already booked:"),
    ],
)
def test_parse_response_activity_errors(
    caplog,
    fa_fixture,
    error_code,
    log_response,
):
    r = Response()
    content = f'"error_code": "{error_code}"'
    r._content = bytes(f"{{{content}}}", "utf-8")
    _parse_response(r, fa_fixture)
    assert (
        f"{log_response} Feelgood_Activity: "
        "Badminton, 16:00, 123123123123123123, haha.se" in caplog.text
    )


def test_parse_response_unhandled_error(caplog, fa_fixture):
    r = Response()
    r._content = b'{"error_code": "OH_SHIT"}'
    _parse_response(r, fa_fixture)
    assert "Unhandled response from feelgood:" in caplog.text
    assert "OH_SHIT" in caplog.text


def test_parse_response_message_this_time_etc(caplog, fa_fixture):
    r = Response()
    r._content = bytes(
        '{"message": "Denna tid är inte tillgänglig längre."}', "utf-8"
    )
    _parse_response(r, fa_fixture)
    assert (
        "Activity is fully booked already: Feelgood_Activity: " in caplog.text
    )
    assert "Badminton, 16:00, 123123123123123123, haha.se" in caplog.text


def test_parse_response_unknown(caplog, fa_fixture):
    r = Response()
    r.status_code = 666
    r._content = b'{"manamana": "duuuduuu dudu"}'
    _parse_response(r, fa_fixture)
    assert (
        "Feelgood_Activity: "
        "Badminton, 16:00, 123123123123123123, haha.se" in caplog.text
    )
    assert "r.status_code=666" in caplog.text
    assert "{'manamana': 'duuuduuu dudu'}" in caplog.text


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
    result = _match_yml_activity_to_remote(urls, yml_acts, feelgood_activities)
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


def test_get_simple_epoch():
    now = datetime.today().replace(second=0, microsecond=0)
    epoch = _get_simple_epoch(
        now.date(), now.time().isoformat(timespec="minutes")
    )
    assert epoch == int(now.timestamp())


def test_wait_for_time_positive():
    now = datetime.now()
    now = now.replace(microsecond=0)
    future = now + timedelta(seconds=2)
    _wait_for_time(future.hour, future.minute, future.second)
    assert datetime.now().replace(microsecond=0) == future


def test_wait_for_time_negative(caplog):
    now = datetime.now()
    now = now.replace(microsecond=0)
    past = now + timedelta(seconds=-1)
    _wait_for_time(past.hour, past.minute, past.second)
    assert "Time difference negative. Booking immediately!" in caplog.text
