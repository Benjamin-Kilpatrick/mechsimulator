"""
The FigureStyle class. This class is used to create headers and footers for new pages when they are loaded
"""
from abc import ABC, abstractmethod

from matplotlib.figure import Figure

from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.reaction import Reaction
from data.job.job import Job
from data.mechanism.mechanism import Mechanism

class FigureStyle:
    """
    This class applies the headers and footers to a figure.
    """

    COLORS = ['Red', 'Blue', 'Green', 'Black', 'Magenta', 'Pink']

    REACTION_DISPLAY_NAMES = {
        Reaction.SHOCKTUBE: 'ST',
        Reaction.RAPID_COMPRESSION_MACHINE: 'RCM',
        Reaction.JET_STREAM_REACTOR: 'JSR',
        Reaction.PLUG_FLOW_REACTOR: 'PFR',
        Reaction.CONST_T_P: 'Const. TP',
        Reaction.FREE_FLAME: 'Free flame',
    }

    MEASUREMENT_DISPLAY_NAMES = {
        Measurement.ABSORPTION: 'Absorption',
        Measurement.EMISSION: 'Emission',
        Measurement.CONCENTRATION: 'Concentration',
        Measurement.ION: 'Ion',
        Measurement.PRESSURE: 'Pressure',
        Measurement.IGNITION_DELAY_TIME: 'IDT',
        Measurement.OUTLET: 'Outlet',
        Measurement.LAMINAR_FLAME_SPEED: 'Flame speed',
        Measurement.HALF_LIFE: 'Half-life',
    }

    def __init__(self, job: Job, mechanism: Mechanism, exp_set: ExperimentSet):
        self.job = job
        self.mechanism = mechanism
        self.exp_set = exp_set

    def add_headers_and_footers(self, fig:Figure):
        """ Adds header and footer text to a figure
        """
        self.do_legend(fig)
        self.do_source_headers(fig)
        self.do_footers(fig)
        self.do_title(fig)

    def do_legend(self, fig:Figure):
        # Make some text describing the legends
        header_x_positions = [0.06, 0.37, 0.68]
        header_y_positions = [0.9, 0.92]

        for mech_idx, mechanism in enumerate(self.job.mechanisms):
            header = f'{FigureStyle.COLORS[mech_idx % len(FigureStyle.COLORS)]} lines: {mechanism.mechanism_name}'
            if mech_idx < 3:  # three mechs per row
                y_idx = 0
            else:
                y_idx = 1
            fig.text(header_x_positions[mech_idx % 3], header_y_positions[y_idx],
                     header, fontsize=12, color=FigureStyle.COLORS[mech_idx % len(FigureStyle.COLORS)])

    def do_source_headers(self, fig:Figure):
        # Make some text describing the experimental set
        source = self.mechanism.mechanism_name
        description = self.exp_set.metadata.description
        reaction_type = FigureStyle.REACTION_DISPLAY_NAMES[self.exp_set.reaction]
        meas_type = FigureStyle.MEASUREMENT_DISPLAY_NAMES[self.exp_set.measurement]
        fig.text(0.01, 0.98, f'Source: {source}', fontsize=10)
        fig.text(0.01, 0.96, f'Description: {description}', fontsize=10)
        fig.text(0.77, 0.98, f'Reac. type: {reaction_type}', fontsize=10)
        fig.text(0.77, 0.96, f'Meas. type: {meas_type}', fontsize=10)

    def do_title(self, fig:Figure):
        # TODO! figure out this stuff where to get the title and how pages work within a group
        group_title = self.get_group_title()
        pg_idx = self.get_page_index()
        pgs_per_grp = self.get_pages_per_group()
        title = f'{group_title}\n(pg. {pg_idx + 1} of {pgs_per_grp})'
        fig.suptitle(title, y=0.99, fontsize=16)

    def do_footers(self, fig:Figure):
        # footers
        ylabel = self.get_x_label()
        xlabel = self.get_y_label()
        footnote1 = f'Y-axis: {ylabel}\n'
        footnote2 = f'X-axis: {xlabel}\n'
        footnotes = footnote1 + footnote2
        fig.text(0.11, 0.06, footnotes, fontsize=10, va="top", ha="left")

    def get_pages_per_group(self) -> int:
        return 0

    def get_page_index(self) -> int:
        return 0

    def get_group_title(self) -> str:
        return ""

    def get_x_label(self) -> str:
        return ""

    def get_y_label(self) -> str:
        return ""

class StyleGenerator(ABC):

    @abstractmethod
    def generate(self, job:Job, mechanism:Mechanism, experiment_set:ExperimentSet) -> FigureStyle:
        pass