from enum import Enum, auto
from .ferry_companies import FerryCompany


class Ferry(Enum):
    MVALFRED = auto()


class FerryObject:

    enum = None
    company_enum = None
    id = None
    name = None
    human_capacity = None
    car_capacity = None
    is_accessible = None

    def __init__(self, enum: Ferry, comapny_enum: FerryCompany, id: str, name: str, human_capacity: int, car_capacity: int, is_accessible: bool):
        self.enum = enum
        self.company_enum = comapny_enum
        self.id = id
        self.name = name
        self.human_capacity = human_capacity
        self.car_capacity = car_capacity
        self.is_accessible = is_accessible


FERRIES = {
    Ferry.MVALFRED:
    FerryObject(
        enum=Ferry.MVALFRED,
        comapny_enum=FerryCompany.PENTLANDFERRIES,
        id="1",
        name="MV Alffred",
        human_capacity=430,
        car_capacity=98,
        is_accessible=False,
    ),
}


class FerryInfoGetter:

    @staticmethod
    def get_ferry_id(ferry: FerryCompany):
        return FERRIES[ferry].id

    @staticmethod
    def get_company(ferry: FerryCompany):
        return FERRIES[ferry].company_enum

    @staticmethod
    def get_ferry_name(ferry: FerryCompany):
        return FERRIES[ferry].name

    @staticmethod
    def get_ferry_human_capacity(ferry: FerryCompany):
        return FERRIES[ferry].human_capacity

    @staticmethod
    def get_ferry_car_capacity(ferry: FerryCompany):
        return FERRIES[ferry].car_capacity

    @staticmethod
    def get_ferry_accessibility(ferry: FerryCompany):
        return FERRIES[ferry].is_accessible
