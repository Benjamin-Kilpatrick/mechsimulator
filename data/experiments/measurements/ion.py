from data.experiments.common.variable import Variable
from data.experiments.measurements.measurement import Measurement


class Ion(Measurement):
    def __init__(self,
                 variable: Variable,
                 timestep: float,
                 end_time: float):
        Measurement.__init__(self, variable)
        self.timestep: float = timestep
        self.end_time: float = end_time
