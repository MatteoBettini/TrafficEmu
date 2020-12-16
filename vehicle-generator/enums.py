from enum import Enum, unique

@unique
class VehicleClasses(Enum):
    #https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html#abstract_vehicle_class
    PASSENGER = "passenger"
    PEDESTRIAN = "pedestrian"
    EMERGENCY = "emergency"
    AUTHORITY = "authority"
    BICYCLE = "bicycle"
    TRUCK = "truck"

@unique
class EmmissionClasses(Enum):
    # https://sumo.dlr.de/docs/Models/Emissions.html
    ZERO = "Zero"
    ELECTRIC = "Energy"
    PC_G_EU4 = "HBEFA3/PC_G_EU4"