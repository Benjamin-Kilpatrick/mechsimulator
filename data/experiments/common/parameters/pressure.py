from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class Pressure(IParameter):
    def __init__(self,
                 pressure: float,
                 parameter: Optional[IParameter] = None):
        self.pressure: float = pressure
        IParameter.__init__(self, parameter)

    def get_pressure(self) -> float:
        return self.pressure

    def set_pressure(self, pressure: float):
        self.pressure = pressure