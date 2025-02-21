from typing import Optional, List, Any

import numpy

from data.experiments.common.temperature_profile import TemperatureProfile
from data.experiments.reactions.reaction import Reaction


class PlugFlowReactor(Reaction):
    def __init__(self,
                 temperature: float,
                 pressure: float,
                 length: float,
                 mdot: float,
                 area: float,
                 res_time: Optional[float] = None,
                 x_profile: Optional[numpy.ndarray] = None,
                 temperature_profile: Optional[List[TemperatureProfile]] = None,
                 t_profile_setpoints: Optional[numpy.ndarray] = None):
        Reaction.__init__(self, temperature, pressure)
        self.length: float = length
        self.res_time: float = res_time
        self.mdot: float = mdot
        self.area: float = area
        self.x_profile: Optional[numpy.ndarray] = x_profile
        self.t_profile: Optional[List[TemperatureProfile]] = temperature_profile
        self.t_profile_setpoints: Optional[numpy.ndarray] = t_profile_setpoints
