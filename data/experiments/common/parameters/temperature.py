from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class Temperature(IParameter):
    def __init__(self,
                 temperature: float,
                 parameter: Optional[IParameter] = None):
        self.temperature: float = temperature
        IParameter.__init__(self, parameter)

    def get_temperature(self) -> float:
        return self.temperature

    def set_temperature(self, temperature: float):
        self.temperature = temperature