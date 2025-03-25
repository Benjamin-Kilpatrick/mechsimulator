from typing import List

from data.experiments.common.calculation_type import CalculationType
from data.experiments.experiment_set import ExperimentSet
from data.job.job import Job
from data.mechanism.mechanism import Mechanism
from serial.plotter import plotter_main, plotter_util, outcome
from serial.plotter.outcome import build_figs_axes, _mech_frmt, single_mech


class Plotter:
    @staticmethod
    def plot(job: Job, filename: str='output.pdf', output_path: str=None):

        for experiment_set in job.experiment_files:

            figs_axes = Plotter.single_experiment_set(experiment_set, job.mechanisms)

            plotter_util.build_pdf(figs_axes, filename=filename, path=output_path)

    @staticmethod
    def single_experiment_set_outcome(experiment_set: ExperimentSet, mechanisms: List[Mechanism]):

        # Plot the data
        # set_ydata = experiment_set
        set_xdata = experiment_set.get_time_x_data()

        exp_set = ExperimentSet
        cond_src = experiment_set.condition_source
        mech_opts_lst = mechanisms

        conditions = experiment_set.get_conditions()
        for condition in conditions:
            for variable in condition.results.get_variables():
                var_val = condition.results.get_variable(variable)

            for target in condition.results.get_targets():
                tar_val = condition.results.get_target(target)

        figs_axes = Plotter.single_set_outcome(set_ydata, set_xdata, exp_set, cond_src,
                                               mech_opts_lst=mech_opts_lst)
        # Send the data to the writer
        # EDIT: just writing to .npy files for now...
        source = exp_set['overall']['source']
        description = exp_set['overall']['description']
        np.save(f'results_{source}_{description}.npy', set_ydata)
        np.save(f'results_xdata_{source}_{description}.npy', set_xdata)
        # this is broken...
        # if exp_set['overall']['meas_type'] in parser.exp_checker.POINT_MEAS_TYPES:
        #    writer.sim_data.write_mech_results(exp_set, set_ydata)
        # else:
        #    writer.sim_data.write_mech_results_time(
        #        exp_set, set_ydata, set_xdata, cond_src)

    @staticmethod
    def single_experiment_set(experiment_set: ExperimentSet, mechanisms: List[Mechanism]):# (exp_set, gases, mech_spc_dcts, calc_type, x_src, cond_src, mech_opts_lst=None):
        """ Plots a single set (i.e., with any number of mechanisms)
        :param experiment_set: Experiment set
        :param mechanisms: Mechanisms
        """
        if experiment_set.calculation_type == CalculationType.OUTCOME:
            Plotter.single_experiment_set_outcome(experiment_set, mechanisms)
        elif experiment_set.calculation_type == CalculationType.SENSITIVITY:
            # Calculate the sensitivity coefficients
            set_sens, set_xdata = sim.old.simulator_main.single_set_outcome(exp_set, gases, mech_spc_dcts, 'sens',
                                                                            x_src)
            # Sort the sensitivity coefficients
            sorted_set_sens, sorted_set_rxns = sim.old.sort_sens.sort_single_set(
                set_sens, gases)
            # Remove endpoints if a JSR; super hacky :(
            if exp_set['overall']['reac_type'] == 'jsr':
                sorted_set_sens[:, :, 0, :] = np.nan
                sorted_set_sens[:, :, -1, :] = np.nan
            # Calculate the reference results (having to do this twice; once inside
            # sens and once here. Could do once and then pass to the sens code)
            set_ref_results, _ = sim.old.simulator_main.single_set_outcome(exp_set, gases, mech_spc_dcts, 'outcome',
                                                                           x_src)
            # Plot the data
            np.save('sens.npy', sorted_set_sens)
            np.save('sens_xdata.npy', set_xdata)
            figs_axes = plotter_sens.single_set_outcome(sorted_set_sens[:, :NRXNS], set_xdata,
                                                        sorted_set_rxns[:, :NRXNS], set_ref_results, exp_set)
            # Send the data to the writer
            if exp_set['overall']['meas_type'] in ('idt',):
                targs = exp_set['plot']['idt_targ'][0]
            else:
                targs = exp_set['spc'].keys()
            # targs = ['pressure',]
            # writer.new_sens.mult_mechs(sorted_set_sens, sorted_set_rxns, targs,
            #                           set_xdata, set_ref_results)
        elif experiment_set.calculation_type == CalculationType.PATHWAY:
            # Obtain the end states of each simulation; has shape (nmechs, nconds)
            set_end_tpx, set_xdata = sim.old.simulator_main.single_set_outcome(exp_set, gases, mech_spc_dcts,
                                                                               'pathways', x_src)
            figs_axes = pathways.single_set_outcome(set_end_tpx, set_xdata, exp_set, cond_src, gases)
        else:
            raise NotImplementedError(f"calc_type {experiment_set.calculation_type} is not implemented!")
        return figs_axes

    @staticmethod
    def single_set_outcome(set_ydata, set_xdata, exp_set, conds_src, mech_opts_lst=None):
        """ Plots results from a single set (i.e., any number of mechanisms). Also
            plots the experimental data if there are any

            :param set_ydata: the simulation results for a single set (i.e., for
                multiple mechanisms); shape=(nmechs, nconds, ntargs,
                ntimes) (the last dimension is omitted for some meas_types)
            :type set_ydata: numpy.ndarray
            :param set_xdata: the uniform x data used for all mechanisms; 1-D
            :type set_xdata: numpy.ndarray
            :param exp_set: exp_set object
            :type exp_set: dict
            :param conds_src: the source of the conditions; 'plot' or 'exps'
            :type conds_src: str
            :return figs_axes: list of figures with plots [(fig1, ax1), ...]
            :rtype: list
        """

        # Initialize some variables
        set_frmt = exp_set['plot_format']
        nmechs = len(set_ydata)
        if nmechs > 6:
            # Only 6 default colors defined at top of file...should fix this
            print('More than 6 mechanisms! This will cause plotting problems')

        # Build the empty figures and axes
        figs_axes = build_figs_axes(exp_set, set_frmt, conds_src, mech_opts_lst,
                                    nmechs)

        # Loop over each mechanism and plot
        mech_xdata = set_xdata  # xdata is same for all mechs
        for mech_idx in range(nmechs):
            mech_ydata = set_ydata[mech_idx]
            mech_frmt = _mech_frmt(exp_set, set_frmt, conds_src, mech_idx=mech_idx)
            figs_axes = single_mech(mech_ydata, mech_xdata, figs_axes, mech_frmt,
                                    exp_set, mech_idx=mech_idx)

        # Plot experimental data if present
        exp_ydata = exp_set['overall']['exp_ydata']
        exp_xdata = exp_set['overall']['exp_xdata']
        mech_frmt = _mech_frmt(exp_set, set_frmt, conds_src)
        figs_axes = single_mech(exp_ydata, exp_xdata, figs_axes, mech_frmt, exp_set)

        return figs_axes