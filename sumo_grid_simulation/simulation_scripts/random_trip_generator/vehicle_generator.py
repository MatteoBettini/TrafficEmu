from xml.dom import minidom
from xml.dom.minidom import Document, Element

from pathlib import Path

from simulation_scripts.enums import VehicleClasses, EmmissionClasses
from simulation_scripts.utils import PathUtils


class Vehicle:
    # https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html#available_vtype_attributes

    def __init__(
            self,
            id: str,
            vehicle_class: int,
            emission_class: int,
            accel: float = 2.6,
            decel: float = 4.5,
            max_speed: float = 55.55,
            speed_factor: float = 1.0,
            speed_dev: float = 0.1
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
            speed_dev (float, optional): The deviation of the speedFactor. Defaults to 0.1.

        Raises:
            TypeError: [description]
        """
        self.id = id
        self.accel = accel
        self.decel = decel

        if VehicleClasses.get_by_number(vehicle_class) is None:
            raise TypeError(
                'vehicle_class must be an instance of VehicleClasses Enum')
        self.vehicle_class = VehicleClasses.get_by_number(vehicle_class)

        if EmmissionClasses.get_by_number(emission_class) is None:
            raise TypeError(
                'emission_class must be an instance of EmmissionClasses Enum')
        self.emission_class = EmmissionClasses.get_by_number(emission_class)

        self.max_speed = max_speed
        self.speed_factor = speed_factor
        self.speed_dev = speed_dev


class VehicleGenerator:

    @staticmethod
    def generate_additional_file(vehicles: list = []):
        additional_file = VehicleGenerator.__generate_additional_file(vehicles)
        f_add = open(PathUtils.additional_file, "w")
        f_add.write(additional_file)
        f_add.close()

    @staticmethod
    def __generate_additional_file(vehicles: list = []):
        doc = minidom.Document()

        root = doc.createElement('additional')

        doc.appendChild(root)

        for vehicle in vehicles:
            root.appendChild(
                VehicleGenerator.__generate_vehicle_element(doc, vehicle))

        xml_str = doc.toprettyxml(indent="\t")
        return xml_str

    @staticmethod
    def __generate_vehicle_element(doc: Document, vehicle: Vehicle) -> Element:
        element = doc.createElement('vType')
        element.setAttribute('id', vehicle.id)
        element.setAttribute('vClass', vehicle.vehicle_class.tag)
        element.setAttribute('emissionClass', vehicle.emission_class.tag)
        element.setAttribute('accel', str(vehicle.accel))
        element.setAttribute('decel', str(vehicle.decel))
        element.setAttribute('maxSpeed', str(vehicle.max_speed))
        element.setAttribute('speedFactor', str(vehicle.speed_factor))
        element.setAttribute('speedDev', str(vehicle.speed_dev))
        return element