import csv
import warnings
from typing import List, Dict

import cantera
import rdkit
from rdkit import RDLogger
import rdkit.Chem as RDChem
from typing_extensions import Any

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
        # TODO actually implement sens
        'sens'
    )
    # Prevents some weird valence error warnings
    _LOGGER = RDLogger.logger()
    _LOGGER.setLevel(RDLogger.ERROR)

    def to_smiles(rdm):
        """ Generate a SMILES string from an RDKit molecule object.

            :param rdm: molecule object
            :type rdm: RDKit molecule object
            :rtype: str
        """
        return RDChem.MolToSmiles(rdm)

    def from_smiles(smi, print_debug=False):
        """ Generate an RDKit molecule object from a SMILES string.

            :param smi: SMILES string
            :type smi: str
            :param print_debug: control the printing of a debug message
            :type print_debug: bool
            :rtype: RDKit molecule object
        """

        rdm = RDChem.MolFromSmiles(smi)
        if rdm is not None and print_debug:
            print('rdm fails for {} by returning {}'.format(smi, rdm))

        return rdm

    def to_inchi(rdm, options='', with_aux_info=False):
        """ Generate an InChI string from an RDKit molecule object.

            :param rdm: molecule object
            :type rdm: RDKit molecule object
            :param options:
            :type options: str
            :param with_aux_info: include auxiliary information
            :type with_aux_info: bool
            :rtype: str
        """

        if with_aux_info:
            ret = RDChem.inchi.MolToInchiAndAuxInfo(rdm, options=options)
        else:
            ret = RDChem.inchi.MolToInchi(rdm, options=options)

        return ret

    def from_inchi(ich, print_debug=False):
        """ Generate an RDKit molecule object from an InChI string.

            :param ich: InChI string
            :type ich: str
            :param print_debug: control the printing of a debug message
            :type print_debug: bool
            :rtype: RDKit molecule object
        """

        rdm = RDChem.inchi.MolFromInchi(ich, treatWarningAsError=False)
        if rdm is None and print_debug:
            print('rdm fails for {} by returning {}'.format(ich, rdm))

        return rdm


    @staticmethod
    def generate_species(columns: List[str], row: List[str]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        parameter: str
        value: str

        for parameter, value in zip(columns, row):
            if parameter in ('charge', 'mult', 'exc_flag') and parameter != '':
                out[parameter] = int(value)
            out[parameter] = value

        return out


    @staticmethod
    def fill_in_species(species_dict: Dict[str, Any]) -> Dict[str, Any]:
        if 'inchi' not in species_dict or species_dict['inchi'] == '':
            species_dict['inchi'] = MechanismReader.to_inchi(MechanismReader.from_smiles(
                species_dict['smiles']))
        elif 'smiles' not in species_dict:
            species_dict['smiles'] = MechanismReader.to_smiles(MechanismReader.from_inchi(
                species_dict['inchi']))
        if 'charge' not in species_dict or species_dict['charge'] == '':
            species_dict['charge'] = 0
        if 'exc_flag' not in species_dict or species_dict['exc_flag'] == '':
            species_dict['exc_flag'] = 0

        return species_dict


    @staticmethod
    def read_species_file(species_file: str) -> List[Species]:
        out: List[Species] = []
        with open(Utils.get_full_path(EnvPath.SPECIES, species_file)) as f:
            reader = csv.reader(f, quotechar='\'', delimiter=',', quoting=csv.QUOTE_ALL)
            columns = reader.__next__()
            for row in reader:
                species_dict = MechanismReader.fill_in_species(MechanismReader.generate_species(columns, row))
                out.append(
                    Species(
                        species_dict['name'],
                        species_dict['smiles'],
                        species_dict['inchi'],
                        species_dict['mult'],
                        species_dict['charge'],
                        species_dict['exc_flag'] == 1
                    )
                )
                """name, smiles, inchi, mult, charge, excited = row
                out.append(
                    Species(
                        name,
                        smiles,
                        inchi,
                        int(mult),
                        int(charge),
                        excited == '1'
                    )
                )"""
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

