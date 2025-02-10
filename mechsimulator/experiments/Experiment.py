from typing import List

import numpy

from common.UnitValue import UnitValue
from experiments.Mixture import Mixture


class ExperimentState:
    def __init__(self):
        raise NotImplementedError

class Result:
    def __init__(self, values: numpy.ndarray, bounds: UnitValue):
        self.values: numpy.ndarray = values
        self.bounds = bounds

class Experiment:
    def __init__(self,
                 id: int,
                 experiment_state: ExperimentState,
                 mixtures: List[Mixture],
                 results: List[Result]
                 ):

        self.id: int = id
        self.experiment_state: ExperimentState = experiment_state
        self.mixtures: List[Mixture] = mixtures
        self.results: List[Result] = results

