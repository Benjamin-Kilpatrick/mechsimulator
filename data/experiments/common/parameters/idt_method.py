from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class IdtMethod(IParameter):
    def __init__(self,
                 idt_method: str,
                 parameter: Optional[IParameter] = None):
        self.idt_method: str = idt_method
        IParameter.__init__(self, parameter)

    def get_idt_method(self) -> str:
        return self.idt_method

    def set_idt_method(self, idt_method: str):
        self.idt_method = idt_method
