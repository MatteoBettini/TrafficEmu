from pathlib import Path
import sys
import os

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.absolute()

def checkSumoHome():
    if 'SUMO_HOME' in os.environ:
        sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
    else:
        print("SUMO_HOME must be declared")
        sys.exit(1)

class PathUtils:

    # FOLDERS

    # Sumo root
    sumo_grid_simulation_folder = get_project_root() / 'sumo_grid_simulation'

    # Second level folder
    simulation_input_files_folder = sumo_grid_simulation_folder / 'simulation_input_files'
    simulation_output_files_folder = sumo_grid_simulation_folder / 'simulation_output_files'
    simulation_scripts_folder = sumo_grid_simulation_folder / 'simulation_scripts'

    # Grid plain xml folder
    grid_plain_xml_folder = simulation_input_files_folder / 'grid_plain_xml'

    # Script folders
    grid_generator_folder = simulation_scripts_folder / 'grid_generator'
    random_trip_generator_folder = simulation_scripts_folder / 'random_trip_generator'



    # FILES

    # Files for the grid
    edge_types_file = grid_plain_xml_folder / 'edge_types.typ.xml'
    edges_file = grid_plain_xml_folder / 'edges.edg.xml'
    nodes_file = grid_plain_xml_folder / 'nodes.nod.xml'
    grid_net_file = simulation_input_files_folder / 'grid.net.xml'

    # Files for the trips
    routes_file = simulation_input_files_folder / 'veh_passenger.rou.xml'
    trips_file = simulation_input_files_folder / 'veh_passenger.trips.xml'
    additional_file = simulation_input_files_folder / 'veh.add.xml'

    # Output files
    emissions_file = simulation_output_files_folder / 'emissions_output.xml'
    statistics_file = simulation_output_files_folder / 'statistics_output.xml'
    trip_info_file = simulation_output_files_folder / 'tripinfo.xml'

    # Sumo configuration files
    sumo_config_file = simulation_input_files_folder / 'grid.sumocfg'
    gui_view_file = simulation_input_files_folder / 'custom_sumo_gui_view.xml'






