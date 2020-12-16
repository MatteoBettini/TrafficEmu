import os
import sys
import subprocess
from pathlib import Path

if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
else:
    print("SUMO_HOME must be declared")
    sys.exit(1)


folder_path = Path(__file__).resolve().parent.absolute() 
net_file = folder_path.parent.absolute() / 'grid_simulation' / 'grid.net.xml' # -n
trip_file = folder_path / 'trips.trips.xml' # --output-trip-file
route_file = folder_path / 'routes.rou.xml' # --route-file

end_time = 3600 # -e
trip_interval = 0 # -b
period = 10 # --period <FLOAT>. By default this generates vehicles with a constant period and arrival rate of (1/period) per second. By using values below 1, multiple arrivals per second can be achieved.
use_binomial=True
binomial = 1 # --binomial <INT> he number of departures per seconds will be drawn from a binomial 
                         # distribution with n=N and p=PERIOD/N where PERIOD is the argument given to 
                         # option --period.

# To let n vehicles depart between times t0 and t1 set the options
# -b t0 -e t1 -p ((t1 - t0) / n)

seed=None

fringe_factor = 10 # --fringe-factor <FLOAT>. EG If the value 10 is given, edges that have no successor or no predecessor will be 10 times more likely to be chosen as start- or endpoint of a trip. This is useful when modelling through-traffic which starts and ends at the outside of the simulated area.

python_command = ['python', 
    os.environ['SUMO_HOME'] + '/tools/randomTrips.py', 
    '--net-file', str(net_file),
    '--output-trip-file', str(trip_file),
    '--route-file', str(route_file),
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