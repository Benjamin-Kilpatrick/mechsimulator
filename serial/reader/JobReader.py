import pandas

from data.job.job import Job
from serial.common.file_type import FileType
from serial.common.utils import Utils


class JobReader:
    @staticmethod
    def read_file(job_file: str) -> Job:
        file_type: FileType = Utils.get_file_type(job_file)
        if file_type == FileType.EXCEL:
            return JobReader.read_excel_file(job_file)
        if file_type == FileType.YAML:
            return JobReader.read_yaml_file(job_file)

        raise Exception(f"File {job_file} is in an unsupported format, only .xlsl and .yaml files are supported")

    @staticmethod
    def read_excel_file(job_file: str) -> Job:
        excel = pandas.ExcelFile(job_file, engine='openpyxl')
        experiments = excel.parse('exp')
        mechanisms = excel.parse('mech')
        print(experiments)
        print(mechanisms)

    @staticmethod
    def read_yaml_file(job_file: str) -> Job:
        pass
