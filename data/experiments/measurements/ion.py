from data.common.value import Value
from data.experiments.common.variable import Variable
from data.experiments.measurements.measurement import Measurement


class Ion(Measurement):
    def __init__(self,
                 value: Value,
                 timestep: float,
                 end_time: float):
        Measurement.__init__(self, value)
        self.timestep: float = timestep
        self.end_time: float = end_time
