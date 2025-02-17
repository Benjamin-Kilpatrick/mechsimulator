from typing import Optional

from experiments.measurements.measurement import Measurement
from experiments.reactions.reaction import Reaction
from experiments.reactions.reaction_type import ReactionType


class ConstantTemperaturePressure(Reaction):
    def __init__(self,
                 measurement: Measurement,
                 temperature: float,
                 pressure: float,
                 end_time: float):
        Reaction.__init__(self, measurement, temperature, pressure)
        self.end_time: float = end_time

    def get_type(self) -> ReactionType:
        return ReactionType.CONSTANT_TEMPERATURE_PRESSURE
