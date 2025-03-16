import csv
import warnings
from typing import List

import cantera

from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species
from serial.common.env_path import EnvPath
from serial.common.utils import Utils


class MechanismReader:
    """
    Static methods to read a mechanism file
    """

    @staticmethod
    def read_species_file(species_file: str) -> List[Species]:
        """
        Read a species file into a list of Species
        :param species_file: the file name of the species file without the path
        :return: a list of Species
        """
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
        """
        Read a mechanism file into a Solution
        :param mechanism_file: the file name of the mechanism file without the path
        :return: a Solution
        """
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
        """
        Read a mechanism file into a Mechanism
        :param mechanism_file: the file name of the mechanism file without the path
        :param species_file: the file name of the species file without the path
        :param mechanism_name: the name of the mechanism
        :return: a Mechanism
        """
        solution: cantera.Solution = MechanismReader.read_mechanism_file(mechanism_file)
        species: List[Species] = MechanismReader.read_species_file(species_file)
        return Mechanism(solution, species, mechanism_name)

