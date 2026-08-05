===========
Quick start
===========

Importing :mod:`spiffyplots` registers the bundled Matplotlib styles. Import it
before selecting the base ``spiffy`` style:

.. code-block:: python

    import matplotlib
    import spiffyplots
    from spiffyplots import MultiPanel, figsize

    matplotlib.style.use("spiffy")

Create multi-panel figures with :class:`~spiffyplots.multipanel.MultiPanel`.
Use :func:`spiffyplots.figsize` to express dimensions in centimetres or
millimetres while still passing the inches Matplotlib expects:

.. code-block:: python

    figsize_overview = figsize(11, 3.5, units="cm")

    figure = MultiPanel(shape=(1, 2), figsize=figsize_overview, labels=False)
    figure.panels[0].plot([0, 1, 2], [0, 1, 4])
    figure.panels[1].plot([0, 1, 2], [0, 1, 2])

    figure.savefig("overview.pdf", dpi=300, bbox_inches="tight")
    figure.close()

``MultiPanel`` can also perform the same conversion directly:

.. code-block:: python

    figure = MultiPanel(
        shape=(1, 2), figsize=(110, 35), units="mm", labels=False
    )
    figure.close()

For arithmetic with Matplotlib's other figure constructors, :data:`spiffyplots.CM`
and :data:`spiffyplots.MM` convert one centimetre or millimetre to inches.

The bundled color and modifier styles compose with the base style:

.. code-block:: python

    matplotlib.style.use(["spiffy", "muted", "minor-ticks"])

See :class:`~spiffyplots.multipanel.MultiPanel` for custom grid layouts,
label-grid layouts, and panel access by position or label.
