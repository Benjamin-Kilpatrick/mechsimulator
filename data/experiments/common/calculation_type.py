from enum import Enum


class CalculationType(Enum):
    OUTCOME = 0
    PATHWAY = 1
    SENSITIVITY = 2

    INVALID = -1

