from typing import List, Dict, Optional

from data.experiments.common.target import Target
from data.mechanism.species import Species


class TargetSpecies:
    def __init__(self):
        self.all_targets: List[Species] = []
        self.special_targets: Dict[Target, List[Species]] = {}

    def get_all_targets(self) -> List[Species]:
        return self.all_targets

    def get_special_targets(self, target: Target) -> List[Species]:
        if target in self.special_targets:
            return self.special_targets[target]

        raise Exception(f'Target {target.name} not found')

    def add_target(self, species: Species):
        self.all_targets.append(species)

    def add_special_target(self, target: Target, species: Species):
        if target not in self.special_targets:
            self.special_targets[target] = []

        self.special_targets[target].append(species)

    def get_species_by_name(self, name: str) -> Optional[Species]:
        for species in self.all_targets:
            if name == species.name:
                return species
        return None
