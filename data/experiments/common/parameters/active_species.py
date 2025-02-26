from typing import Optional, List

from data.experiments.common.parameters.parameter import IParameter


class ActiveSpecies(IParameter):
    def __init__(self,
                 active_species: List[str],
                 parameter: Optional[IParameter] = None):
        self.active_species: List[str] = active_species
        IParameter.__init__(self, parameter)

    def get_active_species(self) -> List[str]:
        return self.active_species

    def set_active_species(self, active_species: List[str]):
        self.active_species = active_species


