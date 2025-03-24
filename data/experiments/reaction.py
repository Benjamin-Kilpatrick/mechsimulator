from enum import Enum


class Reaction(Enum):
    """
    The different types of reactions
    """
    SHOCKTUBE = 0
    """shocktube"""
    PLUG_FLOW_REACTOR = 1
    """plug flow reactor"""
    JET_STREAM_REACTOR = 2
    """jet stream reactor"""
    RAPID_COMPRESSION_MACHINE = 3
    """rapid compression machine"""
    CONST_T_P = 4
    """constant time and pressure"""
    FREE_FLAME = 5
    """free flame"""
