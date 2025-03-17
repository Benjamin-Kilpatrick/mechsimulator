from enum import Enum


class FileType(Enum):
    """
    File type is used for Experiment files and Job files since they can both be read interchangeably
    """
    EXCEL = 0
    YAML = 1
    INVALID = -1
