from typing import List

import pandas

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.experiment_set import ExperimentSet
from data.job.job import Job
from data.mechanism.mechanism import Mechanism
from serial.common.env_path import EnvPath
from serial.common.file_type import FileType
from serial.common.utils import Utils
from serial.reader.ExperimentReader import ExperimentReader
from serial.reader.MechanismReader import MechanismReader


class JobReader:
    @staticmethod
    def read_file(job_file: str) -> Job:
        """
        test
        :param job_file:
        :return:
        """
        file_type: FileType = Utils.get_file_type(job_file)
        if file_type == FileType.EXCEL:
            return JobReader.read_excel_file(job_file)
        if file_type == FileType.YAML:
            return JobReader.read_yaml_file(job_file)

        raise Exception(f"File {job_file} is in an unsupported format, only .xlsl and .yaml files are supported")

    @staticmethod
    def read_excel_file(job_file: str) -> Job:
        excel = pandas.ExcelFile(Utils.get_full_path(EnvPath.JOB, job_file), engine='openpyxl')
        exps = excel.parse('exp')
        mechs = excel.parse('mech')

        num_exps = exps.shape[0]
        num_mechs = mechs.shape[0]

        experiment_sets: List[ExperimentSet] = []
        mechanisms: List[Mechanism] = []

        for i in range(num_exps):
            experiment_set_file: str = exps['exp_filenames'][i]
            calculation_type: CalculationType = Utils.parse_calculation_type(exps['calc_types'][i])
            x_source: DataSource = Utils.parse_datasource(exps['x_srcs'][i])
            condition_source: DataSource = Utils.parse_datasource(exps['cond_srcs'][i])

            experiment_sets.append(
                ExperimentReader.read_file(
                    experiment_set_file,
                    calculation_type,
                    x_source,
                    condition_source
                )
            )

        for i in range(num_mechs):
            mechanism_filename: str = mechs['mech_filenames'][i]
            species_filename: str = mechs['spc_filenames'][i]
            mech_names: str = mechs['mech_names'][i]

            mechanisms.append(
                MechanismReader.read_file(
                    mechanism_filename,
                    species_filename,
                    mech_names
                )
            )

        return Job(experiment_sets, mechanisms)

    @staticmethod
    def read_yaml_file(job_file: str) -> Job:
        pass
