"""
Defines the Panel object class that inherits from matplotlib.Axes.
"""
from matplotlib.axes import Axes

# Spiffy functions to call from axis objects
from .. import multiline


class Panel(Axes):
    def multiline(self, x, y, c, **kwargs):
        """
        Plot multiple lines color-coded with a colormap.
        See spiffyplots.lineplots.multiline for full documentation
        """
        return multiline(x, y, c, axis=self, **kwargs)
