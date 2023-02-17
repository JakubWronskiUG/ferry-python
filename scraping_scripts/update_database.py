from enum import Enum, auto
from pymongo import MongoClient
from objects.ferries import Ferry, FerryInfoGetter
from objects.ferry_companies import FerryCompany, CompanyInfoGetter
from objects.ports import Port, PortInfoGetter
from objects.trips import TripObject, TripsParser


class Collection(Enum):
    COMPANY = auto()
    FERRY = auto()
    COMPANY_TO_FERRY_MAPPING = auto()
    PORT = auto()
    TRIP = auto()


class DBUpdater:

    client = None
    # db_name = 'test-python'
    db_name = 'test'
    db = None

    collections = {
        Collection.COMPANY: 'company',
        Collection.FERRY: 'ferries',
        Collection.PORT: 'ports',
        Collection.TRIP: 'trips',
        Collection.COMPANY_TO_FERRY_MAPPING: 'company_to_ferry_mapping'
    }

    MONGODB_USER = 'python-user'
    MONGODB_PASSWORD = 'pythonpassword'
    MONGODB_CONNECTION_STRING = "mongodb+srv://{}:{}@cluster0.qlxmvjb.mongodb.net/?retryWrites=true&w=majority&authSource=admin".format(
        MONGODB_USER,
        MONGODB_PASSWORD,
    )

    def __init__(self):
        self.client = MongoClient(self.MONGODB_CONNECTION_STRING)
        self.db = self.client[self.db_name]

    def append_company_collection(self, company: FerryCompany):

        company_collection = self.collections[Collection.COMPANY]

        update_dict = {
            'companyId': CompanyInfoGetter.get_company_id(company),
            'companyName': CompanyInfoGetter.get_company_name(company),
            'companyHomeUrl': CompanyInfoGetter.get_company_home_url(company),
            'companyTicketsUrl': CompanyInfoGetter.get_company_tickets_url(company)
        }

        self.db[company_collection].insert_one(update_dict)

    def append_ferry_collection(self, ferry: Ferry):

        ferry_collection = self.collections[Collection.FERRY]

        update_dict = {
            'ferryId': FerryInfoGetter.get_ferry_id(ferry),
            'ferryName': FerryInfoGetter.get_ferry_name(ferry),
            'ferryHumanCapacity': FerryInfoGetter.get_ferry_human_capacity(ferry),
            'ferryCarCapacity': FerryInfoGetter.get_ferry_car_capacity(ferry),
            'ferryIsAccessible': FerryInfoGetter.get_ferry_accessibility(ferry),
        }

        self.db[ferry_collection].insert_one(update_dict)

    def append_company_to_ferry_mapping_collection(self, ferry: Ferry):

        ferry_mapping_collection = self.collections[Collection.COMPANY_TO_FERRY_MAPPING]

        update_dict = {
            'ferryId': FerryInfoGetter.get_ferry_id(ferry),
            'companyId': CompanyInfoGetter.get_company_id(FerryInfoGetter.get_company(ferry)),
        }

        self.db[ferry_mapping_collection].insert_one(update_dict)

    def append_ports_collection(self, port: Port):

        ports_collection = self.collections[Collection.PORT]

        update_dict = {
            'portId': PortInfoGetter.get_port_id(port),
            'portName': PortInfoGetter.get_port_name(port),
            'city': PortInfoGetter.get_port_city(port),
            'island': PortInfoGetter.get_port_island(port),
            'country': PortInfoGetter.get_port_country(port),
        }

        self.db[ports_collection].insert_one(update_dict)

    def append_trips_collection(self, trip):
        trips_collection = self.collections[Collection.TRIP]
        update_dict = {
            'tripId': trip.id,
            'ferryId': trip.ferry_id,
            'portFromId': trip.port_from_id,
            'portToId': trip.port_to_id,
            'tripDate': trip.trip_date,
            'hourStart': trip.hour_start,
            'durationMinutes': trip.duration_minutes
        }

        self.db[trips_collection].insert_one(update_dict)
        print("Processed trip: ", trip.id)

    def update_databases(self):

        # clear all collections
        for collection in self.collections.values():
            self.db[collection].delete_many({})

        for company in FerryCompany:  # update companies
            self.append_company_collection(company)

        for ferry in Ferry:  # update ferries
            self.append_ferry_collection(ferry)

        for ferry in Ferry:  # update mapping
            self.append_company_to_ferry_mapping_collection(ferry)

        for port in Port:   # update ports
            self.append_ports_collection(port)

        parser = TripsParser()
        for trip in parser.get_all_trips():
            self.append_trips_collection(trip)

        db = self.client['test']['companies']
        dict = {'name': 'test_company'}
        # db.insert_one(dict)
        print(db)


updater = DBUpdater()

updater.update_databases()
