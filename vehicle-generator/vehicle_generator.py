from xml.dom import minidom
from xml.dom.minidom import Document

from pathlib import Path

from enums import VehicleClasses, EmmissionClasses

class Vehicle:
    # https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html#available_vtype_attributes

    def __init__(
        self,
        id: str,
        vehicle_class: VehicleClasses,
        emission_class: EmmissionClasses,
        accel: float = 2.6,
        decel: float = 4.5,
        max_speed: float = 55.55,
        speed_factor: float = 1.0,
        ):
        """[summary]

        Args:
            id (str): [description]
            vehicle_class (VehicleClasses): [description]
            emission_class (EmmissionClasses): [description]
            accel (float, optional): The acceleration ability of vehicles of this type (in m/s^2). Defaults to 2.6.
            decel (float, optional): The deceleration ability of vehicles of this type (in m/s^2). Defaults to 4.5.
            max_speed (float, optional): The vehicle's maximum velocity (in m/s). Defaults to 55.55.
            speed_factor (float, optional): The vehicles expected multiplicator for lane speed limits. Defaults to 1.0.

        Raises:
            TypeError: [description]
        """
        self.id = id
        self.accel = accel
        self.decel = decel

        if not isinstance(vehicle_class, VehicleClasses):
            raise TypeError('vehicle_class must be an instance of VehicleClasses Enum')
        self.vehicle_class = vehicle_class.value

        if not isinstance(emission_class, EmmissionClasses):
            raise TypeError('emission_class must be an instance of EmmissionClasses Enum')
        self.emission_class = emission_class.value

        self.max_speed = max_speed
        self.speed_factor = speed_factor

class VehicleGenerator():
    folder_path = Path(__file__).resolve().parent.absolute()
    output_file_path = folder_path / "veh.rou.xml" 

    @staticmethod
    def generate_routes_file(size: int):
        routes_file = VehicleGenerator.__generate_routes_file(size)
        f_routes = open(VehicleGenerator.output_file_path, "w")
        f_routes.write(routes_file)
        f_routes.close()

    @staticmethod
    def __generate_routes_file(size: int):
        doc = minidom.Document()

        root = doc.createElement('routes')
        root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.setAttribute('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
        doc.appendChild(root)

        vType_passenger = Vehicle(
            id="veh_passenger",
            vehicle_class=VehicleClasses.PASSENGER,
            emission_class=EmmissionClasses.ZERO
            )
        vType_passenger_element = doc.createElement('vType')
        vType_passenger_element.setAttribute('id', vType_passenger.id)
        vType_passenger_element.setAttribute('vClass', vType_passenger.vehicle_class)
        vType_passenger_element.setAttribute('emissionClass', vType_passenger.emission_class)
        vType_passenger_element.setAttribute('accel', str(vType_passenger.accel))
        vType_passenger_element.setAttribute('decel', str(vType_passenger.decel))
        vType_passenger_element.setAttribute('maxSpeed', str(vType_passenger.max_speed))
        vType_passenger_element.setAttribute('speedFactor', str(vType_passenger.speed_factor))
        root.appendChild(vType_passenger_element)

        xml_str = doc.toprettyxml(indent="\t")
        return xml_str


VehicleGenerator.generate_routes_file(1)