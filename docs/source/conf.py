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

from importlib import import_module
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx import addnodes
import json
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src", "geant_argus")),
)


class RenderAsJSON(Directive):
    # cf. https://stackoverflow.com/a/59883833

    required_arguments = 1

    def run(self):
        module_path, member_name = self.arguments[0].rsplit(".", 1)

        member_data = getattr(import_module(module_path), member_name)
        code = json.dumps(member_data, indent=2)

        literal = nodes.literal_block(code, code)
        literal["language"] = "json"

        return [
            addnodes.desc_name(text=member_name),
            addnodes.desc_content("", literal),
        ]


def setup(app):
    app.add_directive("asjson", RenderAsJSON)


# -- Project information -----------------------------------------------------

project = "geant-argus"
copyright = "2025, GÉANT Vereniging"
author = "swd@geant.org"

# The full version, including alpha/beta/rc tags
release = "0.27"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.extlinks",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Both the class’ and the __init__ method’s docstring
# are concatenated and inserted.
autoclass_content = "both"
autodoc_typehints = "none"

# the tags variable is injected by sphinx into conf.py
# (toggle this by running ``sphinx-build -t drawio``)
if tags.tags.get("drawio", False):  # noqa F821
    extensions.append("sphinxcontrib.drawio")
    drawio_disable_verbose_electron = True


extlinks = {
    "argus": ("https://argus-server.readthedocs.io/en/latest/%s", None),
    "django": ("https://docs.djangoproject.com/en/5.1s/%s", None),
}
