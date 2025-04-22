from typing import Dict, Any, List

from pint import Quantity
from typing_extensions import Self

from data.experiments.common.condition import Condition


class ConditionSet:
    """
    A set of variable conditions
    """
    def __init__(self):
        """
        Constructor
        """
        self.condition_set: Dict[Condition, Quantity] = {}

    def __repr__(self) -> str:
        return f"<VariableSet variables={self.condition_set.keys()}>"

    def set(self, variable: Condition, value: Quantity):
        """
        Set a variable's value
        :param variable: the type of variable
        :param value: the value of the variable, either scalar or array
        """
        self.condition_set[variable] = value

    def get(self, variable: Condition) -> Quantity:
        """
        Get the value of a variable
        :param variable: the type of variable
        :return: the value of the variable, either scalar or array
        """
        return self.condition_set[variable]

    def has(self, condition: Condition) -> bool:
        """
        Check if a variable has been set
        :param condition: the type of variable
        :return: True if the variable has been set, False otherwise
        """
        return condition in self.condition_set.keys()

    def clone(self) -> Self:
        """
        Create a shallow copy
        :return: the shallow copy
        """
        variable_set: ConditionSet = ConditionSet()
        variable_set.condition_set = self.condition_set.copy()
        return variable_set

    def get_conditions(self) -> List[Condition]:
        """
        Get a list of all set variables
        :return: list of all set variables
        """
        return list(self.condition_set.keys())


    def copy(self):
        cond_dict: Dict[Condition, Quantity] = {condition: quantity for condition, quantity in self.condition_set.items()}
        condition_set = ConditionSet()
        condition_set.condition_set = cond_dict
        return condition_set
