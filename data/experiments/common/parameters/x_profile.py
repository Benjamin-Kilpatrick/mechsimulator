from typing import Optional

import numpy

from data.experiments.common.parameters.parameter import IParameter


class XProfile(IParameter):
    def __init__(self,
                 x_profile: numpy.ndarray,
                 parameter: Optional[IParameter] = None):
        self.x_profile: numpy.ndarray = x_profile
        IParameter.__init__(self, parameter)

    def get_x_profile(self) -> numpy.ndarray:
        return self.x_profile

    def set_x_profile(self, x_profile: numpy.ndarray):
        self.x_profile = x_profile