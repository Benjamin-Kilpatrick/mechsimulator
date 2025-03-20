from typing import List

from data.experiments.common.variable_set import VariableSet
from data.experiments.results import Results
from data.mixtures.compound import Compound


class Experiment:
    """
    An aggregation of conditions, mixture of compounds and measured results
    """
    def __init__(self,
                 conditions: VariableSet,
                 compounds: List[Compound],
                 results: Results):
        """
        Constructor
        :param conditions: The experimental conditions
        :param compounds: The starting mixture of gas compounds
        :param results: Measured results (may be empty for simulated experiments)
        """
        self.conditions: VariableSet = conditions
        self.compounds: List[Compound] = compounds
        self.results: Results = results

    def __repr__(self) -> str:
        out = f"<Experiment variables:{self.variables}>"
        for compound in self.compounds:
            out += f"\n\t{compound}"
        return out