from data.job.job import Job
from serial.plotter import plotter_main, plotter_util


class Plotter:
    @staticmethod
    def plot(job: Job):
        for experiment_set in job.experiment_files:
            figs_axes = plotter_main.single_set(experiment_set, job.mechanisms)
            plotter_util.build_pdf(figs_axes)
