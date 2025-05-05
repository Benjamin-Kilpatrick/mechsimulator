from enum import Enum


class EnvPath(Enum):
    """
    This enum contains the names of environment variables used to identify the path to various directories where data
    files are loaded from. The environment variables are loaded from the .env file by the `get_full_path` function in
    serial.common.utils.
    """
    DOCS = 'DOCS_PATH'
    """documentation path"""
    EXPERIMENT = 'EXPERIMENT_PATH'
    """experiment files path"""
    MECHANISM = 'MECHANISM_PATH'
    """mechanism files path"""
    JOB = 'JOB_PATH'
    """job files path"""
    SPECIES = 'SPECIES_PATH'
    """species files path"""
    RESULT = 'RESULT_PATH'
    """output files directory path"""
