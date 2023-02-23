from enum import Enum, auto
import pandas as pd
from datetime import datetime, timedelta

from scraper import TimeTableScraper
from .ferry_companies import FerryCompany, CompanyInfoGetter
from .ports import Port, PortInfoGetter


class TripObject:

    id = None
    ferry_id = None
    port_from_id = None
    port_to_id = None
    trip_date = None
    hour_start = None
    duration_minutes = None

    def __init__(self, id: str, ferry_id: str, port_from_id: str, port_to_id: str, trip_date: str, hour_start: str, duration_minutes: str):
        self.id = id
        self.ferry_id = ferry_id
        self.port_from_id = port_from_id
        self.port_to_id = port_to_id
        self.trip_date = trip_date
        self.hour_start = hour_start
        self.duration_minutes = duration_minutes


class TripsParser:

    scraper = TimeTableScraper()

    def get_all_trips(self):

        ret = []
        for company in FerryCompany:

            timetables_info_array = self.scraper.get_timetables_for_company(
                company)

            i = 0
            for timetables_info_block in timetables_info_array:
                table = timetables_info_block.timetable
                ferry_id = timetables_info_block.ferry_id if timetables_info_block.ferry_id is not None else CompanyInfoGetter.get_company_default_ferry_id
                port_from = timetables_info_block.port_from
                port_to = timetables_info_block.port_to

                current_date = datetime.now()

                for d in range(30):
                    weekday = current_date.strftime('%A')[:3].upper()
                    trips = table.loc[:, weekday]
                    for trip_time in trips:
                        object = TripObject(
                            str(i),
                            ferry_id,
                            PortInfoGetter.get_port_id(port_from),
                            PortInfoGetter.get_port_id(port_to),
                            current_date.strftime("%Y-%m-%d"),
                            trip_time,
                            "75",
                        )
                        ret.append(object)
                        i += 1

                    current_date = current_date + timedelta(days=1)

        return ret
