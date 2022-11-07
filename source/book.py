import requests
import datetime
import yaml
import argparse

"""
how to unbook:
https://feelgood.wondr.se/w_booking\
    /activities/cancel/{activity_code}/1?force=1
how to book:
https://feelgood.wondr.se/w_booking\
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
    except Exception as expt:
        raise expt


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
        help="Add an optional time if you do not want to use the config time",
        required=False,
    )

    parsed = parser.parse_args()
    input_vars = {
        "username": parsed.username,
        "password": parsed.password,
        "test": parsed.test
    }

    if parsed.time:
        input_vars["time"] = parsed.time

    return input_vars


def parse_day(day):
    pass


def get_date(offset: int, verbose=False):
    dt = datetime.date.today()
    new_date = dt - datetime.timedelta(days=-offset)

    if verbose:
        print("Today -v-")
        print(f"Datetime is: {dt}")
        print(f"Weekday is: {dt.isoweekday()}")
        print("Offset day -v-")
        print(f"Datetime is: {new_date}")
        print(f"Weekday is: {new_date.isoweekday()}")

    return new_date


def main():
    """get parser args"""

    banner = read_yaml("source/banner.yml")

    print(banner["banner"])

    config = read_yaml("source/config.yml")

    input_vars = initialize_parser()

    if (input_vars["test"]):
        print("---running as test, no booking will be made---")

    if ("time" in input_vars):
        print(f"\
            An input time of {input_vars['time']} overrides \
                the config time of: {config['activity']['time']}")
        config["activity"]["time"] = input_vars["time"]

    date_next_week = get_date(offset=6)

    specific_url = f"https://feelgood.wondr.se/w_booking/activities/list?from=\
        {date_next_week}&to={date_next_week}&today=0&location=&user=&mine=0&\
            type=&only_try_it=0&facility=60a7ac3f-b774-4228-a9a3-056c0a10010d"

    payload = {
        "User": {
            "email": input_vars["username"],
            "password": input_vars["password"]
            }
        }

    headers = config["headers"]

    print(f"Match activity string : {config['activity']['name']}")
    print(f"Match activity time   : {config['activity']['time']}")

    with requests.session() as s:
        s.post(config["url"]["login"], json=payload)
        r = s.get(config["url"]["home"])
        r = s.get(config["url"]["book"])

        r = s.get(specific_url, headers=headers)

        activity_dict = r.json()
        foundSomething = False
        for act in activity_dict["activities"]:
            # Create config file for activity type and time

            if config["activity"]["name"] in act["ActivityType"]["name"]\
                and\
                    config["activity"]["time"] in act["Activity"]["start"]:
                print(f"Found activity matching: \
                    {config['activity']['name']} \
                        at time: {config['activity']['time']}")
                print(act["ActivityType"]["name"])
                print(act["Activity"]["id"])
                print(act["Activity"]["start"])
                booking_url = f"https://feelgood.wondr.se/w_booking/\
                    activities/participate/{act['Activity']['id']}/?force=1"
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
