from typing import Dict, Any, List

from pint import Quantity
from typing_extensions import Self

from data.experiments.common.variable import Variable


class VariableSet:
    """
    A set of variable conditions
    """
    def __init__(self):
        """
        Constructor
        """
        self.variable_set: Dict[Variable, Quantity] = {}

    def __repr__(self) -> str:
        return f"<VariableSet variables={self.variable_set.keys()}>"

    def set(self, variable: Variable, value: Quantity):
        """
        Set a variable's value
        :param variable: the type of variable
        :param value: the value of the variable, either scalar or array
        """
        self.variable_set[variable] = value

    def get(self, variable: Variable) -> Quantity:
        """
        Get the value of a variable
        :param variable: the type of variable
        :return: the value of the variable, either scalar or array
        """
        return self.variable_set[variable]

    def has(self, variable: Variable) -> bool:
        """
        Check if a variable has been set
        :param variable: the type of variable
        :return: True if the variable has been set, False otherwise
        """
        return variable in self.variable_set.keys()

    def clone(self) -> Self:
        """
        Create a shallow copy
        :return: the shallow copy
        """
        variable_set: VariableSet = VariableSet()
        variable_set.variable_set = self.variable_set.copy()
        return variable_set

    def get_variables(self) -> List[Variable]:
        """
        Get a list of all set variables
        :return: list of all set variables
        """
        return list(self.variable_set.keys())

