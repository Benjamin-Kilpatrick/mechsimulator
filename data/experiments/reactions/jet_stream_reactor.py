from data.experiments.reactions.reaction import Reaction


class JetStreamReactor(Reaction):
    def __init__(self,
                 temperature: float,
                 pressure: float,
                 res_time: float,
                 mdot: float,
                 vol: float):
        Reaction.__init__(self, temperature, pressure)
        self.res_time: float = res_time
        self.mdot: float = mdot
        self.vol: float = vol
