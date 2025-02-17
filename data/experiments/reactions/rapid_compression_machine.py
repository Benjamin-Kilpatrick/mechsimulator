from typing import Optional

import numpy

from data.experiments.reactions.reaction import Reaction


class RapidCompressionMachine(Reaction):
    def __init__(self,
                 temperature: float,
                 pressure: float,
                 end_time: float,
                 time: Optional[float] = None,
                 volume_of_time: Optional[numpy.ndarray] = None):
        Reaction.__init__(self, temperature, pressure)
        self.end_time: float = end_time
        self.time: Optional[float] = time
        self.volume_of_time: Optional[numpy.ndarray] = volume_of_time
