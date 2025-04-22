from typing import Tuple, List, Dict

import numpy

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.condition import Condition
from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.mixture import Mixture
from data.experiments.mixture_type import MixtureType
from data.experiments.reaction import Reaction
from data.experiments.target_species import TargetSpecies
from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species


class SimulatorUtils:
    @staticmethod
    def interpolate(ydata: numpy.ndarray, xdata: numpy.ndarray, desired_xdata: numpy.ndarray) -> numpy.ndarray:
        """ Takes a y data array with some inconsistent and/or unknown step size in
            the x variable and interpolates the y data to make the x data have a
            uniform step size. The input y data may be a Numpy array of dimension 1
            or 2 (the second dimension must be the x dimension). xdata will usually
            be time or position

            :param ydata: Numpy array containing y data to be interpolated; can be
                one array (ndim=1) or multiple arrays (ndim=2) to be interpolated. Assumes x is the second dimension.
            :param xdata: Numpy array containing the x data corresponding to the y
                data; must have ndim=1 and be monotonically increasing
            :param desired_xdata: desired grid of x values to which the y data will
                be interpolated; must have ndim=1 and be monotonically increasing
            :return interp_ydata: the interpolated y data
        """

        num_dims = numpy.ndim(ydata)
        assert numpy.all(xdata[1:] > xdata[:-1]), (
            'xdata should be monotonically increasing ')

        # Interpolate the data; method depends on the dimensionality
        if num_dims == 1:
            interp_ydata = numpy.interp(desired_xdata, xdata, ydata)
        elif num_dims == 2:
            narrs = numpy.shape(ydata)[0]
            nxdata = len(desired_xdata)
            interp_ydata = numpy.ndarray((narrs, nxdata))
            for arr_idx, arr in enumerate(ydata):
                interp_ydata[arr_idx, :] = numpy.interp(desired_xdata, xdata, arr)
        else:
            raise ValueError(f'ydata arrays should have number of dimensions 1 or 2, not {num_dims}')

        # Get idxs beyond which the data doesn't extend
        high_cutoff = numpy.argmin(abs(desired_xdata - xdata[-1]))  # first match
        low_cutoff = numpy.argmin(abs(desired_xdata - xdata[0]))  # first match
        # Correct case when max desired_xdata is less than max xdata
        if max(desired_xdata) < max(xdata):
            high_cutoff = len(desired_xdata)

        # Set interpolated y data that extend past the given y data to NaN
        if num_dims == 1:
            interp_ydata[high_cutoff:] = numpy.nan
            interp_ydata[:low_cutoff] = numpy.nan
        else:  # num_dims = 2
            interp_ydata[:, high_cutoff:] = numpy.nan
            interp_ydata[:, :low_cutoff] = numpy.nan

        return interp_ydata

    @staticmethod
    def generate_p_of_t(end_time, dpdt):
        """ Creates a P(t) array from an end_time and a dP/dt

            :param end_time: final time of the simulation (seconds)
            :param dpdt: linear change in pressure during the simulation (%/ms)
            :return p_of_t: array of noramlized pressure starting at 1 and going
                to the end pressure calculated by the end_time and dpdt
            :rtype: Numpy array of shape (2,
        """

        times = numpy.array([0, end_time])
        end_pressure = 1 + ((end_time * 1e3) * dpdt) / 100
        pressures = numpy.array([1, end_pressure])
        p_of_t = numpy.vstack((times, pressures))

        return p_of_t

    @staticmethod
    def generate_ydata_shape(experiment_set: ExperimentSet, mechanism: Mechanism) -> Tuple:
        # Conditions length
        shape: List[int] = [len(experiment_set.generate_conditions())]
        if experiment_set.calculation_type == CalculationType.PATHWAY:
            return tuple(shape)

        # Targets length
        if experiment_set.measurement in (Measurement.ABSORPTION, Measurement.EMISSION):
            num_wavelengths = len(experiment_set.condition_range.conditions.get(Condition.WAVELENGTH))
            num_active_species = len(experiment_set.condition_range.conditions.get(Condition.ACTIVE_SPECIES))
            shape.append(num_wavelengths * (num_active_species + 1))  # Add one for aggregation
        elif experiment_set.measurement == Measurement.HALF_LIFE:
            shape.append(1)
        else:
            shape.append(len(experiment_set.get_target_species()))

        # Times length
        if experiment_set.measurement in (
                Measurement.ABSORPTION, Measurement.EMISSION,
                Measurement.PRESSURE, Measurement.CONCENTRATION
        ):
            shape.append(len(experiment_set.get_time_x_data()))

        # Prepend metadata if necessary
        if experiment_set.calculation_type == CalculationType.SENSITIVITY:
            shape = [mechanism.solution.n_reactions] + shape

        return tuple(shape)

    @staticmethod
    def raise_reaction_measurement_error(reaction: Reaction, measurement: Measurement):
        raise ValueError(f"{reaction} reactions are not equipped to calculate {measurement}")

    @staticmethod
    def raise_invalid_pathways_error(reaction: Reaction):
        raise ValueError(f"{reaction} cannot calculate pathways")

    @staticmethod
    def rename_list_species(species: List[Species], mech_dict: Dict[Species, Species]):
        for spc in species:
            if spc in mech_dict:
                spc.name = mech_dict[spc].name

    @staticmethod
    def rename_targets(targets: TargetSpecies, mech_dict: Dict[Species, Species]):
        SimulatorUtils.rename_list_species(targets.all_targets, mech_dict)
        for target_type in targets.get_special_target_enumerations():
            SimulatorUtils.rename_list_species(targets.get_special_targets(target_type), mech_dict)

    @staticmethod
    def rename_mixture(mixtures: Dict[MixtureType, Mixture], mech_dict: Dict[Species, Species]):
        for mixture_type, mixture in mixtures.items():
            mix_list = [spc for spc, _ in mixture.species]
            SimulatorUtils.rename_list_species(mix_list, mech_dict)

            if mixture.balanced in mech_dict:
                mixture.balanced.name = mech_dict[mixture.balanced].name

    @staticmethod
    def rename_all_species(experiment_set: ExperimentSet, mechanism: Mechanism):
        mech_species: Dict[Species, Species] = {}
        for species in mechanism.species:
            mech_species[species] = species

        # rename simulated species
        SimulatorUtils.rename_list_species(experiment_set.simulated_species, mech_species)
        SimulatorUtils.rename_targets(experiment_set.targets, mech_species)
        SimulatorUtils.rename_mixture(experiment_set.simulated_mixture, mech_species)

        # rename the mixtures in measured experiments
        for measured in experiment_set.measured_experiments:
            SimulatorUtils.rename_mixture(measured.mixtures, mech_species)

    @staticmethod
    def convert_gas_mixture(mixture: Mixture) -> Dict[str, float]:
        out: Dict[str, float] = {}
        sum: float = 0.0
        for spc, quantity in mixture.species:
            # maybe works???
            out[spc.name] = quantity.to('%')
            sum += out[spc.name]

        if mixture.balanced is not None:
            out[mixture.balanced.name] = 1.0 - sum

        return out

    @staticmethod
    def convert_fuel_mixture(fuel: Mixture, oxidizers: Mixture) -> Tuple[str, str]:
        fuel_strs: List[str] = [f'{spc.name}: {ratio.magnitude}' for spc, ratio in fuel.species]
        oxid_strs: List[str] = [f'{spc.name}: {ratio.magnitude}' for spc, ratio in oxidizers.species]

        fuel_string: str = ', '.join(fuel_strs)
        oxid_string: str = ', '.join(oxid_strs)

        return fuel_string, oxid_string
