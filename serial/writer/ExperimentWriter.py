from typing import Dict

import numpy
import yaml

from data.experiments.common.variable import Variable
from data.experiments.experiment import Experiment
from data.experiments.experiment_set import ExperimentSet
from yaml import dump

from data.mechanism.species import Species
from data.mixtures.compound import Compound


class ExperimentWriter:
    @staticmethod
    def write_yaml(
            experiment_file: str,
            experiment_set: ExperimentSet):
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
                    'type': experiment_set.condition_range.variable.name,
                    'start': f"{experiment_set.condition_range.start:D}",
                    'end': f"{experiment_set.condition_range.end:D}",
                    'inc': f"{experiment_set.condition_range.inc:D}"
                },
                'variables': []
            },
            'species': [],
            'compounds': [],
            'measured_experiments': []
        }

        variable: Variable
        for variable in experiment_set.condition_range.get_variables():
            value = experiment_set.condition_range.get(variable)
            if isinstance(value, numpy.ndarray):
                value = value.tolist()
            output_dict['simulation_conditions']['variables'].append(
                {
                    'name': variable.name,
                    'value': f"{value:D}" if value is not None else None
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

        compound: Compound
        for compound in experiment_set.simulated_compounds:
            output_dict['compounds'].append(
                {
                    'name': compound.species.name,
                    'concentration':
                        {
                            'value': compound.concentration.value,
                            'lower_bound': compound.concentration.lower_bound,
                            'upper_bound': compound.concentration.upper_bound
                        },
                    'is_balanced': compound.is_balanced
                }
            )

        experiment: Experiment
        for experiment in experiment_set.measured_experiments:
            experiment_dict = {
                'variables': [],
                'compounds': [],
                'results': {
                    'variables': {},
                    'targets': {}
                }
            }

            for variable in experiment.conditions.get_variables():
                experiment_dict['variables'].append(
                    {
                        'name': variable.name,
                        'value': experiment.conditions.get(variable)
                    }
                )

            for compound in experiment.compounds:
                experiment_dict['compounds'].append(
                    {
                        'name': compound.species.name,
                        'concentration':
                            {
                                'value': compound.concentration.value,
                                'lower_bound': compound.concentration.lower_bound,
                                'upper_bound': compound.concentration.upper_bound
                            },
                        'is_balanced': compound.is_balanced
                    }
                )

            for variable in experiment.results.get_variables():
                experiment_dict['results']['variables'][variable.name] = experiment.results.get_variable(variable)

            for target in experiment.results.get_targets():
                experiment_dict['results']['targets'][target] = experiment.results.get_target(target)

        with open(experiment_file, 'w') as f:
            yaml.dump(output_dict, f)
