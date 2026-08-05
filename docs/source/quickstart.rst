===========
Quick start
===========

Importing :mod:`spiffyplots` registers the bundled Matplotlib styles. Import it
before selecting the base ``spiffy`` style:

.. code-block:: python

    import matplotlib
    import spiffyplots
    from spiffyplots import MultiPanel

    matplotlib.style.use("spiffy")

Create multi-panel figures with :class:`~spiffyplots.multipanel.MultiPanel`.
Figure dimensions are converted from centimetres here because Matplotlib
expects inches:

.. code-block:: python

    cm = 1 / 2.54
    figsize_overview = (11 * cm, 3.5 * cm)

    figure = MultiPanel(shape=(1, 2), figsize=figsize_overview, labels=False)
    figure.panels[0].plot([0, 1, 2], [0, 1, 4])
    figure.panels[1].plot([0, 1, 2], [0, 1, 2])

    figure.savefig("overview.pdf", dpi=300, bbox_inches="tight")
    figure.close()

The bundled color and modifier styles compose with the base style:

.. code-block:: python

    matplotlib.style.use(["spiffy", "muted", "minor-ticks"])

See :class:`~spiffyplots.multipanel.MultiPanel` for custom grid layouts,
label-grid layouts, and panel access by position or label.
