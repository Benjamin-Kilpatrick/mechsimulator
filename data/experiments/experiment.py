from typing import List

from data.experiments.common.variable_set import VariableSet
from data.experiments.results import Results
from data.mixtures.compound import Compound


class Experiment:
    def __init__(self,
                 variables: VariableSet,
                 compounds: List[Compound],
                 results: Results):
        self.variables: VariableSet = variables
        self.compounds: List[Compound] = compounds
        self.results: Results = results

