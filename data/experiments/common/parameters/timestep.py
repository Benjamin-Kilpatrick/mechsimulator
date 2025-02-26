from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class Timestep(IParameter):
    def __init__(self,
                 timestep: float,
                 parameter: Optional[IParameter] = None):
        self.timestep: float = timestep
        IParameter.__init__(self, parameter)

    def get_timestep(self) -> float:
        return self.timestep

    def set_timestep(self, timestep: float):
        self.timestep = timestep
