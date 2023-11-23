from loguru import logger
import datetime
import requests
from book_feelgood.parse import (
        read_yaml,
        parse_day,
        log_dict,
        get_date,
        load_config,
        splash,
        initialize_parser
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
    if activities_file:
        logger.add(f"logs/{activities_file}.log")

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

    future_date = get_date(offset=int(day_offset))

    # Check if date_next_week matches any config days
    yml_acts = []
    for yml_act in activities["activities"]:
        if future_date.isoweekday() == parse_day(yml_act["day"]):
            logger.info("Activity day matches, will look for:")
            log_dict(yml_act)
            yml_acts.append(yml_act)

    if not yml_acts:
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

        activities_to_book = []

        for f_act in feelgood_activities["activities"]:
            for yml_act in yml_acts:
                if (
                        yml_act["name"] in f_act["ActivityType"]["name"] and
                        yml_act["time"] in f_act["Activity"]["start"]
                ):
                    booking_url = (
                        f"{urls['base_url']}"
                        f"{urls['participate']}"
                        f"{f_act['Activity']['id']}"
                    )

                    fa = feelgood_activity(
                        url=booking_url,
                        name=f_act["ActivityType"]["name"],
                        start=f_act["Activity"]["start"],
                    )
                    if "start_time" in yml_act:
                        fa.start_time = (yml_act["start_time"])
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
                if "Boka" in activity_to_book.name:
                    logger.info(
                        f"  Start time: {activity_to_book.start_time}"
                    )
                    hour_min_split = activity_to_book.start_time.split(":")
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
                    logger.debug(activity_to_book.name)
                    logger.debug("Booking url that would be used:")
                    logger.debug(activity_to_book.url)
                    logger.debug("Payload that would be used:")
                    logger.debug(payload)
                else:
                    r = s.post(
                        activity_to_book.url,
                        headers=headers,
                        params=params,
                        json=payload
                    )
                    logger.debug(f"{r.json()=}")
                    if (
                        r.status_code == 200 and
                        r.json()["result"] == "ok"
                    ):
                        logger.success("Successfully booked:")
                        logger.success(f"  {activity_to_book.name}")
                        logger.success(f"  {activity_to_book.start}")
                        logger.success(f"  {activity_to_book.start_time}")
                    elif (
                        r.json()["error_code"] == 'ACTIVITY_FULL'
                    ):
                        logger.error("Activity is fully booked already:")
                        logger.error(f"  {activity_to_book.name}")
                        logger.error(f"  {activity_to_book.start}")
                        logger.error(f"  {activity_to_book.start_time}")
                    else:
                        logger.error("Something went wrong:")
                        logger.error(f"  {activity_to_book.name}")
                        logger.error(f"  {activity_to_book.start}")
                        logger.error(f"  {activity_to_book.start_time}")
                        logger.error(f"{r.status_code=}")
                        logger.error(f"{r.text=}")
        else:
            logger.warning("No matching activity was found.")


if __name__ == "__main__":
    book(**initialize_parser())
