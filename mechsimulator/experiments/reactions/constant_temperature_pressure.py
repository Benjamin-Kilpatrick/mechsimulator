from experiments.reactions.reaction import Reaction


class ConstantTemperaturePressure(Reaction):
    def __init__(self,
                 temperature: float,
                 pressure: float,
                 end_time: float):
        Reaction.__init__(self, temperature, pressure)
        self.end_time: float = end_time
