from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class Volume(IParameter):
    def __init__(self,
                 volume: float,
                 parameter: Optional[IParameter] = None):
        self.volume: float = volume
        IParameter.__init__(self, parameter)

    def get_volume(self) -> float:
        return self.volume

    def set_volume(self, volume: float):
        self.volume = volume