import yaml


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
