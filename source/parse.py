import yaml


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