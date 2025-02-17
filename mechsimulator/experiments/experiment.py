from typing import List, Optional

from experiments.condition import Condition
from experiments.datapoint import Datapoint
from experiments.result import Result
from mixtures.compound import Compound


class Experiment:
    def __init__(self,
                 conditions: List[Condition],
                 datapoint: Optional[Datapoint]):
        self.conditions: List[Condition] = conditions
        self.datapoint: Datapoint = datapoint

    def populate_datapoint(self,
                           mixture: List[Compound],
                           results: List[Result]) -> Datapoint:
        self.datapoint = Datapoint(mixture, results)

        return self.datapoint
