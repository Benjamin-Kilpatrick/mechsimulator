from typing import List

from data.experiments.common.variable_set import VariableSet
from data.experiments.results import Results
from data.mixtures.compound import Compound


class Experiment:
    def __init__(self,
                 conditions: VariableSet,
                 compounds: List[Compound],
                 results: Results):
        self.conditions: VariableSet = conditions
        self.compounds: List[Compound] = compounds
        self.results: Results = results

