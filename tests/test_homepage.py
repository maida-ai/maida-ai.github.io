import unittest
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from app import app


STOREFRONT_DEMO_URL = (
    "https://github.com/maida-ai/maida-tutorials/tree/main/demos/pr-gate"
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

    def test_homepage_links_to_storefront_demo(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn(f'href="{STOREFRONT_DEMO_URL}"', html)
        self.assertIn("Try the offline example", html)

    def test_first_screen_proves_the_shipping_regression_before_setup(self) -> None:
        html = self.client.get("/").get_data(as_text=True)
        hero = html.split('id="product"', 1)[1].split('</section>', 1)[0]
        for fact in (
            "VIP shipping remains $0", "VIP shipping becomes $15",
            "Original regression test preserved", "Agent changes the test expectation",
            "Application tests pass", "Application tests also pass",
            "Reviewed Maida check passes", "Reviewed Maida check rejects the change",
        ):
            self.assertIn(fact, hero)
        self.assertLess(hero.index("shipping-proof"), hero.index("Check a Claude Code task"))
        self.assertIn('class="button button--primary" href="/docs/getting-started/"', hero)
        self.assertIn(f'href="{STOREFRONT_DEMO_URL}#try-the-offline-example"', hero)
        self.assertIn("Try the offline example", hero)
        self.assertIn('/static/storefront-proof.png', hero)
        self.assertEqual(self.client.get('/static/storefront-proof.png').status_code, 200)

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

    def test_brand_uses_inline_mark_with_wordmark_and_theme_tokens(self) -> None:
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
                self.assertIn('class="brand-mark"', html)
                self.assertIn("brand-mark__bracket", html)
                self.assertIn("brand-mark__dot", html)
                self.assertNotIn('<img src="/static/favicon.svg"', html)
                self.assertNotIn('class="brand-lockup__ai"', html)

        home = self.client.get("/").get_data(as_text=True)
        about = self.client.get("/about/").get_data(as_text=True)
        self.assertIn('data-maida-theme="light"', home)
        self.assertIn('data-maida-theme="dark"', about)

        site_mark = (PROJECT_ROOT / "static" / "favicon.svg").read_text()
        docs_mark = (PROJECT_ROOT / "docs" / "assets" / "favicon.svg").read_text()
        self.assertEqual(site_mark, docs_mark)
        self.assertIn('id="maida-symbol"', site_mark)
        self.assertIn('id="left-bracket"', site_mark)
        self.assertIn('id="right-bracket"', site_mark)
        self.assertIn('id="core-dot"', site_mark)
        self.assertIn("prefers-color-scheme: dark", site_mark)
        self.assertIn("--maida-logo-bracket", site_mark)
        self.assertIn("--maida-logo-dot", site_mark)

        css = (PROJECT_ROOT / "tailwind" / "input.css").read_text()
        self.assertIn(".brand-mark__bracket", css)
        self.assertIn("var(--maida-logo-bracket)", css)
        self.assertIn("var(--maida-logo-dot)", css)

    def test_homepage_uses_accessible_trajectory_visuals(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        text = unescape(html)
        self.assertGreaterEqual(html.count('class="trajectory-graphic'), 1)
        self.assertIn("Shipping refactor execution comparison", text)
        self.assertIn("Both paths finish with four passing application tests", text)
        self.assertNotIn("lookup_order", text)
        self.assertNotIn("crm_update", text)

    def test_site_loads_brand_tokens_before_compiled_styles(self) -> None:
        response = self.client.get("/")
        html = response.get_data(as_text=True)
        tokens = '<link rel="stylesheet" href="/static/brand-tokens.css" />'
        styles = '<link rel="stylesheet" href="/static/styles.css" />'
        self.assertIn(tokens, html)
        self.assertIn(styles, html)
        self.assertLess(html.index(tokens), html.index(styles))

        css = (PROJECT_ROOT / "tailwind" / "input.css").read_text()
        self.assertIn("--home-paper: var(--maida-paper);", css)
        self.assertIn("--pass-bright: var(--maida-mint);", css)
        self.assertIn("--fail-bright: var(--maida-coral);", css)
        self.assertNotIn("--home-paper: #f2f1eb;", css)

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

    def test_homepage_offers_task_and_offline_example_with_local_first_claims(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        text = unescape(response.get_data(as_text=True))
        self.assertIn("Green tests can hide", text)
        self.assertIn("a broken agent change.", text)
        self.assertIn("Don't let broken", text)
        self.assertIn("uv run --frozen python demo.py", text)
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
        self.assertIn("2 blocking checks failed", text)
        self.assertIn("1/3 trials completed", text)
        self.assertIn("invariant_violation", text)
        self.assertIn("New tool used: <code>rewrite_regression_test</code>", html)
        self.assertIn("Tool removed: <code>repair_shipping_rule</code>", html)
        self.assertIn("no_new_tools", text)
        self.assertIn("forbidden_tools", text)
        self.assertNotIn("+150%", text)
        self.assertIn(f'href="{STOREFRONT_DEMO_URL}"', html)


if __name__ == "__main__":
    unittest.main()
