from enum import Enum, auto


class FerryCompany(Enum):
    PENTLANDFERRIES = auto()
    CALMAC = auto()

class ScrapingType(Enum):
    HTMLTABLE = auto()
    JPGTABLE = auto()


class FerryCompanyObject:

    enum = None
    id = None
    name = None
    timetable_url = None
    home_url = None
    tickets_url = None
    scraping_type = None
    default_ferry_id = None

    def __init__(self, enum: FerryCompany, id: str, name: str, timetable_urls: list, home_url: str, tickets_url: str, scraping_type: ScrapingType, default_ferry_id: str, default_trip_duration: int):
        self.enum = enum
        self.id = id
        self.name = name
        self.timetable_urls = timetable_urls
        self.home_url = home_url
        self.tickets_url = tickets_url
        self.scraping_type = scraping_type
        self.default_ferry_id = default_ferry_id
        self.default_trip_duration = default_trip_duration


COMPANIES = {
    FerryCompany.PENTLANDFERRIES:
        FerryCompanyObject(
            enum=FerryCompany.PENTLANDFERRIES,
            id="1",
            name="Pentland Ferries",
            timetable_urls=['https://pentlandferries.co.uk/timetable-2/'],
            home_url='https://pentlandferries.co.uk',
            tickets_url='https://pentlandferries.co.uk',
            scraping_type=ScrapingType.HTMLTABLE,
            default_ferry_id="1",
            default_trip_duration=75
        ),
    FerryCompany.CALMAC:
        FerryCompanyObject(
            enum=FerryCompany.CALMAC,
            id="2",
            name = "Calmac",
            timetable_urls=['https://www.calmac.co.uk/image/7941/Table-02-Tarbert---Portavadie-Winter-2022---2023-timetable---This-image-is-currently-not-accessible-to-screen-readers.-Please-phone-0800-066-5000-for-timetable-details/original.jpg?m=1663683765797'],
            home_url='https://calmac.co.uk',
            tickets_url='https://ticketing.calmac.co.uk/booking/asp/web100.asp',
            scraping_type=ScrapingType.JPGTABLE,
            default_ferry_id="1",#TODO
            default_trip_duration=75 #TODO

        )
}


class CompanyInfoGetter:

    @staticmethod
    def get_company_id(company: FerryCompany):
        return COMPANIES[company].id

    @staticmethod
    def get_company_name(company: FerryCompany):
        return COMPANIES[company].name

    @staticmethod
    def get_company_timetable_urls(company: FerryCompany):
        return COMPANIES[company].timetable_urls

    @staticmethod
    def get_company_home_url(company: FerryCompany):
        return COMPANIES[company].home_url

    @staticmethod
    def get_company_tickets_url(company: FerryCompany):
        return COMPANIES[company].tickets_url

    @staticmethod
    def get_company_scraping_type(company: FerryCompany):
        return COMPANIES[company].scraping_type

    @staticmethod
    def get_company_default_ferry_id(company: FerryCompany):
        return COMPANIES[company].default_ferry_id
    
    @staticmethod
    def get_company_default_trip_duration(company: FerryCompany):
        return COMPANIES[company].default_trip_duration
