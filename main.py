import os
import sys
from typing import List
from dotenv import load_dotenv

from data.job.job import Job
from serial import plotter_main, plotter_util
from serial.reader.JobReader import JobReader
from sim import simulator_main


def run_job(job_dct):  # TODO: Remove function
    # Get filenames and other info from the job_dct
    exp_filenames = job_dct['exp_filenames']
    mech_filenames = job_dct['mech_filenames']
    spc_filenames = job_dct['spc_filenames']
    calc_types = job_dct['calc_types']
    x_srcs = job_dct['x_srcs']
    cond_srcs = job_dct['cond_srcs']

    # Load objects using the filenames
    # exp_sets = [serial.exp.load_exp_set(os.path.join(os.getenv("EXPERIMENT_PATH"), filename)) for filename in exp_filenames] #parser.main.mult_exp_files(EXP_PATH, exp_filenames)
    # gases = [serial.mech.load_solution_obj(os.path.join(os.getenv("MECHANISM_PATH"), filename)) for filename in mech_filenames] #parser.main.mult_mech_files(MECH_PATH, mech_filenames)
    # mech_spc_dcts = [serial.spc.load_mech_spc_dct(os.path.join(os.getenv("SPECIES_PATH"), filename)) for filename in spc_filenames] #parser.main.mult_files(SPC_PATH, spc_filenames, 'spc')


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
            simulator_main.single_set(experiment_set)

    # Output jobs
    for job in jobs:
        for experiment_set in job.experiment_files:
            figs_axes = plotter_main.single_set(experiment_set, job.mechanisms)
            plotter_util.build_pdf(figs_axes)


if __name__ == "__main__":
    main()
