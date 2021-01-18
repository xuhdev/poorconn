# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'poorconn'
copyright = '2020–2021, Hong Xu <hong@topbug.net>'
author = 'Hong Xu'


# -- General configuration ---------------------------------------------------

rst_epilog = """
.. _pytest: https://www.pytest.org
.. _CPython: https://github.com/python/cpython
"""

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

autosummary_generate = True
autosummary_imported_members = True

autodoc_member_order = 'groupwise'
autodoc_typehints = 'description'

autodoc_type_aliases = {
    'DelayBeforeSendingOnceController': 'DelayBeforeSendingOnceController',
    'PatchableSocket': 'PatchableSocket',
}

intersphinx_mapping = {'pytest': ('https://docs.pytest.org/en/stable/', None),
                       'python': ('https://docs.python.org/3', None)}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.tox', 'tests', 'git']

highlight_language = 'none'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'
html_title = 'poorconn'
templates_path = ['_templates']
html_static_path = ['_static']
html_css_files = ['css/custom.css']
