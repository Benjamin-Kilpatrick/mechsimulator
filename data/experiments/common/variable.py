from enum import Enum


class Variable(Enum):
    """
    Variable types used in Experiments
    """
    TIME_STEP = 0
    END_TIME = 1
    WAVELENGTH = 2
    ACTIVE_SPECIES = 3
    ABS_COEFFICIENT = 4
    PATH_LENGTH = 5
    IGNITION_DELAY_TARGETS = 6
    IGNITION_DELAY_METHOD = 7
    TARGET_SPECIES = 8
    TEMPERATURE = 9
    PRESSURE = 10
    PHI = 11
    DPDT = 12
    LENGTH = 13
    RES_TIME = 14
    MDOT = 15
    AREA = 16
    VOLUME = 17
    TIME = 18
    V_OF_T = 19
    X_PROFILE = 20
    TIME_PROFILE = 21
    TIME_PROFILE_SETPOINTS = 22
