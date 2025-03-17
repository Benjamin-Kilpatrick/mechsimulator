from enum import Enum


class Reaction(Enum):
    """
    The different types of reactions.
    """
    SHOCKTUBE = 0
    PLUG_FLOW_REACTOR = 1
    JET_STREAM_REACTOR = 2
    RAPID_COMPRESSION_MACHINE = 3
    CONST_T_P = 4
    FREE_FLAME = 5
