from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class Mdot(IParameter):
    def __init__(self,
                 mdot: float,
                 parameter: Optional[IParameter] = None):
        self.mdot: float = mdot
        IParameter.__init__(self, parameter)

    def get_mdot(self) -> float:
        return self.mdot

    def set_mdot(self, mdot: float):
        self.mdot = mdot