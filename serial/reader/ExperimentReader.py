import math
from typing import Dict, Any, List

import numpy
import pandas
from pandas import DataFrame

from data.common.value import Value
from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.common.phi import Phi
from data.experiments.common.variable_range import VariableRange
from data.experiments.common.variable_set import Variable, VariableSet
from data.experiments.experiment import Experiment
from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.metadata import MetaData
from data.experiments.reaction import Reaction
from data.mechanism.species import Species
from data.mixtures.compound import Compound
from serial.common.env_path import EnvPath
from serial.common.file_type import FileType
from serial.common.utils import Utils

class ExperimentReader:
    """
    Static class that holds methods used to read Experiment files
    """

    @staticmethod
    def read_file(
            experiment_file: str,
            calculation_type: CalculationType,
            source_mode: DataSource
    ) -> ExperimentSet:
        """
        The top level method that reads the experiment file.
        :param experiment_file: Path to the experiment file with either a ".yaml" or a ".xlsl" extension
        :param calculation_type: Calculation type to use for this experiment
        :param source_mode: Source mode to use for this experiment
        """
        file_type: FileType = Utils.get_file_type(experiment_file)
        full_filename: str = Utils.get_full_path(EnvPath.EXPERIMENT, experiment_file)
        if file_type == FileType.EXCEL:
            return ExperimentReader.read_excel_file(full_filename, calculation_type, source_mode)
        if file_type == FileType.YAML:
            return ExperimentReader.read_yaml_file(full_filename, calculation_type, source_mode)

        raise Exception(f"File {experiment_file} is in an unsupported format, only .xlsl and .yaml files are supported")

    @staticmethod
    def convert_excel_sheet_to_dict(sheet: DataFrame, out_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Converts a Excel sheet to a dictionary.
        :param sheet: Excel sheet to convert
        :param out_dict: the dict that is added to. The original dict will not be modified by this function
        :return: the dict that has been converted
        """
        return_dict: Dict[str, Dict[str, Any]] = out_dict.copy()
        for _, row in sheet.iterrows():
            group = None
            if 'group' in row:
                group = row['group']
            else:
                group = row['type']
            if group in return_dict.keys():
                parameter = row['parameter']
                if group == 'spc':
                    return_dict['spc'][parameter] = [x for x in row[2:6]]
                else:
                    value = row['value']
                    units = row['units']
                    bounds = (None, None)
                    bounds_type = None
                    other = None
                    if 'lower bound' in row and 'upper bound' in row and 'bound type':
                        bounds = (row['lower bound'], row['upper bound'])
                        bounds_type = row['bound type']
                        other = [x for x in row[7:] if not math.isnan(x)]
                    else:
                        other = [x for x in row[4:] if not math.isnan(x)]

                    parsed_row: Dict = {
                                'value': value,
                                'units': units,
                                'other': other,
                                'bounds': bounds,
                                'bounds_type': bounds_type
                            }
                    if parameter == 't_profile':
                        if 't_profile' not in return_dict['plot']:
                            return_dict['plot']['t_profile'] = []
                        return_dict['plot']['t_profile'].append(parsed_row)
                    else:
                        return_dict[group][parameter] = parsed_row
        return return_dict

    @staticmethod
    def read_excel_file(
            experiment_file: str,
            calculation_type: CalculationType,
            source_mode: DataSource
    ) -> ExperimentSet:
        """
        Read and Excel sheet from an Excel file and get experiment set.
        :experiment_file: Path to the Excel file
        :calculation_type: Calculation type to use for this experiment
        :source_mode: Source mode to use for this experiment
        :return: the experiment set that has been read
        """
        excel = pandas.ExcelFile(experiment_file, engine='openpyxl')
        info: DataFrame = excel.parse('info')
        experiment_sheets: List[str] = list(filter(lambda x: x != 'info', excel.sheet_names))

        info_dict: Dict[str, Dict[str, Any]] = {'spc': {}, 'overall': {}, 'plot': {}, 'mix': {}, 'plot_format': {}}

        info_dict = ExperimentReader.convert_excel_sheet_to_dict(info, info_dict)

        plot_data: Dict[str, Any] = info_dict['plot']
        start: float = plot_data['start']['value']
        end: float = plot_data['end']['value']
        inc: float = plot_data['inc']['value']
        # num_conditions = int((end - start) / inc) + 1

        overall: Dict[str, Any] = info_dict['overall']
        meta_data: MetaData = MetaData(overall['version']['value'], overall['source']['value'],
                                       overall['description']['value'])

        reaction: Reaction = Utils.parse_reaction_type(overall['reac_type']['value'])
        measurement: Measurement = Utils.parse_measurement_type(overall['meas_type']['value'])
        variable: Variable = Utils.convert_excel_str_variable(plot_data['variable']['value'])
        variable_set: VariableSet = ExperimentReader.parse_variables_excel(reaction, measurement, variable, plot_data)
        variable_range: VariableRange = VariableRange(variable, start, end, inc, variable_set)

        measured_experiments: List[Experiment] = []

        simulated_species: List[Species] = ExperimentReader.parse_species_excel(info_dict['spc'])
        simulated_compounds: List[Compound] = ExperimentReader.parse_compounds_excel(info_dict['mix'], simulated_species)

        sheet: str
        for sheet in experiment_sheets:
            exp_sheet: DataFrame = excel.parse(sheet)
            exp_dict: Dict[str, Dict[str, Any]] = {'overall': {}, 'conds': {}, 'mix': {}, 'result': {}}
            exp_dict = ExperimentReader.convert_excel_sheet_to_dict(exp_sheet, exp_dict)

            exp_conditions: VariableSet = ExperimentReader.read_all_variables_excel(exp_dict['conds'])
            exp_compounds: List[Compound] = ExperimentReader.parse_compounds_excel(exp_dict['mix'], simulated_species)

            measured_experiments.append(
                Experiment(
                    exp_conditions,
                    exp_compounds
                )
            )

        return ExperimentSet(
            meta_data,
            calculation_type,
            source_mode,
            variable_range,
            reaction,
            measurement,
            simulated_species,
            simulated_compounds,
            measured_experiments
        )

    @staticmethod
    def read_yaml_file(
            experiment_file: str,
            calculation_type: CalculationType,
            source_mode: DataSource
    ) -> ExperimentSet:
        """
        Read and YAML experiment file and get experiment set.
        :param experiment_file: Path to the experiment file
        :param calculation_type: Calculation type to use for this experiment
        :param source_mode: Source mode to use for this experiment
        :return: the experiment set that has been read
        """
        pass

    @staticmethod
    def parse_species_excel(data: Dict[str, Any]) -> List[Species]:
        """
        :param data: Dictionary of data from an Excel file gotten by the convert_excel_sheet_to_dict function in the
        spc section.
        :return: List of Species objects
        """
        species: List[Species] = []
        species_name: str
        for species_name in data.keys():
            species_row = data[species_name]
            species.append(
                Species(
                    species_name,
                    species_row[0],
                    None,
                    int(species_row[1]),
                    int(species_row[2]),
                    int(species_row[3]) == 1
                )
            )
        return species

    @staticmethod
    def parse_compounds_excel(data: Dict[str, Any], species: List[Species]) -> List[Compound]:
        """
        :param data: Dictionary of data from an Excel file gotten by the convert_excel_sheet_to_dict function in the
        mix section.
        :param species: List of Species objects
        :return: List of Compound objects
        """
        species_lookup: Dict[str, Species] = {}
        for spc in species:
            species_lookup[spc.name] = spc

        compounds: List[Compound] = []
        compound_name: str
        for compound_name in data.keys():
            compound_dict: Dict[str, Any] = data[compound_name]
            compound_quantity = compound_dict['value']
            value: Value
            if 'bounds' in compound_dict:
                # TODO properly parse bounds and type
                bounds = compound_dict['bounds']
                bounds_type = compound_dict['bounds_type']
                value = Value(compound_quantity, bounds[0], bounds[1])
            else:
                value = Value(compound_quantity, compound_quantity, compound_quantity)

            compounds.append(
                Compound(
                    species_lookup[compound_name],
                    value,
                    compound_quantity == 'bal'
                )
            )

        return compounds

    @staticmethod
    def get_variable_excel(variable: Variable, data: Dict[str, Any], require: bool):
        """
        Load the variable form the Excel files loaded data
        :param variable: Variable
        :param data: Dictionary of data from an Excel file
        :param require: whether the value is required for this variable
        :return: ndarray or None if the value is optional and not found
        """
        variable_name: str = Utils.convert_variable_excel_str(variable)
        if variable_name in data:
            var_data: Dict = data[variable_name]

            if variable == Variable.TIME_STEP or \
                    variable == Variable.END_TIME or \
                    variable == Variable.WAVELENGTH or \
                    variable == Variable.ACTIVE_SPECIES or \
                    variable == Variable.ABS_COEFFICIENT or \
                    variable == Variable.PATH_LENGTH or \
                    variable == Variable.IGNITION_DELAY_TARGETS or \
                    variable == Variable.IGNITION_DELAY_METHOD or \
                    variable == Variable.TARGET_SPECIES or \
                    variable == Variable.TEMPERATURE or \
                    variable == Variable.PRESSURE or \
                    variable == Variable.LENGTH or \
                    variable == Variable.RES_TIME or \
                    variable == Variable.MDOT or \
                    variable == Variable.AREA:
                return var_data['value']
            elif variable == Variable.PHI:
                # TODO implement parsing phi
                raise NotImplementedError()
            elif variable == Variable.DPDT or \
                    variable == Variable.TIME or \
                    variable == Variable.V_OF_T or \
                    variable == Variable.X_PROFILE or \
                    variable == Variable.TIME_PROFILE_SETPOINTS:
                return numpy.asarray([float(i) for i in var_data['other']])
            elif variable == Variable.TIME_PROFILE:
                return numpy.asarray([float(i) for i in var_data[0]['other']])

        elif require:
            raise KeyError(f"Missing required variable: {variable.name}")
        # return a none type if the value is optional and not found
        return None

    @staticmethod
    def read_all_variables_excel(data: Dict[str, Dict[str, Any]]) -> VariableSet:
        """
        Read all the variables from the Excel files loaded data dict
        :param data: Dictionary of data from an Excel file
        :return: VariableSet object
        """
        variable_set: VariableSet = VariableSet()

        variable: Variable
        for variable in Variable:
            value: Any = ExperimentReader.get_variable_excel(variable, data, False)
            variable_set.set(variable, value)

        return variable_set

    @staticmethod
    def parse_variables_excel(
            reaction: Reaction,
            measurement: Measurement,
            variable: Variable,
            data: Dict[str, Any]) -> VariableSet:
        """
        :param reaction: Reaction
        :param measurement: Measurement
        :param variable: Variable
        :param data: Dictionary of data from an Excel file
        :return: VariableSet object
        """

        variable_set: VariableSet = VariableSet()

        if variable != Variable.TEMPERATURE:
            temperature: float = ExperimentReader.get_variable_excel(Variable.TEMPERATURE, data, True)
            variable_set.set(Variable.TEMPERATURE, temperature)
        elif variable != Variable.PRESSURE:
            pressure: float = ExperimentReader.get_variable_excel(Variable.PRESSURE, data, True)
            variable_set.set(Variable.PRESSURE, pressure)

        if reaction == Reaction.SHOCKTUBE:
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, data, True)
            dpdt: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.DPDT, data, False)

            variable_set.set(Variable.END_TIME, end_time)
            variable_set.set(Variable.DPDT, dpdt)
        elif reaction == Reaction.PLUG_FLOW_REACTOR:
            length: float = ExperimentReader.get_variable_excel(Variable.LENGTH, data, True)
            res_time: float = ExperimentReader.get_variable_excel(Variable.RES_TIME, data, False)
            mdot: float = ExperimentReader.get_variable_excel(Variable.MDOT, data, False)
            if res_time is None and mdot is None:
                raise RuntimeError('Either mdot or res time are required for plug flow reactor')
            area: float = ExperimentReader.get_variable_excel(Variable.AREA, data, True)
            x_profile: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.X_PROFILE, data, False)
            t_profile: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.TIME_PROFILE, data, False)
            t_profile_setpoints: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.TIME_PROFILE_SETPOINTS,
                                                                                     data, False)

            variable_set.set(Variable.LENGTH, length)
            variable_set.set(Variable.RES_TIME, res_time)
            variable_set.set(Variable.MDOT, mdot)
            variable_set.set(Variable.AREA, area)
            variable_set.set(Variable.X_PROFILE, x_profile)
            variable_set.set(Variable.TIME_PROFILE, t_profile)
            variable_set.set(Variable.TIME_PROFILE_SETPOINTS, t_profile_setpoints)
        elif reaction == Reaction.JET_STREAM_REACTOR:
            volume: float = ExperimentReader.get_variable_excel(Variable.VOLUME, data, True)
            res_time: float = ExperimentReader.get_variable_excel(Variable.RES_TIME, data, False)
            mdot: float = ExperimentReader.get_variable_excel(Variable.MDOT, data, False)
            if res_time is None and mdot is None:
                raise RuntimeError('Either mdot or res time are required for plug flow reactor')

            variable_set.set(Variable.VOLUME, volume)
            variable_set.set(Variable.RES_TIME, res_time)
            variable_set.set(Variable.MDOT, mdot)
        elif reaction == Reaction.RAPID_COMPRESSION_MACHINE:
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, data, True)
            time: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.TIME, data, False)
            v_of_t: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.V_OF_T, data, False)

            variable_set.set(Variable.END_TIME, end_time)
            variable_set.set(Variable.TIME, time)
            variable_set.set(Variable.V_OF_T, v_of_t)
        elif reaction == Reaction.CONST_T_P:
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, data, True)

            variable_set.set(Variable.END_TIME, end_time)
        elif reaction == Reaction.FREE_FLAME:
            if variable != Variable.PHI:
                phi: Phi = ExperimentReader.get_variable_excel(Variable.PHI, data, False)
                variable_set.set(Variable.PHI, phi)
        else:
            raise NotImplementedError(f"Reaction {reaction.name} is not implemented")

        if measurement == Measurement.ABS or measurement == Measurement.EMISSION:
            time_step: float = ExperimentReader.get_variable_excel(Variable.TIME_STEP, data, True)
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, data, True)
            wavelength: float = ExperimentReader.get_variable_excel(Variable.WAVELENGTH, data, True)
            active_species: List[str] = ExperimentReader.get_variable_excel(Variable.ACTIVE_SPECIES, data, True)

            variable_set.set(Variable.TIME_STEP, time_step)
            variable_set.set(Variable.END_TIME, end_time)
            variable_set.set(Variable.WAVELENGTH, wavelength)
            variable_set.set(Variable.ACTIVE_SPECIES, active_species)
        elif measurement == Measurement.IGNITION_DELAY_TIME:
            ignition_delay_targets: List[str] = ExperimentReader.get_variable_excel(Variable.IGNITION_DELAY_TARGETS, data, True)
            ignition_delay_method: str = ExperimentReader.get_variable_excel(Variable.IGNITION_DELAY_METHOD, data, True)
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, data, True)

            variable_set.set(Variable.IGNITION_DELAY_TARGETS, ignition_delay_targets)
            variable_set.set(Variable.IGNITION_DELAY_METHOD, ignition_delay_method)
            variable_set.set(Variable.END_TIME, end_time)
        elif measurement == Measurement.OUTLET:
            pass
        elif measurement == Measurement.ION or measurement == Measurement.PRESSURE or measurement == Measurement.CONCENTRATION:
            time_step: float = ExperimentReader.get_variable_excel(Variable.TIME_STEP, data, True)
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, data, True)

            variable_set.set(Variable.TIME_STEP, time_step)
            variable_set.set(Variable.END_TIME, end_time)
        elif measurement == Measurement.LFS:
            pass
        elif measurement == Measurement.HALF_LIFE:
            target_species: str = ExperimentReader.get_variable_excel(Variable.TARGET_SPECIES, data, True)
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, data, True)

            variable_set.set(Variable.TARGET_SPECIES, target_species)
            variable_set.set(Variable.END_TIME, end_time)
        else:
            raise NotImplementedError(f"Measurement {measurement.name} is not implemented")

        return variable_set

