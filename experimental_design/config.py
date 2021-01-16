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

__C.PARAMETERS_OPTS.GRID_SIZE = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
__C.PARAMETERS_OPTS.EDGE_MAX_SPEED = [8, 19]
__C.PARAMETERS_OPTS.EDGE_LENGTH = [30, 70] 
__C.PARAMETERS_OPTS.NUM_LANES = [1, 2, 3]
__C.PARAMETERS_OPTS.ACCEL = [1.5, 5]

# Parameters
__C.PARAMETERS = edict()

__C.PARAMETERS.GRID_SIZE = DiscreteParameter('gridSize',
    domain=__C.PARAMETERS_OPTS.GRID_SIZE)
__C.PARAMETERS.EDGE_MAX_SPEED = ContinuousParameter('edgeMaxSpeed',
    min_value=min(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED),
    max_value=max(__C.PARAMETERS_OPTS.EDGE_MAX_SPEED))
__C.PARAMETERS.EDGE_LENGTH = ContinuousParameter('edgeLength',
    min_value=min(__C.PARAMETERS_OPTS.EDGE_LENGTH),
    max_value=max(__C.PARAMETERS_OPTS.EDGE_LENGTH))
__C.PARAMETERS.NUM_LANES = DiscreteParameter('numberOfLanes',
    domain=__C.PARAMETERS_OPTS.NUM_LANES)
__C.PARAMETERS.ACCEL = ContinuousParameter('accel',
    min_value=min(__C.PARAMETERS_OPTS.ACCEL),
    max_value=max(__C.PARAMETERS_OPTS.ACCEL))

# OFAT Parameters
__C.OFAT = edict()

__C.OFAT.GRID_SIZE = DiscreteParameter('gridSize',
    domain=[20])
__C.OFAT.EDGE_MAX_SPEED = ContinuousParameter('edgeMaxSpeed',
    min_value=25,
    max_value=25)
__C.OFAT.EDGE_LENGTH = ContinuousParameter('edgeLength',
    min_value=70,
    max_value=70)
__C.OFAT.NUM_LANES = DiscreteParameter('numberOfLanes',
    domain=[1])
__C.OFAT.ACCEL = ContinuousParameter('accel',
    min_value=1.5,
    max_value=1.5)

__C.OFAT.TIME = edict()

__C.OFAT.TIME.GRID_SIZE = DiscreteParameter('gridSize',
    domain=[20])
__C.OFAT.TIME.EDGE_MAX_SPEED = ContinuousParameter('edgeMaxSpeed',
    min_value=8,
    max_value=8)
__C.OFAT.TIME.EDGE_LENGTH = ContinuousParameter('edgeLength',
    min_value=70,
    max_value=70)
__C.OFAT.TIME.NUM_LANES = DiscreteParameter('numberOfLanes',
    domain=[1])
__C.OFAT.TIME.ACCEL = ContinuousParameter('accel',
    min_value=1.5,
    max_value=1.5)

__C.OFAT.CO2 = edict()

__C.OFAT.CO2.GRID_SIZE = DiscreteParameter('gridSize',
    domain=[20])
__C.OFAT.CO2.EDGE_MAX_SPEED = ContinuousParameter('edgeMaxSpeed',
    min_value=25,
    max_value=25)
__C.OFAT.CO2.EDGE_LENGTH = ContinuousParameter('edgeLength',
    min_value=70,
    max_value=70)
__C.OFAT.CO2.NUM_LANES = DiscreteParameter('numberOfLanes',
    domain=[1])
__C.OFAT.CO2.ACCEL = ContinuousParameter('accel',
    min_value=1.5,
    max_value=1.5)

# Human readable parameter names
__C.NAMES = edict()

__C.NAMES.GRID_SIZE = 'Grid Size'
__C.NAMES.EDGE_MAX_SPEED = 'Edge Max Speed'# (m/s)'
__C.NAMES.EDGE_LENGTH = 'Edge Length'# (m)'
__C.NAMES.NUM_LANES = 'Number of Lanes'
__C.NAMES.ACCEL = 'Acceleration'# (m/s$^2$)'


def get_parameter_space():
    return ParameterSpace([i for i in __C.PARAMETERS.values()])

def get_ofat_parameter_spaces_from_results(df):
    def get_parameter(name: str, mode: str, idx: int):
        if mode == 'locked':
            return DiscreteParameter(name, domain=[df.iloc[0][idx]])
        else:
            return __C['PARAMETERS'][name]

    parameter_spaces = []
    for i in __C.PARAMETERS_OPTS.items():
        parameter_space = []
        for idx, j in enumerate(__C.PARAMETERS_OPTS.items()):
            if i[0] == j[0]:
                mode = 'variable'
            else:
                mode = 'locked'
            parameter_space.append(get_parameter(j[0], mode, idx))
        parameter_spaces.append(
            {
                'space': ParameterSpace(parameter_space),
                'name': __C.NAMES[i[0]]
            }
        )
    return parameter_spaces

def get_ofat_parameter_spaces(variant=None):
    def get_parameter(name: str, mode: str):
        if mode == 'locked':
            if variant==None:
                return __C['OFAT'][name]
            else:
                return __C['OFAT'][variant][name]
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
