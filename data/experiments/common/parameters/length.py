from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class Length(IParameter):
    def __init__(self,
                 length: float,
                 parameter: Optional[IParameter] = None):
        self.length: float = length
        IParameter.__init__(self, parameter)

    def get_length(self) -> float:
        return self.length

    def set_length(self, length: float):
        self.length = length
