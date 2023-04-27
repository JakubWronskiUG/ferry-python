from collections import namedtuple
from enum import Enum, auto
from objects.ports import Port

class WrongWeekday(Exception):
    pass

class Timetable:

    weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']    
    weekday_times = None
    ferry_id = None
    departure_port = None
    arrival_port = None

    def __init__(self, departure_port: Port, arrival_port: Port, ferry_id: str):
        self.departure_port = departure_port
        self.arrival_port = arrival_port
        self.ferry_id = ferry_id
        self.weekday_times = {weekday:[] for weekday in self.weekdays}

    def __str__(self):
        print('Timetable: ', self.weekday_times)
        return "Departure port: " + str(self.departure_port) + "\nArrival port: " + str(self.arrival_port) +"\nFerry ID: " + str(self.ferry_id)
    
    #Format:
    # routes -> {"mon": [(time1, time2), (time1a, time2a)]}

    def load_route(self, departures: list, arrivals: list, weekday: str):

        if weekday not in self.weekdays:
            raise WrongWeekday

        times =  namedtuple("TimesTouple", "departure arrival")
        
        for departure, arrival in zip(departures, arrivals):
            t = times(departure, arrival)
            self.weekday_times[weekday].append(t)
    
    def get_times(self):
        return self.weekday_times

        
        