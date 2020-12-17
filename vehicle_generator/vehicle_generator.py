from xml.dom import minidom
from xml.dom.minidom import Document, Element

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
            raise TypeError(
                'vehicle_class must be an instance of VehicleClasses Enum')
        self.vehicle_class = vehicle_class.value

        if not isinstance(emission_class, EmmissionClasses):
            raise TypeError(
                'emission_class must be an instance of EmmissionClasses Enum')
        self.emission_class = emission_class.value

        self.max_speed = max_speed
        self.speed_factor = speed_factor


class VehicleGenerator:

    @staticmethod
    def generate_additional_file(output_file_path: Path, vehicles: list = []):
        additional_file = VehicleGenerator.__generate_additional_file(vehicles)
        f_add = open(output_file_path, "w")
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
        element.setAttribute('vClass', vehicle.vehicle_class)
        element.setAttribute('emissionClass', vehicle.emission_class)
        element.setAttribute('accel', str(vehicle.accel))
        element.setAttribute('decel', str(vehicle.decel))
        element.setAttribute('maxSpeed', str(vehicle.max_speed))
        element.setAttribute('speedFactor', str(vehicle.speed_factor))
        return element

if __name__ == "__main__":
    folder_path = Path(__file__).resolve().parent.absolute()
    output_file_path = folder_path / "veh.add.xml"

    vehicles = []
    vehicles.append(
        Vehicle(
            id="veh_passenger",
            vehicle_class=VehicleClasses.PASSENGER,
            emission_class=EmmissionClasses.PC_G_EU4
        )
    )
    vehicles.append(
        Vehicle(
            id="veh_emergency",
            vehicle_class=VehicleClasses.EMERGENCY,
            emission_class=EmmissionClasses.PC_G_EU4
        )
    )
    VehicleGenerator.generate_additional_file(output_file_path, vehicles)
