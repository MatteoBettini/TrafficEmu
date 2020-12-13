import os
import subprocess
from pathlib import Path

folder_path = Path(__file__).resolve().parent.absolute()

nodes_file = folder_path / 'grid-plain-xml' / 'nodes.nod.xml'
edges_file = folder_path / 'grid-plain-xml' / 'edges.edg.xml'
type_file = folder_path / 'grid-plain-xml' / 'edge_types.typ.xml'
output_file = folder_path / 'grid.net.xml'

netconvert_command = ['netconvert',
                      '--node-files=' + str(nodes_file),
                      '--edge-files=' + str(edges_file),
                      '--type-files=' + str(type_file),
                      '--output-file=' + str(output_file)]

if __name__ == '__main__':
    # os.system(netconvert_command)

    process = subprocess.Popen(netconvert_command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output, error = process.communicate()

    if output:
        print(output.decode())
    if error:
        print(error.decode())
