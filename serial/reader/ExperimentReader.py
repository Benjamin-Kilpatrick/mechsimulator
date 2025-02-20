import math
from typing import Dict, Any

import pandas

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.experiment_set import ExperimentSet
from serial.common.env_path import EnvPath
from serial.common.file_type import FileType
from serial.common.utils import Utils


class ExperimentReader:
    @staticmethod
    def read_file(
            experiment_file: str,
            calculation_type: CalculationType,
            source_mode: DataSource
    ) -> ExperimentSet:
        file_type: FileType = Utils.get_file_type(experiment_file)
        full_filename: str = Utils.get_full_path(EnvPath.EXPERIMENT, experiment_file)
        if file_type == FileType.EXCEL:
            return ExperimentReader.read_excel_file(full_filename, calculation_type, source_mode)
        if file_type == FileType.YAML:
            return ExperimentReader.read_yaml_file(full_filename, calculation_type, source_mode)

        raise Exception(f"File {experiment_file} is in an unsupported format, only .xlsl and .yaml files are supported")

    @staticmethod
    def read_excel_file(
            experiment_file: str,
            calculation_type: CalculationType,
            source_mode: DataSource
    ) -> ExperimentSet:
        excel = pandas.ExcelFile(experiment_file, engine='openpyxl')
        info = excel.parse('info')

        info_dict: Dict[str, Dict[str, Any]] = {'spc': {}, 'overall': {}, 'plot': {}, 'mix': {}, 'plot_format': {}}

        for _, row in info.iterrows():
            group = row['group']
            if group in info_dict.keys():
                parameter = row['parameter']
                if group == 'spc':
                    info_dict['spc'][parameter] = [x for x in row[2:6]]
                else:
                    value = row['value']
                    units = row['units']
                    other = [x for x in row[4:] if not math.isnan(x)]
                    info_dict[group][parameter] = {
                        'value': value,
                        'units': units,
                        'other': other
                    }
        print(info_dict)


    @staticmethod
    def read_yaml_file(
            experiment_file: str,
            calculation_type: CalculationType,
            source_mode: DataSource
    ) -> ExperimentSet:
        pass