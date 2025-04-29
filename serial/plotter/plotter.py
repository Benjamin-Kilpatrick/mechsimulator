import os
from abc import ABC, abstractmethod
from typing import List, Any, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter as Formatter
import matplotlib.backends.backend_pdf as plt_pdf
from pint import Quantity

#from rdkit.Contrib.LEF.AddLabels import labels

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.condition import Condition
from data.experiments.common.data_source import DataSource


from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.reaction import Reaction
from data.job.job import Job
from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species
from serial.plotter import plotter_main, plotter_util, outcome
from serial.plotter.outcome import build_figs_axes, _mech_frmt, single_mech

# TODO! Figure out replacement with M.
# this is a mapping from variable type to allowed unit
# the first value in the tuple is the default unit
VARIABLE_UNITS = {
    Condition.TEMPERATURE: ('K', 'C', 'F', 'R'),
    Condition.PRESSURE: ('atm', 'bar', 'kPa', 'Pa', 'MPa', 'torr'),
    Condition.TIME: ('s', 'ms', 'micros'),
    #Condition.CONC: ('X', 'ppm', '%', 'molec/cm3'),
    Condition.LENGTH: ('m', 'cm', 'mm'),
    Condition.AREA: ('m2', 'cm2', 'mm2'),
    Condition.VOLUME: ('m3', 'cm3', 'mm3'),
    Condition.ABS_COEFFICIENT: ('m-1atm-1', 'cm-1atm-1',),
    #Condition.ABS: ('%', 'fraction'),
    Condition.DPDT: ('%/ms',),
    Condition.MDOT: ('kg/s', 'g/s'),
    #Condition.VELOCITY: ('cm/s', 'm/s'),
    Condition.PHI: ('',)
}

VARIABLE_DISPLAY_NAMES = {
    Condition.TEMPERATURE: 'Temperature',
    Condition.PRESSURE: 'Pressure',
    Condition.TIME: 'Time',
    #Condition.CONC: 'Mole fraction',
    Condition.LENGTH: 'Length',
    Condition.AREA: 'Area',
    Condition.VOLUME: 'Volume',
    Condition.ABS_COEFFICIENT: 'Absorption coefficient',
    Condition.DPDT: 'dP/dt',
    Condition.MDOT: 'Mass flow rate',
    #Condition.VELOCITY: 'Velocity',
    Condition.PHI: 'Equivalence ratio',
}

MEASUREMENT_UNITS = {
    #Condition.TEMPERATURE: ('K', 'C', 'F', 'R'),
    #Condition.PRESSURE: ('atm', 'bar', 'kPa', 'Pa', 'MPa', 'torr'),
    #Condition.TIME: ('s', 'ms', 'micros'),
    Measurement.CONCENTRATION: ('X', 'ppm', '%', 'molec/cm3'),
    #Condition.LENGTH: ('m', 'cm', 'mm'),
    #Condition.AREA: ('m2', 'cm2', 'mm2'),
    #Condition.VOLUME: ('m3', 'cm3', 'mm3'),
    #Condition.ABS_COEFFICIENT: ('m-1atm-1', 'cm-1atm-1',),
    Measurement.ABSORPTION: ('%', 'fraction'),
    #Condition.DPDT: ('%/ms',),
    #Condition.MDOT: ('kg/s', 'g/s'),
    #Condition.VELOCITY: ('cm/s', 'm/s'),
    #Condition.PHI: ('',)
}

COLORS = ['Red', 'Blue', 'Green', 'Black', 'Magenta', 'Pink']
LINESTYLES = ['-', '--', '-.', ':']

REACTION_DISPLAY_NAMES = {
    Reaction.SHOCKTUBE:                  'ST',
    Reaction.RAPID_COMPRESSION_MACHINE:  'RCM',
    Reaction.JET_STREAM_REACTOR:         'JSR',
    Reaction.PLUG_FLOW_REACTOR:          'PFR',
    Reaction.CONST_T_P:                  'Const. TP',
    Reaction.FREE_FLAME:                 'Free flame',
}

MEASUREMENT_DISPLAY_NAMES = {
    Measurement.ABSORPTION:          'Absorption',
    Measurement.EMISSION:            'Emission',
    Measurement.CONCENTRATION:       'Concentration',
    Measurement.ION:                 'Ion',
    Measurement.PRESSURE:            'Pressure',
    Measurement.IGNITION_DELAY_TIME: 'IDT',
    Measurement.OUTLET:              'Outlet',
    Measurement.LAMINAR_FLAME_SPEED: 'Flame speed',
    Measurement.HALF_LIFE:           'Half-life',
}


class PlotterFormat:
    def __init__(self):
        self.plot_points:bool = True
        self.xunit = None
        self.yunit = None
        self.ylimit = [0.0, 0.0055] # TODO! where did this come from
        self.xlimit = None
        self.omit_targs = None
        self.exp_on_top = True
        self.rows = 4
        self.cols = 3
        self.marker_size = 15
        self.group_by = 'cond'
        self.exp_color = 'black'
        self.xscale = 'linear'
        self.yscale = 'linear'

    def get_num_plots_per_page(self) -> int:
        return self.rows * self.cols

