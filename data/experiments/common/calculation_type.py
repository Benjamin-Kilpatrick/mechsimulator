from enum import Enum


class CalculationType(Enum):
    """Enum for calculation types"""
    OUTCOME = 0
    """outcome"""
    PATHWAY = 1
    """pathway"""
    SENSITIVITY = 2
    """sensitivity"""

    INVALID = -1
    """invalid calculation"""
