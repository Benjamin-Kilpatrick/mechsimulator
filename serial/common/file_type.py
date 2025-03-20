from enum import Enum


class FileType(Enum):
    """
    File type of input files
    """
    EXCEL = 0
    """excel file (.xlsl)"""
    YAML = 1
    """yaml file (.yaml)"""
    INVALID = -1
    """invalid file type"""
