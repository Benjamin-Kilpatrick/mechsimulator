from typing import List

from data.experiments.common.variable_set import VariableSet
from data.experiments.measurement import Measurement
from data.experiments.reaction import Reaction
from data.mixtures.compound import Compound


class Experiment:
    """
    An Experiment has a variable set and a list of compounds
    """
    def __init__(self,
                 variables: VariableSet,
                 compounds: List[Compound]):
        self.variables: VariableSet = variables
        self.compounds: List[Compound] = compounds

    def __repr__(self) -> str:
        out = f"<Experiment variables:{self.variables}>"
        for compound in self.compounds:
            out += f"\n\t{compound}"
        return out