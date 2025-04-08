from typing import List

from pint import Quantity

from data.experiments.common.condition import Condition
from data.experiments.common.condition_set import ConditionSet
from data.experiments.results import Results
from data.mixtures.compound import Compound


class Experiment:
    """
    An aggregation of conditions, mixture of compounds and measured results
    """

    def __init__(self,
                 conditions: ConditionSet,
                 compounds: List[Compound],
                 results: Results):
        """
        Constructor
        :param conditions: The experimental conditions
        :param compounds: The starting mixture of gas compounds
        :param results: Measured results (may be empty for simulated experiments)
        """
        self.conditions: ConditionSet = conditions
        self.compounds: List[Compound] = compounds
        self.results: Results = results

    def __repr__(self) -> str:
        out = f"<Experiment variables:{self.variables}>"
        for compound in self.compounds:
            out += f"\n\t{compound}"
        return out

    def get_compounds(self) -> List[Compound]:
        """
        Get the list of compound mixtures
        :return: a list of compound mixtures
        """
        return self.compounds

    def get_results(self) -> Results:
        """
        Get the set of results
        :return: a set of results
        """
        return self.results

    def has(self, condition: Condition) -> bool:
        """
        Check if the experiment contains this condition
        :param condition: the condition to check
        :return: if the condition is present
        """
        return self.conditions.has(condition)

    def get(self, condition: Condition) -> Quantity:
        """
        Get a condition's value, which is either a scalar or array
        :param condition: the condition to get the value of
        :return: the value of the condition
        """
        return self.conditions.get(condition)
