from data.experiments.common.phi import Phi
from data.experiments.reactions.reaction import Reaction


class FreeFlame(Reaction):
    def __init__(self,
                 temperature: float,
                 pressure: float,
                 phi: Phi):
        Reaction.__init__(self, temperature, pressure)
        self.phi: Phi = phi
