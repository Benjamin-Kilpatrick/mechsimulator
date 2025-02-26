from typing import Optional

from data.experiments.common.parameters.parameter import IParameter
from data.experiments.common.phi import Phi


class PhiRatio(IParameter):
    def __init__(self,
                 phi: Phi,
                 parameter: Optional[IParameter] = None):
        self.phi: Phi = phi
        IParameter.__init__(self, parameter)

    def get_phi(self) -> Phi:
        return self.phi

    def set_phi(self, phi: Phi):
        self.phi = phi