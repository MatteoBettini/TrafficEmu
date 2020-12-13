import os
import sys
import optparse
from sumolib import checkBinary
import traci
from pathlib import Path

simulation_seed = 42
simulation_delay = 300

simulation_name = 'grid.sumocfg'
folder_path = Path(__file__).resolve().parent.absolute()

simulation_file = folder_path / simulation_name
trip_info_file = folder_path / 'simulation-output-files' / 'tripinfo.xml'
statistics_file = folder_path / 'simulation-output-files' / 'statistics_output.xml'
custom_gui_view_file = folder_path.parent / 'custom_sumo_gui_view.xml'

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

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

    print()
    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, '--configuration-file', simulation_file,
                 '--start',
                 '--seed', str(simulation_seed),
                 '--delay', str(simulation_delay),
                 '--gui-settings-file', custom_gui_view_file,
                 '--quit-on-end',
                 '--tripinfo-output', trip_info_file,
                 '--statistics-output', statistics_file])

    run()
