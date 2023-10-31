import argparse
import datetime
from loguru import logger
import requests

from parse import (
    read_yaml,
    parse_day
)

"""
base url for book/unbook:
https://feelgood.wondr.se/w_booking
how to unbook:
    /activities/cancel/<activity_code>/1?force=1
how to book:
    /activities/participate/<activity_code>/?force=1
"""


def initialize_parser() -> dict:
    """
    Needed input arguments for this program
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-usr", "--username",
        help="The username for feelgood login",
        required=True
    )

    parser.add_argument(
        "-pw", "--password",
        help="The password for feelgood login",
        required=True
        )

    parser.add_argument(
        "-act", "--activities_file",
        help="Activities.yml file to use",
        required=False
    )

    parser.add_argument(
        "-tst", "--test",
        nargs='?',
        help="Do a dry run",
        type=bool,
        default=False,
        required=False
    )

    parser.add_argument(
        "-t", "--time",
        help="Add an optional time in place of config",
        required=False,
    )

    parser.add_argument(
        "-n", "--name",
        help="Add optional name in place of config",
        required=False
        )

    parser.add_argument(
        "-d", "--day",
        help="Add optional day in place of config",
        required=False
    )

    parser.add_argument(
        "-do", "--day-offset",
        help="Add optional offset day in place of config",
        required=False
    )

    parser.add_argument(
        "-st", "--start-time",
        help="Optional start time for Boka activities",
        required=False
    )

    parsed = parser.parse_args()

    return vars(parsed)


def log_dict(dictionary: dict, indent: int = 0):
    offset = ""
    for _ in range(0, indent):
        offset = f"{offset}  "
    for key, item in dictionary.items():
        if isinstance(item, dict):
            logger.info(f"{offset}{key}:")
            log_dict(item, indent=indent+1)
        elif isinstance(item, list):
            logger.info(f"{offset}{key}:")
            for i in item:
                log_dict(i, indent=indent+1)
        else:
            logger.info(f"{offset}{key}: {item}")


def get_date(offset: int, verbose=False):
    dt = datetime.date.today()
    new_date = dt - datetime.timedelta(days=-offset)

    if verbose:
        logger.debug("Verbose mode for get_date:")
        logger.debug("Today:")
        logger.debug(f"  Datetime is: {dt}")
        logger.debug(f"  Weekday is: {parse_day(dt.isoweekday())}")
        logger.debug("Offset day:")
        logger.debug(f"  Datetime is: {new_date}")
        logger.debug(f"  Weekday is: {parse_day(new_date.isoweekday())}")

    return new_date


def splash():
    banner = read_yaml("config/banner.yml")
    logger.success(banner["banner"])


def load_config():
    config = read_yaml("config/config.yml")
    return (
        config["settings"],
        config["urls"],
        config["headers"]
    )


class feelgood_activity:
    def __init__(
            self,
            url: str,
            name: str,
            start: str,
            start_time=0

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


def book(
        username: str,
        password: str,
        activities_file: str,
        test: bool,
        time: str,
        start_time: str,
        name: str,
        day: str,
        day_offset: str
):
    splash()
    settings, urls, headers = load_config()

    if test:
        logger.info("---running as test, no booking will be made---")
    activities = None
    if activities_file:
        activities = read_yaml(f"activities/{activities_file}.yml")
        logger.info(
            f"Running using activities from activities/{activities_file}.yml"
        )
    else:
        if (
            name and
            time and
            day
        ):
            test_act = {
                    "name": name,
                    "time": time,
                    "day": day
                }
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

    future_date = get_date(
            offset=int(day_offset),
            verbose=test
        )

    # Check if date_next_week matches any config days
    book_acts = []
    for act in activities["activities"]:
        if future_date.isoweekday() == parse_day(act["day"]):
            logger.info("Activity day matches, will look for:")
            log_dict(act)
            book_acts.append(act)

    if not book_acts:
        logger.success("No activities to book today, bye!")
        exit(0)

    with requests.session() as s:
        get_activities_url = (
            f"{urls['base_url']}{urls['list']}"
        )

        params = {
            "from": future_date,
            "to": future_date,
            "today": 0,
            "mine": 0,
            "only_try_it": 0,
            "facility": settings['facility']
        }

        payload = {
            "User": {
                "email": username,
                "password": password
                }
        }

        s.post(f"{urls['base_url']}", json=payload)
        r = s.get(get_activities_url, params=params, headers=headers)
        feelgood_activities = r.json()

        activities_to_book = [feelgood_activity]

        for act in feelgood_activities["activities"]:
            for book_act in book_acts:
                if (
                        book_act["name"] in act["ActivityType"]["name"] and
                        book_act["time"] in act["Activity"]["start"]
                ):
                    booking_url = (
                        f"{urls['base_url']}"
                        f"{urls['participate']}"
                        f"{act['Activity']['id']}"
                    )

                    fa = feelgood_activity(
                        url=booking_url,
                        name=act["ActivityType"]["name"],
                        start=act["Activity"]["start"],
                    )
                    if "start_time" in book_act:
                        fa.start_time = (book_act["start_time"])
                    logger.info("Found activity matching:")
                    logger.info(f"  {fa.name}")
                    logger.info(f"  {fa.start}")

                    activities_to_book.append(fa)

        if activities_to_book:
            for activity_to_book in activities_to_book:
                params = {
                    "force": 1
                }
                payload = {
                    "ActivityBooking": {
                        "participants": 1,
                        "resources": {}
                    },
                    "send_confirmation": 1
                }
                if "Boka" in activity_to_book().name:
                    logger.info(
                        f"  Start time: {activity_to_book().start_time}"
                    )
                    hour_min_split = activity_to_book().start_time.split(":")
                    epoch = datetime.datetime.combine(
                        future_date,
                        datetime.time(
                            int(hour_min_split[0]),
                            int(hour_min_split[1])
                        )
                        ).timestamp()
                    epoch = int(epoch)
                    payload["ActivityBooking"]["book_start"] = str(epoch)
                    payload["ActivityBooking"]["book_length"] = "30"

                if test:
                    logger.debug("Book act name")
                    logger.debug(activity_to_book().name)
                    logger.debug("Booking url that would be used:")
                    logger.debug(activity_to_book().url)
                    logger.debug("Payload that would be used:")
                    logger.debug(payload)
                else:
                    r = s.post(
                        activity_to_book().url,
                        headers=headers,
                        params=params,
                        json=payload
                    )
                    if (
                        r.status_code == 200 and
                        r.json()["result"] == "ok"
                    ):
                        logger.success(
                            "Successfully booked "
                            f"{activity_toname}"
                        )
                    else:
                        logger.error(
                            "Something went wrong when booking"
                            f" {activity_to_book().name}"
                        )
                        logger.error(f"{r.status_code=}")
                        logger.error(f"{r.text=}")
                        exit(666)
        else:
            logger.warning("No matching activity was found.")


if __name__ == "__main__":
    book(**initialize_parser())
