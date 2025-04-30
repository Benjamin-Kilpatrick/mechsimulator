from abc import ABC
from typing import List

from matplotlib.figure import Figure
from serial.plotter.plotter_format import PlotterFormat

class FigureContainer(ABC):

    def add_figure(self):
        pass

    def get_figures(self) -> List[Figure]:
        pass

    def get_figure(self) -> Figure:
        pass

class PlotterFigureAxesIterator:
    """
    This is an iterator class that gives the properly indexed list of axes such that each axis falls on the correct
    location in the grid.
    """
    def __init__(self, fig_cont: FigureContainer, plot_format: PlotterFormat):
        self.fig_cont:FigureContainer = fig_cont
        self.rows:int = plot_format.rows
        self.cols:int = plot_format.cols

        # state
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        rc = self.rows * self.cols

        # add a new figure if the page is full
        if (rc * len(self.fig_cont.get_figures())) <= self.index:
            self.fig_cont.add_figure()

        fig = self.fig_cont.get_figure()
        axis: Axes = fig.add_subplot(self.rows, self.cols, (self.index % rc) + 1)
        self.index += 1
        return axis

