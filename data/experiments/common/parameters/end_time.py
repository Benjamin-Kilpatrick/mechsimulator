from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class EndTime(IParameter):
    def __init__(self,
                 end_time: float,
                 parameter: Optional[IParameter] = None):
        self.end_time: float = end_time
        IParameter.__init__(self, parameter)

    def get_end_time(self) -> float:
        return self.end_time

    def set_end_time(self, end_time: float):
        self.end_time = end_time
