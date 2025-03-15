""" Runs one or more job files

    Example: python run.py jobfile1 jobfile2 ...
    BK_USED
"""
import os
import sys

from dotenv import load_dotenv

from serial.reader.JobReader import JobReader
from serial.writer.ExperimentWriter import ExperimentWriter

"""assert len(sys.argv) > 1, 'At least one input must be given!'
print(os.getcwd())
JOB_FILES = sys.argv[1:]
main.run_jobs(JOB_FILES)"""

def test():
    print('hi')

def main():
    load_dotenv()
    job = JobReader.read_file('benes_job.xlsx')

    for experiment_file in job.experiment_files:
        ExperimentWriter.write_yaml(f'new_benes_{experiment_file.metadata.source}.yaml', experiment_file)

    print(job)

    test()


main()
