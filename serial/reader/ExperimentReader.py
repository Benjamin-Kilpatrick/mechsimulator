import math
from collections.abc import Iterable
from typing import Dict, Any, List, Optional

import numpy
import pandas

from data.common.value import Value
from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.common.temperature_profile import TemperatureProfile
from data.experiments.common.variable import Variable
from data.experiments.experiment import Experiment
from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurements.abs import Abs
from data.experiments.measurements.concentration import Concentration
from data.experiments.measurements.emission import Emission
from data.experiments.measurements.half_life import HalfLife
from data.experiments.measurements.ion import Ion
from data.experiments.measurements.lfs import Lfs
from data.experiments.measurements.measurement import Measurement
from data.experiments.measurements.outlet import Outlet
from data.experiments.measurements.pressure import Pressure
from data.experiments.metadata import MetaData
from data.experiments.reactions.constant_temperature_pressure import ConstantTemperaturePressure
from data.experiments.reactions.jet_stream_reactor import JetStreamReactor
from data.experiments.reactions.plug_flow_reactor import PlugFlowReactor
from data.experiments.reactions.rapid_compression_machine import RapidCompressionMachine
from data.experiments.reactions.reaction import Reaction
from data.experiments.reactions.shock_tube import ShockTube
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
        variable: str = plot_data['variable']['value']
        start: float = plot_data['start']['value']
        end: float = plot_data['end']['value']
        inc: float = plot_data['inc']['value']

        num_conditions = int((end - start) / inc) + 1

        plot_data[variable] = {
            'value': numpy.linspace(start, end, num_conditions).tolist(),
            'units': plot_data['start']['units'],
            'other': []
        }

        overall: Dict[str, Any] = info_dict['overall']
        meta_data: MetaData = MetaData(overall['version']['value'], overall['source']['value'],
                                       overall['description']['value'])

        variable_name: str = plot_data['variable']['value']
        start: float = plot_data['start']['value']
        end: float = plot_data['end']['value']
        inc: float = plot_data['inc']['value']
        variable: Variable = Variable(variable_name, start, end, inc)

        reactions: List[Reaction] = ExperimentReader.parse_reaction_excel_info(
            overall['reac_type']['value'],
            num_conditions,
            plot_data
        )

        measurements: List[Measurement] = ExperimentReader.parse_measurement_excel_info(
            overall['meas_type']['value'],
            variable,
            plot_data
        )

        sim_experiments: List[Experiment] = [
            Experiment(
                reactions[i],
                measurements[i]
            ) for i in range(num_conditions)
        ]

        return ExperimentSet(
            meta_data,
            calculation_type,
            source_mode,
            sim_experiments,
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
    def parse_measurement_excel_info(measurement_type: str, variable: Variable, plot_data: Dict[str, Any]) -> List[Measurement]:
        if measurement_type == 'abs' or measurement_type == 'emis':
            timestep: float = plot_data['timestep']['value']
            end_time: float = plot_data['end_time']['value']
            wavelength: float = plot_data['wavelength']['value']
            active_species: str = plot_data['active_spc']['value']

            if measurement_type == 'abs':
                # TODO add support for abs_coeff and path_length

                return [
                    Abs(
                        Value(
                            variable.name,
                            value, value, value
                        ),
                        timestep,
                        end_time,
                        wavelength,
                        active_species
                    ) for value in variable
                ]
            else:
                return [
                    Emission(
                        Value(
                            variable.name,
                            value, value, value
                        ),
                        timestep,
                        end_time,
                        wavelength,
                        active_species
                    ) for value in variable
                ]
        if measurement_type == 'idt':
            # TODO figure out idt targets
            idt_target: str
            idt_method: str = plot_data['idt_method']['value']
            raise NotImplementedError
        if measurement_type == 'outlet':
            return [
                Outlet(
                    Value(
                        variable.name,
                        value, value, value
                    ),
                ) for value in variable
            ]
        if measurement_type == 'ion':
            time_step: float = plot_data['time_step']['value']
            end_time: float = plot_data['end_time']['value']
            return [
                Ion(
                    Value(
                        variable.name,
                        value, value, value
                    ),
                    time_step,
                    end_time
                ) for value in variable
            ]
        if measurement_type == 'pressure':
            time_step: float = plot_data['time_step']['value']
            end_time: float = plot_data['end_time']['value']
            return [
                Pressure(
                    Value(
                        variable.name,
                        value, value, value
                    ),
                    time_step,
                    end_time
                ) for value in variable
            ]
        if measurement_type == 'conc':
            time_step: float = plot_data['time_step']['value']
            end_time: float = plot_data['end_time']['value']
            return [
                Concentration(
                    Value(
                        variable.name,
                        value, value, value
                    ),
                    time_step,
                    end_time
                ) for value in variable
            ]
        if measurement_type == 'lfs':
            return [
                Lfs(
                    Value(
                        variable.name,
                        value, value, value
                    )
                ) for value in variable
            ]
        if measurement_type == 'half_life':
            end_time: float = plot_data['end_time']['value']
            target_species: str = plot_data['target_spc']['value']
            return [
                HalfLife(
                    Value(
                        variable.name,
                        value, value, value
                    ),
                    end_time,
                    target_species
                ) for value in variable
            ]

        raise RuntimeError(f'Measurement type {measurement_type} not supported')
            



    @staticmethod
    def parse_reaction_excel_info(reaction: str, num_conditions: int, plot_data: Dict[str, Any]) -> List[Reaction]:
        temperature = plot_data['temp']['value']
        pressure = plot_data['pressure']['value']

        if not isinstance(temperature, Iterable) is not list or len(temperature) != num_conditions:
            temperature = [temperature] * num_conditions
        if not isinstance(pressure, Iterable) or len(pressure) != num_conditions:
            pressure = [pressure] * num_conditions

        if reaction == 'st':
            end_time: float = plot_data['end_time']['value']
            dpdt = None
            if 'dpdt' in plot_data:
                dpdt: float = plot_data['dpdt']['value']

            return [
                ShockTube(
                    temperature[i],
                    pressure[i],
                    end_time,
                    dpdt
                ) for i in range(num_conditions)
            ]
        if reaction == 'pfr':
            length: float = plot_data['length']['value']
            mdot: float = plot_data['mdot']['value']
            area: float = plot_data['area']['value']

            res_time: Optional[float] = None
            x_profile: Optional[numpy.ndarray] = None
            temperature_profile: Optional[List[TemperatureProfile]] = None
            t_profile_setpoints: Optional[numpy.ndarray] = None

            if 'res_time' in plot_data:
                res_time = plot_data['res_time']['value']
            if 'x_profile' in plot_data:
                x_profile = numpy.asarray(plot_data['x_profile']['other'])
            if 't_profile' in plot_data:
                temperature_profile = [TemperatureProfile(t['value'], numpy.asarray(t['other'])) for t in plot_data['t_profile']]
            if 't_profile_setpoints' in plot_data:
                t_profile_setpoints = numpy.asarray(plot_data['t_profile_setpoints']['other'])

            return [
                PlugFlowReactor(
                    temperature[i],
                    pressure[i],
                    length,
                    mdot,
                    area,
                    res_time,
                    x_profile,
                    temperature_profile,
                    t_profile_setpoints
                ) for i in range(num_conditions)
            ]
        if reaction == 'jsr':
            res_time: float = plot_data['res_time']['value']
            mdot: float = plot_data['mdot']['value']
            vol: float = plot_data['vol']['value']
            return [
                JetStreamReactor(
                    temperature[i],
                    pressure[i],
                    res_time,
                    mdot,
                    vol
                ) for i in range(num_conditions)
            ]
        if reaction == 'rcm':
            end_time: float = plot_data['end_time']['value']
            time: float = plot_data['time']['value']

            # TODO need to extrapolate
            v_of_t: numpy.ndarray = numpy.asarray(plot_data['v_of_t']['other'])
            return [
                RapidCompressionMachine(
                    temperature[i],
                    pressure[i],
                    end_time,
                    time,
                    v_of_t
                ) for i in range(num_conditions)
            ]
        if reaction == 'const_t_p':
            end_time: float = plot_data['end_time']['value']
            return [
                ConstantTemperaturePressure(
                    temperature[i],
                    pressure[i],
                    end_time
                ) for i in range(num_conditions)
            ]
        if reaction == 'free_flame':
            raise NotImplementedError

