from typing import List

import numpy
from typing_extensions import Any

from data.experiments.common.variable import Variable
from data.experiments.common.variable_set import VariableSet


class VariableRange:
    def __init__(self,
                 variable: Variable,
                 start: float,
                 end: float,
                 inc: float,
                 variable_set: VariableSet):
        self.variable: Variable = variable
        self.start: float = start
        self.end: float = end
        self.inc: float = inc
        self.variable_set: VariableSet = variable_set

    def generate(self) -> List[VariableSet]:
        out: List[VariableSet] = []
        curr: float = self.start
        while curr <= self.end:
            variable_set: VariableSet = self.variable_set.clone()
            variable_set.set(self.variable, curr)
            out.append(variable_set)
            curr += self.inc

        return out

    def get_variables(self) -> List[Variable]:
        return self.variable_set.get_variables()

    def get(self, variable: Variable) -> Any:
        return self.variable_set.get(variable)
