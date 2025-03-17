from typing import List

from pint import Quantity

from data.experiments.common.variable import Variable
from data.experiments.common.variable_set import VariableSet


class VariableRange:
    """
    The range for a variable used to change a single variable over time
    """
    def __init__(self,
                 variable: Variable,
                 start: Quantity,
                 end: Quantity,
                 inc: Quantity,
                 conditions: VariableSet):
        self.variable: Variable = variable
        self.start: Quantity = start
        self.end: Quantity = end
        self.inc: Quantity = inc
        self.conditions: VariableSet = conditions

    def __repr__(self) -> str:
        return f"<VariableRange variable type:{self.variable} ({self.start}, {self.end}) inc:{self.inc}>"

    def generate(self) -> List[VariableSet]:
        """
        Generate a list of variable sets
        """
        out: List[VariableSet] = []
        curr: Quantity = self.start
        while curr <= self.end:
            variable_set: VariableSet = self.conditions.clone()
            variable_set.set(self.variable, curr)
            out.append(variable_set)
            curr += self.inc

        return out

    def get_variables(self) -> List[Variable]:
        return self.conditions.get_variables()

    def get(self, variable: Variable) -> Quantity:
        return self.conditions.get(variable)
