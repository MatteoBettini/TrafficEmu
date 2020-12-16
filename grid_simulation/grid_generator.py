from xml.dom import minidom
from pathlib import Path
import math
from xml.dom.minidom import Document
import subprocess
from grid_simulation.enums import *

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

    __junctionType = JunctionType(1).name
    __tlType = TrafficLightType(2).name
    __tlLayout = TrafficLightLayout(1).name
    __keepClear = True
    __edgeType = EdgeType(1).name
    __edgeLength = 50
    __numberOfLanes = 1
    __edgeMaxSpeed = 13.9
    __edgePriority = 0

    folder_path = Path(__file__).resolve().parent.absolute()
    xml_folder = Path('grid_plain_xml')

    nodes_file_path = folder_path / xml_folder / 'nodes.nod.xml'
    edges_file_path = folder_path / xml_folder / 'edges.edg.xml'
    type_file_path = folder_path / xml_folder / 'edge_types.typ.xml'
    output_file_path = folder_path / 'grid.net.xml'

    netconvert_command = ['netconvert',
                          '--node-files=' + str(nodes_file_path),
                          '--edge-files=' + str(edges_file_path),
                          '--type-files=' + str(type_file_path),
                          '--output-file=' + str(output_file_path)]

    @staticmethod
    def generate_grid_net(gridSize: int, junctionType: int = 1, tlType: int = 2, tlLayout: int = 1, keepClearJunctions: bool = True,
                          edgeType: int = 1, edgeLength: float = 50, numberOfLanes: int = 1, edgeMaxSpeed: float = 13.9, edgePriority: int = 0):

        assert gridSize > 1, 'gridSize should be greater than 1'
        assert junctionType in [jt.value for jt in JunctionType], 'Specified junctionType is not supported'
        assert tlType in [tlt.value for tlt in TrafficLightType], 'Specified tlType is not supported'
        assert tlLayout in [tll.value for tll in TrafficLightLayout], 'Specified tlLayout is not supported'
        assert edgeType in [et.value for et in EdgeType], 'Specified edgeType is not supported'
        assert edgeLength > 0, 'Edge length should be greater then 0'
        assert numberOfLanes > 0, 'The number of lanes must be at leat 1'
        assert edgeMaxSpeed > 0, 'The maximum speed on the roads should be greater than 0'
        assert edgePriority >= 0, 'Priority cannot be negative'


        GridGenerator.__junctionType = JunctionType(junctionType).name
        GridGenerator.__tlType = TrafficLightType(tlType).name
        GridGenerator.__tlLayout = TrafficLightLayout(tlLayout).name
        GridGenerator.__keepClear = keepClearJunctions
        GridGenerator.__edgeType = EdgeType(edgeType).name
        GridGenerator.__edgeLength = edgeLength
        GridGenerator.__numberOfLanes = numberOfLanes
        GridGenerator.__edgeMaxSpeed = edgeMaxSpeed
        GridGenerator.__edgePriority = edgePriority

        f_nodes, f_edges, outer_nodes = GridGenerator.__generate_grid_xml(gridSize)
        GridGenerator.generate_net_from_xml()

        return f_nodes, f_edges, outer_nodes

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
    def __generate_grid_xml(size: int):
        if size <= 0:
            return None

        nodes_file, outer_nodes = GridGenerator.__generate_nodes_file(size)
        edges_file = GridGenerator.__generate_edges_file(size)

        f_nodes = open(GridGenerator.nodes_file_path, "w")
        f_nodes.write(nodes_file)
        f_nodes.close()

        f_edges = open(GridGenerator.edges_file_path, "w")
        f_edges.write(edges_file)
        f_edges.close()

        return f_nodes, f_edges, outer_nodes

    @staticmethod
    def __generate_nodes_file(size: int):
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

        if size > 1:
            for i in range(size-1):
                doc = GridGenerator.__increase_grid_size(doc)
            outer_nodes = [1]
            for i in range(2, size-1, 1):
                outer_nodes.append((i-1)**2 + 1) # bottom row
                outer_nodes.append(i**2) # left row
            for i in range((size-1)**2 + 1, size**2, 1):
                outer_nodes.append(i) # top and right row

        xml_str = doc.toprettyxml(indent="\t")
        return xml_str, outer_nodes

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
    def __generate_edges_file(size: int):

        doc = minidom.Document()

        root = doc.createElement('edges')
        root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.setAttribute('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/edges_file.xsd')
        doc.appendChild(root)

        if size > 1:
            for i in range(size - 1):
                doc = GridGenerator.__add_edges_to_grid(doc, i+2)

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
            edge.setAttribute('id', 'e' + str(start) + 'to' + str(end))
            edge.setAttribute('from', 'n' + str(start))
            edge.setAttribute('to', 'n' + str(end))

            edge.setAttribute('numLanes', str(GridGenerator.__numberOfLanes))
            edge.setAttribute('speed', str(GridGenerator.__edgeMaxSpeed))
            edge.setAttribute('priority', str(GridGenerator.__edgePriority))
            edge.setAttribute('type', GridGenerator.__edgeType)

            edge_inverse = doc.createElement('edge')
            edge_inverse.setAttribute('id', 'e' + str(end) + 'to' + str(start))
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
