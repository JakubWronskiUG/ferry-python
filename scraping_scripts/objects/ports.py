from enum import Enum, auto


class Port(Enum):
    GILLSBAY = auto()
    STMARGARETSHOPE = auto()
    OBAN = auto()
    CRAIGNURE = auto()


class PortObject:

    enum = None
    id = None
    name = None
    city = None
    island = None
    country = None

    def __init__(self, enum: Port, id: str, name: str, city: str, island: str, country: str):
        self.enum = enum
        self.id = id
        self.name = name
        self.city = city
        self.island = island
        self.country = country


PORTS = {
    Port.GILLSBAY:
    PortObject(
        enum=Port.GILLSBAY,
        id="1",
        name="Gills Bay",
        city="Wick",
        island="Mainland",
        country="Scotland"
    ),
    Port.STMARGARETSHOPE:
    PortObject(
        enum=Port.STMARGARETSHOPE,
        id="2",
        name="St Margaret’s Hope",
        city="Wick",
        island="Orkney",
        country="Scotland"
    ),
    Port.OBAN:
    PortObject(
        enum=Port.OBAN,
        id='3',
        name='Oban',
        city='Oban',
        island='Mainland',
        country='Scotland'
    ),
    Port.CRAIGNURE:
    PortObject(
        enum=Port.CRAIGNURE,
        id='4',
        name='Craignure',
        city='Craignure',
        island='Mull',
        country='Scotland'
    )
}


class PortInfoGetter:

    @staticmethod
    def get_port_id(port: Port):
        return PORTS[port].id

    @staticmethod
    def get_port_name(port: Port):
        return PORTS[port].name

    @staticmethod
    def get_port_city(port: Port):
        return PORTS[port].city

    @staticmethod
    def get_port_island(port: Port):
        return PORTS[port].island

    @staticmethod
    def get_port_country(port: Port):
        return PORTS[port].country
    
    @staticmethod
    def get_port_from_text(text: str) -> Port:
        for port in Port:
            if text.lower().find(PortInfoGetter.get_port_name(port).lower()) != -1:
                return port
        return None
