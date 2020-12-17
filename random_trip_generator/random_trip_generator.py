import os
import sys
import subprocess
from pathlib import Path

if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
else:
    print("SUMO_HOME must be declared")
    sys.exit(1)


class RandomTripGenerator:

    @staticmethod
    def generate_random_trips(
        net_file: Path,
        trip_file: Path,
        route_file: Path,
        additional_file: Path,
        vehicle_id: str,
        vehicle_class: str,
        begin_time: float = 0,
        end_time: float = 3600,
        period: float = 10,
        binomial: int = 1,
        fringe_factor: float = 10,
        use_binomial: bool = True,
        seed: int = None,
    ):
        """Creates random trips for a single type of vehicle.

        Args:
            net_file (Path): [Input] Location of the .net.xml file.
            trip_file (Path): [Output] Location of the .trip.xml file.
            route_file (Path): [Output] Location of the .rou.xml and .rou.alt.xml files.
            additional_file (Path): [Input] Location of the .add.xml file with the vType description.
            vehicle_id (str): ID of the vehicle type, for example 'slow_passenger'
            vehicle_class (str): vClass of the vehicle, for example 'passenger'
            begin_time (float, optional): Simulation begin time in ms. Defaults to 0.
            end_time (float, optional): Simulation end time in ms. Defaults to 3600.
            period (float, optional): Generates vehicles with a constant period and arrival rate of (1/period) per second. By using values below 1, multiple arrivals per second can be achieved.. Defaults to 10.
            binomial (int, optional): The number of departures per seconds will be drawn from a binomial distribution with n=N and p=PERIOD/N where PERIOD is the argument given to option `period`. Defaults to 1.
            fringe_factor (float, optional): If the value 10 is given, edges that have no successor or no predecessor will be 10 times more likely to be chosen as start- or endpoint of a trip. This is useful when modelling through-traffic which starts and ends at the outside of the simulated area. Defaults to 10.
            use_binomial (bool, optional): Defaults to True.
            seed (int, optional): Seed for the generator. Leave as None for random seed. Defaults to None.
        """

        # To let n vehicles depart between times t0 and t1 set the options
        # --begin t0 --end t1 --period ((t1 - t0) / n)

        python_command = ['python',
                          os.environ['SUMO_HOME'] + '/tools/randomTrips.py',
                          '--net-file', str(net_file),
                          '--output-trip-file', str(trip_file),
                          '--route-file', str(route_file),
                          '--begin', str(float(begin_time)),
                          '--end', str(float(end_time)),
                          '--allow-fringe',
                          '--fringe-factor', str(float(fringe_factor)),
                          '--validate',
                          '--additional-files', str(additional_file),
                          '--trip-attributes', 'type=\"' + str(vehicle_id) + '\"',
                          '--edge-permission', str(vehicle_class),
                          '--period', str(float(period)),
                          #   '--verbose'
                          ]

        if seed is not None:
            python_command.append('--seed')
            python_command.append(str(int(seed)))

        if use_binomial is True:
            python_command.append('--binomial')
            python_command.append(str(int(binomial)))

        process = subprocess.Popen(python_command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output, error = process.communicate()

        if output:
            print(output.decode())
        if error:
            print(error.decode())


if __name__ == "__main__":
    vehicle_id = 'veh_passenger'
    vehicle_class = 'passenger'
    folder_path = Path(__file__).resolve().parent.absolute()
    net_file = folder_path.parent.absolute() / 'grid_simulation' / 'grid.net.xml'
    trip_file = folder_path / (vehicle_id + '.trips.xml')  # --output-trip-file
    route_file = folder_path / (vehicle_id + '.rou.xml')  # --route-file
    additional_file = folder_path.parent.absolute() / 'vehicle_generator' / 'veh.add.xml'

    RandomTripGenerator.generate_random_trips(
        net_file=net_file,
        trip_file=trip_file,
        route_file=route_file,
        additional_file=additional_file,
        vehicle_id=vehicle_id,
        vehicle_class=vehicle_class
    )
