from typing import Optional

import numpy

from data.experiments.reactions.reaction import Reaction


class ShockTube(Reaction):
    def __init__(self,
                 temperature: float,
                 pressure: float,
                 end_time: float,
                 dpdt: Optional[float] = None):
        Reaction.__init__(self, temperature, pressure)
        self.end_time: float = end_time
        self.dpdt: Optional[float] = dpdt
        
        self.p_of_t: Optional[numpy.ndarray] = None

        if self.dpdt is not None:
            self.p_of_t = ShockTube.create_p_of_t(end_time, dpdt)

    @staticmethod
    def create_p_of_t(end_time, dpdt):
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