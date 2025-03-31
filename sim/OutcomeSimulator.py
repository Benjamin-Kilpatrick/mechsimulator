from typing import List

import numpy

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
        mech_ydata = numpy.ndarray(SimulatorUtils.generate_ydata_shape(experiment_set, mechanism), dtype='float')
        p_of_t = SimulatorUtils.generate_p_of_t(
            experiment_set.condition_range.conditions.get(Condition.END_TIME),
            experiment_set.condition_range.conditions.get(Condition.DPDT)
        )
        end_time = experiment_set.condition_range.conditions.get(Condition.END_TIME)
        curr_ndx = 0
        for experiment in experiment_set.simulated_experiments:
            concentrations, pressures, temps, times = Reactors.st(
                experiment.conditions.get(Condition.TEMPERATURE), experiment.conditions.get(Condition.PRESSURE),
                experiment.compounds, mechanism,
                experiment_set.get_target_species(), end_time, p_of_t
            )

            if experiment_set.measurement == Measurement.CONCENTRATION:
                # interpolate raw concentrations to fit uniform times
                concentrations = SimulatorUtils.interpolate(concentrations, times, experiment_set.get_time_x_data())
                T_of_t = SimulatorUtils.interpolate(temps, times, experiment_set.get_time_x_data())
                ydata = numpy.append(concentrations, T_of_t[numpy.newaxis, :], axis=0)

            elif experiment_set.measurement == Measurement.IGNITION_DELAY_TIME:
                raise NotImplementedError('IGNITION_DELAY_TIME is not implemented yet')

            elif experiment_set.measurement == Measurement.HALF_LIFE: # TODO: Currently assumes only one target
                half_value = concentrations[0][0] / 2
                index = numpy.abs(concentrations[0] - half_value).argmin()
                ydata = times[index]
                # NaN if half value not reached
                if half_value < numpy.min(concentrations[0]):
                    ydata = numpy.nan

            elif experiment_set.measurement == Measurement.ABSORPTION:
                active_species = experiment_set.condition_range.conditions.get(Condition.ACTIVE_SPECIES)
                absorption_coefficients = experiment_set.condition_range.conditions.get(Condition.ABS_COEFFICIENT)
                path_length = experiment.conditions.get(Condition.PATH_LENGTH)
                pressure = experiment.conditions.get(Condition.PRESSURE)
                target_species = experiment_set.get_target_species()
                num_wavelengths = len(experiment_set.condition_range.conditions.get(Condition.WAVELENGTH))
                num_active_species = len(active_species)
                num_targets = mech_ydata.shape[1] if experiment_set.calculation_type == CalculationType.OUTCOME else mech_ydata.shape[2]

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
                raise ValueError(f'Shock tube reactions are not equipped to calculate {experiment_set.measurement}')

            mech_ydata[curr_ndx] = ydata
            curr_ndx += 1
        return mech_ydata

    def process_st(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def plug_flow_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_pfr(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def jet_stream_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_jsr(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def rapid_compression_machine(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_rcm(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def const_t_p(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_const_t_p(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def free_flame(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_free_flame(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError
