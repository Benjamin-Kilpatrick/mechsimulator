from typing import List, Dict

from pint import Quantity

from data.experiments.common.condition import Condition
from data.experiments.common.condition_set import ConditionSet
from data.experiments.mixture import Mixture
from data.experiments.mixture_type import MixtureType
from data.experiments.results import Results


class Experiment:
    """
    An aggregation of conditions, mixture of compounds and measured results
    """

    def __init__(self,
                 conditions: ConditionSet,
                 mixtures: Dict[MixtureType, Mixture],
                 results: Results):
        """
        Constructor
        :param conditions: The experimental conditions
        :param compounds: The starting mixture of gas compounds
        :param results: Measured results (may be empty for simulated experiments)
        """
        self.conditions: ConditionSet = conditions
        self.mixtures: Dict[MixtureType, Mixture] = mixtures
        self.results: Results = results

    def __repr__(self) -> str:
        out = f"<Experiment variables:{self.variables}>"
        for species, quantity in self.mixtures.species:
            out += f"\n\t{species.name} {quantity}"
        if self.mixtures.balanced is not None:
            out += f"\n\t{self.mixtures.balanced.name} balanced"
        return out



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

    def get_mixture(self, mixture_type: MixtureType) -> Mixture:
        if mixture_type in self.mixtures:
            return self.mixtures[mixture_type]
        raise Exception(f'{mixture_type.name} not found')
