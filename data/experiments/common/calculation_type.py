from enum import Enum


class CalculationType(Enum):
    """Enum for calculation types"""
    OUTCOME = 0
    PATHWAY = 1
    SENSITIVITY = 2

    INVALID = -1

#CalculationType.OUTCOME = CalculationType.OUTCOME