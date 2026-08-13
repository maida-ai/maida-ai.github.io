"""Sphinx configuration for the public Maida documentation."""

from pathlib import Path
from shutil import copytree, ignore_patterns

project = "Maida"
author = "Maida.AI"
copyright = "Maida.AI"

extensions = [
    "myst_parser",
    "sphinx_copybutton",
]

source_suffix = {".md": "markdown"}
root_doc = "index"
exclude_patterns = [
    "assets/examples/__pycache__",
    "Thumbs.db",
    ".DS_Store",
]

myst_heading_anchors = 4

html_theme = "pydata_sphinx_theme"
html_title = "Maida Docs"
html_baseurl = "https://maida.ai/docs/"
html_favicon = "assets/favicon.svg"
html_static_path = ["_static"]
templates_path = ["_templates"]
html_css_files = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap",
    "maida-docs.css",
]
html_copy_source = False
html_show_sourcelink = False
html_use_index = False
html_domain_indices = False
html_permalinks_icon = "#"

html_context = {
    "default_mode": "light",
    "github_user": "maida-ai",
    "github_repo": "maida-ai.github.io",
    "github_version": "main",
    "doc_path": "docs",
}

html_theme_options = {
    "navbar_start": ["maida-brand.html"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["search-button-field", "theme-switcher", "navbar-icon-links"],
    "navbar_persistent": [],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/maida-ai/maida",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        }
    ],
    "collapse_navigation": True,
    "navigation_depth": 4,
    "show_nav_level": 1,
    "show_toc_level": 2,
    "navigation_with_keys": True,
    "search_as_you_type": True,
    "search_bar_text": "Search Maida docs",
    "back_to_top_button": True,
    "show_prev_next": True,
    "article_header_start": ["breadcrumbs"],
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "primary_sidebar_end": [],
    "footer_start": [],
    "footer_center": [],
    "footer_end": [],
    "pygments_light_style": "github-light",
    "pygments_dark_style": "github-dark",
}

html_sidebars = {
    "index": [],
    "**": ["sidebar-nav-bs.html"],
}

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True


def _copy_download_assets(app, exception) -> None:
    """Preserve the public example URLs used by docs and external links."""
    if exception is not None:
        return

    source = Path(app.srcdir) / "assets" / "examples"
    destination = Path(app.outdir) / "assets" / "examples"
    copytree(
        source,
        destination,
        dirs_exist_ok=True,
        ignore=ignore_patterns("__pycache__", "*.py[co]"),
    )


def setup(app) -> None:
    app.connect("build-finished", _copy_download_assets)
