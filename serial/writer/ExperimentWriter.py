from typing import Dict

import numpy
import yaml

from data.experiments.common.condition import Condition
from data.experiments.experiment import Experiment
from data.experiments.experiment_set import ExperimentSet
from data.experiments.mixture import Mixture
from data.experiments.mixture_type import MixtureType
from data.mechanism.species import Species
from serial.common.utils import Utils


class ExperimentWriter:
    """
    Experiment writer class with static methods to write experiment data.
    """
    @staticmethod
    def write_yaml(
            experiment_file: str,
            experiment_set: ExperimentSet):
        """
        Write experiment data to a yaml file
        :param experiment_file: full path to where experiment file will be saved
        :param experiment_set: experiment set
        """
        output_dict: Dict = {
            'meta-data': {
                'version': experiment_set.metadata.version,
                'source': experiment_set.metadata.source,
                'description': experiment_set.metadata.description
            },
            'calculation_type': experiment_set.calculation_type.name,
            'x_source': experiment_set.x_source.name,
            'condition_source': experiment_set.condition_source.name,
            'reaction': experiment_set.reaction.name,
            'measurement': experiment_set.measurement.name,
            'simulation_conditions': {
                'range': {
                    'type': experiment_set.condition_range.variable_of_interest.name,
                    'start': f"{experiment_set.condition_range.start:D}",
                    'end': f"{experiment_set.condition_range.end:D}",
                    'inc': f"{experiment_set.condition_range.inc:D}"
                },
                'conditions': []
            },
            'species': [],
            'mixture': {},
            'measured_experiments': []
        }

        condition: Condition
        for condition in experiment_set.condition_range.get_conditions():
            value = experiment_set.condition_range.get(condition)
            if isinstance(value, numpy.ndarray):
                value = value.tolist()
            output_dict['simulation_conditions']['conditions'].append(
                {
                    'name': condition.name,
                    'value': Utils.convert_quantity_to_str(value)
                }
            )

        species: Species
        for species in experiment_set.simulated_species:
            output_dict['species'].append(
                {
                    'name': species.name,
                    'smiles': species.smiles,
                    'InChI': species.InChI,
                    'spin': species.spin,
                    'charge': species.charge,
                    'excited': species.excited
                }
            )
        mixture_type: MixtureType
        mix: Mixture
        for mixture_type, mix in experiment_set.simulated_mixture.items():
            output_dict['mixture'][mixture_type.name] = []

            species: Species
            for species, quantity in mix.species:
                output_dict['mixture'][mixture_type.name].append({
                    'name': species.name,
                    'concentration': {
                        'value': f'{quantity:D}'
                    }
                })
            if mix.balanced is not None:
                output_dict['mixture'][mixture_type.name].append({
                        'name': mix.balanced.name,
                        'concentration': {
                            'value': 'bal'
                        }
                    }
                )

        experiment: Experiment
        for experiment in experiment_set.measured_experiments:
            experiment_dict = {
                'conditions': [],
                'mixture': {},
                'results': {
                    'conditions': {},
                    'targets': {}
                }
            }

            for condition in experiment.conditions.get_conditions():
                experiment_dict['conditions'].append(
                    {
                        'name': condition.name,
                        'value': Utils.convert_quantity_to_str(experiment.conditions.get(condition))
                    }
                )

            mixture_type: MixtureType
            mix: Mixture
            for mixture_type, mix in experiment.mixtures.items():
                experiment_dict['mixture'][mixture_type.name] = []

                species: Species
                for species, quantity in mix.species:
                    experiment_dict['mixture'][mixture_type.name].append({
                        'name': species.name,
                        'concentration': {
                            'value': f'{quantity:D}'
                        }
                    })

                if mix.balanced is not None:
                    experiment_dict['mixture'][mixture_type.name].append({
                            'name': mix.balanced.name,
                            'concentration': {
                                'value': 'bal'
                            }
                        }
                    )

            for condition in experiment.results.get_variables():
                experiment_dict['results']['conditions'][condition.name] = Utils.convert_quantity_to_str(experiment.results.get_variable(condition))

            for target in experiment.results.get_targets():
                experiment_dict['results']['targets'][target] = Utils.convert_quantity_to_str(experiment.results.get_target(target))

            output_dict['measured_experiments'].append(experiment_dict)

        with open(experiment_file, 'w') as f:
            yaml.dump(output_dict, f, width=100)
