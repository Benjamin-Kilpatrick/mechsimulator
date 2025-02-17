from experiments.common.variable import Variable
from experiments.measurements.measurement import Measurement
from experiments.measurements.measurement_type import MeasurementType


class Concentration(Measurement):
    def __init__(self,
                 variable: Variable,
                 timestep: float,
                 end_time: float):
        Measurement.__init__(self, variable)
        self.timestep: float = timestep
        self.end_time: float = end_time

    def get_type(self) -> MeasurementType:
        return MeasurementType.CONCENTRATION
