# Changelog

All notable changes to this project will be documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/).

### Unreleased

#### Bugfixes

- Fix the PyPI version badge.

### v0.8.0 (07-Aug-2026)

#### New features

- Add `spiffyplots.journals`: figure specifications for several journals. For now, Nature, Science, Cell, Journal of Neuroscience, eLife, PLOS Computational
  Biology, JMLR and TMLR.
- Add a journal style sheet per entry, generated from `spiffyplots.journals`. E.g.
  `plt.style.use(["spiffy", "nature"])` sets default font sizes and default figure size accordingly.
- Add `spiffyplots.label_panels`: FUnction to draw panel letters on any matplotlib figure, not
  just a `MultiPanel`.
- Add the `latex-helvetica` style sheet: LaTeX rendering with Helvetica for both
  text and math. Requires the `sfmath` LaTeX package.

#### Changed

- Set constrained-layout padding to 0 and panel spacing to 0.05.
- **Changed default font sizes to 7-8pt.**
- **Changed the default figure size to 4 x 2.5 in.**
- Panel letters now default to `rcParams["axes.labelsize"]`
- **The default font is now Helvetica**
- Math now renders in the text font when not using latex.
- The `latex` style sheet now resets the font list, so
  `plt.style.use(["spiffy", "latex"])` gives Computer Modern Sans with Computer
  Modern math.

#### Bugfixes

- Fix `multiline`: accept a shared 1D `x` or one array per line, validate that
  x/y point counts and line/value counts agree, and preserve explicit axis
  limits instead of forcing autoscale.

### v0.7.0 (06-Aug-2026)

#### New features

- Add `spiffyplots.colors`: easy access to colors from various color schemes
  (`colors.tol_vibrant.blue`), plus `from_cmap` and `shades`.
- Add `spiffyplots.cmap`: Paul Tol's colormaps, registered under a `tol.`
  prefix and reachable by short name. If installed, also imports colormaps from 
  `cmcrameri` and `colorcet`. Also
  `from_colors`, `from_base` and `discrete_rainbow`.
- Add the `tol-high-contrast`, `tol-medium-contrast`, `tol-light` and
  `okabe-ito` color style sheets.
- Add a `colormaps` extra: `pip install "spiffyplots[colormaps]"` pulls in
  `cmcrameri` and `colorcet`.
- Add a `figsize` converter, `CM` and `MM` constants, and a `units` option for
  constructing `MultiPanel` figures in centimetres or millimetres.
- Add `save`, `savefig` and `close` methods to `MultiPanel`
- Add `populate_random_data` for quickly filling MultiPanel figures with example data.

#### Changed

- Switched to MIT license.
- **The default `image.cmap` is now Paul Tol's `tol.iridescent`**
- **Every color cycle now ends with black, then grey**.
- **`bright` and `muted` changed color order.** They now follow Paul Tol's recommendation. 
- **Renamed the color sheets** to `tol-bright`, `tol-muted` and `tol-vibrant`,
  with the bare names kept as aliases.
- Color sheets are generated from `spiffyplots.colors` by
  `python -m spiffyplots._genstyles`.
- Removed the `high-vis` and `retro` color sheets.
- Removed the `heatmap` sheet.
- Document that `MultiPanel.width_ratios` has one value per column of the
  computed `shape`, rather than one value per visible panel.
- Remove the unused `spiffyplots.base` and
  `spiffyplots.axis` modules.
- Require Python 3.10 or newer and Matplotlib 3.8 or newer.
- Use lowercase panel labels and panel attribute names by
  default. Uppercase remains available with `label_case="uppercase"`.
- Refresh and automate generation of the Matplotlib and Spiffyplots
  comparison figures.
- Refresh the `MultiPanel` notebook with populated grid and label examples.
- Ship the style sheets inside the package and register them with Matplotlib
  when `spiffyplots` is imported, instead of copying them into the Matplotlib
  config directory at install time. Now requires importing `spiffyplots` before calling
  `plt.style.use`.
- Use `uv` for development and Ruff for linting and formatting.
- Replace Travis with GitHub Actions and PyPI Trusted Publishing.
- Restore reproducible Read the Docs builds and add documentation checks to CI.
- Forward figure arguments, including DPI, and adjust default label positions.

#### Bugfixes

- Preserve explicitly declared `MultiPanel` dimensions on export and warn when
  `bbox_inches="tight"` would change them.
- Export PDF and PostScript text as embedded TrueType fonts and preserve SVG
  text as editable text instead of outlines in the base style.
- Accept nested Python sequences as label grids and support arbitrary labels
  and more than 26 panels.
- Warn when constrained layout ignores explicit `MultiPanel` margins or
  spacing, while retaining support for row and column ratios.
- Reject unknown `MultiPanel` keyword arguments before creating a figure.
- Accept list and NumPy array spans and NumPy integer coordinates in
  `MultiPanel` grid specifications.
- Report the overlapping coordinates in `MultiPanel` layout warnings.
- Align panel labels using point offsets from their panels and avoid creating
  extra invisible axes for labels.
- Allow `MultiPanel` to create single-panel layouts and save to PDF with the
  default `format="pdf"` argument.
- Install the style sheets. `pip install spiffyplots` previously shipped none
  of them, so `plt.style.use("spiffy")` failed on a clean environment.
- Correct `multiline` to use the supplied coordinates and axis.

### v0.6.1 (26-May-2021)

- Enable constrained layout by default and update styles and examples.

### v0.6.0 (26-May-2021)

- Add example notebooks and initial axis and line-plotting helpers.
- Simplify distribution packaging and remove universal wheel support.

### v0.5.2a (13-Oct-2020)

- Add label-array grid layouts to `MultiPanel`.
- Improve overlapping-panel detection and warnings, and fix setuptools packaging.
- Update project metadata, development requirements, and Travis deployment.

### v0.4.5 (14-Jun-2020)

- Align figure labels and add multipanel examples and documentation.

### v0.4.4 (14-Jun-2020)

- Add the heatmap style.
- Fix `MultiPanel` keyword handling.
- Reorganize the Sphinx documentation and expand tests.

### v0.4.3 (12-Jun-2020)

- Adopt pytest, coverage reporting, Black, Flake8, and pre-commit checks.

### v0.4.2 (12-Jun-2020)

- Add the `MultiPanel` class.
- Correct stylesheet typos and expand tests.

### v0.4.1 (10-Jun-2020)

- Correct the right-axis style.

### v0.4.0 (10-Jun-2020)

- Add top-axis and right-axis styles.

### v0.3.12 (10-Jun-2020)

- Add wheel tooling to the package requirements.

### v0.3.11 (10-Jun-2020)

- Configure Travis to publish source distributions only.

### v0.3.10 (10-Jun-2020)

- Refine the manifest and setuptools configuration.

### v0.3.9 (10-Jun-2020)

- Include Matplotlib style files in built distributions.

### v0.3.7 (10-Jun-2020)

- Fix setuptools installation behavior.

### v0.3.6 (10-Jun-2020)

- Fix the version-bumping configuration.

### v0.3.5 (10-Jun-2020)

- Expand the source-distribution manifest.

### v0.3.4 (10-Jun-2020)

- Configure Travis to publish wheels only.

### v0.3.3 (10-Jun-2020)

- Update post-install style copying and the package manifest.

### v0.3.2 (10-Jun-2020)

- Rework post-install style copying.

### v0.3.1 (10-Jun-2020)

- Initial tagged release with styles, packaging, tests, and CI.
