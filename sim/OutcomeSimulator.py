from typing import List

from data.experiments.common.variable import Variable
from data.experiments.experiment_set import ExperimentSet
from data.mechanism.mechanism import Mechanism
from sim.ReactionSimulator import ReactionSimulator
from sim.Reactors import Reactors


class OutcomeSimulator(ReactionSimulator):
    def shock_tube(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        for experiment in experiment_set.simulated_experiments:
            Reactors.const_t_p(
                experiment.conditions.get(Variable.TEMPERATURE),
                experiment.conditions.get(Variable.PRESSURE),
                experiment.experiment.compounds,
                mechanism,
                experiment.conditions.get(Variable.TARGET_SPECIES),
                experiment.conditions.get(Variable.END_TIME)
            )

    def process_st(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def plug_flow_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_pfr(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def jet_stream_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_jsr(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def rapid_compression_machine(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_rcm(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def const_t_p(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_const_t_p(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def free_flame(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_free_flame(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def get_basic_conditions(self, experiment_set: ExperimentSet):
        temps = experiment_set.variable_range.get(Variable.TEMPERATURE)
        pressures = experiment_set.variable_range.get(Variable.PRESSURE)
        times = experiment_set.variable_range.get(Variable.END_TIME) \
            if experiment_set.variable_range.variable_set.has(Variable.END_TIME) \
            else experiment_set.variable_range.get(Variable.RES_TIME)
        target_species = experiment_set.variable_range.get(Variable.TARGET_SPECIES)
        return temps, pressures, times, target_species