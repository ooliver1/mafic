# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from __future__ import annotations

import os
import sys
from typing import Any

from sphinx.config import Config

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))
from mafic import __version__  # noqa: E402

project = "Mafic"
copyright = "2022-present, Oliver Wilkes"
author = "Oliver Wilkes"

release = version = __version__


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # In sphinx.
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    # External.
    "sphinxcontrib_trio",
    "sphinx_inline_tabs",
    "sphinx_autodoc_typehints",
    # Internal.
    "attributetable",
    "exception_hierarchy",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# html_theme_options = {
#     "light_css_variables": {
#         "color-brand-primary": "#4C8CBF",
#         "color-brand-content": "#306998",
#         "color-admonition-background": "blue",
#     },
#     "dark_css_variables": {
#         "color-brand-primary": "#306998",
#         "color-brand-content": "#FFE871",
#         "color-admonition-background": "yellow",
#     },
# }
default_dark_mode = True


# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autodoc_typehints = "both"
autodoc_default_options = {"members": True, "show-inheritance": True}
autodoc_type_aliases = {"StrategyList": "mafic.pool.StrategyList"}
autodoc_typehints_description_target = "documented"

from mafic.ip import RoutePlannerStatus  # noqa: E402

# Desired explicit aliases.
from mafic.pool import StrategyList  # noqa: E402
from mafic.strategy import StrategyCallable  # noqa: E402
from mafic.type_variables import ClientT  # noqa: E402

aliases = {
    ClientT: ":data:`~mafic.type_variables.ClientT`",
    StrategyCallable: ":data:`~mafic.strategy.StrategyCallable`",
    StrategyList: ":data:`~mafic.pool.StrategyList`",
    StrategyList[ClientT]: ":data:`~mafic.pool.StrategyList`",
    RoutePlannerStatus: ":data:`~mafic.ip.RoutePlannerStatus`",
}


def typehints_formatter(annotation: Any, _: Config) -> str | None:
    return aliases.get(annotation, None)


intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
    "dpy": ("https://discordpy.readthedocs.io/en/stable/", None),
    "nc": ("https://docs.nextcord.dev/en/stable/", None),
    "dis": ("https://docs.disnake.dev/en/stable/", None),
    "pyc": ("https://docs.pycord.dev/en/stable/", None),
}
