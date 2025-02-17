from data.experiments.common.variable import Variable
from data.experiments.datapoint import Datapoint


class Measurement:
    def __init__(self, variable: Variable):
        self.variable: Variable = variable

    def initialize_datapoint(self, data):
        raise NotImplementedError

    def get_datapoint(self) -> Datapoint:
        raise NotImplementedError
