from enum import Enum


class Measurement(Enum):
    """
    The different types of measurements
    """

    ABSORPTION = 0
    """absorption"""
    EMISSION = 1
    """emission"""
    IGNITION_DELAY_TIME = 2
    """ignition delay time"""
    OUTLET = 3
    """outlet"""
    ION = 4
    """ion (unimplemented)"""
    PRESSURE = 5
    """pressure"""
    CONCENTRATION = 6
    """concentration"""
    # TODO get the actual name
    LAMINAR_FLAME_SPEED = 7
    """LFS"""
    HALF_LIFE = 8
    """half life"""
