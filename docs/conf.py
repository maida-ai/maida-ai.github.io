"""Sphinx configuration for the public Maida documentation."""

from html import escape
import json
import os
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
docs_channel = os.environ.get("MAIDA_DOCS_CHANNEL", "release")
release = os.environ.get("MAIDA_DOCS_VERSION")
if release is None:
    release = json.loads(
        (Path(__file__).resolve().parents[1] / "tests/contracts/current-main.json").read_text()
    )["engine_ref"]
version = release
docs_url = "/docs/main/" if docs_channel == "main" else "/docs/"
html_title = f"Maida Docs — {'main (unreleased)' if docs_channel == 'main' else release}"
html_baseurl = f"https://maida.ai{docs_url}"
maida_install_command = (
    'uv tool install "git+https://github.com/maida-ai/maida.git@main"'
    if docs_channel == "main"
    else f'uv tool install "maida-ai=={release.removeprefix("v")}"'
)
html_favicon = "assets/favicon.svg"
html_static_path = ["_static"]
templates_path = ["_templates"]
html_css_files = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap",
    "brand-tokens.css",
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
    "docs_url": docs_url,
}

html_theme_options = {
    "navbar_start": ["maida-brand.html"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["version-switcher", "search-button-field", "theme-switcher", "navbar-icon-links"],
    "switcher": {"json_url": "/docs/versions.json", "version_match": release},
    # The builder creates this shared manifest after both versions succeed.
    # Do not fetch the previously deployed manifest during a local build.
    "check_switcher": False,
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

if docs_channel == "main":
    html_theme_options["announcement"] = (
        'main (unreleased): these docs describe development code. '
        '<a href="/docs/">Read the pinned release documentation.</a>'
    )
    if os.environ.get("MAIDA_DOCS_PATH"):
        html_theme_options["announcement"] = (
            'Local preview of main (unreleased). '
            '<a href="/docs/">Read the pinned release documentation.</a>'
        )

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
    if not source.is_dir():
        return  # Current content links to tutorials; older releases have assets.
    copytree(
        source,
        destination,
        dirs_exist_ok=True,
        ignore=ignore_patterns("__pycache__", "*.py[co]"),
    )


def setup(app) -> None:
    app.connect("build-finished", _copy_download_assets)
    app.connect("source-read", _render_install_command)
    app.connect("source-read", _include_optional_navigation)


def _include_optional_navigation(app, docname, source) -> None:
    """Place newer capture pages in navigation without breaking older releases."""
    optional_pages = {
        "guides/index": ["codex"],
        "cli": ["cli/capture-codex-hook"],
    }
    pages = [
        f"/{page}" for page in optional_pages.get(docname, [])
        if (Path(app.srcdir) / f"{page}.md").is_file()
    ]
    if pages:
        source[0] += "\n\n```{toctree}\n:hidden:\n\n" + "\n".join(pages) + "\n```\n"


def _render_install_command(app, docname, source) -> None:
    if docname == "index":
        source[0] = source[0].replace(
            "{{ maida_install_command }}", escape(maida_install_command, quote=False)
        )
