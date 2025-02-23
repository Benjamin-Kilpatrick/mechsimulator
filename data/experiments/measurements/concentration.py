from data.common.value import Value
from data.experiments.measurements.measurement import Measurement



class Concentration(Measurement):
    def __init__(self,
                 value: Value,
                 timestep: float,
                 end_time: float):
        Measurement.__init__(self, value)
        self.timestep: float = timestep
        self.end_time: float = end_time
