from matplotlib.figure import Figure as mpl_Figure


class Figure(mpl_Figure):
    """
    Top-level container for any figure.
    """

    def add_subplot(self, *args, **kwargs):
        """
        Overrides the add_subplot function to add a
        spiffyplots `Panel` object instead of a matplotlib `Axes` object.
        """
