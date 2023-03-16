from enum import Enum, auto
import pandas as pd
from datetime import datetime, timedelta

from scraper import TimeTableScraper
from .ferry_companies import FerryCompany, CompanyInfoGetter
from .ports import Port, PortInfoGetter
from ..settings import Settings

class TripObject:

    id = None
    ferry_id = None
    port_from_id = None
    port_to_id = None
    trip_date = None
    hour_start = None
    hour_end = None

    def __init__(self, id: str, ferry_id: str, port_from_id: str, port_to_id: str, trip_date: str, hour_start: str, hour_end: str):
        self.id = id
        self.ferry_id = ferry_id
        self.port_from_id = port_from_id
        self.port_to_id = port_to_id
        self.trip_date = trip_date
        self.hour_start = hour_start
        self.hour_end = hour_end


class TripsParser:

    scraper = TimeTableScraper()

    def get_all_trips(self):

        ret = []
        for company in FerryCompany:

            timetables = self.scraper.get_timetables_for_company(company)
            print(timetables)
            i = 0
            for timetable in timetables:
                
                # table = timetables_info_block.timetable
                # ferry_id = timetables_info_block.ferry_id if timetables_info_block.ferry_id is not None else CompanyInfoGetter.get_company_default_ferry_id
                # port_from = timetables_info_block.port_from
                # port_to = timetables_info_block.port_to

                current_date = datetime.now()
                times = timetable.get_times()

                for d in range(Settings.days_to_generate):
                    weekday = current_date.strftime('%A')[:3].lower()
                    trips = times[weekday]
                    for trip_times in trips:
                        object = TripObject(
                            str(i),
                            timetable.ferry_id,
                            PortInfoGetter.get_port_id(timetable.departure_port),
                            PortInfoGetter.get_port_id(timetable.arrival_port),
                            current_date.strftime("%Y-%m-%d"),
                            trip_times.departure,
                            trip_times.arrival
                        )
                        ret.append(object)
                        i += 1

                    current_date = current_date + timedelta(days=1)

        return ret
