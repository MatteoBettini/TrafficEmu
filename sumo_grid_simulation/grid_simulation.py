import optparse
from sumolib import checkBinary
from sumolib.output import parse as parse_sumo_output
import traci

from sumo_grid_simulation.simulation_scripts.utils import *

from sumo_grid_simulation.simulation_scripts.grid_generator.grid_generator import GridGenerator
from sumo_grid_simulation.simulation_scripts.random_trip_generator.vehicle_generator import VehicleGenerator, Vehicle
from sumo_grid_simulation.simulation_scripts.random_trip_generator.random_trip_generator import RandomTripGenerator

checkSumoHome()

class Simulator:


    vehicle_id = 'veh_passenger'

    def __init__(self, show_gui=False, seed=42, step_delay: int = 0,
                 begin_time: float = 0, end_time: float = 3600,
                 trips_generator_period: float = 10, trips_generator_fringe_factor: float = 10,
                 trips_generator_binomial: int = 1, trips_generator_use_binomial: bool = True):
        """
        :param show_gui: show gui with simulation? requires `sumo-gui` installed
        :param step_delay: ms between each simulation step (for debugging)
        """
        self.verbose = 1 if show_gui else 0
        self.seed = seed
        self.step_delay = step_delay

        self.begin_time = begin_time
        self.end_time = end_time

        self.trips_generator_period = trips_generator_period
        self.trips_generator_fringe_factor = trips_generator_fringe_factor
        self.trips_generator_binomial = trips_generator_binomial
        self.trips_generator_use_binomial = trips_generator_use_binomial

        if show_gui:
            self.sumoBinary = checkBinary('sumo-gui')
        else:
            self.sumoBinary = checkBinary('sumo')

        if not os.path.isdir(PathUtils.simulation_output_files_folder):
            os.mkdir(PathUtils.simulation_output_files_folder)

    def simulate(
            self,
            # grid generation params
            gridSize: int,
            junctionType: int = 1,
            tlType: int = 2,
            tlLayout: int = 1,
            edgeMaxSpeed: float = 13.9,
            keepClearJunction: bool = True,
            edgeType: int = 1,
            edgeLength: float = 50,
            numberOfLanes: int = 1,
            edgePriority: int = 0,
            # trip generation params
            vehicleClass: int = 1,  # 1 is passenger
            emissionClass: int = 3, # 3 is PC_G_EU4
            accel: float = 2.6,
            decel: float = 4.5,
            maxSpeed: float = 55.55,
            speedFactor: float = 1.0,
            speedDev: float = 0.1,
    ):
        """
        The user function that feeds into emukit.

        :param speedDev:
        :param speedFactor:
        :param maxSpeed:
        :param decel:
        :param emissionClass:
        :param vehicleClass:
        :param accel:
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


        VehicleGenerator.generate_additional_file([Vehicle(
            id=Simulator.vehicle_id,
            vehicle_class=vehicleClass,
            emission_class=emissionClass,
            accel=accel,
            decel=decel,
            max_speed=maxSpeed,
            speed_factor=speedFactor,
            speed_dev=speedDev
        )])

        # generate trips in generated network
        RandomTripGenerator.generate_random_trips(
            vehicle_id=Simulator.vehicle_id,
            vehicle_class=vehicleClass,
            seed=self.seed,
            begin_time=self.begin_time,
            end_time=self.end_time,
            period=self.trips_generator_period,
            binomial=self.trips_generator_binomial,
            fringe_factor=self.trips_generator_fringe_factor,
            use_binomial=self.trips_generator_use_binomial,
        )

        # traci starts sumo as a subprocess and then this script connects and runs
        traci.start([
            self.sumoBinary,
            # '--configuration-file', Simulator.simulation_file,
            '--net-file', str(PathUtils.grid_net_file),
            '--route-files', str(PathUtils.routes_file),
            '--start',
            '--seed', str(self.seed),
            '--delay', str(self.step_delay),
            '--gui-settings-file', str(PathUtils.gui_view_file),
            '--quit-on-end',
            '--tripinfo-output', str(PathUtils.trip_info_file),
            '--statistics-output', str(PathUtils.statistics_file),
            '--emission-output', str(PathUtils.emissions_file)
        ])

        self.run()

        emissions = self.parse_emissions_output()
        statistics = self.parse_statistics_output()

        return {**emissions, **statistics}


    @staticmethod
    def parse_emissions_output():
        out = {'CO': 0, 'CO2': 0, 'HC':0, 'NOx': 0, 'PMx': 0,
               'fuel': 0, 'noise': 0, 'num_emissions_samples': 0}
        emissions_output = parse_sumo_output(PathUtils.emissions_file, ['vehicle'])
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

    @staticmethod
    def parse_statistics_output():
        statistics_output = parse_sumo_output(
            PathUtils.statistics_file,
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
    out = simulator.simulate(6)
    print(out)
