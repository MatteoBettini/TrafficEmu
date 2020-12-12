import os
import sys
import optparse

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary
import traci

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('--nogui', action='store_true',
                          default=False, help='run the commandline version of sumo')
    options, args = opt_parser.parse_args()
    return options


# traci control loop
def run():

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(step)
        step += 1

    traci.close()
    sys.stdout.flush()


if __name__ == '__main__':
    options = get_options()
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, '-c', 'grid-simulation/grid.sumocfg',
                 '--tripinfo-output', 'grid-simulation/tripinfo.xml',
                 '--start',
                 '--delay', '300',
                 '--gui-settings-file', 'custom_gui_view.xml'])
    run()
