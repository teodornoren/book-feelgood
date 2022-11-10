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
        "-a", "--activity",
        help="Add optional activity in place of config",
        required=False
        )

    parsed = parser.parse_args()
    input_vars = {
        "username": parsed.username,
        "password": parsed.password,
        "test": parsed.test
    }

    if parsed.time:
        input_vars["time"] = parsed.time
    if parsed.activity:
        input_vars["activity"] = parsed.activity

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
        raise ValueError(f"Could not parse day input {err_msg}")

    return day_parsed


def print_dict(dictionary: dict):
    for key, item in dictionary.items():
        print(f"{key}: {item}")


def get_date(offset: int, verbose=False):
    dt = datetime.date.today()
    new_date = dt - datetime.timedelta(days=-offset)

    if verbose:
        print(
            f"""Verbose mode for get_date:
    Today -v-
    Datetime is: {dt}
    Weekday is: {parse_day(dt.isoweekday())}
    Offset day -v-
    Datetime is: {new_date}
    Weekday is: {parse_day(new_date.isoweekday())}
            """)

    return new_date


def splash():
    banner = read_yaml("source/banner.yml")
    print(banner["banner"])


def parse_activities() -> dict:
    acts = read_yaml("activities.yml")

    for key, value in acts.items():
        print(key, value)


def main():
    """get parser args"""

    splash()

    parse_activities()

    config = read_yaml("source/config.yml")
    activities = read_yaml("activities.yml")
    input_vars = initialize_parser()

    if (input_vars["test"]):
        print("---running as test, no booking will be made---")

    if ("time" in input_vars):
        print(
            f"An input time of {input_vars['time']} overrides "
            f" the config time of:{config['activity']['time']}"
            )
        config["activity"]["time"] = input_vars["time"]
    # Offset of 6 is the maximum that new activities appear
    date_next_week = get_date(offset=6, verbose=input_vars["test"])

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

    specific_url = (
        "https://feelgood.wondr.se/w_booking/activities/list?from="
        f"{date_next_week}&to={date_next_week}&today=0&location=&user=&mine=0&"
        f"type=&only_try_it=0&facility={activities['facility']}"
    )

    payload = {
        "User": {
            "email": input_vars["username"],
            "password": input_vars["password"]
            }
        }

    headers = read_yaml("source/headers.yml")
    if (input_vars["test"]):
        print(">--headers-start-<")
        for header, value in headers.items():
            print(f"    {header}: {value}")
        print(">--headers-end--<")

    with requests.session() as s:
        s.post(config["url"]["login"], json=payload)
        r = s.get(config["url"]["home"])
        r = s.get(config["url"]["book"])

        r = s.get(specific_url, headers=headers)

        activity_dict = r.json()
        foundSomething = False
        for act in activity_dict["activities"]:
            for book_act in book_acts:
                if book_act["name"] in act["ActivityType"]["name"]\
                    and\
                        book_act["time"] in act["Activity"]["start"]:
                    print(f"""
    Found activity matching:
    Name: {book_act['name']}
    Time: {book_act['time']}
    Activity details:
        {act["ActivityType"]["name"]}
        {act["Activity"]["id"]}
        {act["Activity"]["start"]}
                        """)
                    booking_url = (
                        "https://feelgood.wondr.se/w_booking/"
                        "activities/participate/"
                        f"{act['Activity']['id']}/?force=1"
                    )
                    if not input_vars["test"] and not foundSomething:
                        s.post(booking_url, headers=headers)
                    else:
                        print("Booking url that would be used:")
                        print(booking_url)

                    foundSomething = True

    if not foundSomething:
        print("No matching activity was found, sorry about that.")


if __name__ == "__main__":
    main()
