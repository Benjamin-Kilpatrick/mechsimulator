from typing import Optional

import numpy

from data.experiments.common.parameters.parameter import IParameter


class TProfileSetpoints(IParameter):
    def __init__(self,
                 t_profile_setpoints: numpy.ndarray,
                 parameter: Optional[IParameter] = None):
        self.t_profile_setpoints: numpy.ndarray = t_profile_setpoints
        IParameter.__init__(self, parameter)

    def get_t_profile_setpoints(self) -> numpy.ndarray:
        return self.t_profile_setpoints

    def set_t_profile_setpoints(self, t_profile_setpoints: numpy.ndarray):
        self.t_profile_setpoints = t_profile_setpoints