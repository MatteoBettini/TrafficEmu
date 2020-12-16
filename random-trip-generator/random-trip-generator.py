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
        grid_net_file: Path, 
        trip_file: Path, 
        route_file: Path,
        end_time: float = 3600,
        begin_time: float = 0,
        period: float = 10,
        binomial: int = 1,
        fringe_factor: float = 10,
        use_binomial: bool = True,
        seed: int = None,
        ):
        """[summary]

        Args:
            grid_net_file (Path): [description]
            trip_file (Path): [description]
            route_file (Path): [description]
            end_time (float, optional): [description]. Defaults to 3600.
            begin_time (float, optional): [description]. Defaults to 0.
            period (float, optional): Generates vehicles with a constant period and arrival rate of (1/period) per second. By using values below 1, multiple arrivals per second can be achieved.. Defaults to 10.
            binomial (int, optional): The number of departures per seconds will be drawn from a binomial distribution with n=N and p=PERIOD/N where PERIOD is the argument given to option `period`. Defaults to 1.
            fringe_factor (float, optional): If the value 10 is given, edges that have no successor or no predecessor will be 10 times more likely to be chosen as start- or endpoint of a trip. This is useful when modelling through-traffic which starts and ends at the outside of the simulated area. Defaults to 10.
            use_binomial (bool, optional): [description]. Defaults to True.
            seed (int, optional): [description]. Defaults to None.
        """

        # To let n vehicles depart between times t0 and t1 set the options
        # --begin t0 --end t1 --period ((t1 - t0) / n)

        python_command = ['python', 
            os.environ['SUMO_HOME'] + '/tools/randomTrips.py', 
            '--net-file', str(grid_net_file),
            '--output-trip-file', str(trip_file),
            '--route-file', str(route_file),
            '--begin', str(float(begin_time)),
            '--end', str(float(end_time)),
            '--allow-fringe', 
            '--fringe-factor', str(float(fringe_factor)),
            '--validate',
            '--vehicle-class', 'passenger',
            '--edge-permission', 'passenger',
            '--period', str(float(period))]

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
    folder_path = Path(__file__).resolve().parent.absolute() 
    grid_net_file = folder_path.parent.absolute() / 'grid_simulation' / 'grid.net.xml'
    trip_file = folder_path / 'trips.trips.xml' # --output-trip-file
    route_file = folder_path / 'routes.rou.xml' # --route-file

    RandomTripGenerator.generate_random_trips(
        grid_net_file=grid_net_file,
        trip_file=trip_file,
        route_file=route_file
        )