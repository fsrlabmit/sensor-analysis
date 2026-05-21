# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
project = 'fsrlab-sensor-analysis'
copyright = '2026, Kexin Dong, Sam Gould'
author = 'Kexin Dong, Sam Gould'
release = '2.0'

# -- General configuration ---------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.duration",
]

# Make autosectionlabel prefix labels by document, and only auto-label up to H2 —
# H3+ headings (e.g. "Edit", "Submit", "Add to cluster" repeated across STEP 4 / 5 / 6)
# would otherwise collide.
autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2

# MyST extensions — enable $...$ / $$...$$ math, colon-fence admonitions, etc.
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_static_path = ['_static', 'css']
html_permalinks_icon = '<span>#</span>'
html_theme = 'sphinxawesome_theme'
html_theme_options = {
    "show_prev_next": True,
    "show_scrolltop": True,
    "show_breadcrumbs": True,
}

html_css_files = []
