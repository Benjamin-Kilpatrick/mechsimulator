import os

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from serial.common.env_path import EnvPath
from serial.common.file_type import FileType


class Utils:
    @staticmethod
    def get_file_type(filename: str) -> FileType:
        if filename.endswith('.yaml'):
            return FileType.YAML
        if filename.endswith('.xlsx'):
            return FileType.EXCEL
        return FileType.INVALID

    @staticmethod
    def parse_datasource(x_source: str, condition_source: str) -> DataSource:
        if x_source == 'plot' and condition_source == 'plot':
            return DataSource.X_SIM_COND_SIM
        if x_source == 'plot' and condition_source == 'exp':
            return DataSource.X_SIM_COND_MEAS
        if x_source == 'exp' and condition_source == 'exp':
            return DataSource.X_MEAS_COND_MEAS
        if x_source == 'exp' and condition_source == 'plot':
            return DataSource.X_MEAS_COND_SIM

        return DataSource.INVALID

    @staticmethod
    def parse_calculation_type(calculation_type: str) -> CalculationType:
        if calculation_type == 'outcome':
            return CalculationType.OUTCOME
        if calculation_type == 'pathways':
            return CalculationType.PATHWAY
        if calculation_type == 'sens':
            return CalculationType.SENSITIVITY
        return CalculationType.INVALID

    @staticmethod
    def get_full_path(path: EnvPath, filename: str) -> str:
        prefix: str = os.getenv(path.value)
        return prefix + '/' + filename

