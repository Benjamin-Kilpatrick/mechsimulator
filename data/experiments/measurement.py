from enum import Enum


class Measurement(Enum):
    """
    The different types of measurement
    """
    ABSORPTION = 0
    EMISSION = 1
    IGNITION_DELAY_TIME = 2
    OUTLET = 3
    ION = 4
    PRESSURE = 5
    CONCENTRATION = 6
    LFS = 7
    HALF_LIFE = 8
