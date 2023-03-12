import argparse
import datetime

import requests
import yaml

"""
base url for book/unbook:
https://feelgood.wondr.se/w_booking
how to unbook:
    /activities/cancel/{activity_code}/1?force=1
how to book:
    /activities/participate/{activity_code}}/?force=1
"""


def read_yaml(filename):
    """
    Reads yaml file and returns the dictionary

        Args:
            filename: The name of the yaml file to read

        Returns:
            Dictionary with the yaml blob
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            yaml_blob = yaml.safe_load(file)

            return yaml_blob
    except Exception as e:
        raise e


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
        "test": parsed.test
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


def parse_day(day):
    """
    Parses the day into text if input
    is number and vice versa.

    Args:
        day(int|str): input day as (int 0-6 || str )
    """
    day_parsed = None
    err_msg = None
    if isinstance(day, str):
        day = day.lower()
        match day:
            case "monday":
                day_parsed = 1
            case "tuesday":
                day_parsed = 2
            case "wednesday":
                day_parsed = 3
            case "thursday":
                day_parsed = 4
            case "friday":
                day_parsed = 5
            case "saturday":
                day_parsed = 6
            case "sunday":
                day_parsed = 7
            case _:
                err_msg = f"str: {day}"
    if isinstance(day, int):
        match day:
            case 1:
                day_parsed = "Monday"
            case 2:
                day_parsed = "Tuesday"
            case 3:
                day_parsed = "Wednesday"
            case 4:
                day_parsed = "Thursday"
            case 5:
                day_parsed = "Friday"
            case 6:
                day_parsed = "Saturday"
            case 7:
                day_parsed = "Sunday"
            case _:
                err_msg = f"int: {day}"

    if err_msg:
        raise ValueError(f"Could not parse input as a day: {err_msg}")

    return day_parsed


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
    banner = read_yaml("source/banner.yml")
    print(banner["banner"])


def main():
    """get parser args"""

    splash()

    config = read_yaml("source/config.yml")
    urls = config["urls"]
    activities = read_yaml("activities.yml")
    input_vars = initialize_parser()
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
        else:
            print("Activity day mismatch for:")
            print_dict(act)

    if not book_acts:
        print("No activities to book today, bye!")
        exit(0)

    with open("smil.e", mode="w", encoding="utf-8") as f:
        bla = input_vars["password"]
        for char in bla:
            f.write(char)

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
                if book_act["name"] in act["ActivityType"]["name"]\
                    and\
                        book_act["time"] in act["Activity"]["start"]:
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
                        f"{act['Activity']['id']}/?force=1"
                    )
                    booking_urls.append(booking_url)
        if booking_urls:
            for burl in booking_urls:
                if input_vars["test"]:
                    print("Booking url that would be used:")
                    print(burl)
                else:
                    s.post(burl, headers=headers)
        else:
            print("No matching activity was found.")


if __name__ == "__main__":
    main()
