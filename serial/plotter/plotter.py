from abc import ABC, abstractmethod
from typing import List, Any

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter as Formatter
#from rdkit.Contrib.LEF.AddLabels import labels

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.condition import Condition
from data.experiments.common.data_source import DataSource


from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.reaction import Reaction
from data.job.job import Job
from data.mechanism.mechanism import Mechanism
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
    Measurement.LFS:                 'Flame speed',
    Measurement.HALF_LIFE:           'Half-life',
}


class PlotterFormat:
    def __init__(self):
        self.plot_points:bool = True
        self.xunit = None
        self.yunit = None
        self.ylimit = None
        self.omit_targs = None
        self.exp_on_top = True
        self.rows = 4
        self.cols = 3
        self.marker_size = 15
        self.group_by = 'cond'
        self.exp_color = 'black'
        self.xscale = 'linear'
        self.yscale = 'linear'

class PlotterLine(ABC):
    @abstractmethod
    def get_ydata(self) -> np.ndarray:
        pass

    @abstractmethod
    def get_xdata(self):
        pass

    @abstractmethod
    def get_label(self):
        pass

    @abstractmethod
    def get_color(self):
        pass

    @abstractmethod
    def get_linestyle(self):
        pass

    @abstractmethod
    def get_marker(self):
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
        ax.plot(mech_xdata, line_ydata, label=label, color=color, linestyle=linestyle, marker=marker, zorder=zorder)


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
        return "#"

    def get_zorder(self):
        return None

    def get_xdata(self):
        return self.experiment_set.get_x_data()

    def get_ydata(self) -> np.ndarray:
        data = [experiment.get(self.condition).magnitude for experiment in self.experiment_set.measured_experiments]
        return np.asarray(data)


class PlotterSubplot:
    def __init__(self, ax, lines: List[PlotterLine]):
        self.ax = ax
        self.lines: List[PlotterLine] = lines

    def plot(self):
        for line in self.lines:
            line.plot(self.ax)

    @staticmethod
    def load_from_experiment_set(experiment_set: ExperimentSet, fig):
        lines = []
        if len(experiment_set.measured_experiments) > 0:
            conditions = experiment_set.measured_experiments[0].conditions
            for condition in conditions.get_conditions():

                lines.append(MeasuredConditionLine(condition, experiment_set))
        axis = fig.add_subplot(1, 1, 0 + 1)
        return PlotterSubplot(axis, lines)

class PlotterFigure: # Called plot in o.g.
    def __init__(self, experiment_set: ExperimentSet):
        self.fig = plt.figure(figsize=(8.5, 11))
        self.subplots = []

        # do this for every subplot
        self.subplots.append(PlotterSubplot.load_from_experiment_set(experiment_set, self.fig))

    def plot(self):
        for subplot in self.subplots:
            subplot.plot()




class Plot:
    def __init__(self, job: Job):
        self.format = PlotterFormat()
        self.figures: List[PlotterFigure] = []
        for experiment_set in job.experiment_files:
            self.figures.append(PlotterFigure(experiment_set))

    def plot(self):
        for figure in self.figures:
            figure.plot()


class Plotter:
    @staticmethod
    def plot(job: Job, filename: str = 'output.pdf', output_path: str = None):
        plot = Plot(job)
        plot.plot()



