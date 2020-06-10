# Contributing

Contributions are welcome, and they are greatly appreciated!

You can contribute in many ways:

## Types of Contributions

### Implement new features

* New styles
* Journal-specific style sheets
* Helper functions and object classes for multipanel figures

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

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    `$ mkvirtualenv spiffyplots`

    `$ cd spiffyplots/`

    `$ python setup.py develop`

4. Create a branch for local development::

    `$ git checkout -b name-of-your-bugfix-or-feature`

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass `flake8` and the
   tests, including testing other Python versions with `tox`:

    `$ flake8 spiffyplots tests`

    `$ python setup.py test or pytest`

    `$ tox`

   To get `flake8` and `tox`, just pip install them into your virtualenv requirements-dev.txt .

6. Commit your changes and push your branch to GitHub::

    `$ git add .`

    `$ git commit -m "Your detailed description of your changes."`

    `$ git push origin name-of-your-bugfix-or-feature`

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.5, 3.6, 3.7 and 3.8, and for PyPy. Check
   https://travis-ci.com/JRBCH/spiffyplots/pull_requests
   and make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests:

    $ python -m unittest tests.test_spiffyplots

## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed.
Then run:

`$ bump2version patch # ` (possible #: major / minor / patch)

`$ git push`

`$ git push --tags`

Travis will then deploy to PyPI if tests pass.
