from enum import Enum


class DataSource(Enum):
    SIMULATION = 0
    """simulation source
    Designated as plot or plots in the Job file.
    """
    MEASURED = 1
    """measured source
    Designated as exp or exps in the Job file.
    """

    INVALID = -1
    """invalid source"""