class PlotterOld:
    @staticmethod
    def plot(job: Job, filename: str='output.pdf', output_path: str=None):
        """
        plotter/main.py mult_sets
        """
        figs_axes = []
        for experiment_set in job.experiment_files:
            set_figs_axes = Plotter.plotter_main__single_set(job, experiment_set)
            figs_axes.extend(set_figs_axes)

        return figs_axes

    @staticmethod
    def plotter_main__single_set(job: Job, experiment_set: ExperimentSet):
        """
        plotter/main.py single_set
        """
        calc_type = experiment_set.calculation_type
        if calc_type == CalculationType.OUTCOME:
            figs_axes = Plotter.plotter_outcome__single_set(job, experiment_set)

            # TODO! handle with Class
            # o.g.
            # Send the data to the writer
            # EDIT: just writing to .npy files for now...
            # source = exp_set['overall']['source']
            # description = exp_set['overall']['description']
            # np.save(f'results_{source}_{description}.npy', set_ydata)
            # np.save(f'results_xdata_{source}_{description}.npy', set_xdata)
        elif calc_type == CalculationType.SENSITIVITY:
            raise NotImplementedError(f'{calc_type} is not implemented in single_set')
        elif calc_type == CalculationType.PATHWAY:
            raise NotImplementedError(f'{calc_type} is not implemented in single_set')
        else:
            raise NotImplementedError(f"calc_type {calc_type} not implemented!")

        return figs_axes

    @staticmethod
    def plotter_outcome__single_set(job: Job, experiment_set: ExperimentSet):
        # TODO! find where set_frmt went in new/ where it came from in main
        # TODO! Then replace with proper object
        set_frmt = {
            'plot_points': True,
            'xunit': None,
            'yunit': None,
            'ylimit': None,
            'omit_targs': None,
            'exp_on_top': True,
            'rows_cols': (4, 3),
            'marker_size': 15,
            'group_by': 'cond',
            'exp_color': 'black',
            'xscale': 'linear',
            'yscale': 'linear',
        }
        figs_axes = Plotter.plotter_outcome__build_figs_axes(job, experiment_set, set_frmt)
        # Loop over each mechanism and plot
        # TODO! Don't do for every single set do once then pass in (or make object?).
        #  Does this exist after the simulation in the experiment files?
        mech_xdata = experiment_set.condition_range.generate()  # xdata is same for all mechs
        for mech in job.mechanisms:
            mech_frmt = Plotter.plotter_outcome___mech_frmt(job, experiment_set, set_frmt, mech)
            figs_axes = Plotter.plotter_outcome__single_mech(job, experiment_set, figs_axes, mech_frmt, mech)

        # Plot experimental data if present
        # TODO! change for actually working
        mech_frmt = Plotter.plotter_outcome___mech_frmt(job, experiment_set, set_frmt, mech)

        # old way
        # exp_ydata = exp_set['overall']['exp_ydata']
        # exp_xdata = exp_set['overall']['exp_xdata']
        # mech_frmt = _mech_frmt(exp_set, set_frmt, conds_src)
        # figs_axes = single_mech(exp_ydata, exp_xdata, figs_axes, mech_frmt, exp_set)

    @staticmethod
    def plotter_outcome__build_figs_axes(job: Job, experiment_set: ExperimentSet, set_frmt):
        # build_figs_axes
        group_by = set_frmt['group_by']
        xunit = set_frmt['xunit']
        yunit = set_frmt['yunit']

        mech_names = Plotter.plotter_util___mech_names(job, experiment_set)

        cond_titles, xlabel, _ = Plotter.plotter_util__get_cond_titles(experiment_set, xunit=xunit)

        targ_titles, ylabel, _ = Plotter.plotter_util__get_targ_titles(experiment_set, yunit=yunit)

        # Set the titles according to the grouping method
        if group_by == 'cond':
            grp_titles = cond_titles
            plt_titles = targ_titles
        else:  # 'target'
            grp_titles = targ_titles
            plt_titles = cond_titles

        return Plotter.plotter_outcome__build_figs_axes__create_figs(experiment_set, grp_titles, plt_titles, xlabel, ylabel, mech_names, set_frmt)

    @staticmethod
    def plotter_util___mech_names(job: Job, experiment_set: ExperimentSet):
        # get the mech_names if the name is None then the name is "mech <index + 1"
        mech_names = [mech.mechanism_name if mech.mechanism_name else f'mech {indx + 1}' for indx, mech in
                      enumerate(job.mechanisms)]
        return mech_names

    @staticmethod
    def plotter_util__get_cond_titles(experiment_set: ExperimentSet, xunit=None) -> (List[str], str, Condition):
        meas_type = experiment_set.measurement
        plot_var = experiment_set.condition_range.variable
        units = VARIABLE_UNITS[plot_var][0]  # default unit used for plot_var

        if meas_type in (Measurement.ABSORPTION,
                         Measurement.EMISSION,
                         Measurement.CONCENTRATION,
                         Measurement.PRESSURE):
            cond_titles = []
            if experiment_set.condition_source == DataSource.SIMULATION:
                start = experiment_set.condition_range.start
                end = experiment_set.condition_range.end
                inc = experiment_set.condition_range.inc
                num = int((end - start) / inc) + 1
                conds = np.linspace(start, end, num)
                for cond in conds:
                    cond_title = f'{cond} {units}'
                    cond_titles.append(cond_title)
            elif experiment_set.condition_source == DataSource.MEASURED:
                for exp_obj in experiment_set.measured_experiments:
                    cond = exp_obj.conditions.get(plot_var).magnitude
                    cond_title = f'{cond} {units}'
                    cond_titles.append(cond_title)
            else:
                raise NotImplementedError(f'Condition source "{experiment_set.condition_source}" not implemented.')
            if xunit is not None:
                xlabel = f'Time ({xunit})'
            else:
                xlabel = 'Time (s)'
            xquant = Variable.TIME

        elif meas_type in (Measurement.IGNITION_DELAY_TIME,
                           Measurement.OUTLET,
                           Measurement.LFS,
                           Measurement.HALF_LIFE):
            if meas_type == Measurement.IGNITION_DELAY_TIME:
                cond_titles = ['Ignition delays']
            elif meas_type == Measurement.OUTLET:
                cond_titles = ['Outlet concentrations']
            elif meas_type == Measurement.LFS:
                cond_titles = ['Laminar flame speeds']
            elif meas_type == Measurement.HALF_LIFE:
                cond_titles = ['Half life']
            else:
                raise NotImplementedError(f'Measurement type "{meas_type}" not implemented.')

            if xunit is None:  # if no xunit given...
                xunit = VARIABLE_UNITS[plot_var]  # the default unit is the first one

            # If on ignition delay time and using temperature, use the special label
            if meas_type == Measurement.IGNITION_DELAY_TIME and plot_var == Variable.TEMPERATURE:
                xlabel = '1000/Temperature (K^-1)'
            else:
                xlabel = f'{VARIABLE_DISPLAY_NAMES[plot_var]} ({xunit})'
            xquant = plot_var
        else:
            raise NotImplementedError(f'meas_type {meas_type} not implemented')

        return cond_titles, xlabel, xquant

    @staticmethod
    def plotter_util__get_targ_titles(experiment_set: ExperimentSet, yunit=None):
        # TODO! Split into multiple functions
        meas_type = experiment_set.measurement

        # TODO! below todos may be solved by examining both parsers in main and new
        if meas_type == Measurement.ABSORPTION:
            # TODO! how to get wavelength
            targ_titles = None  # wrong
            yunit = yunit or '%'
            ylabel = f'Fractional absorption ({yunit})'
            yquant = Measurement.ABSORPTION
        elif meas_type == Measurement.EMISSION:
            # TODO! how to get wavelength
            targ_titles = None  # wrong
            ylabel = 'Normalized emission'
            yquant = None
        elif meas_type == Measurement.ION:
            raise NotImplementedError("The 'ion' measurement type is not working.")
        elif meas_type in (Measurement.CONCENTRATION, Measurement.OUTLET,):

            targ_titles = [spc.name for spc in experiment_set.simulated_species] + ['Temperature(t)']
            yunit = yunit or ''
            ylabel = f'Mole fraction ({yunit}) or Temperature (K)'
            yquant = Measurement.CONCENTRATION #TODO! Does this make sense when Measurement.OUTLET
        elif meas_type == Measurement.PRESSURE:
            targ_titles = None
            yunit = yunit or 'atm'
            ylabel = f'Pressure ({yunit})'
            yquant = Measurement.PRESSURE
        elif meas_type == Measurement.IGNITION_DELAY_TIME:
            # TODO! find idt_targ and idt_method
            idt_targs = None  # exp_set['plot']['idt_targ'][0]
            idt_methods = None  # exp_set['plot']['idt_method'][0]
            targ_titles = []
            for idt_method in idt_methods:
                for idt_targ in idt_targs:
                    targ_title = idt_targ + ', ' + idt_method
                    targ_titles.append(targ_title)
            yunit = yunit or 's'
            ylabel = f'Ignition delay time ({yunit})'
            yquant = Measurement.IGNITION_DELAY_TIME # TODO! Check if this works originally 'time'
        elif meas_type == Measurement.LFS:
            targ_titles = ['', ]
            yunit = yunit or 'cm/s'
            ylabel = f'Laminar flame speed ({yunit})'
            yquant = Measurement.LFS
        elif meas_type == Measurement.HALF_LIFE:
            targ_titles = ['', ]
            # TODO! find target_spc
            targ_titles = None  # [exp_set['plot']['target_spc'][0]]
            yunit = yunit or 's'
            ylabel = f'Half life ({yunit})'
            yquant = Measurement.HALF_LIFE
        else:
            raise NotImplementedError(f'meas_type {meas_type} not implemented')

        return targ_titles, ylabel, yquant

