import os
from typing import List, Any, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter as Formatter
import matplotlib.backends.backend_pdf as plt_pdf
from pint import Quantity

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.condition import Condition
from data.experiments.common.data_source import DataSource


from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.reaction import Reaction
from data.job.job import Job
from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species
from serial.plotter.concentration import PlotterConcentrationSubplot
from serial.plotter.line import PlotterLine
from serial.plotter.outlet import PlotterSpeciesSubplot

from serial.plotter.plotter_format import PlotterFormat
from serial.plotter.plotter_iterator import FigureContainer, PlotterFigureAxesIterator
from serial.plotter.subplot import PlotterSubplot

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

