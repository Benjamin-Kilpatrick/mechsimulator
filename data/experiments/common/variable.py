from enum import Enum


class Variable(Enum):
    """
    Variable types used in Experiments
    """
    TIME_STEP = 0
    """time step"""
    END_TIME = 1
    """end time"""
    WAVELENGTH = 2
    """wavelength"""
    ACTIVE_SPECIES = 3
    """active species"""
    ABS_COEFFICIENT = 4
    """absorption coefficient"""
    PATH_LENGTH = 5
    """path length"""
    IGNITION_DELAY_TARGETS = 6
    """ignition delay targets"""
    IGNITION_DELAY_METHOD = 7
    """ignitiion delay method"""
    TARGET_SPECIES = 8
    """target species"""
    TEMPERATURE = 9
    """temperature"""
    PRESSURE = 10
    """pressure"""
    PHI = 11
    """phi"""
    DPDT = 12
    """dPdT"""
    LENGTH = 13
    """length"""
    RES_TIME = 14
    """res time"""
    MDOT = 15
    """mdot"""
    AREA = 16
    """area"""
    VOLUME = 17
    """volume"""
    TIME = 18
    """time"""
    V_OF_T = 19
    """v of t"""
    X_PROFILE = 20
    """x profile"""
    TIME_PROFILE = 21
    """time profile"""
    TIME_PROFILE_SETPOINTS = 22
    """time profile set points"""
