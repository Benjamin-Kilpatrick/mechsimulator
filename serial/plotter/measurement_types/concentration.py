from typing import List

import numpy as np
from matplotlib.axes import Axes

from data.experiments.common.data_source import DataSource
from data.experiments.experiment_set import ExperimentSet
from data.mechanism.species import Species
from serial.plotter.line import PlotterLine
from serial.plotter.plotter_format import PlotterFormat
from serial.plotter.plotter_iterator import PlotterFigureAxesIterator
from serial.plotter.subplot import PlotterSubplot
from pint import Quantity


class PlotterConcentrationMeasurementLine(PlotterLine):

    def __init__(self, spc: Species, experiment_set: ExperimentSet, condition_index):
        self.spc = spc
        self.experiment_set = experiment_set
        self.condition_index = condition_index

    def get_label(self):
        return "Ur mom"

    def get_color(self):
        return "black"

    def get_linestyle(self):
        return '-'

    def get_marker(self):
        return ''

    def get_zorder(self):
        return None

    def get_xdata(self):
        # return self.experiment_set.get_x_data(x_source=DataSource.MEASURED)
        return self.experiment_set.get_experiment_x_data(self.experiment_set.measured_experiments[self.condition_index])

    def get_ydata(self) -> np.ndarray:
        print('name', self.spc.name)
        return self.experiment_set.measured_experiments[self.condition_index].results.get_target(self.spc.name)


class PlotterConcentrationSimulatedLine(PlotterLine):

    def __init__(self, spc: Species, experiment_set: ExperimentSet, condition_index):
        self.spc = spc
        self.experiment_set = experiment_set
        self.condition_index = condition_index

    def get_label(self):
        return "Ur mom"

    def get_color(self):
        return "red"

    def get_linestyle(self):
        return '-'

    def get_marker(self):
        return ''

    def get_zorder(self):
        return 1

    def get_xdata(self):
        return self.experiment_set.get_x_data()

    def get_ydata(self) -> np.ndarray:
        return self.experiment_set.all_simulated_experiments[0][self.condition_index].results.get_target(self.spc.name)



class PlotterConcentrationSubplot(PlotterSubplot):
    def __init__(self, ax: Axes, spc, experiment_set: ExperimentSet, plot_format: PlotterFormat, condition_index:int, quantities: Quantity):
        lines = [
            PlotterConcentrationMeasurementLine(spc, experiment_set, condition_index),
            PlotterConcentrationSimulatedLine(spc, experiment_set, condition_index)
        ]
        super().__init__(ax, lines, plot_format, spc)
        title = f"{quantities}"
        self.ax.set_title(title)


    @staticmethod
    def load_from_experiment_set(experiment_set: ExperimentSet, plot_format: PlotterFormat,
                                 axes_iterator: PlotterFigureAxesIterator, quantities: List[Quantity], spc: Species) -> list:
        subplots = []
        # load spc data

        for condition_index, condition in enumerate(quantities):
            axis: Axes = axes_iterator.__next__()
            subplots.append(
                PlotterConcentrationSubplot(axis, spc, experiment_set, plot_format, condition_index, condition))

        return subplots