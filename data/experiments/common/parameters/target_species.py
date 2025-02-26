from typing import Optional, List

from data.experiments.common.parameters.parameter import IParameter


class TargetSpecies(IParameter):
    def __init__(self,
                 target_species: List[str],
                 parameter: Optional[IParameter] = None):
        self.target_species: List[str] = target_species
        IParameter.__init__(self, parameter)

    def get_target_species(self) -> List[str]:
        return self.target_species

    def set_target_species(self, target_species: List[str]):
        self.target_species = target_species


