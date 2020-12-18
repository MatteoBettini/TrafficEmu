import os
import sys
import optparse
from sumolib import checkBinary
from sumolib.output import parse as parse_sumo_output
import traci
from pathlib import Path
from grid_simulation.grid_generator import GridGenerator
from random_trip_generator import RandomTripGenerator

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class Simulator:

    simulation_name = 'grid.sumocfg'
    simulation_output_dir = 'simulation-output-files'

    folder_path = Path(__file__).resolve().parent.absolute()
    if not os.path.isdir(folder_path / simulation_output_dir):
        os.mkdir(folder_path / simulation_output_dir)

    simulation_file = folder_path / simulation_name
    trip_info_file = folder_path / simulation_output_dir / 'tripinfo.xml'
    statistics_file = folder_path / simulation_output_dir / 'statistics_output.xml'
    emissions_file = folder_path / simulation_output_dir / 'emissions_output.xml'
    custom_gui_view_file = folder_path.parent / 'custom_sumo_gui_view.xml'

    vehicle_id = 'veh_passenger'
    vehicle_class = 'passenger'
    net_file = folder_path / 'grid.net.xml'
    trip_file = folder_path / (vehicle_id + '.trips.xml')  # --output-trip-file
    route_file = folder_path / (vehicle_id + '.rou.xml')  # --route-file
    additional_file = folder_path.parent.absolute() / 'vehicle_generator' / 'veh.add.xml'


    def __init__(self, show_gui=False, seed=42, step_delay=0):
        """
        :param show_gui: show gui with simulation? requires `sumo-gui` installed
        :param step_delay: ms between each simulation step (for debugging)
        """
        self.verbose = 1 if show_gui else 0
        self.seed = seed
        self.step_delay = step_delay
        if show_gui:
            self.sumoBinary = checkBinary('sumo-gui')
        else:
            self.sumoBinary = checkBinary('sumo')

    def simulate(
            self,
            gridSize: int,         # grid generation params
            junctionType: int = 1,
            tlType: int = 2,
            edgeMaxSpeed: float = 13.9,
            tlLayout: int = 1,
            keepClearJunction: bool = True,
            edgeType: int = 1,
            edgeLength: float = 50,
            numberOfLanes: int = 1,
            edgePriority: int = 0,
            begin_time: float = 0,  # trip generation params
            end_time: float = 3600,
            period: float = 10,
            binomial: int = 1,
            fringe_factor: float = 10,
            use_binomial: bool = True
    ):
        """
        The user function that feeds into emukit.

        :param gridSize: The size of the grid (the number of junctions on one side)
                Discrete variable, Domain [2, +inf]
        :param junctionType: How the traffic is regualted in the junctions, explaination of the different types can be found at https://sumo.dlr.de/docs/Networks/PlainXML.html#node_descriptions
                Discrete variable, Domain can be seen in the enums.py file
        :param tlType: An optional type for the traffic light algorithm (see https://sumo.dlr.de/docs/Networks/PlainXML.html#node_descriptions)
                Discrete variable, Domain can be seen in the enums.py file
        :param tlLayout: An optional layout for the traffic light plan (see https://sumo.dlr.de/docs/Networks/PlainXML.html#node_descriptions)
                Discrete variable, Domain can be seen in the enums.py file
        :param keepClearJunction: Whether the junction-blocking-heuristic should be activated at the junctions
                Boolean varaible
        :param edgeType: edge type for the roads, from those specified in the grid_plain_xml/edge_types file, this parameter is currently unused as it is overwritten by numLanes, speed and priority parameters
                Discrete variable, Domain can be seen in the enums.py file
        :param edgeLength: The length of the roads in the network
                Continuous variable, Domain [1, +inf]
        :param numberOfLanes: The number of lanes for the roads in the network
                Discrete variable, Domain [1, +inf]
        :param edgeMaxSpeed: The maximum speed possible for the edges in the network
                Continuous variable, Domain [0, +inf]
        :param edgePriority: The priority of the edges in the network, currently useless as all the edges are set to the same priority
                Discrete variable, Domain [0, +inf]

        :return: dictionary containing relevant outputs such as trip time, and total carbon emissions
        """

        # generate the sumo network
        GridGenerator.generate_grid_net(
            gridSize, junctionType,
            tlType, tlLayout,
            keepClearJunction,
            edgeType, edgeLength,
            numberOfLanes, edgeMaxSpeed,
            edgePriority
        )

        # generate trips in generated network
        RandomTripGenerator.generate_random_trips(
            net_file=Simulator.net_file,
            trip_file=Simulator.trip_file,
            route_file=Simulator.route_file,
            additional_file=Simulator.additional_file,
            vehicle_id=Simulator.vehicle_id,
            vehicle_class=Simulator.vehicle_class,
            begin_time=begin_time,
            end_time=end_time,
            period=period,
            binomial=binomial,
            fringe_factor=fringe_factor,
            use_binomial=use_binomial,
            seed=self.seed,
        )

        # traci starts sumo as a subprocess and then this script connects and runs
        traci.start([
            self.sumoBinary,
            # '--configuration-file', Simulator.simulation_file,
            '--net-file', self.net_file,
            '--route-files', self.route_file,
            '--start',
            '--seed', str(self.seed),
            '--delay', str(self.step_delay),
            '--gui-settings-file', self.custom_gui_view_file,
            '--quit-on-end',
            '--tripinfo-output', self.trip_info_file,
            '--statistics-output', self.statistics_file,
            '--emission-output', self.emissions_file
        ])

        self.run()

        emissions = self.parse_emissions_output()
        statistics = self.parse_statistics_output()

        return {**emissions, **statistics}


    def parse_emissions_output(self):
        out = {'CO': 0, 'CO2': 0, 'HC':0, 'NOx': 0, 'PMx': 0,
               'fuel': 0, 'noise': 0, 'num_emissions_samples': 0}
        emissions_output = parse_sumo_output(self.emissions_file, ['vehicle'])
        for sample in emissions_output:
            out['CO'] += float(sample.CO)
            out['CO2'] += float(sample.CO2)
            out['HC'] += float(sample.HC)
            out['NOx'] += float(sample.NOx)
            out['PMx'] += float(sample.PMx)
            out['fuel'] += float(sample.fuel)
            out['noise'] += float(sample.noise)
            out['num_emissions_samples'] += 1

        return out

    def parse_statistics_output(self):
        statistics_output = parse_sumo_output(
            self.statistics_file,
            ['vehicleTripStatistics']
        )
        stat = next(statistics_output)  # only one sample
        out = {'departDelay': float(stat.departDelay),
               'departDelayWaiting': float(stat.departDelayWaiting),
               'duration': float(stat.duration),
               'routeLength': float(stat.routeLength),
               'speed': float(stat.speed),
               'timeLoss': float(stat.timeLoss),
               'waitingTime': float(stat.waitingTime)}

        return out

    def run(self):
        """ traci control loop that runs the simulation """
        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            if self.verbose: print(step)
            step += 1
        traci.close()
        sys.stdout.flush()


if __name__ == '__main__':
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('--showgui', action='store_true',
                          default=True, help='run the commandline version of sumo')
    options, args = opt_parser.parse_args()

    simulator = Simulator(options.showgui, step_delay=30)
    out = simulator.simulate(4)
    print(out)
