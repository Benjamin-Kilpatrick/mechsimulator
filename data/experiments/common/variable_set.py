from typing import Dict, Any

from typing_extensions import Self

from data.experiments.common.variable import Variable


class VariableSet:
    """
    A set of variables used in Experiments
    """
    def __init__(self):
        self.variable_set: Dict[Variable, Any] = {}

    def __repr__(self) -> str:
        return f"<VariableSet variables={self.variable_set.keys()}>"

    def set(self, variable: Variable, value: Any):
        """
        Set the variable to the value
        :param variable: The variable to set
        :param value: The value to set
        """
        self.variable_set[variable] = value

    def get(self, variable: Variable) -> Any:
        """
        Get the variable's value
        :param variable: The variable to get
        :return: The value
        """
        return self.variable_set[variable]

    def has(self, variable: Variable) -> bool:
        """
        Check if a variable has a value
        :param variable: The variable to check
        :return: bool True if the variable exists in the set otherwise false
        """
        return variable in self.variable_set.keys()

    def clone(self) -> Self:
        """
        Create a shallow copy of the variable_set
        :return: The cloned variable_set
        """
        variable_set: VariableSet = VariableSet()
        variable_set.variable_set = self.variable_set.copy()
        return variable_set
