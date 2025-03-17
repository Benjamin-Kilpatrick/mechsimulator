from typing import List

from data.experiments.common.variable_set import VariableSet
from data.experiments.results import Results
from data.mixtures.compound import Compound


class Experiment:
    """
    An Experiment has a variable set and a list of compounds
    """
    def __init__(self,
                 conditions: VariableSet,
                 compounds: List[Compound],
                 results: Results):
        self.conditions: VariableSet = conditions
        self.compounds: List[Compound] = compounds
        self.results: Results = results

    def __repr__(self) -> str:
        out = f"<Experiment variables:{self.variables}>"
        for compound in self.compounds:
            out += f"\n\t{compound}"
        return out