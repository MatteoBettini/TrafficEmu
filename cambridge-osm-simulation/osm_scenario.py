from flow.scenarios import Scenario
from flow.core.params import InitialConfig
from flow.core.params import TrafficLightParams

import xml.etree.ElementTree as ElementTree
from lxml import etree
from collections import defaultdict

DEFAULT_PROBABILITY = 0
DEFAULT_LENGTH = 5
DEFAULT_VCLASS = 0

class OSMScenario(Scenario):
    def __init__(
        self,
        name,
        vehicles,
        net_params,
        initial_config=InitialConfig(),
        traffic_lights=TrafficLightParams()
    ):
        super(OSMScenario, self).__init__(name, vehicles, net_params, initial_config, traffic_lights)

    @staticmethod
    def _vehicle_infos(file_names):
        """Import of vehicle from a configuration file.

        This is a utility function for computing vehicle information. It
        imports a network configuration file, and returns the information on
        the vehicle and add it into the Vehicle object.

        Parameters
        ----------
        file_names : list of str
            path to the xml file to load

        Returns
        -------
        dict <dict>

            * Key = id of the vehicle
            * Element = dict of departure speed, vehicle type, depart Position,
              depart edges
        """
        # this is meant to deal with the case that there is only one rou file
        if isinstance(file_names, str):
            file_names = [file_names]

        vehicle_data = dict()
        routes_data = dict()
        type_data = defaultdict(int)

        for filename in file_names:
            # import the .net.xml file containing all edge/type data
            parser = etree.XMLParser(recover=True)
            tree = ElementTree.parse(filename, parser=parser)
            root = tree.getroot()

            # collect the departure properties and routes and vehicles whose
            # properties are instantiated within the .rou.xml file. This will
            # only apply if such data is within the file (it is not implemented
            # by scenarios in Flow).
            for vehicle in root.findall('vehicle'):
                # collect the edges the vehicle is meant to traverse
                route = vehicle.find('route')
                route_edges = route.attrib["edges"].split(' ')

                # collect the names of each vehicle type and number of vehicles
                # of each type
                type_vehicle = vehicle.attrib['type']
                type_data[type_vehicle] += 1

                vehicle_data[vehicle.attrib['id']] = {
                    'departSpeed': vehicle.attrib.get('departSpeed', "random"), ##CHANGED
                    'depart': vehicle.attrib['depart'],
                    'typeID': type_vehicle,
                    'departPos': vehicle.get('departPos', "random_free"), ##CHANGED
                }

                routes_data[vehicle.attrib['id']] = route_edges

            # collect the edges the vehicle is meant to traverse for the given
            # sets of routes that are not associated with individual vehicles
            for route in root.findall('route'):
                route_edges = route.attrib["edges"].split(' ')
                routes_data[route.attrib['id']] = route_edges

        return vehicle_data, routes_data

    @staticmethod
    def _vehicle_type(filename):
        """Import vehicle type data from a *.add.xml file.

        This is a utility function for outputting all the type of vehicle.

        Parameters
        ----------
        filename : str
            path to the vtypes.add.xml file to load

        Returns
        -------
        dict or None
            the key is the vehicle_type id and the value is a dict we've type
            of the vehicle, depart edges, depart Speed, departPos. If no
            filename is provided, this method returns None as well.
        """
        if filename is None:
            return None

        parser = etree.XMLParser(recover=True)
        tree = ElementTree.parse(filename, parser=parser)

        root = tree.getroot()
        veh_type = {}

        # this hack is meant to support the LuST scenario and Flow scenarios
        root = [root] if len(root.findall('vTypeDistribution')) == 0 \
            else root.findall('vTypeDistribution')

        for r in root:
            for vtype in r.findall('vType'):
                # TODO: make for everything
                veh_type[vtype.attrib['id']] = {
                    'vClass': vtype.attrib.get('vClass', DEFAULT_VCLASS),
                    'accel': vtype.attrib['accel'],
                    'decel': vtype.attrib['decel'],
                    'sigma': vtype.attrib.get('sigma', 0.5), ## CHANGED
                    'length': vtype.attrib.get('length', DEFAULT_LENGTH),
                    'minGap': vtype.attrib['minGap'],
                    'maxSpeed': vtype.attrib['maxSpeed'],
                    'probability': vtype.attrib.get(
                        'probability', DEFAULT_PROBABILITY),
                    'speedDev': vtype.attrib.get('speedDev', 0.1) ##CHANGED
                }

        return veh_type