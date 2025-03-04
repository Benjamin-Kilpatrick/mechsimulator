from typing import Dict, Any

from typing_extensions import Self

from data.experiments.common.variable import Variable


class VariableSet:
    def __init__(self):
        self.variable_set: Dict[Variable, Any] = {}

    def set(self, variable: Variable, value: Any):
        self.variable_set[variable] = value

    def get(self, variable: Variable) -> Any:
        return self.variable_set[variable]

    def has(self, variable: Variable) -> bool:
        return variable in self.variable_set.keys()

    def clone(self) -> Self:
        variable_set: VariableSet = VariableSet()
        variable_set.variable_set = self.variable_set.copy()
        return variable_set
