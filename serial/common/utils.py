import os
from typing import Dict, Optional, Union

import numpy
import pint
from pint import Quantity
from typing_extensions import Self

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.common.condition import Condition
from data.experiments.measurement import Measurement
from data.experiments.reaction import Reaction
from serial.common.env_path import EnvPath
from serial.common.file_type import FileType


class Utils:
    """
    A static class that contains utility functions used in the serial package.
    """
    @staticmethod
    def get_file_type(filename: str) -> FileType:
        """
        Get the file type from a filename or path
        :param filename: filename or path
        :return: file type or INVALID if not '.yaml' or '.xlsx'
        """
        if filename.endswith('.yaml'):
            return FileType.YAML
        if filename.endswith('.xlsx'):
            return FileType.EXCEL
        return FileType.INVALID

    @staticmethod
    def parse_datasource(source: str) -> DataSource:
        """
        Mapping the source str to DataSource enum. Will default to DataSource.INVALID if the str is
        not in the mapping.
        :param source: source str
        :return: DataSource
        """
        if source == 'plot' or source == 'plots':
            return DataSource.SIMULATION
        if source == 'exp' or source == 'exps':
            return DataSource.MEASURED
        return DataSource.INVALID

    @staticmethod
    def parse_calculation_type(calculation_type: str) -> CalculationType:
        """
        Mapping the calculation_type str to CalculationType enum. Will default to CalculationType.INVALID if the str is
        not in the mapping.
        :param calculation_type: calculation_type str
        :return: CalculationType
        """
        if calculation_type == 'outcome':
            return CalculationType.OUTCOME
        if calculation_type == 'pathways':
            return CalculationType.PATHWAY
        if calculation_type == 'sens':
            return CalculationType.SENSITIVITY
        return CalculationType.INVALID

    @staticmethod
    def get_full_path(path: EnvPath, filename: str) -> str:
        """
        Takes an environment variable name enum and a file name. Returns the full path to the file.
        This function relies upon the environment variables set by the user in the .env file.
        :param path: The enum of which environment variable to check for the path
        :param filename: The name of the file that should be located in the path
        :return: The full path to the file
        """
        prefix: str = os.getenv(path.value)
        return os.path.join(prefix, filename)

    @staticmethod
    def parse_measurement_type(measurement_type: str) -> Measurement:
        """
        Map a measurement type string to a Measurement type enum. Will create a SyntaxError if the measurement_type is
        not a valid mapping.
        :param measurement_type: The measurement type string
        :return: Measurement type enum
        """
        if measurement_type == 'abs':
            return Measurement.ABSORPTION
        if measurement_type == 'emis':
            return Measurement.EMISSION
        if measurement_type == 'idt':
            return Measurement.IGNITION_DELAY_TIME
        if measurement_type == 'outlet':
            return Measurement.OUTLET
        if measurement_type == 'ion':
            return Measurement.ION
        if measurement_type == 'pressure':
            return Measurement.PRESSURE
        if measurement_type == 'conc':
            return Measurement.CONCENTRATION
        if measurement_type == 'lfs':
            return Measurement.LFS
        if measurement_type == 'half_life':
            return Measurement.HALF_LIFE
        raise SyntaxError(f"Invalid measurement type: {measurement_type}")

    @staticmethod
    def parse_reaction_type(reaction_type: str) -> Reaction:
        """
        Map the reaction_type str to Reaction enum. Will create a SyntaxError if the reaction_type is not in the
        mapping.
        :param reaction_type: The reaction type string
        :return: Reaction enum
        """
        if reaction_type == 'st':
            return Reaction.SHOCKTUBE
        if reaction_type == 'pfr':
            return Reaction.PLUG_FLOW_REACTOR
        if reaction_type == 'jsr':
            return Reaction.JET_STREAM_REACTOR
        if reaction_type == 'rcm':
            return Reaction.RAPID_COMPRESSION_MACHINE
        if reaction_type == 'const_t_p':
            return Reaction.CONST_T_P
        if reaction_type == 'free_flame':
            return Reaction.FREE_FLAME
        raise SyntaxError(f"Invalid reaction type: {reaction_type}")

    # map from string to Variable
    VAR_CONVERT: Dict[str, Condition] = {
        'timestep': Condition.TIME_STEP,
        'end_time': Condition.END_TIME,
        'wavelength': Condition.WAVELENGTH,
        'active_spc': Condition.ACTIVE_SPECIES,
        'abs_coeff': Condition.ABS_COEFFICIENT,
        'path_length': Condition.PATH_LENGTH,
        'idt_targ': Condition.IGNITION_DELAY_TARGETS,
        'idt_method': Condition.IGNITION_DELAY_METHOD,
        'target_spc': Condition.TARGET_SPECIES,
        'temp': Condition.TEMPERATURE,
        'pressure': Condition.PRESSURE,
        'phi': Condition.PHI,
        'dpdt': Condition.DPDT,
        'length': Condition.LENGTH,
        'res_time': Condition.RES_TIME,
        'mdot': Condition.MDOT,
        'area': Condition.AREA,
        'vol': Condition.VOLUME,
        'time': Condition.TIME,
        'v_of_t': Condition.V_OF_T,
        'x_profile': Condition.X_PROFILE,
        't_profile': Condition.TIME_PROFILE,
        't_profile_setpoints': Condition.TIME_PROFILE_SETPOINTS
    }

    # map from variable to string
    INV_VAR_CONVERT: Dict[Condition, str] = {v: k for k, v in VAR_CONVERT.items()}

    @classmethod
    def convert_excel_str_variable(cls: Self, variable: str) -> Condition:
        """
        Convert a variable from an excel variable string to a Variable enum. Will raise a KeyError if the variable
        string is not in the mapping.
        :param variable: the variable string
        :return: Variable enum
        """
        if variable in cls.VAR_CONVERT:
            return cls.VAR_CONVERT[variable]
        else:
            raise KeyError(f'{variable} not found')

    @classmethod
    def convert_variable_excel_str(cls: Self, variable: Condition) -> str:
        """
        Convert a variable from Variable enum string to an excel variable string. Will raise a KeyError if the variable
        string is not in the mapping.
        :param variable: the type of variable
        :return: string
        """
        if variable in cls.INV_VAR_CONVERT:
            return cls.INV_VAR_CONVERT[variable]
        else:
            raise KeyError(f'{variable.name} not found')


    @staticmethod
    def convert_quantity_to_str(value: Quantity) -> str:
        if value is not None and hasattr(value, 'shape') and value.shape[0] > 1:
            return numpy.array2string(numpy.asarray(value), threshold=100000, max_line_width=float("inf"), precision=6, separator=',')
        else:
            return f"{value:D}" if value is not None else None
