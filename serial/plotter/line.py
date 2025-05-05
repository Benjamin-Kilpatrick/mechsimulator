from abc import ABC, abstractmethod

import numpy as np


class PlotterLine(ABC):
    """
    An actual line that will be plotted in a figure. This class should be extended and used in an object that extends
    PlotterSubplot.
    """

    @abstractmethod
    def get_ydata(self) -> np.ndarray:
        pass

    @abstractmethod
    def get_xdata(self):
        pass

    @abstractmethod
    def get_label(self) -> str:
        pass

    @abstractmethod
    def get_color(self):
        pass

    @abstractmethod
    def get_linestyle(self):
        pass

    @abstractmethod
    def get_marker(self) -> float:
        pass

    @abstractmethod
    def get_zorder(self):
        pass

    def plot(self, ax):
        try:
            mech_xdata = self.get_xdata()
            line_ydata = self.get_ydata()
            label = self.get_label()
            color = self.get_color()
            linestyle = self.get_linestyle()
            marker = self.get_marker()
            zorder = self.get_zorder()
            ax.plot(mech_xdata, line_ydata, label=label, color=color, linestyle=linestyle, marker=marker, zorder=zorder)
        except Exception as e:
            print(e)
