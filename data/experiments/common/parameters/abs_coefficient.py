from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class AbsCoefficient(IParameter):
    def __init__(self,
                 abs_coeff: float,
                 parameter: Optional[IParameter] = None):
        self.abs_coeff: float = abs_coeff
        IParameter.__init__(self, parameter)

    def get_abs_coeff(self) -> float:
        return self.abs_coeff

    def set_abs_coeff(self, abs_coeff: float):
        self.abs_coeff = abs_coeff
