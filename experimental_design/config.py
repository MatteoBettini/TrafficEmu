from emukit.core import ParameterSpace, ContinuousParameter, DiscreteParameter
from statistics import mean
from easydict import EasyDict as edict
import numpy as np


def __find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

__C = edict()
# Consumers can get config by: from experimental_design.config import cfg
cfg = __C

# Parameter Space Options
__C.PARAMETERS_OPTS = edict()

__C.PARAMETERS_OPTS.GRID_SIZE = [3, 4, 5, 6, 7, 8, 9, 10]
__C.PARAMETERS_OPTS.EDGE_MAX_SPEED = [8, 20]  # 28.8 km/h to 72 km/h
__C.PARAMETERS_OPTS.NUM_LANES = [1, 2, 3]
__C.PARAMETERS_OPTS.ACCEL = [1., 3]  # 1. m/s^2 to 3 m/s^2

# Parameters
__C.PARAMETERS = edict()

__C.PARAMETERS.GRID_SIZE = DiscreteParameter('gridSize',
    domain=__C.PARAMETERS_OPTS.GRID_SIZE)
__C.PARAMETERS.EDGE_MAX_SPEED = ContinuousParameter('edgeMaxSpeed',
    min_value=min(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED),
    max_value=max(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED))
__C.PARAMETERS.NUM_LANES = DiscreteParameter('numberOfLanes',
    domain=__C.PARAMETERS_OPTS.NUM_LANES)
__C.PARAMETERS.ACCEL = ContinuousParameter('accel',
    min_value=min(__C.PARAMETERS_OPTS.ACCEL),
    max_value=max(__C.PARAMETERS_OPTS.ACCEL))

# OFAT Parameters
__C.OFAT = edict()

__C.OFAT.GRID_SIZE = DiscreteParameter('gridSize',
    domain=[__find_nearest(__C.PARAMETERS_OPTS.GRID_SIZE, mean(__C.PARAMETERS_OPTS.GRID_SIZE))])
__C.OFAT.EDGE_MAX_SPEED = ContinuousParameter('edgeMaxSpeed',
    min_value=mean(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED),
    max_value=mean(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED))
__C.OFAT.NUM_LANES = DiscreteParameter('numberOfLanes',
    domain=[__find_nearest(__C.PARAMETERS_OPTS.NUM_LANES, mean(__C.PARAMETERS_OPTS.NUM_LANES))])
__C.OFAT.ACCEL = ContinuousParameter('accel',
    min_value=mean(__C.PARAMETERS_OPTS.ACCEL),
    max_value=mean(__C.PARAMETERS_OPTS.ACCEL))

# Human readable parameter names
__C.NAMES = edict()

__C.NAMES.GRID_SIZE = 'Grid Size'
__C.NAMES.EDGE_MAX_SPEED = 'Edge Max Speed (m/s)'
__C.NAMES.NUM_LANES = 'Number of Lanes'
__C.NAMES.ACCEL = 'Acceleration (m/s$^2$)'


def get_parameter_space():
    gridSize = __C.PARAMETERS.GRID_SIZE
    edgeMaxSpeed = __C.PARAMETERS.EDGE_MAX_SPEED
    numberOfLanes = __C.PARAMETERS.NUM_LANES
    accel = __C.PARAMETERS.ACCEL

    return ParameterSpace([gridSize, edgeMaxSpeed, numberOfLanes, accel])


def get_ofat_parameter_spaces():

    def get_parameter(name: str, mode: str):
        if mode == 'locked':
            return __C['OFAT'][name]
        else:
            return __C['PARAMETERS'][name]

    parameter_spaces = []
    for i in __C.PARAMETERS_OPTS.items():
        parameter_space = []
        for j in __C.PARAMETERS_OPTS.items():
            if i[0] == j[0]:
                mode = 'variable'
            else:
                mode = 'locked'
            parameter_space.append(get_parameter(j[0], mode))
        parameter_spaces.append(
            {
                'space': ParameterSpace(parameter_space),
                'name': __C.NAMES[i[0]]
            }
        )
    return parameter_spaces
