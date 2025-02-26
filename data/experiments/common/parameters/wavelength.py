from typing import Optional

from data.experiments.common.parameters.parameter import IParameter


class Wavelength(IParameter):
    def __init__(self,
                 wavelength: float,
                 parameter: Optional[IParameter] = None):
        self.wavelength: float = wavelength
        IParameter.__init__(self, parameter)

    def get_wavelength(self) -> float:
        return self.wavelength

    def set_wavelength(self, wavelength: float):
        self.wavelength = wavelength
