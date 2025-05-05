from abc import ABC
from typing import List

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from serial.plotter.figure_style import StyleGenerator
from serial.plotter.plotter_format import PlotterFormat

class FigureContainer(ABC):
    """
    This class allows the iterator to get new figures. It is an interface that should be extended by c class that
    contains figures such as PlotterFigure.
    """

    def add_figure(self, style_generator:StyleGenerator = None):
        pass

    def get_figures(self) -> List[Figure]:
        pass

    def get_figure(self, style_generator:StyleGenerator = None) -> Figure:
        pass

class PlotterFigureAxesIterator:
    """
    This is an iterator class that gives the properly indexed list of axes such that each axis falls on the correct
    location in the grid.
    If there are not enough spaces left for a new subplot on the current figure a new figure will be created.
    """
    def __init__(self, fig_cont: FigureContainer, plot_format: PlotterFormat):
        self.fig_cont:FigureContainer = fig_cont
        self.rows:int = plot_format.rows
        self.cols:int = plot_format.cols

        # state
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self, style_generator=None):
        """
        Returns an axis/subplot
        """
        rc = self.rows * self.cols

        # add a new figure if the page is full
        if (rc * len(self.fig_cont.get_figures())) <= self.index:
            self.fig_cont.add_figure(style_generator=style_generator)

        fig = self.fig_cont.get_figure()
        axis: Axes = fig.add_subplot(self.rows, self.cols, (self.index % rc) + 1)

        axis.tick_params(axis='both', which='major', labelsize=8)
        axis.tick_params(axis='both', which='minor', labelsize=8)

        fig.subplots_adjust(wspace=0.38, hspace=0.23)

        self.index += 1

        return axis

