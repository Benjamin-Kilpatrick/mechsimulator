from typing import List

from data.experiments.common.variable_set import VariableSet
from data.experiments.measurement import Measurement
from data.experiments.reaction import Reaction
from data.mixtures.compound import Compound


class Experiment:
    def __init__(self,
                 variables: VariableSet,
                 compounds: List[Compound]):
        self.variables: VariableSet = variables
        self.compounds: List[Compound] = compounds

