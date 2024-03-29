import argparse
import datetime

import yaml
from loguru import logger


def initialize_parser(arg_list: list[str] = None) -> dict:
    """
    Needed input arguments for this program
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-usr",
        "--username",
        help="The username for feelgood login",
        required=True,
    )

    parser.add_argument(
        "-pw",
        "--password",
        help="The password for feelgood login",
        required=True,
    )

    parser.add_argument(
        "-act",
        "--activities_file",
        help="Activities.yml file to use",
        required=False,
    )

    parser.add_argument(
        "-tst",
        "--test",
        action=argparse.BooleanOptionalAction,
        help="Do a dry run",
        required=False,
    )

    parser.add_argument(
        "-t",
        "--book_time",
        help="Add an optional time in place of config",
        required=False,
    )

    parser.add_argument(
        "-n",
        "--name",
        help="Add optional name in place of config",
        required=False,
    )

    parser.add_argument(
        "-d",
        "--day",
        help="Add optional day in place of config",
        required=False,
    )

    parser.add_argument(
        "-do",
        "--day-offset",
        help="Add optional offset day in place of config",
        required=False,
    )

    parser.add_argument(
        "-st",
        "--start-time",
        help="Optional start time for Boka activities",
        required=False,
    )

    parsed = parser.parse_args(arg_list)

    return vars(parsed)


def parse_day(day: int | str) -> int | str:
    """
    Converts a day between its numerical and textual representations.

    This function accepts either an integer (1-7) or a string representing a
    day of the week. If an integer is provided, it will be converted to the
    corresponding day name (e.g., 1 -> "Monday"). If a string is provided, it
    will be converted to the corresponding integer value (e.g., "Tuesday" -> 2)

    Args:
        day (int | str): The input day to be parsed. Can be an integer (1-7)
        or a day name string.

    Returns:
        int | str: The parsed day, either as an integer (1-7)
        or a day name string.

    Raises:
        ValueError: If the input cannot be parsed as a valid day.
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


def read_yaml(filename: str) -> dict:
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


def log_dict(dictionary: dict, indent: int = 0):
    """
    Log the contents of a dictionary recursively, with optional indentation.

    Args:
        dictionary (dict): The dictionary to log.
        indent (int, optional): The level of indentation for logging.
            Defaults to 0.

    Returns:
        None
    """
    offset = ""
    for _ in range(0, indent):
        offset = f"{offset}  "
    for key, item in dictionary.items():
        if isinstance(item, dict):
            logger.info(f"{offset}{key}:")
            log_dict(item, indent=indent + 1)
        elif isinstance(item, list):
            logger.info(f"{offset}{key}:")
            for i in item:
                log_dict(i, indent=indent + 1)
        else:
            logger.info(f"{offset}{key}: {item}")


def get_date(day_offset: int) -> datetime.date:
    """
    Get the date with a specified offset from today.

    Args:
        day_offset (int): The number of days to offset from today.

    Returns:
        datetime.date: The date with the specified offset.
    """
    dt = datetime.date.today()
    new_date = dt + datetime.timedelta(days=day_offset)

    return new_date


def splash():
    banner = read_yaml("config/banner.yml")
    logger.success(banner["banner"])


def load_config():
    config = read_yaml("config/config.yml")
    return (config["settings"], config["urls"], config["headers"])
