from enum import Enum, unique

class AbstractEnum(Enum):

    def __init__(self, number: int, tag: str):
        super().__init__()
        self.number = number
        self.tag = tag

@unique
class JunctionType(AbstractEnum):

    @staticmethod
    def get_by_number(number: int):
        for i in JunctionType:
            if i.number == number:
                return i
        return None

    PRIORITY = 1, 'priority'
    TRAFFIC_LIGHT = 2, 'traffic_light'
    TRAFFIC_LIGHT_UNREGULATED = 3, 'traffic_light_unregulated'
    TRAFFIC_LIGHT_ON_RED = 4, 'traffic_light_right_on_red'
    RIGHT_BEFORE_LEFT = 5, 'right_before_left'
    UNREGULATED = 6, 'unregulated'
    PRIORITY_STOP = 7, 'priority_stop'
    ALLWAY_STOP = 8, 'allway_stop'

@unique
class TrafficLightType(AbstractEnum):

    @staticmethod
    def get_by_number(number: int):
        for i in TrafficLightType:
            if i.number == number:
                return i
        return None

    STATIC = 1, 'static'
    ACTUATED = 2, 'actuated'
    DELAY_BASED = 3, 'delay_based'

@unique
class TrafficLightLayout(AbstractEnum):

    @staticmethod
    def get_by_number(number: int):
        for i in TrafficLightLayout:
            if i.number == number:
                return i
        return None

    OPPOSITES = 1, 'opposites'
    INCOMING = 2, 'incoming'
    ALTERNATE_ONE_WAY = 3, 'alternateOneWay'

@unique
class EdgeType(AbstractEnum):

    @staticmethod
    def get_by_number(number: int):
        for i in EdgeType:
            if i.number == number:
                return i
        return None

    NORMAL_ROAD = 1, 'normal_road'
    NORMAL_ROAD_2LANES = 2, 'normal_road_2lanes'
    NORMAL_ROAD_3LANES = 3, 'normal_road_3lanes'
    NORMAL_ROAD_4LANES = 4, 'normal_road_4lanes'
    # Possibly we can add as many types as we like to the edge_types file

@unique
class VehicleClasses(AbstractEnum):

    @staticmethod
    def get_by_number(number: int):
        for i in VehicleClasses:
            if i.number == number:
                return i
        return None

    # https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html#abstract_vehicle_class
    PASSENGER = 1, 'passenger'
    PEDESTRIAN = 2, 'pedestrian'
    EMERGENCY = 3, 'emergency'
    AUTHORITY = 4, 'authority'
    BICYCLE = 5, 'bicycle'
    TRUCK = 6, 'truck'
    BUS = 7, 'bus'
    TAXI = 8, 'taxi'

@unique
class EmmissionClasses(AbstractEnum):

    @staticmethod
    def get_by_number(number: int):
        for i in EmmissionClasses:
            if i.number == number:
                return i
        return None

    # https://sumo.dlr.de/docs/Models/Emissions.html
    ZERO = 1, "Zero"
    ELECTRIC = 2, "Energy"
    PC_G_EU4 = 3, "HBEFA3/PC_G_EU4"
    PC_AVERAGE = 4, "HBEFA3/PC" # average passenger car (all fuel types)
    BUS_AVERAGE = 5, "HBEFA3/Bus" # average urban bus (all fuel types)
    LDV_AVERAGE = 6, "HBEFA3/LDV" # average light duty vehicles (all fuel types) !! KNOWN TO BE FAULTY WITH NOx
