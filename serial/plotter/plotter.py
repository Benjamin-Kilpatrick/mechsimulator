from typing import List

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter as Formatter

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.common.variable import Variable
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
    Variable.TEMPERATURE: ('K', 'C', 'F', 'R'),
    Variable.PRESSURE: ('atm', 'bar', 'kPa', 'Pa', 'MPa', 'torr'),
    Variable.TIME: ('s', 'ms', 'micros'),
    #Variable.CONC: ('X', 'ppm', '%', 'molec/cm3'),
    Variable.LENGTH: ('m', 'cm', 'mm'),
    Variable.AREA: ('m2', 'cm2', 'mm2'),
    Variable.VOLUME: ('m3', 'cm3', 'mm3'),
    Variable.ABS_COEFFICIENT: ('m-1atm-1', 'cm-1atm-1',),
    #Variable.ABS: ('%', 'fraction'),
    Variable.DPDT: ('%/ms',),
    Variable.MDOT: ('kg/s', 'g/s'),
    #Variable.VELOCITY: ('cm/s', 'm/s'),
    Variable.PHI: ('',)
}

VARIABLE_DISPLAY_NAMES = {
    Variable.TEMPERATURE: 'Temperature',
    Variable.PRESSURE: 'Pressure',
    Variable.TIME: 'Time',
    #Variable.CONC: 'Mole fraction',
    Variable.LENGTH: 'Length',
    Variable.AREA: 'Area',
    Variable.VOLUME: 'Volume',
    Variable.ABS_COEFFICIENT: 'Absorption coefficient',
    Variable.DPDT: 'dP/dt',
    Variable.MDOT: 'Mass flow rate',
    #Variable.VELOCITY: 'Velocity',
    Variable.PHI: 'Equivalence ratio',
}

MEASUREMENT_UNITS = {
    #Variable.TEMPERATURE: ('K', 'C', 'F', 'R'),
    #Variable.PRESSURE: ('atm', 'bar', 'kPa', 'Pa', 'MPa', 'torr'),
    #Variable.TIME: ('s', 'ms', 'micros'),
    Measurement.CONCENTRATION: ('X', 'ppm', '%', 'molec/cm3'),
    #Variable.LENGTH: ('m', 'cm', 'mm'),
    #Variable.AREA: ('m2', 'cm2', 'mm2'),
    #Variable.VOLUME: ('m3', 'cm3', 'mm3'),
    #Variable.ABS_COEFFICIENT: ('m-1atm-1', 'cm-1atm-1',),
    Measurement.ABSORPTION: ('%', 'fraction'),
    #Variable.DPDT: ('%/ms',),
    #Variable.MDOT: ('kg/s', 'g/s'),
    #Variable.VELOCITY: ('cm/s', 'm/s'),
    #Variable.PHI: ('',)
}

COLORS = ['Red', 'Blue', 'Green', 'Black', 'Magenta', 'Pink']

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

class Plotter:

    @staticmethod
    def plot(job: Job, filename: str='output.pdf', output_path: str=None):
        """
        plotter/main.py mult_sets
        """
        figs_axes = []
        for experiment_set in job.experiment_files:
            set_figs_axes = Plotter.plotter_main__single_set(job, experiment_set)

    @staticmethod
    def plotter_main__single_set(job: Job, experiment_set: ExperimentSet):
        """
        plotter/main.py single_set
        """
        calc_type = experiment_set.calculation_type
        if calc_type == CalculationType.OUTCOME:
            figs_axes = Plotter.plotter_outcome__single_set(job, experiment_set)
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
        # TODO! Don't do for every single set do once. Does this exist after the simulation in the experiment files?
        mech_xdata = experiment_set.condition_range.generate()  # xdata is same for all mechs
        for mech in job.mechanisms:
            Plotter.plotter_outcome___mech_frmt(job, experiment_set, set_frmt, mech)


    @staticmethod
    def plotter_outcome__build_figs_axes(job: Job, experiment_set: ExperimentSet, set_frmt):
        # build_figs_axes
        group_by = set_frmt['group_by']
        xunit = set_frmt['xunit']
        yunit = set_frmt['yunit']

        mech_names = Plotter.plotter_util___mech_names(job, experiment_set)

        cond_titles, xlabel, _ = Plotter.plotter_util__get_cond_titles(job, experiment_set, xunit=xunit)

        targ_titles, ylabel, _ = Plotter.plotter_util__get_targ_titles(experiment_set, yunit=yunit)

        # Set the titles according to the grouping method
        if group_by == 'cond':
            grp_titles = cond_titles
            plt_titles = targ_titles
        else:  # 'target'
            grp_titles = targ_titles
            plt_titles = cond_titles

        return Plotter.plotter_outcome__build_figs_axes__create_figs(grp_titles, plt_titles, xlabel, ylabel, mech_names, set_frmt)

    @staticmethod
    def plotter_util___mech_names(job: Job, experiment_set: ExperimentSet):
        # get the mech_names if the name is None then the name is "mech <index + 1"
        mech_names = [mech.mechanism_name if mech.mechanism_name else f'mech {indx + 1}' for indx, mech in
                      enumerate(job.mechanisms)]
        return mech_names

    @staticmethod
    def plotter_util__get_cond_titles(job: Job, experiment_set: ExperimentSet, xunit=None):
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

    @staticmethod
    def plotter_outcome__build_figs_axes__create_figs(experiment_set: ExperimentSet, grp_titles, plt_titles, xlabel, ylabel, mech_names, set_frmt):
        nrows, ncols = set_frmt['rows_cols']
        plts_per_pg = nrows * ncols
        ngrps = len(grp_titles)
        plts_per_grp = len(plt_titles)
        pgs_per_grp = Plotter.plotter_outcome___pgs_per_grp(plts_per_grp, plts_per_pg)
        # Loop over each group and build the figures and axes
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

        return None

    @staticmethod
    def plotter_outcome___pgs_per_grp(plts_per_grp, plts_per_pg):
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
        _, _, xquant = Plotter.plotter_util__get_cond_titles(job, experiment_set)
        _, _, yquant = Plotter.plotter_util__get_targ_titles(experiment_set)
        mech_frmt['xconv'] = Plotter.plotter_outcome___mech_frmt__get_conv_factors(xunit, xquant)
        mech_frmt['yconv'] = Plotter.plotter_outcome___mech_frmt__get_conv_factors(yunit, yquant)

    @staticmethod
    def plotter_outcome___mech_frmt__get_conv_factors(units, quant):
        if units in Measurement:
            allowed_units = MEASUREMENT_UNITS[quant][0]
            conv_factors = MEASUREMENT_UNITS[quant][1]
            assert units in allowed_units, (
                f"'{units}' are not allowed units for the quantity '{quant}'")
            idx = allowed_units.index(units)
            conv_factor = 1 / conv_factors[idx]  # conv_factor is the inverse
        elif units in Variable:
            allowed_units = MEASUREMENT_UNITS[quant][0]
            conv_factors = MEASUREMENT_UNITS[quant][1]
            assert units in allowed_units, (
                f"'{units}' are not allowed units for the quantity '{quant}'")
            idx = allowed_units.index(units)
            conv_factor = 1 / conv_factors[idx]  # conv_factor is the inverse
        else:
            conv_factor = 1

        return conv_factor