import os
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.backends.backend_pdf as plt_pdf
from pint import Quantity

from data.experiments.common.condition import Condition

from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.reaction import Reaction
from data.job.job import Job
from data.mechanism.mechanism import Mechanism
from serial.plotter.figure_style import FigureStyle, StyleGenerator
from serial.plotter.measurement_types.concentration import PlotterConcentrationSubplot
from serial.plotter.measurement_types.outlet import PlotterSpeciesSubplot

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
    """
    A figure that is composed of rows and columns of subplots. Multiple figures may be produced if there are enough
    subplots.
    """
    def __init__(self, job: Job, mechanism:Mechanism, experiment_set: ExperimentSet, plot_format: PlotterFormat):
        self.figs: List[Figure] = []
        self.fig_style: List[FigureStyle] = []
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
            measured_quantities: List[Quantity] = [value for value in experiment_set.get_condition_x_data()]
            # measured_quantities: List[Quantity] = [experiment.conditions.get(var_of_int) for experiment in self.experiment_set.measured_experiments]
            for spc in experiment_set.simulated_species:
                self.subplots.extend(PlotterConcentrationSubplot.load_from_experiment_set(experiment_set, plot_format, self.axes_iterator, measured_quantities, spc))
        else:
            raise NotImplementedError

    def get_figures(self) -> List[Figure]:
        return self.figs

    def add_figure(self, style_generator:StyleGenerator = None):
        fig = plt.figure(figsize=(8.5, 11))
        self.figs.append(fig)
        if style_generator:
            self.fig_style.append(style_generator.generate(self.job, self.mechanism, self.experiment_set))
        else:
            self.fig_style.append(None)

    def get_figure(self, style_generator:StyleGenerator = None) -> Figure:
        if len(self.figs) == 0:
            self.add_figure(style_generator=style_generator)
        return self.figs[-1]

    def get_variable_of_interest(self) -> Condition:
        return self.experiment_set.condition_range.variable_of_interest

    def plot(self):
        for fig, fig_style in zip(self.figs, self.fig_style):
            if fig_style:
                fig_style.add_headers_and_footers(fig)

        for subplot in self.subplots:
            subplot.plot()



class Plot:
    """
    A collection of all plots that the plotter will plot. Produces a PDF at the end.
    """
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

