import os
import subprocess

netconvert_command = 'netconvert ' \
                     '--node-files=grid_plain_xml/nodes.nod.xml ' \
                     '--edge-files=grid_plain_xml/edges.edg.xml ' \
                     '--type-files=grid_plain_xml/edge_types.typ.xml ' \
                     '--output-file=grid.net.xml '

if __name__ == '__main__':
    # os.system(netconvert_command)

    process = subprocess.Popen(netconvert_command.split(),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output, error = process.communicate()

    if output:
        print(output.decode())
    if error:
        print(error)