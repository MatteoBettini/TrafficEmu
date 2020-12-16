from enum import Enum

class JunctionType(Enum):
    priority = 1
    traffic_light = 2
    traffic_light_unregulated = 3
    traffic_light_right_on_red = 4
    right_before_left = 5
    unregulated = 6
    priority_stop = 7
    allway_stop = 8

class TrafficLightType(Enum):
    static = 1
    actuated = 2
    delay_based = 3

class TrafficLightLayout(Enum):
    opposites = 1
    incoming = 2
    alternateOneWay = 3

class EdgeType(Enum):
    normal_road = 1
    normal_road_2lanes = 2
    normal_road_3lanes = 3
    normal_road_4lanes = 4
    # Possibly we can add as many types as we like to the edge_types file
