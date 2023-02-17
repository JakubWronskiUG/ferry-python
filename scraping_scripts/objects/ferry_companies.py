from enum import Enum, auto


class FerryCompany(Enum):
    PENTLANDFERRIES = auto()


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

    def __init__(self, enum: FerryCompany, id: str, name: str, timetable_url: str, home_url: str, tickets_url: str, scraping_type: ScrapingType, default_ferry_id: str):
        self.enum = enum
        self.id = id
        self.name = name
        self.timetable_url = timetable_url
        self.home_url = home_url
        self.tickets_url = tickets_url
        self.scraping_type = scraping_type
        self.default_ferry_id = default_ferry_id


COMPANIES = {
    FerryCompany.PENTLANDFERRIES:
    FerryCompanyObject(
        enum=FerryCompany.PENTLANDFERRIES,
        id="1",
        name="Pentland Ferries",
        timetable_url='https://pentlandferries.co.uk/timetable-2/',
        home_url='https://pentlandferries.co.uk',
        tickets_url='https://pentlandferries.co.uk',
        scraping_type=ScrapingType.HTMLTABLE,
        default_ferry_id="1"
    ),
}


class CompanyInfoGetter:

    @staticmethod
    def get_company_id(company: FerryCompany):
        return COMPANIES[company].id

    @staticmethod
    def get_company_name(company: FerryCompany):
        return COMPANIES[company].name

    @staticmethod
    def get_company_timetable_url(company: FerryCompany):
        return COMPANIES[company].timetable_url

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
