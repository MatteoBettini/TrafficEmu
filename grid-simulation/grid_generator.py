from xml.dom import minidom
from pathlib import Path
import math
from xml.dom.minidom import Document
import subprocess

"""
    This class generates grid networks for sumo
    
    The main method to use is:
        generate_grid_net
        
    This method takes as input the size of the grid and creates 3 files:
        - nodes.nod.xml the xml description of the nodes (located in the grid-plain-xml folder)
        - edges.edg.xml the xml description of the edges (located in the grid-plain-xml folder)
        - grid.net.xml the network file that can be opened in sumo-gui and netedit

"""
class GridGenerator:

    __node_type = 'allway_stop'
    __edge_type = 'normal_road'
    __edge_length = 50
    __output_dir = Path('grid-plain-xml')

    folder_path = Path(__file__).resolve().parent.absolute()
    xml_folder = Path('grid-plain-xml')

    nodes_file = folder_path / xml_folder / 'nodes.nod.xml'
    edges_file = folder_path / xml_folder / 'edges.edg.xml'
    type_file = folder_path / xml_folder / 'edge_types.typ.xml'
    output_file = folder_path / 'grid.net.xml'

    netconvert_command = ['netconvert',
                          '--node-files=' + str(nodes_file),
                          '--edge-files=' + str(edges_file),
                          '--type-files=' + str(type_file),
                          '--output-file=' + str(output_file)]

    @staticmethod
    def generate_grid_net(size: int):
        GridGenerator.generate_grid_xml(size)
        GridGenerator.generate_net_from_xml()

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
    def generate_grid_xml(size: int):
        if size <= 0:
            return None

        nodes_file = GridGenerator.__generate_nodes_file(size)
        edges_file = GridGenerator.__generate_edges_file(size)

        nodes_path_file = GridGenerator.__output_dir / 'nodes.nod.xml'
        edges_path_file = GridGenerator.__output_dir / 'edges.edg.xml'

        f_nodes = open(nodes_path_file, "w")
        f_nodes.write(nodes_file)
        f_nodes.close()

        f_edges = open(edges_path_file, "w")
        f_edges.write(edges_file)
        f_edges.close()

        return f_nodes, f_edges

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
        node.setAttribute('type', GridGenerator.__node_type)

        root.appendChild(node)

        if size > 1:
            for i in range(size-1):
                doc = GridGenerator.__increase_grid_size(doc)

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
                x = GridGenerator.__edge_length * grid_size
                y = GridGenerator.__edge_length * i
            else:
                x = GridGenerator.__edge_length * (num_of_nodes_to_insert - i - 1)
                y = GridGenerator.__edge_length * grid_size
            node.setAttribute('x', str(x))
            node.setAttribute('y', str(y))
            node.setAttribute('type', GridGenerator.__node_type)

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
            edge.setAttribute('type', GridGenerator.__edge_type)

            edge_inverse = doc.createElement('edge')
            edge_inverse.setAttribute('id', 'e' + str(end) + 'to' + str(start))
            edge_inverse.setAttribute('from', 'n' + str(end))
            edge_inverse.setAttribute('to', 'n' + str(start))
            edge_inverse.setAttribute('type', GridGenerator.__edge_type)

            root.appendChild(edge)
            root.appendChild(edge_inverse)


            root.appendChild(edge_inverse)

        return doc



if __name__ == '__main__':

    grid_size = 4

    GridGenerator.generate_grid_net(grid_size)

