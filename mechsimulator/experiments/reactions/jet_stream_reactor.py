from experiments.measurements.measurement import Measurement
from experiments.reactions.reaction import Reaction
from experiments.reactions.reaction_type import ReactionType


class JetStreamReactor(Reaction):
    def __init__(self,
                 measurement: Measurement,
                 temperature: float,
                 pressure: float,
                 res_time: float,
                 mdot: float,
                 vol: float):
        Reaction.__init__(self, measurement, temperature, pressure)
        self.res_time: float = res_time
        self.mdot: float = mdot
        self.vol: float = vol

    def get_type(self) -> ReactionType:
        return ReactionType.JET_STREAM_REACTOR
