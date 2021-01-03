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

__C.PARAMETERS_OPTS.GRID_SIZE = [3, 20]
__C.PARAMETERS_OPTS.EDGE_MAX_SPEED = [1, 25]
__C.PARAMETERS_OPTS.MAX_SPEED = [1, 25]
__C.PARAMETERS_OPTS.EDGE_LENGTH = [30, 200]
__C.PARAMETERS_OPTS.NUM_LANES = [1, 2, 3]
__C.PARAMETERS_OPTS.ACCEL = [1., 6.]

# Parameters
__C.PARAMETERS = edict()

__C.PARAMETERS.GRID_SIZE = ContinuousParameter('gridSize', min_value=min(__C.PARAMETERS_OPTS.GRID_SIZE), max_value=max(__C.PARAMETERS_OPTS.GRID_SIZE))
__C.PARAMETERS.EDGE_MAX_SPEED = ContinuousParameter('edgeMaxSpeed', min_value=min(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED), max_value=max(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED))
__C.PARAMETERS.MAX_SPEED = ContinuousParameter('maxSpeed', min_value=min(__C.PARAMETERS_OPTS.MAX_SPEED), max_value=max(__C.PARAMETERS_OPTS.MAX_SPEED))
__C.PARAMETERS.EDGE_LENGTH = ContinuousParameter('edgeLength', min_value=min(__C.PARAMETERS_OPTS.EDGE_LENGTH), max_value=max(__C.PARAMETERS_OPTS.EDGE_LENGTH))
__C.PARAMETERS.NUM_LANES = DiscreteParameter('numberOfLanes', domain=__C.PARAMETERS_OPTS.NUM_LANES)
__C.PARAMETERS.ACCEL = ContinuousParameter('accel', min_value=min(__C.PARAMETERS_OPTS.ACCEL), max_value=max(__C.PARAMETERS_OPTS.ACCEL))

# OFAT Parameters
__C.OFAT = edict()

__C.OFAT.GRID_SIZE = ContinuousParameter('gridSize', min_value=mean(__C.PARAMETERS_OPTS.GRID_SIZE), max_value=mean(__C.PARAMETERS_OPTS.GRID_SIZE))
__C.OFAT.EDGE_MAX_SPEED = ContinuousParameter('edgeMaxSpeed', min_value=mean(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED), max_value=mean(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED))
__C.OFAT.MAX_SPEED = ContinuousParameter('maxSpeed', min_value=mean(__C.PARAMETERS_OPTS.MAX_SPEED), max_value=mean(__C.PARAMETERS_OPTS.MAX_SPEED))
__C.OFAT.EDGE_LENGTH = ContinuousParameter('edgeLength', min_value=mean(__C.PARAMETERS_OPTS.EDGE_LENGTH), max_value=mean(__C.PARAMETERS_OPTS.EDGE_LENGTH))
__C.OFAT.NUM_LANES = DiscreteParameter('numberOfLanes', domain=[__find_nearest(__C.PARAMETERS_OPTS.NUM_LANES, mean(__C.PARAMETERS_OPTS.NUM_LANES))])
__C.OFAT.ACCEL = ContinuousParameter('accel', min_value=mean(__C.PARAMETERS_OPTS.ACCEL), max_value=mean(__C.PARAMETERS_OPTS.ACCEL))


def get_parameter_space():
    gridSize = __C.PARAMETERS.GRID_SIZE
    edgeMaxSpeed = __C.PARAMETERS.EDGE_MAX_SPEED
    maxSpeed = __C.PARAMETERS.MAX_SPEED
    edgeLength = __C.PARAMETERS.EDGE_LENGTH
    numberOfLanes = __C.PARAMETERS.NUM_LANES
    accel = __C.PARAMETERS.ACCEL

    return ParameterSpace([gridSize, edgeMaxSpeed, maxSpeed, edgeLength, numberOfLanes, accel])

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
                mode = 'open'
            else:
                mode = 'locked'
            parameter_space.append(get_parameter(j[0], mode))
        parameter_spaces.append(ParameterSpace(parameter_space))
    return parameter_spaces
