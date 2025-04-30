from typing import List

from matplotlib.axes import Axes

from data.experiments.experiment_set import ExperimentSet
from data.mechanism.species import Species
from serial.plotter.line import PlotterLine
from serial.plotter.plotter_format import PlotterFormat
from serial.plotter.plotter_iterator import PlotterFigureAxesIterator


class PlotterSubplot:
    """
    A subplot/ax that can have multiple lines in it.
    """

    def __init__(self, ax: Axes, lines: List[PlotterLine], plot_format: PlotterFormat, spc: Species):
        self.ax: Axes = ax
        self.lines: List[PlotterLine] = lines
        self.plot_format = plot_format
        self.spc = spc

        # set ax info
        self.ax.set_xscale(plot_format.xscale)
        self.ax.set_yscale(plot_format.yscale)
        if plot_format.ylimit is not None:
            begin, end = plot_format.ylimit
            # self.ax.set_ylim(ymin=begin, ymax=end)
        if plot_format.xlimit is not None:
            self.ax.set_xlim(plot_format.xlimit)

    def plot(self):
        """
        Plots all the lines in the subplot/axes.
        """
        for line in self.lines:
            line.plot(self.ax)

    @staticmethod
    def load_measured_from_experiment_set(experiment_set: ExperimentSet, axes_iterator:PlotterFigureAxesIterator) -> list:
        subplots = []
        return subplots