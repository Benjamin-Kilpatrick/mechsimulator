from typing import Dict, List

import numpy
from pint import Quantity

from data.experiments.common.variable import Variable
from data.experiments.common.variable_set import VariableSet


class Results:
    def __init__(self):
        self.variable_results: VariableSet = VariableSet()
        self.target_results: Dict[str, Quantity] = {}

    def set_variable(self, variable: Variable, value: Quantity):
        self.variable_results.set(variable, value)

    def get_variable(self, variable: Variable) -> Quantity:
        return self.variable_results.get(variable)

    def get_variables(self) -> List[Variable]:
        return self.variable_results.get_variables()

    def set_target(self, name: str, value: Quantity):
        self.target_results[name] = value

    def get_target(self, name: str) -> Quantity:
        return self.target_results[name]

    def get_targets(self) -> List[str]:
        return list(self.target_results.keys())
