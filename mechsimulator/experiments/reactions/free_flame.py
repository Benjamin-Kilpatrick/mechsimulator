from typing import Optional

from experiments.measurements.measurement import Measurement
from experiments.reactions.phi import Phi
from experiments.reactions.reaction import Reaction
from experiments.reactions.reaction_type import ReactionType


class FreeFlame(Reaction):
    def __init__(self,
                 measurement: Measurement,
                 temperature: float,
                 pressure: float,
                 phi: Phi):
        Reaction.__init__(self, measurement, temperature, pressure)
        self.phi: Phi = phi

    def get_type(self) -> ReactionType:
        return ReactionType.FREE_FLAME
