from xml.dom import minidom
import math
from xml.dom.minidom import Document
import subprocess
from sumo_grid_simulation.simulation_scripts.enums import *
from sumo_grid_simulation.simulation_scripts.utils import PathUtils

"""
    This class generates grid networks for sumo
    
    The main method to use is:
        generate_grid_net
        
    There are several input parameters that are specifiable:
        - gridSize: The size of the grid (the number of junctions on one side)
                    Discrete variable, Domain [2, +inf]
        - junctionType: How the traffic is regualted in the junctions, explaination of the different types can be found at https://sumo.dlr.de/docs/Networks/PlainXML.html#node_descriptions
                    Discrete variable, Domain can be seen in the enums.py file
        - tlType: An optional type for the traffic light algorithm (see https://sumo.dlr.de/docs/Networks/PlainXML.html#node_descriptions)
                    Discrete variable, Domain can be seen in the enums.py file
        - tlLayout: An optional layout for the traffic light plan (see https://sumo.dlr.de/docs/Networks/PlainXML.html#node_descriptions)
                    Discrete variable, Domain can be seen in the enums.py file
        - keepClearJunctions: Whether the junction-blocking-heuristic should be activated at the junctions
                    Boolean varaible
        - edgeType: tthe edge type for the roads, from those specified in the grid_plain_xml/edge_types file, this parameter is currently unused as it is overwritten by numLanes, speed and priority parameters
                    Discrete variable, Domain can be seen in the enums.py file
        - edgeLength: The length of the roads in the network
                    Continuous variable, Domain [1, +inf]
        - numberOfLanes: The number of lanes for the roads in the network
                    Discrete variable, Domain [1, +inf]
        - edgeMaxSpeed: The maximum speed possible for the edges in the network
                    Continuous variable, Domain [0, +inf]
        - edgepriority: The priority of the edges in the network, currently useless as all the edges are set to the same priority
                    Discrete variable, Domain [0, +inf]
        
    This method takes as input a series of parameters relating to the grid and creates 3 files:
        - nodes.nod.xml the xml description of the nodes (located in the grid_plain_xml folder)
        - edges.edg.xml the xml description of the edges (located in the grid_plain_xml folder)
        - grid.net.xml the network file that can be opened in sumo-gui and netedit

"""
class GridGenerator:

    __junctionType = JunctionType.PRIORITY.tag
    __tlType = TrafficLightType.ACTUATED.tag
    __tlLayout = TrafficLightLayout.OPPOSITES.tag
    __keepClear = True
    __edgeType = EdgeType.NORMAL_ROAD.tag
    __edgeLength = 50
    __numberOfLanes = 1
    __edgeMaxSpeed = 13.9
    __edgePriority = 0

    netconvert_command = ['netconvert',
                          '--node-files=' + str(PathUtils.nodes_file),
                          '--edge-files=' + str(PathUtils.edges_file),
                          '--type-files=' + str(PathUtils.edge_types_file),
                          '--output-file=' + str(PathUtils.grid_net_file)]

    @staticmethod
    def generate_grid_net(gridSize: int, junctionType: int = 1, tlType: int = 2, tlLayout: int = 1, keepClearJunctions: bool = True,
                          edgeType: int = 1, edgeLength: float = 50, numberOfLanes: int = 1, edgeMaxSpeed: float = 13.9, edgePriority: int = 0):

        assert gridSize > 1, 'gridSize should be greater than 1'
        assert JunctionType.get_by_number(junctionType) is not None, 'Specified junctionType is not supported'
        assert TrafficLightType.get_by_number(tlType) is not None, 'Specified tlType is not supported'
        assert TrafficLightLayout.get_by_number(tlLayout) is not None, 'Specified tlLayout is not supported'
        assert EdgeType.get_by_number(edgeType) is not None, 'Specified edgeType is not supported'
        assert edgeLength > 0, 'Edge length should be greater then 0'
        assert numberOfLanes > 0, 'The number of lanes must be at leat 1'
        assert edgeMaxSpeed > 0, 'The maximum speed on the roads should be greater than 0'
        assert edgePriority >= 0, 'Priority cannot be negative'

        GridGenerator.__junctionType = JunctionType.get_by_number(junctionType).tag
        GridGenerator.__tlType = TrafficLightType.get_by_number(tlType).tag
        GridGenerator.__tlLayout = TrafficLightLayout.get_by_number(tlLayout).tag
        GridGenerator.__keepClear = keepClearJunctions
        GridGenerator.__edgeType = EdgeType.get_by_number(edgeType).tag
        GridGenerator.__edgeLength = edgeLength
        GridGenerator.__numberOfLanes = numberOfLanes
        GridGenerator.__edgeMaxSpeed = edgeMaxSpeed
        GridGenerator.__edgePriority = edgePriority

        f_nodes, f_edges = GridGenerator.__generate_grid_xml(gridSize)
        GridGenerator.generate_net_from_xml()

        return f_nodes, f_edges

    @staticmethod
    def generate_net_from_xml():

        process = subprocess.Popen(GridGenerator.netconvert_command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output, error = process.communicate()

        if output:
            print(output.decode())
        if error:
            print(error.decode())

    @staticmethod
    def __generate_grid_xml(size: int, withOuterNodes: bool = True):
        if size <= 0:
            return None

        nodes_file = GridGenerator.__generate_nodes_file(size, withOuterNodes)
        edges_file = GridGenerator.__generate_edges_file(size, withOuterNodes)

        f_nodes = open(PathUtils.nodes_file, "w")
        f_nodes.write(nodes_file)
        f_nodes.close()

        f_edges = open(PathUtils.edges_file, "w")
        f_edges.write(edges_file)
        f_edges.close()

        return f_nodes, f_edges

    @staticmethod
    def __generate_nodes_file(size: int, withOuterNodes: bool = True):
        doc = minidom.Document()

        root = doc.createElement('nodes')
        root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.setAttribute('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/nodes_file.xsd')
        doc.appendChild(root)

        node = doc.createElement('node')
        node.setAttribute('id', 'n1')
        node.setAttribute('x', '0')
        node.setAttribute('y', '0')
        node.setAttribute('type', GridGenerator.__junctionType)
        node.setAttribute('tlType', GridGenerator.__tlType)
        node.setAttribute('tlLayout', GridGenerator.__tlLayout)
        node.setAttribute('keepClear', str(GridGenerator.__keepClear).lower())

        root.appendChild(node)

        for i in range(size-1):
            doc = GridGenerator.__increase_grid_size(doc)

        if withOuterNodes:
            doc = GridGenerator.__add_outer_nodes(doc)

        xml_str = doc.toprettyxml(indent="\t")
        return xml_str

    @staticmethod
    def __increase_grid_size(doc: Document):

        root = doc.documentElement
        nodes_in_file = [childNode for childNode in root.childNodes if childNode.nodeType == 1]

        # number of nodes in the grid
        num_of_nodes = len(nodes_in_file)
        grid_size = int(math.sqrt(num_of_nodes))
        num_of_nodes_to_insert = 2 * grid_size + 1

        for i in range(num_of_nodes_to_insert):
            node = doc.createElement('node')
            node.setAttribute('id', 'n' + str(num_of_nodes + i + 1))
            if i <= num_of_nodes_to_insert // 2:
                x = GridGenerator.__edgeLength * grid_size
                y = GridGenerator.__edgeLength * i
            else:
                x = GridGenerator.__edgeLength * (num_of_nodes_to_insert - i - 1)
                y = GridGenerator.__edgeLength * grid_size
            node.setAttribute('x', str(x))
            node.setAttribute('y', str(y))

            node.setAttribute('type', GridGenerator.__junctionType)
            node.setAttribute('tlType', GridGenerator.__tlType)
            node.setAttribute('tlLayout', GridGenerator.__tlLayout)
            node.setAttribute('keepClear', str(GridGenerator.__keepClear).lower())

            root.appendChild(node)

        return doc

    @staticmethod
    def __add_outer_nodes(doc: Document):

        root = doc.documentElement
        nodes_in_file = [childNode for childNode in root.childNodes if childNode.nodeType == 1]

        # number of nodes in the grid
        num_of_nodes = len(nodes_in_file)
        grid_size = int(math.sqrt(num_of_nodes))
        num_of_nodes_to_insert = grid_size * 4

        for i in range(num_of_nodes_to_insert):
            node = doc.createElement('node')
            node.setAttribute('id', 'o' + str(i + 1))
            if i < num_of_nodes_to_insert // 4:
                x = GridGenerator.__edgeLength * i
                y = -GridGenerator.__edgeLength
            elif i < 2 * (num_of_nodes_to_insert // 4):
                x = GridGenerator.__edgeLength * grid_size
                y = GridGenerator.__edgeLength * (i - num_of_nodes_to_insert // 4)
            elif i < 3 * (num_of_nodes_to_insert // 4):
                x = GridGenerator.__edgeLength * (grid_size - 1 - (i - 2 * num_of_nodes_to_insert // 4))
                y = GridGenerator.__edgeLength * grid_size
            else:
                x = -GridGenerator.__edgeLength
                y = GridGenerator.__edgeLength * (grid_size - 1 - (i - 3 * num_of_nodes_to_insert // 4))

            node.setAttribute('x', str(x))
            node.setAttribute('y', str(y))

            node.setAttribute('type', JunctionType.PRIORITY.tag)

            root.appendChild(node)

        return doc

    @staticmethod
    def __generate_edges_file(size: int, withOuterNodes: bool = True):

        doc = minidom.Document()

        root = doc.createElement('edges')
        root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.setAttribute('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/edges_file.xsd')
        doc.appendChild(root)

        for i in range(size - 1):
            doc = GridGenerator.__add_edges_to_grid(doc, i+2)

        if withOuterNodes:
            doc = GridGenerator.__add_outer_edges(doc, size)

        xml_str = doc.toprettyxml(indent="\t")
        return xml_str

    @staticmethod
    def __add_edges_to_grid(doc: Document, size: int):

        root = doc.documentElement

        # number of nodes in the grid
        grid_size = size
        old_grid_size = grid_size - 1
        num_of_nodes = grid_size ** 2
        old_num_of_nodes = old_grid_size ** 2

        num_of_edges_to_insert = 4 * old_grid_size

        for i in range(num_of_edges_to_insert):

            if i < num_of_edges_to_insert // 4:
                start = old_num_of_nodes - i
                end = num_of_nodes - i
            elif i < num_of_edges_to_insert // 2:
                start = old_num_of_nodes - i + 1
                end = num_of_nodes - i - 1
            else:
                start = old_num_of_nodes + i - num_of_edges_to_insert // 2 + 1
                end = start + 1

            edge = doc.createElement('edge')
            edge.setAttribute('id', 'n' + str(start) + 'ton' + str(end))
            edge.setAttribute('from', 'n' + str(start))
            edge.setAttribute('to', 'n' + str(end))

            edge.setAttribute('numLanes', str(GridGenerator.__numberOfLanes))
            edge.setAttribute('speed', str(GridGenerator.__edgeMaxSpeed))
            edge.setAttribute('priority', str(GridGenerator.__edgePriority))
            edge.setAttribute('type', GridGenerator.__edgeType)

            edge_inverse = doc.createElement('edge')
            edge_inverse.setAttribute('id', 'n' + str(end) + 'ton' + str(start))
            edge_inverse.setAttribute('from', 'n' + str(end))
            edge_inverse.setAttribute('to', 'n' + str(start))

            edge_inverse.setAttribute('numLanes', str(GridGenerator.__numberOfLanes))
            edge_inverse.setAttribute('speed', str(GridGenerator.__edgeMaxSpeed))
            edge_inverse.setAttribute('priority', str(GridGenerator.__edgePriority))
            edge_inverse.setAttribute('type', GridGenerator.__edgeType)

            root.appendChild(edge)
            root.appendChild(edge_inverse)


            root.appendChild(edge_inverse)

        return doc

    @staticmethod
    def __add_outer_edges(doc: Document, size: int):

        root = doc.documentElement

        grid_size = size
        num_of_edges_to_insert = 4 * grid_size

        for i in range(num_of_edges_to_insert):

            if i < num_of_edges_to_insert // 4:
                start = i ** 2 + 1
                end = i + 1
            elif i < num_of_edges_to_insert // 2:
                start = ((grid_size - 1) ** 2) + i + 1 - num_of_edges_to_insert // 4
                end = i + 1
            elif i < 3 * num_of_edges_to_insert // 4:
                start = ((grid_size - 1) ** 2) + i - num_of_edges_to_insert // 4
                end = i + 1
            else:
                start = (grid_size - (i - 3 * num_of_edges_to_insert // 4)) ** 2
                end = i + 1

            edge = doc.createElement('edge')
            edge.setAttribute('id', 'n' + str(start) + 'too' + str(end))
            edge.setAttribute('from', 'n' + str(start))
            edge.setAttribute('to', 'o' + str(end))

            edge.setAttribute('numLanes', str(GridGenerator.__numberOfLanes))
            edge.setAttribute('speed', str(GridGenerator.__edgeMaxSpeed))
            edge.setAttribute('priority', str(GridGenerator.__edgePriority))
            edge.setAttribute('type', GridGenerator.__edgeType)

            edge_inverse = doc.createElement('edge')
            edge_inverse.setAttribute('id', 'o' + str(end) + 'ton' + str(start))
            edge_inverse.setAttribute('from', 'o' + str(end))
            edge_inverse.setAttribute('to', 'n' + str(start))

            edge_inverse.setAttribute('numLanes', str(GridGenerator.__numberOfLanes))
            edge_inverse.setAttribute('speed', str(GridGenerator.__edgeMaxSpeed))
            edge_inverse.setAttribute('priority', str(GridGenerator.__edgePriority))
            edge_inverse.setAttribute('type', GridGenerator.__edgeType)

            root.appendChild(edge)
            root.appendChild(edge_inverse)

            root.appendChild(edge_inverse)

        return doc
