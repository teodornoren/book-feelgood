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


def print_dict(dictionary: dict, indent: int = 0):
    offset = ""
    for _ in range(0, indent):
        offset = f"{offset}  "
    for key, item in dictionary.items():
        if isinstance(item, dict):
            logger.info(f"{offset}{key}:")
            print_dict(item, indent=indent+1)
        elif isinstance(item, list):
            logger.info(f"{offset}{key}:")
            for i in item:
                print_dict(i, indent=indent+1)
        else:
            logger.info(f"{offset}{key}: {item}")


def get_date(offset: int, verbose=False):
    dt = datetime.date.today()
    new_date = dt - datetime.timedelta(days=-offset)

    if verbose:
        logger.debug(
            "Verbose mode for get_date:\n"
            "Today:\n"
            f"  Datetime is: {dt}\n"
            f"  Weekday is: {parse_day(dt.isoweekday())}\n"
            "Offset day:\n"
            f"  Datetime is: {new_date}\n"
            f"  Weekday is: {parse_day(new_date.isoweekday())}\n"
        )

    return new_date


def splash():
    banner = read_yaml("config/banner.yml")
    logger.critical(banner["banner"])


def load_config():
    config = read_yaml("config/config.yml")
    return (
        config["settings"],
        config["urls"],
        config["headers"]
    )


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
        print_dict(activities)

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
            print_dict(act)
            book_acts.append(act)

    if not book_acts:
        logger.info("No activities to book today, bye!")
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

        booking_urls = []
        s.post(f"{urls['base_url']}", json=payload)

        r = s.get(get_activities_url, params=params, headers=headers)

        activity_dict = r.json()
        for act in activity_dict["activities"]:
            for book_act in book_acts:
                if (
                        book_act["name"] in act["ActivityType"]["name"] and
                        book_act["time"] in act["Activity"]["start"]
                ):
                    logger.info("Found activity matching:")
                    logger.info(f"  {act['ActivityType']['name']}")
                    logger.info(f"  {act['Activity']['start']}")

                    booking_url = (
                        f"{urls['base_url']}"
                        f"{urls['participate']}"
                        f"{act['Activity']['id']}"
                    )
                    booking_urls.append(booking_url)
        if booking_urls:
            for burl in booking_urls:
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
                if book_act["name"] == "Boka":
                    logger.info(f"  Start time: {book_act['start_time']}")
                    hour_min_split = book_act["start_time"].split(":")
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
                    logger.debug(book_act["name"])
                    logger.debug("Booking url that would be used:")
                    logger.debug(burl)
                    logger.debug("Payload that would be used:")
                    logger.debug(payload)
                else:
                    r = s.post(
                        burl,
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
                            f"{act['ActivityType']['name']}"
                        )
                    else:
                        logger.error(
                            "Something went wrong when booking"
                            f" {book_act['name']}"
                        )
                        logger.error(f"{r.status_code=}")
                        logger.error(f"{r.text=}")
                        exit(666)
        else:
            logger.info("No matching activity was found.")


if __name__ == "__main__":
    book(**initialize_parser())
