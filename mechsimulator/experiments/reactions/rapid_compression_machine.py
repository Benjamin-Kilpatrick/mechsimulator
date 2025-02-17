from typing import Optional

import numpy

from experiments.measurements.measurement import Measurement
from experiments.reactions.reaction import Reaction
from experiments.reactions.reaction_type import ReactionType


class RapidCompressionMachine(Reaction):
    def __init__(self,
                 measurement: Measurement,
                 temperature: float,
                 pressure: float,
                 end_time: float,
                 time: Optional[float] = None,
                 volume_of_time: Optional[numpy.ndarray] = None):
        Reaction.__init__(self, measurement, temperature, pressure)
        self.end_time: float = end_time
        self.time: Optional[float] = time
        self.volume_of_time: Optional[numpy.ndarray] = volume_of_time

    def get_type(self) -> ReactionType:
        return ReactionType.RAPID_COMPRESSION_MACHINE
