from enum import Enum


class EnvPath(Enum):
    """
    This enum contains the names of environment variables used to identify the path to various directories where data
    files are loaded from. The environment variables are loaded from the .env file by the `get_full_path` function in
    serial.common.utils.
    """
    DOCS = 'DOCS_PATH'
    EXPERIMENT = 'EXPERIMENT_PATH'
    MECHANISM = 'MECHANISM_PATH'
    JOB = 'JOB_PATH'
    SPECIES = 'SPECIES_PATH'
    RESULT = 'RESULT_PATH'
