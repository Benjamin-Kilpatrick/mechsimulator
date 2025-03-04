from typing import Optional


class OptionalVariable:
    def __init__(self,
                 value: Optional,
                 flag: bool = False):
        self.value: Optional = value
        self.flag: bool = flag


    def set_required(self):
        self.flag = False

    def set_optional(self):
        self.flag = True

    def is_required(self) -> bool:
        return not self.flag
    