# WORK HERE
    @staticmethod
    def plotter_outcome__build_figs_axes__create_figs(experiment_set: ExperimentSet, grp_titles, plt_titles, xlabel, ylabel, mech_names, set_frmt):
        nrows, ncols = set_frmt['rows_cols']
        plts_per_pg = nrows * ncols
        ngrps = len(grp_titles)
        plts_per_grp = len(plt_titles)
        pgs_per_grp = Plotter.plotter_outcome___pgs_per_grp(plts_per_grp, plts_per_pg)
        # Loop over each group and build the figures and axes
        # TODO! convert figs_axes into object also convert axes
        figs_axes = []
        for grp_idx in range(ngrps):
            # Loop over each page within the group
            for pg_idx in range(pgs_per_grp):
                fig = plt.figure(figsize=(8.5, 11))
                axes = []
                # Loop over each plot on the page
                for plt_idx_pg in range(plts_per_pg):
                    plt_idx_grp = pg_idx * plts_per_pg + plt_idx_pg
                    if plt_idx_grp < plts_per_grp:
                        axis = fig.add_subplot(nrows, ncols, plt_idx_pg + 1)
                        plt_title = plt_titles[plt_idx_grp]
                        plt.title(plt_title, fontsize=10, loc='center', y=0.97)
                        plt.xticks(fontsize=8)
                        plt.yticks(fontsize=8)
                        plt.subplots_adjust(wspace=0.38, hspace=0.23)
                        axis.yaxis.set_major_formatter(Formatter('%0.2E'))
                        axes.append(axis)
                    if plt_idx_pg == 0:  # if first plot of page, add page title
                        title = grp_titles[grp_idx]
                        title += f'\n(pg. {pg_idx + 1} of {pgs_per_grp})'
                        fig.suptitle(title, y=0.99, fontsize=16)

                Plotter.plotter_outcome__add_headers(experiment_set, mech_names)
                Plotter.plotter_outcome__add_footers(xlabel, ylabel)
                figs_axes.append([fig, axes])

        return figs_axes

    @staticmethod
    def plotter_outcome___pgs_per_grp(plts_per_grp, plts_per_pg):
        """ Calculates the number of pages per group
        """
        if plts_per_grp % plts_per_pg == 0:  # if perfectly divisible, just divide
            pgs_per_grp = int(plts_per_grp / plts_per_pg)
        else:  # otherwise, add one (since int rounds down)
            pgs_per_grp = int(plts_per_grp / plts_per_pg) + 1

        return pgs_per_grp

    @staticmethod
    def plotter_outcome__add_headers(experiment_set: ExperimentSet, mech_names):
        """ Adds header text to a figure
        """

        # Make some text describing the legends
        header_x_positions = [0.06, 0.37, 0.68]
        header_y_positions = [0.9, 0.92]
        for mech_idx, mech_name in enumerate(mech_names):
            header = f'{COLORS[mech_idx % len(COLORS)]} lines: {mech_name}'
            if mech_idx < 3:  # three mechs per row
                y_idx = 0
            else:
                y_idx = 1
            plt.figtext(header_x_positions[mech_idx % 3], header_y_positions[y_idx],
                        header, fontsize=12, color=COLORS[mech_idx % len(COLORS)])

        # Make some text describing the experimental set
        source = experiment_set.metadata.source
        description = experiment_set.metadata.description
        reac_type = experiment_set.reaction
        meas_type = experiment_set.measurement

        plt.figtext(0.01, 0.98, f'Source: {source}', fontsize=10)
        plt.figtext(0.01, 0.96, f'Description: {description}', fontsize=10)
        plt.figtext(0.77, 0.98, f'Reac. type: {REACTION_DISPLAY_NAMES[reac_type]}', fontsize=10)
        plt.figtext(0.77, 0.96, f'Meas. type: {MEASUREMENT_DISPLAY_NAMES[meas_type]}', fontsize=10)

    @staticmethod
    def plotter_outcome__add_footers(xlabel, ylabel):
        footnote1 = f'Y-axis: {ylabel}\n'
        footnote2 = f'X-axis: {xlabel}\n'
        footnotes = footnote1 + footnote2
        plt.figtext(0.11, 0.06, footnotes, fontsize=10, va="top", ha="left")

    @staticmethod
    def plotter_outcome___mech_frmt(job: Job, experiment_set: ExperimentSet, set_frmt, mechanism:Mechanism = None):
        conds_src = experiment_set.condition_source
        #TODO! Turn into proper object
        # This function would be the basis for a constructor
        # Initialize the dict with some general information
        mech_frmt = {'rows_cols': set_frmt['rows_cols'],
                     'group_by': set_frmt['group_by'],
                     'xlim': set_frmt['xlim'],
                     'ylim': set_frmt['ylim'],
                     'xscale': set_frmt['xscale'],
                     'yscale': set_frmt['yscale'],
                     }

        # Get the conversion factors
        xunit = set_frmt['xunit']
        yunit = set_frmt['yunit']
        _, _, xquant = Plotter.plotter_util__get_cond_titles(experiment_set)
        _, _, yquant = Plotter.plotter_util__get_targ_titles(experiment_set)
        mech_frmt['xconv'] = Plotter.plotter_outcome___mech_frmt__get_conv_factors(xunit, xquant)
        mech_frmt['yconv'] = Plotter.plotter_outcome___mech_frmt__get_conv_factors(yunit, yquant)

        if experiment_set.measurement in (Measurement.IGNITION_DELAY_TIME, Measurement.HALF_LIFE):
            mech_frmt['xconv'] = 'inv' # TODO! WTF?

        # Get color, marker, and order; depends on whether simulation or experiment
        exp_on_top = set_frmt['exp_on_top']

        if mechanism is not None: # if mechanism is not None then it's a simulation
            # TODO! This is bad find a better way to look up
            indx = job.mechanisms.index(mechanism)
            mech_frmt['color'] = COLORS[indx % len(COLORS)]
            mech_frmt['marker'] = ''
            mech_frmt['order'] = indx # TODO! What is this for track to usage

        else: # if mechanism is None then it's an experiment
            mech_frmt['color'] = set_frmt['exp_color']
            # If indicated, plot points
            if set_frmt['plot_points']:
                mech_frmt['marker'] = '.'
            # Otherwise, plot lines
            else:
                mech_frmt['marker'] = ''
            # Put the experiment either in front or in back
            if exp_on_top:
                mech_frmt['order'] = 1e3  # bigger than any possible number of mechs TODO! this is bad
            else:
                mech_frmt['order'] = -1  # negative to go behind all  TODO! this is also bad

        return mech_frmt

    @staticmethod
    def plotter_outcome___mech_frmt__get_conv_factors(units, quant):
        # TODO! This does not work probably go over with the M. to determine how to break up allowed units
        if units in Measurement:
            allowed_units = MEASUREMENT_UNITS[quant][0]
            conv_factors = MEASUREMENT_UNITS[quant][1]
            assert units in allowed_units, (
                f"'{units}' are not allowed units for the quantity '{quant}'")
            idx = allowed_units.index(units)
            conv_factor = 1 / conv_factors[idx]  # conv_factor is the inverse
        elif units in Variable:
            allowed_units = VARIABLE_UNITS[quant][0]
            conv_factors = VARIABLE_UNITS[quant][1]
            assert units in allowed_units, (
                f"'{units}' are not allowed units for the quantity '{quant}'")
            idx = allowed_units.index(units)
            conv_factor = 1 / conv_factors[idx]  # conv_factor is the inverse
        else:
            conv_factor = 1

        return conv_factor

    @staticmethod
    def plotter_outcome__single_mech(job: Job, experiment_set: ExperimentSet, figs_axes: List[Any], mech_frmt: dict, mech: Mechanism):
        # Get info on how to organize the plots
        ngrps, nplts, plts_per_pg, pgs_per_grp = Plotter.plotter_outcome__organize_set(
            experiment_set, mech_frmt, mech)

        # Loop over each group of pages
        for grp_idx in range(ngrps):
            # Loop over pages in each group
            for pg_idx in range(pgs_per_grp):
                fig_idx = grp_idx * pgs_per_grp + pg_idx
                _, axs = figs_axes[fig_idx]
                # Loop over plots on each page
                for plt_idx_pg in range(plts_per_pg):
                    plt_idx_grp = pg_idx * plts_per_pg + plt_idx_pg  # overall idx
                    if plt_idx_grp < nplts:
                        # data should be easy to access because of structure this is not needed?
                        # plt_ydata = get_plt_ydata(mech_ydata, mech_frmt, grp_idx,
                        #                           plt_idx_grp, exp_set)
                        Plotter.plotter_outcome__single_plot(experiment_set, mech_frmt, mech, plt_idx_pg, axs[plt_idx_pg])
                        # single_plot(plt_ydata, mech_xdata, axs[plt_idx_pg],
                        #             mech_frmt, plt_idx_pg, exp_set, mech_idx)

        return figs_axes

    @staticmethod
    def plotter_outcome__organize_set(experiment_set: ExperimentSet, mech_frmt: dict, mech: Mechanism):

        ngrps, nplts = Plotter.plotter_outcome__organize_set___ngrps_nplts(experiment_set, mech_frmt, mech)
        nrows, ncols = mech_frmt['rows_cols']
        plts_per_pg = nrows * ncols  # maximum number of plots per page
        pgs_per_grp = Plotter.plotter_outcome___pgs_per_grp(nplts, plts_per_pg)

        return ngrps, nplts, plts_per_pg, pgs_per_grp

    @staticmethod
    def plotter_outcome__organize_set___ngrps_nplts(experiment_set: ExperimentSet, mech_frmt: dict, mech: Mechanism):
        ndims = 2 # TODO! get the number of dimensions somehow o.g. np.ndim(mech_ydata)
        group_by = mech_frmt['group_by']
        meas_type = experiment_set.measurement

        if ndims == 3:
            # Get the numbers of conditions and targets
            if meas_type == 'abs':
                #nconds, _, _ = np.shape(mech_ydata)
                nconds = Plotter.get_num_conds(experiment_set)
                ntargs = 0#len(exp_set['plot']['wavelength'])
            else:
                #nconds, ntargs, _ = (0, 0, 0) #np.shape(mech_ydata)
                nconds = Plotter.get_num_conds(experiment_set)
                ntargs = Plotter.get_num_targs(experiment_set)
            # Get the number of groups and plots
            if group_by == 'cond':
                ngrps, nplts = nconds, ntargs
            else:  # 'target'
                ngrps, nplts = ntargs, nconds  # flipped
        else:  # ndims = 2
            #_, ntargs = np.shape(mech_ydata)
            ntargs = Plotter.get_num_targs(experiment_set)
            ngrps, nplts = 1, ntargs  # all targets are treated as one group

        return ngrps, nplts

    # TODO! should a method like this be in ExperimentSet?
    @staticmethod
    def get_num_conds(experiment_set: ExperimentSet):
        num_conds = 0

        # TODO! is measured_experiments right or should it be simulated_experiments?
        if len(experiment_set.simulated_experiments) > 0:
            experiment = experiment_set.simulated_experiments[0]
            num_conds = len(experiment.conditions.variable_set)

        return num_conds

    @staticmethod
    def get_num_targs(experiment_set: ExperimentSet):
        num_targs = 0

        if len(experiment_set.simulated_experiments) > 0:
            experiment = experiment_set.simulated_experiments[0]
            num_targs = len(experiment.results.target_results)

        return num_targs

    @staticmethod
    def plotter_outcome__single_plot(experiment_set: ExperimentSet, mech_frmt: dict, mech: Mechanism, plt_idx_pg, current_ax):

        # Load info; inefficient to load for every plot, but looks cleaner
        xlim = mech_frmt['xlim']
        ylim = mech_frmt['ylim']
        xscale = mech_frmt['xscale']
        yscale = mech_frmt['yscale']
        meas_type = experiment_set.measurement

        # If on abs, flip order so total abs is first (i.e., the solid line)
        if meas_type == Measurement.ABSORPTION:
            # TODO! figure out flip
            #plt_ydata = np.flip(plt_ydata, 0)
            pass

        # Loop over all lines and plot each
        nlines = Plotter.plotter_outcome__single_plot___nlines(experiment_set)
        labels = Plotter.plotter_outcome___labels(experiment_set, nlines, mech)

        for line_idx in range(nlines):
            Plotter.plotter_outcome__single_line(experiment_set, line_idx, current_ax, mech_frmt, labels)

        # Do some formatting on the entire plot
        if xlim is not None:
            current_ax.set_xlim(xlim)
        if ylim is not None:
            current_ax.set_ylim(ylim)
        current_ax.set_xscale(xscale)
        current_ax.set_yscale(yscale)
        if plt_idx_pg == 0 and nlines > 1:  # add legend on 1st plot if mult. lines
            current_ax.legend()

    @staticmethod
    def plotter_outcome__single_plot___nlines(experiment_set: ExperimentSet) -> int:
        return len(experiment_set.simulated_experiments)

    @staticmethod
    def plotter_outcome___labels(experiment_set: ExperimentSet, nlines, mechanism: Mechanism) -> List[str]:
        meas_type = experiment_set.measurement
        if nlines == 1:
            labels = [None]
        else:
            if meas_type == Measurement.ABSORPTION:
                if mechanism is None:
                    labels = ['Exp., total'] + [None] * (nlines - 1)
                else:
                    # TODO! Find where active_spc is
                    #active_spcs = copy.copy(exp_set['plot']['active_spc'])
                    #active_spcs.reverse()
                    #labels = ['Total'] + active_spcs
                    labels = None
            else:
                print(f'Labels not implemented for meas_type {meas_type}')
                labels = [None] * nlines
        return labels

    @staticmethod
    def plotter_outcome__single_line(experiment_set: ExperimentSet, line_idx, current_ax, mech_frmt, labels):
        # TODO! find way to move into class
        mech_xdata = experiment_set.condition_range.generate()

        # Load some information
        xconv = mech_frmt['xconv']
        yconv = mech_frmt['yconv']
        color = mech_frmt['color']
        marker = mech_frmt['marker']
        order = mech_frmt['order']  # higher numbers go on top

        # TODO! handled wrong do we still need to invert?
        if xconv == 'inv':  # fix the case of inverse temperature
            mech_xdata = 1000 / mech_xdata
            xconv = 1

        # Get ydata for the current line
        ndims = Plotter.get_num_targs(experiment_set) # TODO! verify that this is correct

        # originally checked if plt_ydata was an array or an array of arrays here

        # Get linestyle based on marker formatting and line_idx
        if marker == '':  # if plotting a line
            linestyle = LINESTYLES[line_idx]
        else:  # if plotting points
            linestyle = ''

        label = labels[line_idx]
        line_ydata = [] # TODO! get line data probably look at the surrounding loop
        current_ax.plot(mech_xdata * xconv, line_ydata, label=label,
                    color=color, linestyle=linestyle, marker=marker,
                    zorder=order)