class PlotterLine(ABC):
    @abstractmethod
    def get_ydata(self) -> np.ndarray:
        pass

    @abstractmethod
    def get_xdata(self):
        pass

    @abstractmethod
    def get_label(self) -> str:
        pass

    @abstractmethod
    def get_color(self):
        pass

    @abstractmethod
    def get_linestyle(self):
        pass

    @abstractmethod
    def get_marker(self) -> float:
        pass

    @abstractmethod
    def get_zorder(self):
        pass

    def plot(self, ax):
        mech_xdata = self.get_xdata()
        line_ydata = self.get_ydata()
        label = self.get_label()
        color = self.get_color()
        linestyle = self.get_linestyle()
        marker = self.get_marker()
        zorder = self.get_zorder()
        try:
            ax.plot(mech_xdata, line_ydata, label=label, color=color, linestyle=linestyle, marker=marker, zorder=zorder)
        except ValueError as e:
            print(e)


class MeasuredConditionLine(PlotterLine):
    """
    For plotting a condition in a measured experiment
    """

    def __init__(self, condition: Condition, experiment_set: ExperimentSet):
        self.condition = condition
        self.experiment_set = experiment_set

    def get_label(self):
        return "Ur mom"

    def get_color(self):
        return "green"

    def get_linestyle(self):
        return "-"

    def get_marker(self):
        return 1.0

    def get_zorder(self):
        return None

    def get_xdata(self):
        return self.experiment_set.get_x_data(x_source=DataSource.MEASURED)

    def get_ydata(self) -> np.ndarray:
        data = [experiment.get(self.condition).magnitude for experiment in self.experiment_set.measured_experiments]
        return np.asarray(data)


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


class FigureContainer(ABC):

    def add_figure(self):
        pass

    def get_figures(self) -> List[Figure]:
        pass

    def get_figure(self) -> Figure:
        pass

class PlotterFigureAxesIterator:
    """
    This is an iterator class that gives the properly indexed list of axes such that each axis falls on the correct
    location in the grid.
    """
    def __init__(self, fig_cont: FigureContainer, plot_format: PlotterFormat):
        self.fig_cont:FigureContainer = fig_cont
        self.rows:int = plot_format.rows
        self.cols:int = plot_format.cols

        # state
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        rc = self.rows * self.cols

        # add a new figure if the page is full
        if (rc * len(self.fig_cont.get_figures())) <= self.index:
            self.fig_cont.add_figure()

        fig = self.fig_cont.get_figure()
        axis: Axes = fig.add_subplot(self.rows, self.cols, (self.index % rc) + 1)
        self.index += 1
        return axis


class PlotterSubplot:
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
        for line in self.lines:
            line.plot(self.ax)

    @staticmethod
    def load_measured_from_experiment_set(experiment_set: ExperimentSet, axes_iterator:PlotterFigureAxesIterator) -> list:
        subplots = []
        # load measured experiments
        # if len(experiment_set.measured_experiments) > 0:
        #     conditions = experiment_set.measured_experiments[0].conditions
        #     for condition in conditions.get_conditions():
        #
        #         lines.append(OutletMeasuredConditionLine(condition, experiment_set))
        # axis = fig.add_subplot(1, 1, 0 + 1)
        return subplots

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
        return '.'

    def get_zorder(self):
        return None

    def get_xdata(self):
        return self.experiment_set.get_x_data(x_source=DataSource.MEASURED)

    def get_ydata(self) -> np.ndarray:
        return self.experiment_set.measured_experiments[self.condition_index].results.target_results.get(self.spc.name)


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
        return None

    def get_xdata(self):
        return self.experiment_set.get_x_data()

    def get_ydata(self) -> np.ndarray:
        return self.experiment_set.all_simulated_experiments[0][self.condition_index].results.target_results.get(self.spc.name)


class PlotterConcentrationSubplot(PlotterSubplot):
    def __init__(self, ax: Axes, spc, experiment_set: ExperimentSet, plot_format: PlotterFormat, condition_index:int, quantities: Quantity):
        lines = [
            PlotterConcentrationMeasurementLine(spc, experiment_set, condition_index),
            PlotterConcentrationSimulatedLine(spc, experiment_set, condition_index)
        ]
        super().__init__(ax, lines, plot_format, spc)
        title = f"{quantities.magnitude} {quantities.units}"
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

