from typing import Optional, List

from data.experiments.common.parameters.parameter import IParameter


class IdtTargets(IParameter):
    def __init__(self,
                 idt_targets: List[str],
                 parameter: Optional[IParameter] = None):
        self.idt_targets: List[str] = idt_targets
        IParameter.__init__(self, parameter)

    def get_idt_targets(self) -> List[str]:
        return self.idt_targets

    def set_idt_targets(self, idt_targets: List[str]):
        self.idt_targets = idt_targets


