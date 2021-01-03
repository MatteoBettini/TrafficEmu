from emukit.core import ParameterSpace, ContinuousParameter, DiscreteParameter

def get_parameter_space():
    gridSize = ContinuousParameter('gridSize', min_value=3, max_value=20)
    edgeMaxSpeed = ContinuousParameter('edgeMaxSpeed', min_value=1, max_value=25)
    maxSpeed = ContinuousParameter('maxSpeed', min_value=1, max_value=25)
    edgeLength = ContinuousParameter('edgeLength', min_value=30, max_value=200)
    numberOfLanes = DiscreteParameter('numberOfLanes', domain=[1,2,3])
    accel = ContinuousParameter('accel', 1., 6.)

    return ParameterSpace([gridSize, edgeMaxSpeed, maxSpeed, edgeLength, numberOfLanes, accel])