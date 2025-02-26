from typing import Optional

import numpy

from data.experiments.common.parameters.parameter import IParameter


class DpDt(IParameter):
    def __init__(self,
                 dpdt: numpy.ndarray,
                 parameter: Optional[IParameter] = None):
        self.dpdt: numpy.ndarray = dpdt
        IParameter.__init__(self, parameter)

    def get_dpdt(self) -> numpy.ndarray:
        return self.dpdt

    def set_dpdt(self, dpdt: numpy.ndarray):
        self.dpdt = dpdt