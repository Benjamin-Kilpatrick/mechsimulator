from enum import Enum


class IDTMethod(Enum):
    BASELINE_EXTRAPOLATION = 0
    MAX_SLOPE = 1
    MAX_VALUE = 2