from typing import Dict

import yaml

from data.experiments.experiment_set import ExperimentSet
from yaml import dump

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
            'source_mode': experiment_set.source_mode.name,
            'reaction': experiment_set.reaction.name,
            'measurement': experiment_set.measurement.name,
            'simulation_conditions': {
                'range': {
                    'type': experiment_set.variable_range.variable.name,
                    'start': experiment_set.variable_range.start,
                    'end': experiment_set.variable_range.end,
                    'inc': experiment_set.variable_range.inc
                },
                'variables': []
            },
            'species': [],
            'compounds': [],
            'measured_experiments': []
        }

        with open(experiment_file) as f:
            yaml_file = yaml.load(f)
            yaml_file.dump(output_dict)
