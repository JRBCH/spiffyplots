# Contributing

Contributions are welcome, and they are greatly appreciated!

You can contribute in many ways:

## Types of Contributions

### Implement new features

Your imagination is your limit, as long as the proposed features are
useful in the broader context of scientific data visualization.

Example features:
* New style sheets
* Journal-specific style sheets
* Plotting functions for specific plots
* Color libraries


### Submit examples

* Submit your visualizations generated with SpiffyPlots
* Make sure to add your source code

### Write Documentation

SpiffyPlots could always use more documentation, whether as part of the
official SpiffyPlots docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/JRBCH/spiffyplots/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `spiffyplots` for local development.

1. Fork the `spiffyplots` repo on GitHub.
2. Clone your fork locally::

    `$ git clone git@github.com:your_name_here/spiffyplots.git`

3. Install [uv](https://docs.astral.sh/uv/), then create and synchronize the local development environment::

    `$ cd spiffyplots/`

    `$ uv sync`

   This project requires Python 3.11 or newer.

4. Create a branch for local development::

    `$ git checkout -b name-of-your-bugfix-or-feature`

   Now you can make your changes locally.

5. If necessary, implement new tests that address your new features.
When you're done making changes, check that your changes pass the tests:

    `$ uv run ruff format --check .`

    `$ uv run ruff check .`

    `$ uv run pytest`

1. Commit your changes and push your branch to GitHub::

    `$ git add .`

    `$ git commit -m "Your detailed description of your changes."`

    `$ git push origin name-of-your-bugfix-or-feature`

2. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. The pull request should work for Python 3.11 and newer. Check
   https://travis-ci.com/JRBCH/spiffyplots/pull_requests
   and make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests (e.g. the multipanel module):

    $ uv run python -m unittest tests.test_multipanel

## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed.
Then run:

`$ uv run bump2version patch # ` (possible #: major / minor / patch)

`$ git push`

`$ git push --tags`

Travis will then deploy to PyPI if tests pass.
