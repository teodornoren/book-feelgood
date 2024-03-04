import datetime
import sys
import time

import requests
from loguru import logger

from book_feelgood.parse import (
    get_date,
    load_config,
    log_dict,
    parse_day,
    read_yaml,
    splash,
)


class Feelgood_Activity:
    def __init__(
        self,
        url: str,
        name: str,
        start: str,
        start_time="0",
    ) -> None:
        self._url = url
        self._name = name
        self._start = start
        self._start_time = start_time

    @property
    def url(self):
        return self._url

    @property
    def start(self):
        return self._start

    @property
    def name(self):
        return self._name

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        self._start_time = start_time

    def summary(self) -> str:
        return (
            f"Feelgood_Activity: {self.name}, {self.start}, {self.start_time}"
        )

    def __repr__(self) -> str:
        return (
            f"Feelgood_Activity: {self.name}, "
            f"{self.start}, {self.start_time}, {self.url}"
        )

    def __eq__(self, __value: object) -> bool:
        return bool(str(self) == str(__value))


def book(
    username: str,
    password: str,
    activities_file: str,
    test: bool,
    book_time: str,
    start_time: str,
    name: str,
    day: str,
    day_offset: str,
) -> None:  # pragma: no cover
    """
    Book activities based on provided parameters.

    Args:
        username (str): The username for logging in.
        password (str): The password for logging in.
        activities_file (str): The file containing activity details.
        test (bool): Flag indicating whether to run in test mode.
        book_time (str): The time to book the activity.
        start_time (str): The start time of the activity.
        name (str): The name of the activity.
        day (str): The day of the activity.
        day_offset (str): The offset for the booking day.

    Returns:
        None
    """
    splash()
    logger.remove()
    logger.add(sys.stdout, enqueue=True)
    settings, urls, headers = load_config()
    if activities_file:
        logger.add(f"logs/{activities_file}.log", enqueue=True)

    if test:
        logger.info("---running as test, no booking will be made---")
    activities = None
    if activities_file:
        activities = read_yaml(f"activities/{activities_file}.yml")
        logger.info(f"Using activities/{activities_file}.yml")
    else:
        if name and book_time and day:
            test_act = {"name": name, "time": book_time, "day": day}
            if start_time:
                test_act["start_time"] = start_time
            activities = {}
            activities["activities"] = [test_act]
        else:
            raise ValueError(
                "To run manually you must at least specify: name, time and day"
            )

        logger.info("Manual activity:")
        log_dict(activities)

    if not day_offset:
        day_offset = settings["day_offset"]

    future_date = get_date(day_offset=int(day_offset))
    # Check if date_next_week matches any config days
    yml_acts = _return_matching_activities(activities, future_date)

    if not yml_acts:
        logger.success("No activities to book today, bye!")
        exit(0)

    with requests.session() as s:
        get_activities_url = f"{urls['base_url']}{urls['list']}"

        params = {
            "from": future_date,
            "to": future_date,
            "today": 0,
            "mine": 0,
            "only_try_it": 0,
            "facility": settings["facility"],
        }

        payload = {"User": {"email": username, "password": password}}

        s.post(f"{urls['base_url']}", json=payload)
        r = s.get(get_activities_url, params=params, headers=headers)
        feelgood_activities = r.json()

        activities_to_book = _match_yml_activity_to_remote(
            urls,
            yml_acts,
            feelgood_activities,
        )

        if activities_to_book:
            bookings = _post_bookings(
                test,
                headers,
                future_date,
                s,
                activities_to_book,
            )
            for booking in bookings:
                _parse_booking(booking)
            logger.info(f"Username: {username}")
        else:
            logger.warning("No matching activity was found.")


def _post_bookings(
    test: bool,
    headers: dict,
    future_date: datetime.date,
    s: requests.session,
    activities_to_book: list[Feelgood_Activity],
) -> list[tuple[requests.Response, Feelgood_Activity]]:
    bookings = []
    for activity_to_book in activities_to_book:
        params = {"force": 1}
        payload = {
            "ActivityBooking": {"participants": 1, "resources": {}},
            "send_confirmation": 1,
        }
        if "Boka" in activity_to_book.name:
            epoch = _get_simple_epoch(future_date, activity_to_book.start_time)
            payload["ActivityBooking"]["book_start"] = str(epoch)
            payload["ActivityBooking"]["book_length"] = "30"

        if test:
            logger.debug(activity_to_book.summary())
            logger.debug(f"Payload: {payload}")
        else:
            hour_goal = 8
            minute_goal = 0
            second_goal = 1
            _wait_for_time(hour_goal, minute_goal, second_goal)

            r = s.post(
                activity_to_book.url,
                headers=headers,
                params=params,
                json=payload,
            )
            bookings.append((r, activity_to_book))

    return bookings


