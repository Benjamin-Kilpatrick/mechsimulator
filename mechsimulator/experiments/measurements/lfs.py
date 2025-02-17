from experiments.common.variable import Variable
from experiments.measurements.measurement import Measurement
from experiments.measurements.measurement_type import MeasurementType


class Lfs(Measurement):
    def __init__(self,
                 variable: Variable):
        Measurement.__init__(self, variable)

    def get_type(self) -> MeasurementType:
        return MeasurementType.LFS
