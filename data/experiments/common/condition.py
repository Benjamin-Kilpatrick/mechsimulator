from enum import Enum

import pint

from data.experiments.common.idt_method import IDTMethod
from data.experiments.common.idt_target import IDTTarget


class Condition(Enum):
    """
    Variable types used in Experiments
    """
    TIME_STEP = (0, pint.Quantity)
    """time step"""
    END_TIME = (1, pint.Quantity)
    """end time"""
    WAVELENGTH = (2, pint.Quantity)
    """wavelength"""

    # to be removed
    # ACTIVE_SPECIES = 3
    # """active species"""

    ABS_COEFFICIENT = (4, pint.Quantity)
    """absorption coefficient"""
    PATH_LENGTH = (5, pint.Quantity)
    """path length"""

    # to be removed
    IGNITION_DELAY_TARGET = (6, IDTTarget)
    """ignition delay objective"""

    IGNITION_DELAY_METHOD = (7, IDTMethod)
    """ignitiion delay method"""

    # not actually a variable
    # TARGET_SPECIES = 8
    # """target species"""

    TEMPERATURE = (9, pint.Quantity)
    """temperature"""
    PRESSURE = (10, pint.Quantity)
    """pressure"""
    PHI = (11, pint.Quantity)
    """phi"""
    DPDT = (12, pint.Quantity)
    """dPdT"""
    LENGTH = (13, pint.Quantity)
    """length"""
    RES_TIME = (14, pint.Quantity)
    """res time"""
    MDOT = (15, pint.Quantity)
    """mdot"""
    AREA = (16, pint.Quantity)
    """area"""
    VOLUME = (17, pint.Quantity)
    """volume"""
    TIME = (18, pint.Quantity)
    """time"""
    V_OF_T = (19, pint.Quantity)
    """v of t"""
    X_PROFILE = (20, pint.Quantity)
    """x profile"""
    TIME_PROFILE = (21, pint.Quantity)
    """time profile"""
    TIME_PROFILE_SETPOINTS = (22, pint.Quantity)
    """time profile set points"""
