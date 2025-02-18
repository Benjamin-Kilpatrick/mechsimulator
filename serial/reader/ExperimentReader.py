from data.experiments.experiment import Experiment
from serial.common.file_type import FileType
from serial.common.utils import Utils


class ExperimentReader:
    @staticmethod
    def read_file(experiment_file: str) -> Experiment:
        file_type: FileType = Utils.get_file_type(experiment_file)
        if file_type == FileType.EXCEL:
            return ExperimentReader.read_excel_file(experiment_file)
        if file_type == FileType.YAML:
            return ExperimentReader.read_yaml_file(experiment_file)

        raise Exception(f"File {experiment_file} is in an unsupported format, only .xlsl and .yaml files are supported")

    @staticmethod
    def read_excel_file(experiment_file: str) -> Experiment:
        pass

    @staticmethod
    def read_yaml_file(experiment_file: str) -> Experiment:
        pass