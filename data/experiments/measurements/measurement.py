from typing import Optional

from data.common.value import Value
from data.experiments.datapoint import Datapoint


class Measurement:
    def __init__(self, value: Value):
        self.value: Value = value

    def initialize_datapoint(self, data):
        raise NotImplementedError

    def get_datapoint(self) -> Datapoint:
        raise NotImplementedError
