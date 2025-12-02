import sys,os
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

sys.path.insert(0, os.path.abspath('..'))



project = 'Rest contact service api'
copyright = '2025, Anastasia Bondarchuk'
author = 'Anastasia Bondarchuk'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]
# conf.py

autodoc_mock_imports = [
    "fastapi",
    "sqlalchemy",
    "src.schemas",
    "src.database.db",
    "src.services.users",
    "src.services.auth",
    "src.services.email",
    "src.security.hashing",
    "src.conf.config"
]



templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'python'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
