import argparse
import datetime

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

    Returns:
        Dictionary containing parmeters
            username(string),
            password(string),
            test(bool),
            time(str)
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
        "-act", "--activities",
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

    parsed = parser.parse_args()
    input_vars = {
        "username": parsed.username,
        "password": parsed.password,
        "test": parsed.test,
        "activities": f"activities/{parsed.activities}.yml"
    }

    if parsed.time and parsed.name and parsed.day:
        input_vars["time"] = parsed.time
        input_vars["name"] = parsed.name
        input_vars["day"] = parsed.day
    elif not parsed.time and not parsed.name and not parsed.day:
        pass
    else:
        raise parser.error(
            "Need to specify input name, time and day"
            )

    input_censor = input_vars
    if input_vars["test"]:
        input_censor["password"] = "**********"
        print_dict(input_censor)

    return input_vars


def print_dict(dictionary: dict, indent: int = 0):
    offset = ""
    for _ in range(0, indent):
        offset = f"{offset}  "
    for key, item in dictionary.items():
        if isinstance(item, dict):
            print(f"{offset}{key}:")
            print_dict(item, indent=indent+1)
        elif isinstance(item, list):
            print(f"{offset}{key}:")
            for i in item:
                print_dict(i, indent=indent+1)
        else:
            print(f"{offset}{key}: {item}")


def get_date(offset: int, verbose=False):
    dt = datetime.date.today()
    new_date = dt - datetime.timedelta(days=-offset)

    if verbose:
        print(
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
    print(banner["banner"])


def main():
    """get parser args"""

    splash()

    config = read_yaml("config/config.yml")
    urls = config["urls"]
    input_vars = initialize_parser()
    activities = read_yaml(input_vars["activities"])
    headers = config["headers"]

    if (input_vars["test"]):
        print("---running as test, no booking will be made---")
        print("config loaded:")
        print_dict(config)

    if ("time" in input_vars):
        print("Overriding activities...")
        override_activities = [{
                "name": input_vars["name"],
                "time": input_vars["time"],
                "day": input_vars["day"]
            }]

        activities["activities"] = override_activities
    date_next_week = get_date(
            offset=activities["day_offset"],
            verbose=input_vars["test"]
        )

    # Check if date_next_week matches any config days
    book_acts = []
    for act in activities["activities"]:
        if date_next_week.isoweekday() == parse_day(act["day"]):
            print("Activity day matches, will book for:")
            print_dict(act)
            book_acts.append(act)

    if not book_acts:
        print("No activities to book today, bye!")
        exit(0)

    with requests.session() as s:
        get_activities_url = (
            f"{urls['base_url']}{urls['list']}"
        )

        params = {
            "from": date_next_week,
            "to": date_next_week,
            "today": 0,
            "mine": 0,
            "only_try_it": 0,
            "facility": activities['facility']
        }

        payload = {
            "User": {
                "email": input_vars["username"],
                "password": input_vars["password"]
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
                    print(
                            "Found activity matching:\n"
                            f"  Name: {book_act['name']}\n"
                            f"  Time: {book_act['time']}\n"
                            "Activity details:\n"
                            f"  {act['ActivityType']['name']}\n"
                            f"  {act['Activity']['id']}\n"
                            f"  {act['Activity']['start']}\n"
                    )
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
                    hour_min_split = book_act["start_time"].split(":")
                    epoch = datetime.datetime.combine(
                        date_next_week,
                        datetime.time(
                            int(hour_min_split[0]),
                            int(hour_min_split[1])
                        )
                        ).timestamp()
                    epoch = int(epoch)
                    payload["ActivityBooking"]["book_start"] = str(epoch)
                    payload["ActivityBooking"]["book_length"] = "30"
                    print(payload)

                if input_vars["test"]:
                    print("Book act name")
                    print(book_act["name"])
                    print("Booking url that would be used:")
                    print(burl)
                    print("Payload that would be used:")
                    print(payload)
                else:
                    r = s.post(
                        burl,
                        headers=headers,
                        params=params,
                        json=payload
                    )
                    print(r.status_code)
                    print(r.text)
        else:
            print("No matching activity was found.")


if __name__ == "__main__":
    main()