class PlotterFigure(FigureContainer): # Called plot in o.g.

    def __init__(self, job: Job, mechanism:Mechanism, experiment_set: ExperimentSet, plot_format: PlotterFormat):
        self.figs: List[Figure] = [] # = plt.figure(figsize=(8.5, 11))
        self.subplots = []
        self.plot_format:PlotterFormat = plot_format
        self.axes_iterator = PlotterFigureAxesIterator(self, self.plot_format)
        self.experiment_set:ExperimentSet = experiment_set
        self.job:Job = job
        self.mechanism:Mechanism = mechanism

        # do this for every subplot
        if experiment_set.measurement == Measurement.OUTLET:
            self.subplots.extend(PlotterSubplot.load_measured_from_experiment_set(experiment_set, self.axes_iterator))
            self.subplots.extend(PlotterSpeciesSubplot.load_from_experiment_set(experiment_set, self.plot_format, self.axes_iterator))
        elif experiment_set.measurement == Measurement.CONCENTRATION:
            var_of_int = self.get_variable_of_interest()
            measured_quantities: List[Quantity] = [experiment.conditions.get(var_of_int) for experiment in self.experiment_set.measured_experiments]
            for spc in experiment_set.simulated_species:
                self.subplots.extend(PlotterConcentrationSubplot.load_from_experiment_set(experiment_set, plot_format, self.axes_iterator, measured_quantities, spc))
        else:
            raise NotImplementedError

    def get_figures(self) -> List[Figure]:
        return self.figs

    def add_figure(self):
        fig = plt.figure(figsize=(8.5, 11))
        self.figs.append(fig)
        PlotterFigure.add_headers_and_footers(self.job, self.mechanism, self.experiment_set, fig)

    def get_figure(self) -> Figure:
        if len(self.figs) == 0:
            self.add_figure()
        return self.figs[-1]

    def get_variable_of_interest(self) -> Condition:
        return self.experiment_set.condition_range.variable_of_interest

    def plot(self):
        for subplot in self.subplots:
            subplot.plot()

    @staticmethod
    def add_headers_and_footers(job: Job, mechanism:Mechanism, exp_set: ExperimentSet, fig: Figure):
        """ Adds header and footer text to a figure
        """

        # Make some text describing the legends
        header_x_positions = [0.06, 0.37, 0.68]
        header_y_positions = [0.9, 0.92]

        for mech_idx, mechanism in enumerate(job.mechanisms):
            header = f'{COLORS[mech_idx % len(COLORS)]} lines: {mechanism.mechanism_name}'
            if mech_idx < 3:  # three mechs per row
                y_idx = 0
            else:
                y_idx = 1
            plt.figtext(header_x_positions[mech_idx % 3], header_y_positions[y_idx],
                        header, fontsize=12, color=COLORS[mech_idx % len(COLORS)])

        # Make some text describing the experimental set
        source = mechanism.mechanism_name
        description = exp_set.metadata.description
        reac_type = REACTION_DISPLAY_NAMES[exp_set.reaction]
        meas_type = MEASUREMENT_DISPLAY_NAMES[exp_set.measurement]
        fig.text(0.01, 0.98, f'Source: {source}', fontsize=10)
        fig.text(0.01, 0.96, f'Description: {description}', fontsize=10)
        fig.text(0.77, 0.98, f'Reac. type: {reac_type}', fontsize=10)
        fig.text(0.77, 0.96, f'Meas. type: {meas_type}', fontsize=10)

        # TODO! figure out this stuff where to get the title and how pages work within a group
        group_title = "Outlet concentrations" # grp_titles[grp_idx]
        pg_idx = 0
        pgs_per_grp = 1
        title = f'{group_title}\n(pg. {pg_idx + 1} of {pgs_per_grp})'
        fig.suptitle(title, y=0.99, fontsize=16)

        # footers
        ylabel = ""
        xlabel = ""
        footnote1 = f'Y-axis: {ylabel}\n'
        footnote2 = f'X-axis: {xlabel}\n'
        footnotes = footnote1 + footnote2
        fig.text(0.11, 0.06, footnotes, fontsize=10, va="top", ha="left")



class Plot:
    def __init__(self, job: Job, mechanism_exps: List[Tuple[Mechanism, ExperimentSet]]):
        self.plot_format = PlotterFormat()
        self.figures:List[PlotterFigure] = []
        self.mechanism_exps:List[Tuple[Mechanism, ExperimentSet]] = mechanism_exps

        for mechanism, experiment_set in self.mechanism_exps:
            self.figures.append(PlotterFigure(job, mechanism, experiment_set, self.plot_format))

    def plot(self, filename, path):
        for figure in self.figures:
            figure.plot()

        print('Producing PDF...')
        if path is not None:
            filename = os.path.join(path, filename)
        pdf = plt_pdf.PdfPages(filename)
        for figs in self.figures:  # don't need the axes
            for fig in figs.get_figures():
                pdf.savefig(fig)
        pdf.close()


class Plotter:
    @staticmethod
    def plot(job: Job, mechanism_exps: List[Tuple[Mechanism, ExperimentSet]], filename: str = 'output.pdf', output_path: str = None):
        plot = Plot(job, mechanism_exps)
        plot.plot(filename, output_path)