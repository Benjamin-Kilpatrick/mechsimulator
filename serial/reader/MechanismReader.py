import csv
import warnings
from typing import List

import cantera
from rdkit import RDLogger

from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species
from serial.common.env_path import EnvPath
from serial.common.utils import Utils


class MechanismReader:
    ALLOWED_COLUMN_NAMES = (
        'name',
        'smiles',
        'inchi',
        'inchikey',
        'mult',
        'charge',
        'exc_flag',
        'sens'
    )
    # Prevents some weird valence error warnings
    _LOGGER = RDLogger.logger()
    _LOGGER.setLevel(RDLogger.ERROR)
    @staticmethod
    def read_species_file(species_file: str) -> List[Species]:
        out: List[Species] = []
        with open(Utils.get_full_path(EnvPath.SPECIES, species_file)) as f:
            reader = csv.reader(f, quotechar='\'', delimiter=',', quoting=csv.QUOTE_ALL)
            columns = reader.__next__()
            for row in reader:
                name, smiles, inchi, mult, charge, excited = row
                out.append(
                    Species(
                        name,
                        smiles,
                        inchi,
                        int(mult),
                        int(charge),
                        excited == '1'
                    )
                )
        return out

    @staticmethod
    def read_mechanism_file(mechanism_file: str) -> cantera.Solution:
        solution: cantera.Solution = cantera.Solution(
            Utils.get_full_path(EnvPath.MECHANISM, mechanism_file)
        )
        return solution


    @staticmethod
    def read_file(
            mechanism_file: str,
            species_file: str,
            mechanism_name: str
    ) -> Mechanism:
        solution: cantera.Solution = MechanismReader.read_mechanism_file(mechanism_file)
        species: List[Species] = MechanismReader.read_species_file(species_file)
        return Mechanism(solution, species, mechanism_name)

