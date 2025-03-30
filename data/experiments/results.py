from typing import Dict, List

import numpy
from pint import Quantity

from data.experiments.common.condition import Condition
from data.experiments.common.condition_set import ConditionSet


class Results:
    """
    This is the y data to the x data of an experiment set. It is a dictionary of conditions and targets
    to their measured value (real or simulated)
    """
    def __init__(self):
        self.condition_results: ConditionSet = ConditionSet()
        self.target_results: Dict[str, Quantity] = {}

    def set_variable(self, condition: Condition, value: Quantity):
        """
        Set a variable's value
        :param condition: the type of variable
        :param value: the value of the variable, either scalar or array
        :return: None
        """
        self.condition_results.set(condition, value)

    def get_variable(self, condition: Condition) -> Quantity:
        """
        Get the value of a variable
        :param condition: the type of variable
        :return: the value of the variable, either scalar or array
        """
        return self.condition_results.get(condition)

    def get_variables(self) -> List[Condition]:
        """
        Get a list of all set variables
        :return: a list of all set variables
        """
        return self.condition_results.get_conditions()

    def set_target(self, name: str, value: Quantity):
        """
        Set the value of a target
        :param name: the name of the target
        :param value: the value of the target, either scalar or array
        :return: None
        """
        self.target_results[name] = value

    def get_target(self, name: str) -> Quantity:
        """
        Get the value of a target
        :param name: the name of the target
        :return: the value of the target
        """
        return self.target_results[name]

    def get_targets(self) -> List[str]:
        """
        Get a list of all set targets
        :return: a list of all set targets
        """
        return list(self.target_results.keys())
