from typing import Tuple, List

import numpy

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.condition import Condition
from data.experiments.common.idt_method import IDTMethod
from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.mechanism.mechanism import Mechanism


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
        shape: List[int] = [len(experiment_set.get_conditions())]
        if experiment_set.calculation_type == CalculationType.PATHWAY:
            return tuple(shape)

        # Targets length
        if experiment_set.measurement in (Measurement.ABSORPTION, Measurement.EMISSION):
            num_wavelengths = len(experiment_set.condition_range.conditions.get(Condition.WAVELENGTH))
            num_active_species = len(experiment_set.condition_range.conditions.get(Condition.ACTIVE_SPECIES))
            shape.append(num_wavelengths * (num_active_species + 1))
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
    def calculate_idt(experiment_set:ExperimentSet, times, pressures, concentrations):  # TODO: Resolve pressure
        """ Gets the ignition delay time for a shock-tube simulation. Can determine
            IDT using one of three methods.

            :param target_profile: the target concentration used to determine IDT
            :param times: the time values corresponding to target
            :param method: the method by which to determine the IDT; options are as
                follows:
                1: intersection of steepest slope with baseline
                2: point of steepest slope
                3: peak value of the target profile
            :type method: str
            :return idt: ignition delay time (s)
            :rtype: float
            :return warnings: possible warnings regarding the IDT determination
            :rtype: list of strs
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

