import math
from typing import Dict, Any, List

import numpy
import pandas

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.common.phi import Phi
from data.experiments.common.variable_range import VariableRange
from data.experiments.common.variable_set import Variable, VariableSet
from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.metadata import MetaData
from data.experiments.reaction import Reaction
from serial.common.env_path import EnvPath
from serial.common.file_type import FileType
from serial.common.utils import Utils


class ExperimentReader:
    @staticmethod
    def read_file(
            experiment_file: str,
            calculation_type: CalculationType,
            source_mode: DataSource
    ) -> ExperimentSet:
        file_type: FileType = Utils.get_file_type(experiment_file)
        full_filename: str = Utils.get_full_path(EnvPath.EXPERIMENT, experiment_file)
        if file_type == FileType.EXCEL:
            return ExperimentReader.read_excel_file(full_filename, calculation_type, source_mode)
        if file_type == FileType.YAML:
            return ExperimentReader.read_yaml_file(full_filename, calculation_type, source_mode)

        raise Exception(f"File {experiment_file} is in an unsupported format, only .xlsl and .yaml files are supported")

    @staticmethod
    def read_excel_file(
            experiment_file: str,
            calculation_type: CalculationType,
            source_mode: DataSource
    ) -> ExperimentSet:
        excel = pandas.ExcelFile(experiment_file, engine='openpyxl')
        info = excel.parse('info')

        info_dict: Dict[str, Dict[str, Any]] = {'spc': {}, 'overall': {}, 'plot': {}, 'mix': {}, 'plot_format': {}}

        for _, row in info.iterrows():
            group = row['group']
            if group in info_dict.keys():
                parameter = row['parameter']
                if group == 'spc':
                    info_dict['spc'][parameter] = [x for x in row[2:6]]
                else:
                    value = row['value']
                    units = row['units']
                    other = [x for x in row[4:] if not math.isnan(x)]
                    if parameter == 't_profile':
                        if 't_profile' not in info_dict['plot']:
                            info_dict['plot']['t_profile'] = []
                        info_dict['plot']['t_profile'].append(
                            {
                                'value': value,
                                'units': units,
                                'other': other
                            }
                        )
                    else:
                        info_dict[group][parameter] = {
                            'value': value,
                            'units': units,
                            'other': other
                        }

        plot_data: Dict[str, Any] = info_dict['plot']
        start: float = plot_data['start']['value']
        end: float = plot_data['end']['value']
        inc: float = plot_data['inc']['value']
        num_conditions = int((end - start) / inc) + 1

        overall: Dict[str, Any] = info_dict['overall']
        meta_data: MetaData = MetaData(overall['version']['value'], overall['source']['value'],
                                       overall['description']['value'])

        reaction: Reaction = Utils.parse_reaction_type(overall['reac_type']['value'])
        measurement: Measurement = Utils.parse_measurement_type(overall['meas_type']['value'])
        variable: Variable = Utils.convert_excel_str_variable(plot_data['variable']['value'])
        variable_set: VariableSet = ExperimentReader.parse_variables_excel(reaction, measurement, variable, plot_data)
        variable_range: VariableRange = VariableRange(variable, start, end, inc, variable_set)

        return ExperimentSet(
            meta_data,
            calculation_type,
            source_mode,
            variable_range,
            []
        )

    @staticmethod
    def read_yaml_file(
            experiment_file: str,
            calculation_type: CalculationType,
            source_mode: DataSource
    ) -> ExperimentSet:
        pass

    @staticmethod
    def get_variable_excel(variable: Variable, data: Dict[str, Any], require: bool):
        if variable == Variable.TIME_STEP:
            if 'timestep' in data.keys():
                return data['timestep']['value']
        elif variable == Variable.END_TIME:
            if 'end_time' in data.keys():
                return data['end_time']['value']
        elif variable == Variable.WAVELENGTH:
            if 'wavelength' in data.keys():
                return data['wavelength']['value']
        elif variable == Variable.ACTIVE_SPECIES:
            if 'active_spc' in data.keys():
                return data['active_spc']['value']
        elif variable == Variable.ABS_COEFFICIENT:
            if 'abs_coeff' in data.keys():
                return data['abs_coeff']['value']
        elif variable == Variable.PATH_LENGTH:
            if 'path_length' in data.keys():
                return data['path_length']['value']
        elif variable == Variable.IGNITION_DELAY_TARGETS:
            if 'idt_targ' in data.keys():
                return data['idt_targ']['value']
        elif variable == Variable.IGNITION_DELAY_METHOD:
            if 'idt_method' in data.keys():
                return data['idt_method']['value']
        elif variable == Variable.TARGET_SPECIES:
            if 'target_spc' in data.keys():
                return data['target_spc']['value']
        elif variable == Variable.TEMPERATURE:
            if 'temp' in data.keys():
                return data['temp']['value']
        elif variable == Variable.PRESSURE:
            if 'pressure' in data.keys():
                return data['pressure']['value']
        elif variable == Variable.PHI:
            # TODO implement parsing phi
            raise NotImplementedError()
        elif variable == Variable.DPDT:
            if 'dpdt' in data.keys():
                return numpy.asarray([float(i) for i in data['dpdt']['other']])
        elif variable == Variable.LENGTH:
            if 'length' in data.keys():
                return data['length']['value']
        elif variable == Variable.RES_TIME:
            if 'res_time' in data.keys():
                return data['res_time']['value']
        elif variable == Variable.MDOT:
            if 'mdot' in data.keys():
                return data['mdot']['value']
        elif variable == Variable.AREA:
            if 'area' in data.keys():
                return data['area']['value']
        elif variable == Variable.TIME:
            if 'time' in data.keys():
                return numpy.asarray([float(i) for i in data['time']['other']])
        elif variable == Variable.V_OF_T:
            if 'v_of_t' in data.keys():
                return numpy.asarray([float(i) for i in data['v_of_t']['other']])
        elif variable == Variable.X_PROFILE:
            if 'x_profile' in data.keys():
                return numpy.asarray([float(i) for i in data['x_profile']['other']])
        elif variable == Variable.TIME_PROFILE:
            if 't_profile' in data.keys():
                return numpy.asarray([float(i) for i in data['t_profile'][0]['other']])
        elif variable == Variable.TIME_PROFILE_SETPOINTS:
            if 't_profile_setpoints' in data.keys():
                return numpy.asarray([float(i) for i in data['t_profile_setpoints']['other']])

        if require:
            raise KeyError(f"Missing required variable: {variable.name}")
        # return a none type if the value is optional and not found
        return None

    @staticmethod
    def parse_variables_excel(
            reaction: Reaction,
            measurement: Measurement,
            variable: Variable,
            plot_data: Dict[str, Any]) -> VariableSet:

        variable_set: VariableSet = VariableSet()

        if variable != Variable.TEMPERATURE:
            temperature: float = ExperimentReader.get_variable_excel(Variable.TEMPERATURE, plot_data, True)
            variable_set.set(Variable.TEMPERATURE, temperature)
        elif variable != Variable.PRESSURE:
            pressure: float = ExperimentReader.get_variable_excel(Variable.PRESSURE, plot_data, True)
            variable_set.set(Variable.PRESSURE, pressure)

        if reaction == Reaction.SHOCKTUBE:
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, plot_data, True)
            dpdt: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.DPDT, plot_data, False)

            variable_set.set(Variable.END_TIME, end_time)
            variable_set.set(Variable.DPDT, dpdt)
        elif reaction == Reaction.PLUG_FLOW_REACTOR:
            length: float = ExperimentReader.get_variable_excel(Variable.LENGTH, plot_data, True)
            res_time: float = ExperimentReader.get_variable_excel(Variable.RES_TIME, plot_data, False)
            mdot: float = ExperimentReader.get_variable_excel(Variable.MDOT, plot_data, False)
            if res_time is None and mdot is None:
                raise RuntimeError('Either mdot or res time are required for plug flow reactor')
            area: float = ExperimentReader.get_variable_excel(Variable.AREA, plot_data, True)
            x_profile: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.X_PROFILE, plot_data, False)
            t_profile: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.TIME_PROFILE, plot_data, False)
            t_profile_setpoints: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.TIME_PROFILE_SETPOINTS,
                                                                                     plot_data, False)

            variable_set.set(Variable.LENGTH, length)
            variable_set.set(Variable.RES_TIME, res_time)
            variable_set.set(Variable.MDOT, mdot)
            variable_set.set(Variable.AREA, area)
            variable_set.set(Variable.X_PROFILE, x_profile)
            variable_set.set(Variable.TIME_PROFILE, t_profile)
            variable_set.set(Variable.TIME_PROFILE_SETPOINTS, t_profile_setpoints)
        elif reaction == Reaction.JET_STREAM_REACTOR:
            volume: float = ExperimentReader.get_variable_excel(Variable.VOLUME, plot_data, True)
            res_time: float = ExperimentReader.get_variable_excel(Variable.RES_TIME, plot_data, False)
            mdot: float = ExperimentReader.get_variable_excel(Variable.MDOT, plot_data, False)
            if res_time is None and mdot is None:
                raise RuntimeError('Either mdot or res time are required for plug flow reactor')

            variable_set.set(Variable.VOLUME, volume)
            variable_set.set(Variable.RES_TIME, res_time)
            variable_set.set(Variable.MDOT, mdot)
        elif reaction == Reaction.RAPID_COMPRESSION_MACHINE:
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, plot_data, True)
            time: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.TIME, plot_data, False)
            v_of_t: numpy.ndarray = ExperimentReader.get_variable_excel(Variable.V_OF_T, plot_data, False)

            variable_set.set(Variable.END_TIME, end_time)
            variable_set.set(Variable.TIME, time)
            variable_set.set(Variable.V_OF_T, v_of_t)
        elif reaction == Reaction.CONST_T_P:
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, plot_data, True)

            variable_set.set(Variable.END_TIME, end_time)
        elif reaction == Reaction.FREE_FLAME:
            if variable != Variable.PHI:
                phi: Phi = ExperimentReader.get_variable_excel(Variable.PHI, plot_data, False)
                variable_set.set(Variable.PHI, phi)
        else:
            raise NotImplementedError(f"Reaction {reaction.name} is not implemented")

        # TODO measurement and check for compatible measurement types

        if measurement == Measurement.ABS or measurement == Measurement.EMISSION:
            time_step: float = ExperimentReader.get_variable_excel(Variable.TIME_STEP, plot_data, True)
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, plot_data, True)
            wavelength: float = ExperimentReader.get_variable_excel(Variable.WAVELENGTH, plot_data, True)
            active_species: List[str] = ExperimentReader.get_variable_excel(Variable.ACTIVE_SPECIES, plot_data, True)

            variable_set.set(Variable.TIME_STEP, time_step)
            variable_set.set(Variable.END_TIME, end_time)
            variable_set.set(Variable.WAVELENGTH, wavelength)
            variable_set.set(Variable.ACTIVE_SPECIES, active_species)
        elif measurement == Measurement.IGNITION_DELAY_TIME:
            ignition_delay_targets: List[str] = ExperimentReader.get_variable_excel(Variable.IGNITION_DELAY_TARGETS, plot_data, True)
            ignition_delay_method: str = ExperimentReader.get_variable_excel(Variable.IGNITION_DELAY_METHOD, plot_data, True)
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, plot_data, True)

            variable_set.set(Variable.IGNITION_DELAY_TARGETS, ignition_delay_targets)
            variable_set.set(Variable.IGNITION_DELAY_METHOD, ignition_delay_method)
            variable_set.set(Variable.END_TIME, end_time)
        elif measurement == Measurement.OUTLET:
            pass
        elif measurement == Measurement.ION or measurement == Measurement.PRESSURE or measurement == Measurement.CONCENTRATION:
            time_step: float = ExperimentReader.get_variable_excel(Variable.TIME_STEP, plot_data, True)
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, plot_data, True)

            variable_set.set(Variable.TIME_STEP, time_step)
            variable_set.set(Variable.END_TIME, end_time)
        elif measurement == Measurement.LFS:
            pass
        elif measurement == Measurement.HALF_LIFE:
            target_species: str = ExperimentReader.get_variable_excel(Variable.TARGET_SPECIES, plot_data, True)
            end_time: float = ExperimentReader.get_variable_excel(Variable.END_TIME, plot_data, True)

            variable_set.set(Variable.TARGET_SPECIES, target_species)
            variable_set.set(Variable.END_TIME, end_time)
        else:
            raise NotImplementedError(f"Measurement {measurement.name} is not implemented")

        return variable_set

