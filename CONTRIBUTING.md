# Contributing

I mainly wrote this package for my own use and as a learning opportunity.
However, if you find it useful and want to contribute, any contributions are highly appreciated!

SpiffyPlots requires Python 3.10 or newer and uses
[uv](https://docs.astral.sh/uv/) for development.

## Setup

```console
git clone https://github.com/JRBCH/spiffyplots.git
cd spiffyplots
uv sync
```

## Checks

Before committing Python changes, run:

```console
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

For documentation changes, also run:

```console
uv run --group docs sphinx-build -W --keep-going -b html docs/source docs/_build/html
```

If a change affects figure layout or a Matplotlib style, regenerate and inspect
the comparison figures:

```console
uv run python examples/ex_multipanel.py
```

Keep changes focused, add tests for behavior changes, and update the relevant
documentation for user-facing changes.
