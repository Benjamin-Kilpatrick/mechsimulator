from typing import Optional


class OptionalVariable:
    """
    Variable that may either be set a required or not required
    """
    def __init__(self,
                 value: Optional,
                 flag: bool = False):
        """
        :param value: The value to assign to the variable
        :param flag: True if the variable is optional otherwise false
        """
        self.value: Optional = value
        self.flag: bool = flag


    def set_required(self):
        """
        Sets the variable to be required
        """
        self.flag = False

    def set_optional(self):
        """
        Sets the variable to be optional
        """
        self.flag = True

    def is_required(self) -> bool:
        """
        Checks if the variable is required
        :return: True if the variable is required
        """
        return not self.flag

    def __repr__(self) -> str:
        return f"<OptionalVariable - {'not required' if self.flag else 'required'}:{self.value}>"