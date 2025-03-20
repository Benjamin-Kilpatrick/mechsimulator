from typing import List

from pint import Quantity

from data.experiments.common.variable import Variable
from data.experiments.common.variable_set import VariableSet


class VariableRange:
    """
    A generator of conditions based on a variable of interest
    """
    def __init__(self,
                 variable: Variable,
                 start: Quantity,
                 end: Quantity,
                 inc: Quantity,
                 conditions: VariableSet):
        """
        Constructor
        :param variable: variable of interest
        :param start: start value
        :param end: end value
        :param inc: increment
        :param conditions: set of conditions
        """
        self.variable: Variable = variable
        self.start: Quantity = start
        self.end: Quantity = end
        self.inc: Quantity = inc
        self.conditions: VariableSet = conditions

    def __repr__(self) -> str:
        return f"<VariableRange variable type:{self.variable} ({self.start}, {self.end}) inc:{self.inc}>"

    def generate(self) -> List[VariableSet]:
        """
        Generate a list of conditions, with the variable of interest condition changing from start to end with an
        interval of increment
        :return: a list of conditions
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
        """
        Get a list of all set variables
        :return: a list of all set variables
        """
        return self.conditions.get_variables()

    def get(self, variable: Variable) -> Quantity:
        """
        Get the value of a set variable
        :param variable: the type of variable
        :return:
        """
        return self.conditions.get(variable)
