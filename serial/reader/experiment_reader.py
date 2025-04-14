import math
from typing import Dict, Any, List, Tuple

import numpy
import pandas
from pandas import DataFrame
from pint import Quantity

from data.common.value import Value
from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.common.condition_range import ConditionRange
from data.experiments.common.condition_set import Condition, ConditionSet
from data.experiments.common.target import Target
from data.experiments.experiment import Experiment
from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.metadata import MetaData
from data.experiments.mixture import Mixture
from data.experiments.reaction import Reaction
from data.experiments.results import Results
from data.experiments.target_species import TargetSpecies
from data.mechanism.species import Species
from data.mixtures.compound import Compound
from serial.common.env_path import EnvPath
from serial.common.file_type import FileType
from serial.common.utils import Utils
from serial.reader.unit_parser import UnitParser


class ExperimentReader:
    """
    A static class responsible for parsing experiment files of both excel and yaml extensions
    """

    @staticmethod
    def read_file(
            experiment_file: str,
            calculation_type: CalculationType,
            x_source: DataSource,
            condition_source
    ) -> ExperimentSet:
        """
        The top level method that reads the experiment file.
        :param experiment_file: path to the experiment file with either a ".yaml" or a ".xlsl" extension
        :param calculation_type: calculation type
        :param x_source: x data source
        :param condition_source: condition data source

        :return: an experiment set parsed from experiment_file
        """

        file_type: FileType = Utils.get_file_type(experiment_file)
        full_filename: str = Utils.get_full_path(EnvPath.EXPERIMENT, experiment_file)

        # decide which function to use to parse the file
        if file_type == FileType.EXCEL:
            return ExperimentReader.read_excel_file(full_filename, calculation_type, x_source, condition_source)
        if file_type == FileType.YAML:
            return ExperimentReader.read_yaml_file(full_filename, calculation_type, x_source, condition_source)

        raise Exception(f"File {experiment_file} is in an unsupported format, only .xlsl and .yaml files are supported")

    @staticmethod
    def convert_excel_sheet_to_dict(sheet: DataFrame, out_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Converts an Excel sheet of experiment data to a dictionary to be easier to work with
        :param sheet: Excel sheet to convert
        :param out_dict: contains the top level groups to get from the Excel sheet, will not be modified
        :return: a dictionary that contains experiment file data from the given sheet
        """
        return_dict: Dict[str, Dict[str, Any]] = out_dict.copy()
        for _, row in sheet.iterrows():
            group = None

            # group is sometimes also called type
            if 'group' in row:
                group = row['group']
            else:
                group = row['type']

            # for each of the groups given in out_dict
            if group in return_dict.keys():
                parameter = row['parameter']

                # parse the species data independently
                if group == 'spc':
                    return_dict['spc'][parameter] = [x for x in row[2:6]]
                else:
                    # get value, units, bounds and other
                    # value is for scalar data, other is array types
                    value = row['value']
                    units = row['units']
                    bounds = (None, None)
                    bounds_type = None
                    other = None

                    # if bounds are present, the excel sheet is formatted differently
                    if 'lower bound' in row and 'upper bound' in row and 'bound type':
                        bounds = (row['lower bound'], row['upper bound'])
                        bounds_type = row['bound type']
                        # convert array type
                        other = [x for x in row[7:] if not math.isnan(x)]
                    else:
                        # convert array type
                        other = [x for x in row[4:] if not math.isnan(x)]

                    parsed_row: Dict = {
                        'value': value,
                        'units': units,
                        'other': other,
                        'bounds': bounds,
                        'bounds_type': bounds_type
                    }
                    # t_profile is special and is an array of arrays
                    if parameter == 't_profile':
                        if 't_profile' not in return_dict['plot']:
                            return_dict['plot']['t_profile'] = []
                        return_dict['plot']['t_profile'].append(parsed_row)
                    else:
                        # otherwise set the single parameter
                        return_dict[group][parameter] = parsed_row
        return return_dict

    @staticmethod
    def read_excel_file(
            experiment_file: str,
            calculation_type: CalculationType,
            x_source: DataSource,
            condition_source: DataSource
    ) -> ExperimentSet:
        """
        Parse an experiment Excel sheet
        :param experiment_file: path to the experiment file
        :param calculation_type: calculation type
        :param x_source: x source of experiment data
        :param condition_source: condition source of experiment data
        :return: an experiment set parsed from experiment_file
        """
        excel = pandas.ExcelFile(experiment_file, engine='openpyxl')
        info: DataFrame = excel.parse('info')
        experiment_sheets: List[str] = list(filter(lambda x: x != 'info', excel.sheet_names))

        info_dict: Dict[str, Dict[str, Any]] = {'spc': {}, 'overall': {}, 'plot': {}, 'mix': {}, 'plot_format': {}}

        # info sheet data
        info_dict = ExperimentReader.convert_excel_sheet_to_dict(info, info_dict)

        # plot group
        plot_data: Dict[str, Any] = info_dict['plot']

        # variable of interest range
        start: Quantity = UnitParser.parse_all(plot_data['start']['value'], plot_data['start']['units'])
        end: Quantity = UnitParser.parse_all(plot_data['end']['value'], plot_data['end']['units'])
        inc: Quantity = UnitParser.parse_all(plot_data['inc']['value'], plot_data['inc']['units'])

        # metadata
        overall: Dict[str, Any] = info_dict['overall']
        meta_data: MetaData = MetaData(overall['version']['value'], overall['source']['value'],
                                       overall['description']['value'])

        # reaction, measurement and variable of interest data structures
        reaction: Reaction = Utils.parse_reaction_type(overall['reac_type']['value'])
        measurement: Measurement = Utils.parse_measurement_type(overall['meas_type']['value'])
        variable: Condition = Utils.convert_excel_str_variable(plot_data['variable']['value'])
        variable_set: ConditionSet = ExperimentReader.parse_variables_excel(reaction, measurement, variable, plot_data)
        variable_range: ConditionRange = ConditionRange(variable, start, end, inc, variable_set)

        # species and compounds parsed from experiment sheet
        simulated_species: List[Species] = ExperimentReader.parse_species_excel(info_dict['spc'])
        simulated_mixture: Mixture = ExperimentReader.parse_compounds_excel(info_dict['mix'],
                                                                                     simulated_species)

        measured_experiments: List[Experiment] = []

        targets: TargetSpecies = TargetSpecies()

        for species in simulated_species:
            targets.add_target(species)

        sheet: str
        for sheet in experiment_sheets:
            exp_sheet: DataFrame = excel.parse(sheet)
            exp_dict: Dict[str, Dict[str, Any]] = {'overall': {}, 'conds': {}, 'mix': {}, 'result': {}}
            # experiment numbered sheet data
            exp_dict = ExperimentReader.convert_excel_sheet_to_dict(exp_sheet, exp_dict)

            # conditions and compounds
            exp_conditions: ConditionSet = ExperimentReader.read_all_conditions_excel(exp_dict['conds'])
            exp_mixture: Mixture = ExperimentReader.parse_compounds_excel(exp_dict['mix'], simulated_species)
            results: Results = Results()
            for result_name in exp_dict['result'].keys():
                result_dict = exp_dict['result'][result_name]
                raw_value = result_dict['value']

                # determine it is not scalar
                if raw_value == '-':
                    raw_value = numpy.asarray(result_dict['other'])

                # convert to Pint units
                value: Quantity = UnitParser.parse_all(raw_value, result_dict['units'])
                try:
                    # test to see if it is a variable
                    variable: Condition = Utils.convert_excel_str_variable(result_name)
                    results.set_variable(variable, value)
                except KeyError:
                    # it is a target (str name only)
                    results.set_target(result_name, value)

            measured_experiments.append(
                Experiment(
                    exp_conditions,
                    exp_mixture,
                    results
                )
            )

        return ExperimentSet(
            meta_data,
            calculation_type,
            x_source,
            condition_source,
            variable_range,
            reaction,
            measurement,
            simulated_species,
            simulated_mixture,
            measured_experiments,
            targets
        )

    @staticmethod
    def read_yaml_file(
            experiment_file: str,
            calculation_type: CalculationType,
            x_source: DataSource,
            condition_source: DataSource
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
    def parse_special_targets(data: Dict[str, Any], targets: TargetSpecies):
        if 'half_life_targ' in data['conds']:
            targets.add_special_target(Target.HALF_LIFE, targets.get_species_by_name(data['conds']['half_life_targ']))
        if 'idt_targ' in data['conds']:
            idt_targ: str = data['conds']['idt_targ']
            if idt_targ == 'temp':
                pass
            elif idt_targ == 'pressure':
                pass
            else:
                targets.add_special_target(Target.IGNITION_DELAY, targets.get_species_by_name(idt_targ))
        if 'active_spc' in data['conds']:
            targets.add_special_target(Target.ACTIVE, targets.get_species_by_name(data['conds']['active_spc']))
        if 'fuel' in data['mix']:
            targets.add_special_target(Target.FUEL, targets.get_species_by_name(data['mix']['fuel']))

    @staticmethod
    def parse_species_excel(data: Dict[str, Any]) -> List[Species]:
        """
        Parse species data
        :param data: dictionary of species name to species data from the info sheet
        :return: list of parsed Species
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
    def parse_compounds_excel(data: Dict[str, Any], species: List[Species]) -> Mixture:
        """
        Parse compound data
        :param data: dictionary of mixtures from the info sheet
        :param species: list of all species
        :return: list of compounds
        """

        mixture: Mixture = Mixture()

        spc: Species
        for spc in species:
            if spc.name in data:
                mix_dict: Dict[str, Any] = data[spc.name]
                mixture_quantity = mix_dict['value']
                mixture_units = mix_dict['units']

                # TODO take bounds into account

                if mixture_quantity == 'bal':
                    mixture.add_balanced_species(spc)
                else:
                    mixture.add_species(spc, UnitParser.parse('concentration', mixture_quantity, mixture_units))

        return mixture

    @staticmethod
    def get_variable_excel(condition: Condition, data: Dict[str, Any], require: bool) -> Tuple[Any, float]:
        """
        Get a variable from the excel data, correctly parse if it is scalar or array type, and throw an exception
        if the variable is required and not found
        :param condition: the type of variable
        :param data: dictionary of data from an experiment Excel file
        :param require: whether the variable is required
        :return: scalar/array, or None if the value is optional and not found
        :exception: if variable is not found and require is True
        """
        condition_name: str = Utils.convert_variable_excel_str(condition)
        if condition_name in data:
            condition_data: Dict = data[condition_name]

            if condition == Condition.TIME_STEP or \
                    condition == Condition.END_TIME or \
                    condition == Condition.WAVELENGTH or \
                    condition == Condition.ABS_COEFFICIENT or \
                    condition == Condition.PATH_LENGTH or \
                    condition == Condition.IGNITION_DELAY_METHOD or \
                    condition == Condition.TEMPERATURE or \
                    condition == Condition.PRESSURE or \
                    condition == Condition.PHI or \
                    condition == Condition.LENGTH or \
                    condition == Condition.RES_TIME or \
                    condition == Condition.MDOT or \
                    condition == Condition.AREA:
                return condition_data['value'], condition_data['units']
            elif condition == Condition.DPDT or \
                    condition == Condition.TIME or \
                    condition == Condition.V_OF_T or \
                    condition == Condition.X_PROFILE or \
                    condition == Condition.TIME_PROFILE_SETPOINTS:
                return numpy.asarray([float(i) for i in condition_data['other']]), condition_data['units']
            elif condition == Condition.TIME_PROFILE:
                return numpy.asarray([float(i) for i in condition_data[0]['other']]), condition_data[0]['units']

        elif require:
            raise KeyError(f"Missing required variable: {condition.name}")
        # return a none type if the value is optional and not found
        return None, None

    @staticmethod
    def parse_condition(value: Any, units: str):
        pass

    @staticmethod
    def read_all_conditions_excel(data: Dict[str, Dict[str, Any]]) -> ConditionSet:
        """
        Read all variables in the experiment data sheet dictionary
        :param data: Dictionary of experiment data from an Excel file
        :return: a set of all variable conditions
        """
        condition_set: ConditionSet = ConditionSet()

        condition: Condition
        for condition in Condition:
            if Utils.convert_variable_excel_str(condition) in data:
                value: Any = UnitParser.parse_all(*ExperimentReader.get_variable_excel(condition, data, False))
                condition_set.set(condition, value)

        return condition_set

    @staticmethod
    def parse_variables_excel(
            reaction: Reaction,
            measurement: Measurement,
            variable: Condition,
            data: Dict[str, Any]) -> ConditionSet:
        """
        Parse experiment conditions based on the reaction type and measurement type
        :param reaction: reaction type
        :param measurement: measurement type
        :param variable: variable of interest
        :param data: Dictionary of data from an Excel file
        :return: a set of all variable conditions, both required and optional variables
        """

        variable_set: ConditionSet = ConditionSet()

        if variable != Condition.TEMPERATURE:
            temperature: Quantity = UnitParser.parse(
                'temperature',
                *ExperimentReader.get_variable_excel(Condition.TEMPERATURE, data, True)
            )
            variable_set.set(Condition.TEMPERATURE, temperature)
        elif variable != Condition.PRESSURE:
            pressure: Quantity = UnitParser.parse(
                'pressure',
                *ExperimentReader.get_variable_excel(Condition.PRESSURE, data, True)
            )
            variable_set.set(Condition.PRESSURE, pressure)

        if reaction == Reaction.SHOCKTUBE:
            end_time: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.END_TIME, data, True)
            )
            dpdt: numpy.ndarray = UnitParser.parse(
                'dP/dt',
                *ExperimentReader.get_variable_excel(Condition.DPDT, data, False)
            )

            variable_set.set(Condition.END_TIME, end_time)
            variable_set.set(Condition.DPDT, dpdt)
        elif reaction == Reaction.PLUG_FLOW_REACTOR:
            length: Quantity = UnitParser.parse(
                'length',
                *ExperimentReader.get_variable_excel(Condition.LENGTH, data, True)
            )
            res_time: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.RES_TIME, data, False)
            )
            mdot: Quantity = UnitParser.parse(
                'mdot',
                *ExperimentReader.get_variable_excel(Condition.MDOT, data, False)
            )
            if res_time is None and mdot is None:
                raise RuntimeError('Either mdot or res time are required for plug flow reactor')
            area: Quantity = UnitParser.parse(
                'area',
                *ExperimentReader.get_variable_excel(Condition.AREA, data, True)
            )
            # TODO
            x_profile: numpy.ndarray = UnitParser.parse_all(
                *ExperimentReader.get_variable_excel(Condition.X_PROFILE, data, False)
            )
            t_profile: numpy.ndarray = UnitParser.parse_all(
                *ExperimentReader.get_variable_excel(Condition.TIME_PROFILE, data, False)
            )
            t_profile_setpoints: numpy.ndarray = UnitParser.parse_all(
                *ExperimentReader.get_variable_excel(Condition.TIME_PROFILE_SETPOINTS, data, False)
            )

            variable_set.set(Condition.LENGTH, length)
            variable_set.set(Condition.RES_TIME, res_time)
            variable_set.set(Condition.MDOT, mdot)
            variable_set.set(Condition.AREA, area)
            variable_set.set(Condition.X_PROFILE, x_profile)
            variable_set.set(Condition.TIME_PROFILE, t_profile)
            variable_set.set(Condition.TIME_PROFILE_SETPOINTS, t_profile_setpoints)
        elif reaction == Reaction.JET_STREAM_REACTOR:
            volume: Quantity = UnitParser.parse(
                'volume',
                *ExperimentReader.get_variable_excel(Condition.VOLUME, data, True)
            )
            res_time: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.RES_TIME, data, False)
            )
            mdot: Quantity = UnitParser.parse(
                'mdot',
                *ExperimentReader.get_variable_excel(Condition.MDOT, data, False)
            )
            if res_time is None and mdot is None:
                raise RuntimeError('Either mdot or res time are required for plug flow reactor')

            variable_set.set(Condition.VOLUME, volume)
            variable_set.set(Condition.RES_TIME, res_time)
            variable_set.set(Condition.MDOT, mdot)
        elif reaction == Reaction.RAPID_COMPRESSION_MACHINE:
            end_time: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.END_TIME, data, True)
            )
            time: numpy.ndarray = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.TIME, data, False)
            )
            v_of_t: numpy.ndarray = UnitParser.parse(
                'velocity',
                *ExperimentReader.get_variable_excel(Condition.V_OF_T, data, False)
            )

            variable_set.set(Condition.END_TIME, end_time)
            variable_set.set(Condition.TIME, time)
            variable_set.set(Condition.V_OF_T, v_of_t)
        elif reaction == Reaction.CONST_T_P:
            end_time: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.END_TIME, data, True)
            )

            variable_set.set(Condition.END_TIME, end_time)
        elif reaction == Reaction.FREE_FLAME:
            if variable != Condition.PHI:
                phi: Quantity = UnitParser.parse(
                    'phi',
                    *ExperimentReader.get_variable_excel(Condition.PHI, data, False)
                )
                variable_set.set(Condition.PHI, phi)
        else:
            raise NotImplementedError(f"Reaction {reaction.name} is not implemented")

        if measurement == Measurement.ABSORPTION or measurement == Measurement.EMISSION:
            time_step: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.TIME_STEP, data, True)
            )
            end_time: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.END_TIME, data, True)
            )
            wavelength: Quantity = UnitParser.parse(
                'length',
                *ExperimentReader.get_variable_excel(Condition.WAVELENGTH, data, True)
            )
            variable_set.set(Condition.TIME_STEP, time_step)
            variable_set.set(Condition.END_TIME, end_time)
            variable_set.set(Condition.WAVELENGTH, wavelength)
        elif measurement == Measurement.IGNITION_DELAY_TIME:
            ignition_delay_method: str = \
                ExperimentReader.get_variable_excel(Condition.IGNITION_DELAY_METHOD, data, True)[0]
            end_time: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.END_TIME, data, True)
            )

            variable_set.set(Condition.IGNITION_DELAY_METHOD, ignition_delay_method)
            variable_set.set(Condition.END_TIME, end_time)
        elif measurement == Measurement.OUTLET:
            pass
        elif measurement == Measurement.ION or measurement == Measurement.PRESSURE or measurement == Measurement.CONCENTRATION:
            time_step: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.TIME_STEP, data, True)
            )
            end_time: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.END_TIME, data, True)
            )

            variable_set.set(Condition.TIME_STEP, time_step)
            variable_set.set(Condition.END_TIME, end_time)
        elif measurement == Measurement.LFS:
            pass
        elif measurement == Measurement.HALF_LIFE:
            end_time: Quantity = UnitParser.parse(
                'time',
                *ExperimentReader.get_variable_excel(Condition.END_TIME, data, True)
            )

            variable_set.set(Condition.END_TIME, end_time)
        else:
            raise NotImplementedError(f"Measurement {measurement.name} is not implemented")

        return variable_set
