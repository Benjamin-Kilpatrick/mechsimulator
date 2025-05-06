"""
Does not work. This is a rough draft
"""
import numpy as np
from matplotlib.axes import Axes

from data.experiments.common.data_source import DataSource
from data.experiments.experiment_set import ExperimentSet
from data.mechanism.species import Species
from serial.plotter.line import PlotterLine
from serial.plotter.plotter_format import PlotterFormat
from serial.plotter.plotter_iterator import PlotterFigureAxesIterator
from serial.plotter.subplot import PlotterSubplot


class OutletSpeciesExperimentLine(PlotterLine):

    def __init__(self, spc: Species, experiment_set: ExperimentSet):
        self.experiment_set = experiment_set
        self.spc = spc

    def get_label(self):
        return "Ur mom"

    def get_color(self):
        return "black"

    def get_linestyle(self):
        return ''

    def get_marker(self):
        return '.'

    def get_zorder(self):
        return None

    def get_xdata(self):
        return self.experiment_set.get_x_data(x_source=DataSource.MEASURED)

    def get_ydata(self) -> np.ndarray:
        out = [experiment.results.target_results[self.spc.name][0] if self.spc.name in experiment.results.target_results else None for experiment in self.experiment_set.measured_experiments ]
        return np.asarray(out)

class OutletSpeciesSimulatedLine(PlotterLine):
    def __init__(self, spc: Species, experiment_set: ExperimentSet):
        self.experiment_set = experiment_set
        self.spc = spc

    def get_label(self):
        return "Ur mom"

    def get_color(self):
        return "red"

    def get_linestyle(self):
        return ''

    def get_marker(self):
        return 1.0

    def get_zorder(self):
        return None

    def get_xdata(self):
        return np.asarray([])
        #return self.experiment_set.get_x_data(x_source=DataSource.SIMULATION)

    def get_ydata(self) -> np.ndarray:
        return np.asarray([])
        #size = len(self.experiment_set.get_x_data(x_source=DataSource.SIMULATION)) # TODO! temp until actual data exists
        #return np.asarray([1.0] * size)


# this does outlet subplots
class PlotterSpeciesSubplot(PlotterSubplot):
    def __init__(self, ax: Axes, spc: Species, experiment_set: ExperimentSet, plot_format: PlotterFormat):
        lines = [OutletSpeciesExperimentLine(spc, experiment_set), OutletSpeciesSimulatedLine(spc, experiment_set)]
        super().__init__(ax, lines, plot_format, spc)
        self.ax.set_title(self.spc.name)

    @staticmethod
    def load_from_experiment_set(experiment_set: ExperimentSet, plot_format: PlotterFormat, axes_iterator:PlotterFigureAxesIterator) -> list:
        subplots = []
        # load spc data

        for spc in experiment_set.simulated_species:
            axis: Axes = axes_iterator.__next__()
            subplots.append(PlotterSpeciesSubplot(axis, spc, experiment_set, plot_format))

        return subplots