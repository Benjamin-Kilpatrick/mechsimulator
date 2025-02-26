from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class PathLength(IParameter):
    def __init__(self,
                 path_length: float,
                 parameter: Optional[IParameter] = None):
        self.path_length: float = path_length
        IParameter.__init__(self, parameter)

    def get_path_length(self) -> float:
        return self.path_length

    def set_path_length(self, path_length: float):
        self.path_length = path_length
