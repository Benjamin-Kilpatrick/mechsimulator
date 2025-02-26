from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class ResTime(IParameter):
    def __init__(self,
                 res_time: float,
                 parameter: Optional[IParameter] = None):
        self.res_time: float = res_time
        IParameter.__init__(self, parameter)

    def get_res_time(self) -> float:
        return self.res_time

    def set_res_time(self, res_time: float):
        self.res_time = res_time
        