from typing import Dict, Any, List

from pint import Quantity
from typing_extensions import Self

from data.experiments.common.variable import Variable


class VariableSet:
    def __init__(self):
        self.variable_set: Dict[Variable, Quantity] = {}

    def set(self, variable: Variable, value: Quantity):
        self.variable_set[variable] = value

    def get(self, variable: Variable) -> Quantity:
        return self.variable_set[variable]

    def has(self, variable: Variable) -> bool:
        return variable in self.variable_set.keys()

    def clone(self) -> Self:
        variable_set: VariableSet = VariableSet()
        variable_set.variable_set = self.variable_set.copy()
        return variable_set

    def get_variables(self) -> List[Variable]:
        return list(self.variable_set.keys())

