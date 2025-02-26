from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class Area(IParameter):
    def __init__(self,
                 area: float,
                 parameter: Optional[IParameter] = None):
        self.area: float = area
        IParameter.__init__(self, parameter)

    def get_area(self) -> float:
        return self.area

    def set_area(self, area: float):
        self.area = area