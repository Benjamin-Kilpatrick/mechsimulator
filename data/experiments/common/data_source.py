from enum import Enum


class DataSource(Enum):
    SIMULATION = 0
    """simulation source"""
    MEASURED = 1
    """measured source"""

    INVALID = -1
    """invalid source"""
