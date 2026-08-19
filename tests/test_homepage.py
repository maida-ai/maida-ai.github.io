import unittest
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from app import app


BROKEN_PR_DEMO_URL = (
    "https://github.com/maida-ai/maida-tutorials/tree/main/demos/broken_pr"
)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

HOMEPAGE_CHAPTERS = (
    "product",
    "why-maida",
    "gate",
    "behavior",
    "evidence",
    "how-it-works",
    "local-first",
    "get-started",
)


class HomepageAuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.label_references: list[str] = []
        self.role_images_without_labels: list[str] = []
        self.images_without_alt: list[str] = []
        self.h1_count = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if element_id := attributes.get("id"):
            self.ids.append(element_id)
        if labelled_by := attributes.get("aria-labelledby"):
            self.label_references.extend(labelled_by.split())
        if tag == "h1":
            self.h1_count += 1
        if tag == "img" and "alt" not in attributes:
            self.images_without_alt.append(attributes.get("src", "<unknown>"))
        if attributes.get("role") == "img" and not (
            attributes.get("aria-label") or attributes.get("aria-labelledby")
        ):
            self.role_images_without_labels.append(tag)


class HomepageTests(unittest.TestCase):
    def setUp(self) -> None:
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_homepage_links_to_broken_pr_demo(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn(f'href="{BROKEN_PR_DEMO_URL}"', html)
        self.assertIn("See the broken PR demo", html)

    def test_homepage_is_structured_as_eight_editorial_chapters(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('<main id="main-content">', html)
        for chapter in HOMEPAGE_CHAPTERS:
            self.assertIn(f'id="{chapter}"', html)
            self.assertIn(f'data-nav-section="{chapter}"', html)
        self.assertEqual(html.count("data-nav-section="), len(HOMEPAGE_CHAPTERS))

    def test_navigation_acts_as_a_homepage_table_of_contents(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for href, label in (
            ("/#product", "Product"),
            ("/#why-maida", "Why Maida"),
            ("/#how-it-works", "How it works"),
            ("/#local-first", "Local-first"),
            ("/docs", "Docs"),
        ):
            self.assertIn(f'href="{href}"', html)
            self.assertIn(f">{label}<", html)
        self.assertIn('data-section-link="product"', html)
        self.assertIn('aria-controls="mobile-navigation"', html)

    def test_brand_uses_a_text_wordmark_and_reserves_the_mark_for_favicons(self) -> None:
        for path in (
            "/",
            "/about/",
            "/blog/",
            "/blog/why-your-agent-needs-a-regression-gate/",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                html = response.get_data(as_text=True)

                self.assertEqual(response.status_code, 200)
                self.assertIn('<span class="brand-wordmark">Maida</span>', html)
                self.assertNotIn('<img src="/static/favicon.svg"', html)
                self.assertNotIn('class="brand-lockup__ai"', html)
                self.assertNotIn('id="diff-diamond"', html)

        site_mark = (PROJECT_ROOT / "static" / "favicon.svg").read_text()
        docs_mark = (PROJECT_ROOT / "docs" / "assets" / "favicon.svg").read_text()
        self.assertEqual(site_mark, docs_mark)
        self.assertIn('id="diff-diamond"', site_mark)
        self.assertIn('id="added-arrow"', site_mark)
        self.assertIn('id="changed-arrow"', site_mark)
        self.assertNotIn("<rect", site_mark)

    def test_homepage_uses_accessible_trajectory_visuals(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        text = unescape(html)
        self.assertGreaterEqual(html.count('class="trajectory-graphic'), 2)
        self.assertGreaterEqual(html.count('role="img"'), 3)
        self.assertIn("Baseline and pull request execution trajectories", text)
        self.assertIn("The final answer is identical", text)
        self.assertIn("Behavior: regression", text)

    def test_homepage_uses_semantic_status_color_not_neon_decoration(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for obsolete_class in (
            "bg-grid-pattern",
            "bg-green-radial",
            "text-gradient",
            "btn-glow",
            "shadow-green",
        ):
            self.assertNotIn(obsolete_class, html)

    def test_homepage_leads_with_demo_and_local_first_claims(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        text = unescape(response.get_data(as_text=True))
        self.assertIn("Agents change when code changes.", text)
        self.assertIn("Catch it before merge.", text)
        self.assertIn("Don't let broken", text)
        self.assertIn("maida demo", text)
        self.assertIn("maida demo --regression", text)
        self.assertIn("No Maida cloud required", text)
        self.assertIn("OTel-compatible", text)

    def test_motion_has_a_reduced_motion_fallback(self) -> None:
        css = (PROJECT_ROOT / "tailwind" / "input.css").read_text()
        script = (PROJECT_ROOT / "static" / "site.js").read_text()

        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn(".trace-draw", css)
        self.assertIn("querySelectorAll('.reveal')", script)

    def test_responsive_styles_protect_narrow_layouts_and_navigation(self) -> None:
        css = (PROJECT_ROOT / "tailwind" / "input.css").read_text()
        script = (PROJECT_ROOT / "static" / "site.js").read_text()

        self.assertIn("max-height: calc(100svh - 4.25rem)", css)
        self.assertIn(".pr-evidence__report", css)
        self.assertIn("grid-template-columns: minmax(0, 1fr)", css)
        self.assertIn(".report-table {\n    min-width: 0", css)
        self.assertIn("@media (min-width: 1041px)", css)
        self.assertIn("window.matchMedia('(min-width: 1041px)')", script)

    def test_public_routes_still_render(self) -> None:
        for path in ("/", "/about/", "/blog/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_homepage_accessibility_references_are_well_formed(self) -> None:
        response = self.client.get("/")
        parser = HomepageAuditParser()
        parser.feed(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(parser.h1_count, 1)
        self.assertEqual(len(parser.ids), len(set(parser.ids)), "duplicate HTML ids")
        self.assertEqual(parser.images_without_alt, [])
        self.assertEqual(parser.role_images_without_labels, [])
        self.assertEqual(set(parser.label_references) - set(parser.ids), set())

    def test_homepage_shows_local_regression_report_preview(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        text = unescape(html)
        self.assertIn('aria-labelledby="broken-pr-preview-title"', html)
        self.assertIn("Locally reproduced PR-comment preview", text)
        self.assertIn("❌ Maida verdict: fail", text)
        self.assertIn("3 of 8 checks failed", text)
        self.assertIn("Tool calls", text)
        self.assertIn("+150%", text)
        self.assertIn("lookup_order", text)
        self.assertIn("lookup_order x4", text)
        self.assertIn("repeated 1 -> 4 calls", text)
        self.assertIn(f'href="{BROKEN_PR_DEMO_URL}"', html)


if __name__ == "__main__":
    unittest.main()
