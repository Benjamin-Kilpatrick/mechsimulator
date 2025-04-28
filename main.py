import os
import sys
from typing import List
from dotenv import load_dotenv

from data.job.job import Job
# from serial.plotter import plotter_main, plotter_util
from serial.reader.job_reader import JobReader
from sim.Simulator import Simulator

def main():
    # Read in options
    assert len(sys.argv) > 1, 'At least one input must be given!'
    print(os.getcwd())

    # Read in jobs
    load_dotenv()
    job_files = sys.argv[1:]
    job_path = os.getenv("JOB_PATH")
    jobs: List[Job] = []
    for job_file in job_files:
        file_name = os.path.join(job_path, job_file)
        new_job = JobReader.read_file(file_name)
        jobs.append(new_job)

    # Run each job object
    for job in jobs:
        for experiment_set in job.experiment_files:
            Simulator.run_experiment_set(experiment_set, job.mechanisms)

    # Output jobs plots
    """for job in jobs:
        for experiment_set in job.experiment_files:
            figs_axes = plotter_main.single_set(experiment_set, job.mechanisms)
            plotter_util.build_pdf(figs_axes)"""


if __name__ == "__main__":
    main()
