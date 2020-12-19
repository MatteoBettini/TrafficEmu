import os
import subprocess


from sumo_grid_simulation.simulation_scripts.enums import VehicleClasses
from sumo_grid_simulation.simulation_scripts.utils import PathUtils

class RandomTripGenerator:

    @staticmethod
    def generate_random_trips(
        vehicle_id: str,
        vehicle_class: int,
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


        if VehicleClasses.get_by_number(vehicle_class) is None:
            raise TypeError(
                'vehicle_class must be an instance of VehicleClasses Enum')
        vehicle_class = VehicleClasses.get_by_number(vehicle_class)


        python_command = ['python',
                          os.environ['SUMO_HOME'] + '/tools/randomTrips.py',
                          '--net-file', str(PathUtils.grid_net_file),
                          '--output-trip-file', str(PathUtils.trips_file),
                          '--route-file', str(PathUtils.routes_file),
                          '--begin', str(float(begin_time)),
                          '--end', str(float(end_time)),
                          '--allow-fringe',
                          '--fringe-factor', str(float(fringe_factor)),
                          '--validate',
                          '--additional-files', str(PathUtils.additional_file),
                          '--trip-attributes', 'type=\"' + str(vehicle_id) + '\"',
                          '--edge-permission', str(vehicle_class.tag),
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

