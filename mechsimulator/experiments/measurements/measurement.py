from experiments.common.variable import Variable
from experiments.measurements.measurement_type import MeasurementType


class Measurement:
    def __init__(self, variable: Variable):
        self.variable: Variable = variable

    def get_type(self) -> MeasurementType:
        raise NotImplementedError
