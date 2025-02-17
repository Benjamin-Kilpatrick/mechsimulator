from typing import Optional

from experiments.measurements.measurement import Measurement
from experiments.reactions.reaction import Reaction
from experiments.reactions.reaction_type import ReactionType


class ShockTube(Reaction):
    def __init__(self,
                 measurement: Measurement,
                 temperature: float,
                 pressure: float,
                 end_time: float,
                 dpdt: Optional[float] = None):
        Reaction.__init__(self, measurement, temperature, pressure)
        self.end_time: float = end_time
        self.dpdt: Optional[float] = dpdt

    def get_type(self) -> ReactionType:
        return ReactionType.SHOCK_TUBE
