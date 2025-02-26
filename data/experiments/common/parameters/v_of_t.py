from typing import Optional

import numpy

from data.experiments.common.parameters.parameter import IParameter


class VofT(IParameter):
    def __init__(self,
                 v_of_t: numpy.ndarray,
                 parameter: Optional[IParameter] = None):
        self.v_of_t: numpy.ndarray = v_of_t
        IParameter.__init__(self, parameter)

    def get_v_of_t(self) -> numpy.ndarray:
        return self.v_of_t

    def set_v_of_t(self, v_of_t: numpy.ndarray):
        self.v_of_t = v_of_t