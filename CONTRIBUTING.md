# Contributing

Python 3.10+, [uv](https://docs.astral.sh/uv/) for everything. Branch off
`develop` and merge back into it; `master` tracks the last release.

```console
uv sync
uv run ruff format --check . && uv run ruff check . && uv run pytest
```

Add tests for behaviour changes, and a `CHANGELOG.md` bullet under `Unreleased`
for anything user-facing. Run these when they apply:

```console
uv run --group docs sphinx-build -W --keep-going -b html docs/source docs/_build/html
uv run python examples/ex_multipanel.py   # figure layout or style changes
```

## Generated, do not hand-edit

- `spiffyplots/styles/color/*.mplstyle` are built from `spiffyplots.colors`.
  Edit the colour data there, then run
  `uv run python -m spiffyplots._genstyles`. A test fails if they drift.
- `uv.lock`. Change `pyproject.toml`, then run `uv lock`.

The Matplotlib floor is 3.8, well below the dev environment, and CI tests the
oldest and newest Matplotlib for each supported Python. Do not use API that
only exists in recent releases.
