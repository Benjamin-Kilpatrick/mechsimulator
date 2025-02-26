from typing import Self, Optional, List

import numpy

from data.experiments.common.phi import Phi


class IParameter:
    def __init__(self,
                 parameter: Optional[Self] = None):
        self.parameter: Optional[Self] = parameter

    def get_timestep(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_timestep()
        raise NotImplementedError

    def set_timestep(self, timestep: float):
        if self.parameter is not None:
            self.parameter.set_timestep(timestep)
        raise NotImplementedError

    def get_end_time(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_end_time()
        raise NotImplementedError

    def set_end_time(self, end_time: float):
        if self.parameter is not None:
            self.parameter.set_end_time(end_time)
        raise NotImplementedError

    def get_wavelength(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_wavelength()
        raise NotImplementedError

    def set_wavelength(self, wavelength: float):
        if self.parameter is not None:
            self.parameter.set_wavelength(wavelength)
        raise NotImplementedError

    def get_abs_coeff(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_abs_coeff()
        raise NotImplementedError

    def set_abs_coeff(self, abs_coeff: float):
        if self.parameter is not None:
            self.parameter.set_abs_coeff(abs_coeff)
        raise NotImplementedError

    def get_path_length(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_path_length()
        raise NotImplementedError

    def set_path_length(self, path_length: float):
        if self.parameter is not None:
            self.parameter.set_path_length(path_length)
        raise NotImplementedError

    def get_active_species(self) -> List[str]:
        if self.parameter is not None:
            return self.parameter.get_active_species()
        raise NotImplementedError

    def set_active_species(self, active_species: List[str]):
        if self.parameter is not None:
            self.parameter.set_active_species(active_species)
        raise NotImplementedError

    def get_target_species(self) -> List[str]:
        if self.parameter is not None:
            return self.parameter.get_target_species()
        raise NotImplementedError

    def set_target_species(self, target_species: List[str]):
        if self.parameter is not None:
            self.parameter.set_target_species(target_species)
        raise NotImplementedError

    def get_idt_targets(self) -> List[str]:
        if self.parameter is not None:
            return self.parameter.get_idt_targets()
        raise NotImplementedError

    def set_idt_targets(self, idt_targets: List[str]):
        if self.parameter is not None:
            self.parameter.set_idt_targets(idt_targets)
        raise NotImplementedError

    def get_idt_method(self) -> str:
        if self.parameter is not None:
            return self.parameter.get_idt_method()
        raise NotImplementedError

    def set_idt_method(self, idt_method: str):
        if self.parameter is not None:
            self.parameter.set_idt_method(idt_method)
        raise NotImplementedError

    def get_temperature(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_temperature()
        raise NotImplementedError

    def set_temperature(self, temperature: float):
        if self.parameter is not None:
            self.parameter.set_temperature(temperature)
        raise NotImplementedError

    def get_pressure(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_pressure()
        raise NotImplementedError

    def set_pressure(self, pressure: float):
        if self.parameter is not None:
            self.parameter.set_pressure(pressure)
        raise NotImplementedError

    def get_res_time(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_res_time()
        raise NotImplementedError

    def set_res_time(self, res_time: float):
        if self.parameter is not None:
            self.parameter.set_res_time(res_time)
        raise NotImplementedError

    def get_mdot(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_mdot()
        raise NotImplementedError

    def set_mdot(self, mdot: float):
        if self.parameter is not None:
            self.parameter.set_mdot(mdot)
        raise NotImplementedError

    def get_length(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_length()
        raise NotImplementedError

    def set_length(self, length: float):
        if self.parameter is not None:
            self.parameter.set_length(length)
        raise NotImplementedError

    def get_area(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_area()
        raise NotImplementedError

    def set_area(self, area: float):
        if self.parameter is not None:
            self.parameter.set_area(area)
        raise NotImplementedError

    def get_volume(self) -> float:
        if self.parameter is not None:
            return self.parameter.get_volume()
        raise NotImplementedError

    def set_volume(self, volume: float):
        if self.parameter is not None:
            self.parameter.set_volume(volume)
        raise NotImplementedError

    def get_dpdt(self) -> numpy.ndarray:
        if self.parameter is not None:
            return self.parameter.get_dpdt()
        raise NotImplementedError

    def set_dpdt(self, dpdt: numpy.ndarray):
        if self.parameter is not None:
            self.parameter.set_dpdt(dpdt)
        raise NotImplementedError

    def get_x_profile(self) -> numpy.ndarray:
        if self.parameter is not None:
            return self.parameter.get_x_profile()
        raise NotImplementedError

    def set_x_profile(self, x_profile: numpy.ndarray):
        if self.parameter is not None:
            self.parameter.set_x_profile(x_profile)
        raise NotImplementedError

    def get_t_profile(self) -> numpy.ndarray:
        if self.parameter is not None:
            return self.parameter.get_t_profile()
        raise NotImplementedError

    def set_t_profile(self, t_profile: numpy.ndarray):
        if self.parameter is not None:
            self.parameter.set_t_profile(t_profile)
        raise NotImplementedError

    def get_t_profile_setpoints(self) -> numpy.ndarray:
        if self.parameter is not None:
            return self.parameter.get_t_profile_setpoints()
        raise NotImplementedError

    def set_t_profile_setpoints(self, t_profile_setpoints: numpy.ndarray):
        if self.parameter is not None:
            self.parameter.set_t_profile_setpoints(t_profile_setpoints)
        raise NotImplementedError

    def get_time(self) -> numpy.ndarray:
        if self.parameter is not None:
            return self.parameter.get_time()
        raise NotImplementedError

    def set_time(self, time: numpy.ndarray):
        if self.parameter is not None:
            self.parameter.set_time(time)
        raise NotImplementedError

    def get_v_of_t(self) -> numpy.ndarray:
        if self.parameter is not None:
            return self.parameter.get_v_of_t()
        raise NotImplementedError

    def set_v_of_t(self, v_of_t: numpy.ndarray):
        if self.parameter is not None:
            self.parameter.set_v_of_t(v_of_t)
        raise NotImplementedError

    def get_phi(self) -> Phi:
        if self.parameter is not None:
            return self.parameter.get_phi()
        raise NotImplementedError

    def set_phi(self, phi: Phi):
        if self.parameter is not None:
            self.parameter.set_phi(phi)
        raise NotImplementedError

    def set_parameter(self, parameter: Self):
        self.parameter = parameter

    def get_parameter(self) -> Self:
        return self.parameter

    def has_parameter(self) -> bool:
        return self.parameter is not None
