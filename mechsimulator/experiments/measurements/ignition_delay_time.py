from typing import List

from experiments.common.variable import Variable
from experiments.measurements.measurement import Measurement



class IgnitionDelayTime(Measurement):
    def __init__(self,
                 variable: Variable,
                 end_time: float,
                 idt_targets: List[str],
                 idt_methods: List[str]
                 ):
        Measurement.__init__(self, variable)

        self.end_time: float = end_time
        # TODO make idt target an enum
        self.idt_targets: List[str] = idt_targets
        # TODO make idt method an enum
        self.idt_methods: List[str] = idt_methods
