from typing import List

import pandas

from data.experiments.experiment_set import ExperimentSet
from data.job.job import Job
from data.mechanism.mechanism import Mechanism
from serial.common.env_path import EnvPath
from serial.common.file_type import FileType
from serial.common.utils import Utils
from serial.reader.experiment_reader import ExperimentReader
from serial.reader.mechanism_reader import MechanismReader


class JobReader:
    @staticmethod
    def read_file(job_file: str) -> Job:
        """
        Reads either an Excel or a Yaml file.
        :param job_file: just the file name no path (the full path is found using environment variables)
        :return: the Job object
        """
        file_type: FileType = Utils.get_file_type(job_file)
        if file_type == FileType.EXCEL:
            return JobReader.read_excel_file(job_file)
        if file_type == FileType.YAML:
            return JobReader.read_yaml_file(job_file)

        raise Exception(f"File {job_file} is in an unsupported format, only .xlsl and .yaml files are supported")

    @staticmethod
    def read_excel_file(job_file: str) -> Job:
        """
        read an Excel file
        :param job_file: the file name of the Excel file
        :return: the Job object
        """
        excel = pandas.ExcelFile(Utils.get_full_path(EnvPath.JOB, job_file), engine='openpyxl')
        exps = excel.parse('exp')
        mechs = excel.parse('mech')

        # get experiment sets
        experiment_sets: List[ExperimentSet] = [
            ExperimentReader.read_file(
                experiment_set_file,
                Utils.parse_calculation_type(calculation_type),
                Utils.parse_datasource(x_source),
                Utils.parse_datasource(condition_source)
            )
            for experiment_set_file, calculation_type, x_source, condition_source in
            zip(exps['exp_filenames'], exps['calc_types'], exps['x_srcs'], exps['cond_srcs'])
        ]

        # get mechanisms
        mechanisms: List[Mechanism] = [
            MechanismReader.read_file(
                    mechanism_filename,
                    species_filename,
                    mech_names
                ) for mechanism_filename, species_filename, mech_names in
            zip(mechs['mech_filenames'], mechs['spc_filenames'], mechs['mech_names'])
        ]

        return Job(experiment_sets, mechanisms)

    @staticmethod
    def read_yaml_file(job_file: str) -> Job:
        """
        read a Yaml file
        :param job_file: the file name of the Yaml file
        :return: the Job object
        """
        pass