def _return_matching_activities(
    activities,
    future_date,
):
    yml_acts = []
    for yml_act in activities["activities"]:
        if future_date.isoweekday() == parse_day(yml_act["day"]):
            logger.debug(
                f"Activity local match: name: "
                f"{yml_act['name']}, day: {yml_act['day']}"
            )
            yml_acts.append(yml_act)

    return yml_acts


def _parse_booking(
    booking: tuple[requests.Response, Feelgood_Activity]
) -> None:
    """
    Parse the response from the booking API and log relevant information.

    Args:
        r (Response): The HTTP response object.
        activity_to_book (str): The activity being booked.

    Returns:
        None
    """
    r, activity_to_book = booking
    json = r.json()
    if r.status_code == 200 and json["result"] == "ok":
        logger.success(f"Successfully booked: {activity_to_book}")

    elif "error_code" in json:
        log_error = ""
        if json["error_code"] == "ACTIVITY_FULL":
            log_error = "Activity is fully booked already:"
        elif json["error_code"] == "ACTIVITY_BOOKING_TO_EARLY":
            log_error = "You are trying to book too soon:"
        elif json["error_code"] == "USER_ALREADY_BOOKED":
            log_error = "You are already booked:"
        else:
            log_error = "Unhandled response from feelgood:\n"
            log_dict(json)
        logger.error(f"{log_error} {activity_to_book}")
    elif "message" in json:
        if json["message"] == "Denna tid är inte tillgänglig längre.":
            logger.error(
                f"Activity is fully booked already: {activity_to_book}"
            )
    else:
        logger.error(f"Something went wrong: {activity_to_book}")
        logger.error(f"{r.status_code=}")
        logger.error(f"{json=}")


def _get_simple_epoch(
    date: datetime.datetime,
    time: str,
) -> int:
    """
    Convert a given date and time string to a Unix epoch timestamp.

    Args:
        date (datetime.datetime): The date for which the time is provided.
        time (str): The time in "HH:MM" format.

    Returns:
        int: The Unix epoch timestamp
            corresponding to the provided date and time.
    """
    hour_min_split = time.split(":")
    epoch = datetime.datetime.combine(
        date=date,
        time=datetime.time(int(hour_min_split[0]), int(hour_min_split[1])),
    ).timestamp()
    epoch = int(epoch)
    return epoch


def _match_yml_activity_to_remote(
    urls: dict,
    yml_acts: list[dict],
    feelgood_activities: list[dict],
) -> list[Feelgood_Activity]:
    """
    Generate a list of Feelgood_Activity objects to be booked based on provided
    YAML activities and feelgood activities.

    Args:
        urls (dict):
            Dictionary containing base and participation URLs.
        yml_acts (list[dict]):
            List of YAML activity dictionaries.
        feelgood_activities (list[dict]):
            List of feelgood activity dictionaries.

    Returns:
        list[Feelgood_Activity]:
            List of Feelgood_Activity objects to be booked.
    """
    act_to_book = []
    for f_act in feelgood_activities["activities"]:
        for yml_act in yml_acts:
            if (
                yml_act["name"] in f_act["ActivityType"]["name"]
                and yml_act["time"] in f_act["Activity"]["start"]
            ):
                booking_url = (
                    f"{urls['base_url']}"
                    f"{urls['participate']}"
                    f"{f_act['Activity']['id']}"
                )

                fa = Feelgood_Activity(
                    url=booking_url,
                    name=f_act["ActivityType"]["name"],
                    start=f_act["Activity"]["start"],
                )

                if "start_time" in yml_act:
                    fa.start_time = yml_act["start_time"]

                logger.debug(f"Activity remote match: {fa.summary()}")
                act_to_book.append(fa)

    return act_to_book


def _wait_for_time(
    hour_goal: int,
    minute_goal: int,
    second_goal: int,
) -> None:
    """
    Wait until reaching a specific time today. If
    the time difference is negative,
    the function does not wait and proceeds immediately.

    Args:
        hour_goal (int): The target hour to wait for.
        minute_goal (int): The target minute within the hour to wait for.
        second_goal (int): The target second within the minute to wait for.
    """
    time_goal = datetime.datetime(
        year=datetime.date.today().year,
        month=datetime.date.today().month,
        day=datetime.date.today().day,
        hour=hour_goal,
        minute=minute_goal,
        second=second_goal,
        microsecond=0,
    )
    diff = time_goal - datetime.datetime.now()
    if diff.total_seconds() > 0.0:
        logger.info(f"Sleeping for: {diff}")
        time.sleep(diff.total_seconds())
        logger.success("Done sleeping")
    else:
        logger.warning("Time difference negative. Booking immediately!")
