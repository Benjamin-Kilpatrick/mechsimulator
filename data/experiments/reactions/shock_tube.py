from typing import Optional

from data.experiments.reactions.reaction import Reaction


class ShockTube(Reaction):
    def __init__(self,
                 temperature: float,
                 pressure: float,
                 end_time: float,
                 dpdt: Optional[float] = None):
        Reaction.__init__(self, temperature, pressure)
        self.end_time: float = end_time
        self.dpdt: Optional[float] = dpdt
