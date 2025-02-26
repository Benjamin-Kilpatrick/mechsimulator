from typing import Optional

import numpy

from data.experiments.common.parameters.parameter import IParameter


class TProfile(IParameter):
    def __init__(self,
                 t_profile: numpy.ndarray,
                 parameter: Optional[IParameter] = None):
        self.t_profile: numpy.ndarray = t_profile
        IParameter.__init__(self, parameter)

    def get_t_profile(self) -> numpy.ndarray:
        return self.t_profile

    def set_t_profile(self, t_profile: numpy.ndarray):
        self.t_profile = t_profile