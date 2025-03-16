from typing import List

import numpy

from data.experiments.common.variable import Variable
from data.experiments.common.variable_set import VariableSet


class VariableRange:
    """
    The range for a variable used to change a single variable over time
    """
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

    def __repr__(self) -> str:
        return f"<VariableRange variable type:{self.variable} ({self.start}, {self.end}) inc:{self.inc}>"

    def generate(self) -> List[VariableSet]:
        """
        Generate a list of variable sets
        """
        out: List[VariableSet] = []
        curr: float = self.start
        while curr <= self.end:
            variable_set: VariableSet = self.variable_set.clone()
            variable_set.set(self.variable, curr)
            out.append(variable_set)
            curr += self.inc

        return out
