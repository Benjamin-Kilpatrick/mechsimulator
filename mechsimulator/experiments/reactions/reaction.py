from experiments.measurements.measurement import Measurement
from experiments.reactions.reaction_type import ReactionType


class Reaction:
    def __init__(self,
                 measurement: Measurement,
                 temperature: float,
                 pressure: float):
        self.measurement: Measurement = measurement
        self.temperature: float = temperature
        self.pressure: float = pressure

    def get_type(self) -> ReactionType:
        raise NotImplementedError
