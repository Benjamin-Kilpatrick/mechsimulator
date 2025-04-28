from typing import List

import numpy
import numpy as np

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.condition import Condition
from data.experiments.common.idt_method import IDTMethod
from data.experiments.experiment import Experiment
from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species
from sim.ReactionSimulator import ReactionSimulator
from sim.Reactors import Reactors
from sim.SimulatorUtils import SimulatorUtils


class OutcomeSimulator(ReactionSimulator):
    def shock_tube(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        for experiment in experiments:
            concentrations, pressures, temps, times = Reactors.st(
                *self.get_basic_args(experiment_set, experiment, mechanism),
                experiment_set.condition_range.conditions.get(Condition.END_TIME),
                SimulatorUtils.generate_p_of_t(
                    experiment_set.condition_source,
                    experiment
                )
            )

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                SimulatorUtils.raise_invalid_pathways_error(experiment_set.reaction)

            elif experiment_set.measurement == Measurement.CONCENTRATION:
                # interpolate raw concentrations to fit uniform times
                concentrations = SimulatorUtils.interpolate(concentrations, times, experiment_set.get_time_x_data())
                T_of_t = SimulatorUtils.interpolate(temps, times, experiment_set.get_time_x_data())
                data = numpy.append(concentrations, T_of_t[numpy.newaxis, :], axis=0)
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)

            elif experiment_set.measurement == Measurement.IGNITION_DELAY_TIME:
                data = self.calculate_idt(experiment_set, times, pressures, concentrations)
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)

            elif experiment_set.measurement == Measurement.HALF_LIFE:  # TODO: Currently assumes only one target
                half_value = concentrations[0][0] / 2
                index = numpy.abs(concentrations[0] - half_value).argmin()
                data = times[index]
                # NaN if half value not reached
                if half_value < numpy.min(concentrations[0]):
                    data = numpy.nan
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)

            elif experiment_set.measurement == Measurement.ABSORPTION:
                data = self.calculate_absorption(experiment_set, experiment, concentrations, times)
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)

            elif experiment_set.measurement == Measurement.OUTLET:
                # Get the y value AT end time
                data = self.get_outlet(SimulatorUtils.interpolate(concentrations, times, numpy.array([experiment_set.condition_range.conditions.get(Condition.END_TIME)])))
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)

            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

    def plug_flow_reactor(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        for experiment in experiments:
            concentrations, times, positions, end_gas = Reactors.pfr(
                *self.get_basic_args(experiment_set, experiment, mechanism),
                experiment.conditions.get(Condition.MDOT),
                experiment.conditions.get(Condition.AREA),
                experiment.conditions.get(Condition.LENGTH),
                experiment.conditions.get(Condition.RES_TIME),
                experiment.conditions.get(Condition.X_PROFILE),
                experiment.conditions.get(Condition.TIME_PROFILE),
                experiment.conditions.get(Condition.TIME_PROFILE_SETPOINTS)
            )

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                data = self.get_pathway(end_gas)
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)
            elif experiment_set.measurement == Measurement.OUTLET:
                data = self.get_outlet(concentrations)
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

    def jet_stream_reactor(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism, previous_solutions=None):
        # Make sure that the prev_soln array is the right size (if given)
        num_conditions = len(experiment_set.all_simulated_experiments[0])
        if previous_solutions is not None:
            prev_solns_shape = np.shape(previous_solutions)
            assert prev_solns_shape[0] == num_conditions
            assert prev_solns_shape[1] == mechanism.solution.n_species  # Num targets?

        all_concentrations = np.ndarray((num_conditions, mechanism.solution.n_species))

        for exp_ndx, experiment in enumerate(experiments):
            previous_concentrations = None
            if previous_solutions is not None:
                previous_concentrations = previous_solutions[exp_ndx]

            concentrations, previous_concentrations, end_gas = Reactors.jsr(
                *self.get_basic_args(experiment_set, experiment, mechanism),
                experiment.conditions.get(Condition.RES_TIME),
                experiment.conditions.get(Condition.VOLUME),
                experiment.conditions.get(Condition.MDOT),
                previous_concentrations=previous_concentrations
            )

            if previous_solutions is None: # We're here to GET previous solutions
                all_concentrations[exp_ndx, :] = previous_concentrations

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                data = self.get_pathway(end_gas)
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)
            elif experiment_set.measurement == Measurement.OUTLET:
                # Don't call get_outlet here, special case
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, concentrations)
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

        return all_concentrations

    def rapid_compression_machine(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        for experiment in experiments:
            concentrations, pressures, times = Reactors.rcm(
                *self.get_basic_args(experiment_set, experiment, mechanism),
                experiment.conditions.get(Condition.END_TIME),
                experiment.conditions.get(Condition.V_OF_T)
            )

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                SimulatorUtils.raise_invalid_pathways_error(experiment_set.reaction)
            elif experiment_set.measurement == Measurement.IGNITION_DELAY_TIME:
                data = self.calculate_idt(experiment_set, times, pressures, concentrations)
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

    def const_t_p(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        for experiment in experiments:
            concentrations, pressures, temps, times, end_gas = Reactors.const_t_p(
                *self.get_basic_args(experiment_set, experiment, mechanism),
                experiment.conditions.get(Condition.END_TIME)
            )

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                data = self.get_pathway(end_gas)
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)
            elif experiment_set.measurement == Measurement.CONCENTRATION:
                data = SimulatorUtils.interpolate(concentrations, times, experiment_set.get_time_x_data())
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)
            elif experiment_set.measurement == Measurement.OUTLET:
                data = self.get_outlet(SimulatorUtils.interpolate(concentrations, times, numpy.array(
                    [experiment.conditions.get(Condition.END_TIME)])))
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

    def free_flame(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism, previous_solutions: List = None):
        new_solution_list = []

        for exp_ndx, experiment in enumerate(experiments):
            if previous_solutions is not None:
                previous_solution = previous_solutions[exp_ndx]
            else:
                previous_solution = new_solution_list[exp_ndx - 1] if exp_ndx > 0 else None

            concentrations, positions, velocities, temps = Reactors.free_flame(
                *self.get_basic_args(experiment_set, experiment, mechanism), experiment.conditions.get(Condition.PHI),
                previous_solution=previous_solution
            )
            new_solution = np.vstack((positions / max(positions), temps))  # normalize position
            new_solution_list.append(new_solution)

            if experiment_set.calculation_type == CalculationType.PATHWAY:
                SimulatorUtils.raise_invalid_pathways_error(experiment_set.reaction)
            elif experiment_set.measurement == Measurement.LAMINAR_FLAME_SPEED:
                data = self.calculate_lfs(velocities)
                self.set_targets(experiment, experiment_set.get_target_species(), mechanism, data)
            else:
                SimulatorUtils.raise_reaction_measurement_error(experiment_set.reaction, experiment_set.measurement)

        return new_solution_list

    def calculate_idt(self, experiment_set: ExperimentSet, times, pressures, concentrations):  # TODO: Resolve pressure
        """ Gets the ignition delay time for a reaction. Can determine IDT using one of three methods. Options are as
            follows:
                1: intersection of steepest slope with baseline
                2: point of steepest slope
                3: peak value of the target profile

            @param experiment_set The experiment file which specifies the relevant conditions
            @param times The times which Cantera has given us
            @param pressures The pressures which Cantera has given us
            @param concentrations The concentrations which Cantera has given us
        """

        idt_targets = experiment_set.condition_range.conditions.get(Condition.IGNITION_DELAY_TARGETS)
        idt_methods = experiment_set.condition_range.conditions.get(Condition.IGNITION_DELAY_METHOD)
        target_species = experiment_set.get_target_species()
        ydata = numpy.ndarray((len(idt_targets)))
        for target_ndx, idt_target in enumerate(idt_targets):
            idt_method = idt_methods[target_ndx]
            if idt_target == Condition.PRESSURE:
                target_profile = pressures
            else:
                species_ndx = target_species.index(idt_target)
                target_profile = concentrations[species_ndx]

            # Get first derivative (note: np.gradient uses central differences)
            first_deriv = numpy.gradient(target_profile, times)
            steepest_ndx = numpy.argmax(first_deriv)
            steepest_slope = first_deriv[steepest_ndx]
            steepest_time = times[steepest_ndx]
            steepest_val = target_profile[steepest_ndx]

            # If using the baseline extrapolation or steepest slope methods, check that
            # the max slope isn't the last point
            if steepest_ndx + 1 == len(times) and idt_method in (IDTMethod.BASELINE_EXTRAPOLATION, IDTMethod.MAX_SLOPE):
                print('Max slope at last point')

            if idt_method == IDTMethod.BASELINE_EXTRAPOLATION:
                # Get the slope and intercept of the baseline, assuming 0 for now
                initial_slope = 0
                initial_int = 0
                # Get the y-intercept of the steepest tangent line
                steepest_int = steepest_val - steepest_slope * steepest_time
                # Find the intersection of the two lines
                ydata[target_ndx] = (initial_int - steepest_int) / (steepest_slope - initial_slope)
            elif idt_method == IDTMethod.MAX_SLOPE:
                ydata[target_ndx] = steepest_time
            elif idt_method == IDTMethod.MAX_VALUE:
                # Check that the max value doesn't occur at the last point
                if numpy.argmax(target_profile) + 1 == len(times):
                    print('Peak value at last point')
                ydata[target_ndx] = times[numpy.argmax(target_profile)]
            else:
                raise NotImplementedError

        return ydata

    def get_outlet(self, data):
        return data[:, -1]

    def calculate_absorption(self, experiment_set: ExperimentSet, experiment: Experiment, concentrations, times):
        active_species = experiment.conditions.get(Condition.ACTIVE_SPECIES)
        absorption_coefficients = experiment.conditions.get(Condition.ABS_COEFFICIENT)
        path_length = experiment.conditions.get(Condition.PATH_LENGTH)
        pressure = experiment.conditions.get(Condition.PRESSURE)
        target_species = experiment_set.get_target_species()
        num_wavelengths = len(experiment.conditions.get(Condition.WAVELENGTH))
        num_active_species = len(active_species)

        raw_transmission = numpy.full((len(target_species), num_wavelengths), numpy.nan)
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
        return SimulatorUtils.interpolate(percent_absorption, times, experiment_set.get_time_x_data())

    def get_pathway(self, end_gas):
        return end_gas.TPX

    def calculate_lfs(self, velocities):
        return velocities[0] * 100

    def set_targets(self, experiment, targets: List[Species], mechanism, data):
        for idx, target in enumerate(targets):
            name = target.name
            # ndx = mechanism.solution.species_index(name)
            experiment.results.set_target(name, data[idx])

    def get_basic_args(self, experiment_set, experiment, mechanism):
        return experiment.conditions.get(Condition.TEMPERATURE), experiment.conditions.get(Condition.PRESSURE), experiment.mixtures, mechanism.solution, experiment_set.get_target_species(),
