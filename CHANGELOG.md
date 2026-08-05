# Changelog

All notable changes to this project will be documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/).

### Unreleased

#### New features

- Add `save` and `close` methods to `MultiPanel`.
- Add `populate_random_data` for quickly filling MultiPanel figures with example data.
- Style sheets are reachable by their package-relative name, for example
  `plt.style.use("spiffyplots.styles.spiffy")`, on Matplotlib 3.7 or newer.

#### Changed

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
- Replace Travis with GitHub Actions
- Forward figure arguments, including DPI, and adjust default label positions.

#### Bugfixes

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
