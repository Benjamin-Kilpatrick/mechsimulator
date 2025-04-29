import os
import sys
from typing import List, Tuple
from dotenv import load_dotenv

from data.experiments.experiment_set import ExperimentSet
from data.job.job import Job
from data.mechanism.mechanism import Mechanism
# from serial.plotter import plotter_main, plotter_util
from serial.plotter.plotter import Plotter
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

    completed_jobs: List[Tuple[Job, List[Tuple[Mechanism, ExperimentSet]]]] = []
    # Run each job object
    for job in jobs:
        for experiment_set in job.experiment_files:
            simulated_experiments: List[Tuple[Mechanism, ExperimentSet]] = Simulator.run_experiment_set(experiment_set, job.mechanisms)
            completed_jobs.append((job, simulated_experiments))

    # Output jobs plots
    for job in jobs:
        Plotter.plot(job)


if __name__ == "__main__":
    main()
