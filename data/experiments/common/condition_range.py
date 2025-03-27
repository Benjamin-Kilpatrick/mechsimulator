from typing import List

from pint import Quantity

from data.experiments.common.condition import Condition
from data.experiments.common.condition_set import ConditionSet


class ConditionRange:
    """
    A generator of conditions based on a variable of interest
    """
    def __init__(self,
                 variable_of_interest: Condition,
                 start: Quantity,
                 end: Quantity,
                 inc: Quantity,
                 conditions: ConditionSet):
        """
        Constructor
        :param variable_of_interest: variable of interest
        :param start: start value
        :param end: end value
        :param inc: increment
        :param conditions: set of conditions
        """
        self.variable_of_interest: Condition = variable_of_interest
        self.start: Quantity = start
        self.end: Quantity = end
        self.inc: Quantity = inc
        self.conditions: ConditionSet = conditions

    def __repr__(self) -> str:
        return f"<VariableRange variable type:{self.variable_of_interest} ({self.start}, {self.end}) inc:{self.inc}>"

    def generate(self) -> List[ConditionSet]:
        """
        Generate a list of conditions, with the variable of interest condition changing from start to end with an
        interval of increment
        :return: a list of conditions
        """
        out: List[ConditionSet] = []
        curr: Quantity = self.start
        while curr <= self.end:
            variable_set: ConditionSet = self.conditions.clone()
            variable_set.set(self.variable_of_interest, curr)
            out.append(variable_set)
            curr += self.inc

        return out

    def get_conditions(self) -> List[Condition]:
        """
        Get a list of all set variables
        :return: a list of all set variables
        """
        return self.conditions.get_conditions()

    def get(self, variable: Condition) -> Quantity:
        """
        Get the value of a set variable
        :param variable: the type of variable
        :return:
        """
        return self.conditions.get(variable)
