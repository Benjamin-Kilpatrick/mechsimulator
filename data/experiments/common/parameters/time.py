from typing import Optional

import numpy

from data.experiments.common.parameters.parameter import IParameter


class Time(IParameter):
    def __init__(self,
                 time: numpy.ndarray,
                 parameter: Optional[IParameter] = None):
        self.time: numpy.ndarray = time
        IParameter.__init__(self, parameter)

    def get_time(self) -> numpy.ndarray:
        return self.time

    def set_time(self, time: numpy.ndarray):
        self.time = time