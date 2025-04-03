from typing import List

import numpy
import numpy as np

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.condition import Condition
from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.mechanism.mechanism import Mechanism
from sim.ReactionSimulator import ReactionSimulator
from sim.Reactors import Reactors
from sim.SimulatorUtils import SimulatorUtils


class OutcomeSimulator(ReactionSimulator):
    def shock_tube(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        ydata = numpy.ndarray(SimulatorUtils.generate_ydata_shape(experiment_set, mechanism), dtype='float')
        p_of_t = SimulatorUtils.generate_p_of_t(
            experiment_set.condition_range.conditions.get(Condition.END_TIME),
            experiment_set.condition_range.conditions.get(Condition.DPDT)
        )
        end_time = experiment_set.condition_range.conditions.get(Condition.END_TIME)
        exp_ndx = 0
        for experiment in experiment_set.simulated_experiments:
            concentrations, pressures, temps, times = Reactors.st(
                experiment.conditions.get(Condition.TEMPERATURE), experiment.conditions.get(Condition.PRESSURE),
                experiment.compounds, mechanism,
                experiment_set.get_target_species(), end_time, p_of_t
            )

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                SimulatorUtils.raise_invalid_pathways_error(experiment_set.reaction)

            elif experiment_set.measurement == Measurement.CONCENTRATION:
                # interpolate raw concentrations to fit uniform times
                concentrations = SimulatorUtils.interpolate(concentrations, times, experiment_set.get_time_x_data())
                T_of_t = SimulatorUtils.interpolate(temps, times, experiment_set.get_time_x_data())
                ydata[exp_ndx] = numpy.append(concentrations, T_of_t[numpy.newaxis, :], axis=0)

            elif experiment_set.measurement == Measurement.IGNITION_DELAY_TIME:
                ydata[exp_ndx] = SimulatorUtils.calculate_idt(experiment_set, times, pressures, concentrations)

            elif experiment_set.measurement == Measurement.HALF_LIFE:  # TODO: Currently assumes only one target
                half_value = concentrations[0][0] / 2
                index = numpy.abs(concentrations[0] - half_value).argmin()
                ydata[exp_ndx] = times[index]
                # NaN if half value not reached
                if half_value < numpy.min(concentrations[0]):
                    ydata[exp_ndx] = numpy.nan

            elif experiment_set.measurement == Measurement.ABSORPTION:
                active_species = experiment_set.condition_range.conditions.get(Condition.ACTIVE_SPECIES)
                absorption_coefficients = experiment_set.condition_range.conditions.get(Condition.ABS_COEFFICIENT)
                path_length = experiment.conditions.get(Condition.PATH_LENGTH)
                pressure = experiment.conditions.get(Condition.PRESSURE)
                target_species = experiment_set.get_target_species()
                num_wavelengths = len(experiment_set.condition_range.conditions.get(Condition.WAVELENGTH))
                num_active_species = len(active_species)
                num_targets = ydata.shape[1] if experiment_set.calculation_type == CalculationType.OUTCOME else ydata.shape[2]

                raw_transmission = numpy.full((num_targets, num_wavelengths), numpy.nan)
                for wavelength_ndx in range(num_wavelengths):
                    for species_ndx, curr_species in enumerate(active_species):
                        curr_coefficient = absorption_coefficients[wavelength_ndx + 1].get(curr_species)[0]
                        target_ndx = wavelength_ndx * (num_active_species + 1) + species_ndx
                        if curr_coefficient is not None:
                            curr_concentration = concentrations[target_species.index(curr_species)]
                            absorbance = curr_concentration * curr_coefficient * path_length * pressure
                            raw_transmission[target_ndx] = numpy.exp(-absorbance)
                    total_ndx = (wavelength_ndx + 1) * (num_active_species + 1) - 1
                    raw_transmission[total_ndx] = numpy.nanprod(raw_transmission, axis=0)
                percent_absorption = 100 * (1 - raw_transmission)
                ydata = SimulatorUtils.interpolate(percent_absorption, times, experiment_set.get_time_x_data())

            elif experiment_set.measurement == Measurement.OUTLET:
                # Get the y value AT end time
                ydata = SimulatorUtils.interpolate(concentrations, times, numpy.array([end_time]))
                ydata = ydata[:, -1]
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

            exp_ndx += 1
        return ydata

    def plug_flow_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism):  # TODO: Resolve Pathway
        dtype = 'object' if experiment_set.calculation_type == CalculationType.PATHWAY else 'float'
        ydata = numpy.ndarray(SimulatorUtils.generate_ydata_shape(experiment_set, mechanism), dtype=dtype)
        exp_ndx = 0
        for experiment in experiment_set.generate_simulated_conditions():
            concentrations, times, positions, rop, end_gas = Reactors.pfr(
                experiment.conditions.get(Condition.TEMPERATURE),
                experiment.conditions.get(Condition.PRESSURE),
                experiment.compounds, mechanism,
                experiment_set.get_target_species(),
                experiment.conditions.get(Condition.MDOT),
                experiment.conditions.get(Condition.AREA),
                experiment.conditions.get(Condition.LENGTH),
                experiment.conditions.get(Condition.RES_TIME),
                experiment.conditions.get(Condition.X_PROFILE),
                experiment.conditions.get(Condition.TIME_PROFILE),
                experiment.conditions.get(Condition.TIME_PROFILE_SETPOINTS)
            )

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                ydata[exp_ndx] = end_gas.TPX
            elif experiment_set.measurement == Measurement.OUTLET:
                ydata[exp_ndx] = concentrations[:, -1]  # Outlet just wants last entry
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)
            exp_ndx += 1
        return ydata

    def jet_stream_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism, previous_solutions=None, output_all=False):
        ydata_shape = SimulatorUtils.generate_ydata_shape(experiment_set, mechanism)
        dtype = 'object' if experiment_set.calculation_type == CalculationType.PATHWAY else 'float'
        ydata = numpy.ndarray(ydata_shape, dtype=dtype)

        # Make sure that the prev_soln array is the right size (if given)
        if previous_solutions is not None:
            prev_solns_shape = np.shape(previous_solutions)
            assert prev_solns_shape[0] == ydata_shape[0]  # [0] is # of conditions
            assert prev_solns_shape[1] == mechanism.n_species  # TODO: Have existential crisis about what gas isn_species

        all_concentrations = np.ndarray((ydata_shape[0], mechanism.n_species))

        for exp_ndx, experiment in enumerate(experiment_set.generate_simulated_conditions()):
            concentrations, previous_concentrations, end_gas = Reactors.jsr(
                experiment.conditions.get(Condition.TEMPERATURE),
                experiment.conditions.get(Condition.PRESSURE),
                experiment.compounds, mechanism,
                experiment_set.get_target_species(),
                experiment.conditions.get(Condition.RES_TIME),
                experiment.conditions.get(Condition.VOLUME),
                experiment.conditions.get(Condition.MDOT),
                previous_concentrations=previous_concentrations
            )

            if output_all:
                all_concentrations[exp_ndx, :] = previous_concentrations

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                ydata[exp_ndx] = end_gas.TPX
            elif experiment_set.measurement == Measurement.Outlet:
                ydata[exp_ndx] = concentrations
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

        return ydata, all_concentrations

    def rapid_compression_machine(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        ydata = numpy.ndarray(SimulatorUtils.generate_ydata_shape(experiment_set, mechanism))
        for exp_ndx, experiment in enumerate(experiment_set.generate_simulated_conditions()):
            concentrations, pressures, times = Reactors.rcm(
                experiment.conditions.get(Condition.TEMPERATURE),
                experiment.conditions.get(Condition.PRESSURE),
                experiment.compounds, mechanism,
                experiment_set.get_target_species(),
                experiment.conditions.get(Condition.END_TIME),
                experiment.conditions.get(Condition.V_OF_T)
            )

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                SimulatorUtils.raise_invalid_pathways_error(experiment_set.reaction)
            elif experiment_set.measurement == Measurement.IGNITION_DELAY_TIME:
                ydata[exp_ndx] = SimulatorUtils.calculate_idt(experiment_set, times, pressures, concentrations)
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)


    def const_t_p(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        dtype = 'object' if experiment_set.calculation_type == CalculationType.PATHWAY else 'float'
        ydata = numpy.ndarray(SimulatorUtils.generate_ydata_shape(experiment_set, mechanism), dtype=dtype)

        for exp_ndx, experiment in enumerate(experiment_set.generate_simulated_conditions()):
            concentrations, pressures, temps, times, end_gas = Reactors.const_t_p(
                experiment.conditions.get(Condition.TEMPERATURE),
                experiment.conditions.get(Condition.PRESSURE),
                experiment.compounds,
                mechanism,
                experiment_set.get_target_species(),
                experiment.conditions.get(Condition.END_TIME)
            )

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                ydata[exp_ndx] = end_gas.TPX
            elif experiment_set.measurement == Measurement.CONCENTRATION:
                ydata[exp_ndx] = SimulatorUtils.interpolate(concentrations, times, experiment_set.get_time_x_data())
            elif experiment_set.measurement == Measurement.OUTLET:
                ydata[exp_ndx] = SimulatorUtils.interpolate(
                    concentrations, times, numpy.array([experiment.conditions.get(Condition.END_TIME)]))[:, -1]
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

        return ydata


    def free_flame(self, experiment_set: ExperimentSet, mechanism: Mechanism, previous_solutions: List = None):
        ydata = numpy.ndarray(SimulatorUtils.generate_ydata_shape(experiment_set, mechanism))
        new_solution_list = []

        for exp_ndx, experiment in enumerate(experiment_set.generate_simulated_conditions()):
            if previous_solutions is not None:
                previous_solution = previous_solutions[exp_ndx]
            else:
                previous_solution = new_solution_list[exp_ndx - 1] if exp_ndx > 0 else None
            concentrations, positions, velocities, temps, rop, end_gas = Reactors.free_flame(
                experiment.conditions.get(Condition.TEMPERATURE),
                experiment.conditions.get(Condition.PRESSURE),
                experiment.compounds, mechanism,
                experiment_set.get_target_species(),
                previous_solution = previous_solution
            )
            new_solution = np.vstack((positions / max(positions), temps))  # normalize position
            new_solution_list.append(new_solution)

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                SimulatorUtils.raise_invalid_pathways_error(experiment_set.reaction)
            elif experiment_set.measurement == Measurement.LFS:
                ydata[exp_ndx] = velocities[0] * 100
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

        return ydata, new_solution_list

