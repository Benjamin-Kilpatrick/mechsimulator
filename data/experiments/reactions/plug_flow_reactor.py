from typing import Optional

import numpy

from experiments.measurements.measurement import Measurement
from experiments.reactions.reaction import Reaction


class PlugFlowReactor(Reaction):
    def __init__(self,
                 temperature: float,
                 pressure: float,
                 length: float,
                 res_time: float,
                 mdot: float,
                 area: float,
                 x_profile: Optional[numpy.ndarray] = None,
                 t_profile: Optional[numpy.ndarray] = None,
                 t_profile_setpoints: Optional[numpy.ndarray] = None):
        Reaction.__init__(self, temperature, pressure)
        self.length: float = length
        self.res_time: float = res_time
        self.mdot: float = mdot
        self.area: float = area
        self.x_profile: Optional[numpy.ndarray] = x_profile
        self.t_profile: Optional[numpy.ndarray] = t_profile
        self.t_profile_setpoints: Optional[numpy.ndarray] = t_profile_setpoints
