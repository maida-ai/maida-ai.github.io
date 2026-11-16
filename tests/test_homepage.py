import re
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
    "behavior",
    "evidence",
    "local-first",
    "how-it-works",
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

    def test_homepage_has_seven_chapters_in_requested_order(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('<main id="main-content">', html)
        for chapter in HOMEPAGE_CHAPTERS:
            self.assertIn(f'id="{chapter}"', html)
            self.assertIn(f'data-nav-section="{chapter}"', html)
        self.assertEqual(
            re.findall(r'data-nav-section="([^"]+)"', html),
            list(HOMEPAGE_CHAPTERS),
        )

    def test_navigation_acts_as_a_homepage_table_of_contents(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for href, label in (
            ("/#product", "Product"),
            ("/#why-maida", "The incident"),
            ("/#how-it-works", "Install"),
            ("/#local-first", "Runs locally"),
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
        self.assertEqual(html.count('class="trajectory-graphic'), 1)
        self.assertGreaterEqual(html.count('role="img"'), 2)
        self.assertIn("Baseline and pull request execution trajectories", text)
        self.assertIn("Your agent still returns the right answer, but now it calls 3x the tools.", text)
        hero = html.split('id="product"', 1)[1].split('</section>', 1)[0]
        self.assertIn("<figure", hero)
        self.assertNotIn("hero-branching", html)
        self.assertNotIn("<code", hero)

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

    def test_homepage_uses_required_copy_and_metadata(self) -> None:
        html = self.client.get("/").get_data(as_text=True)
        text = " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())
        for expected in (
            "The behavior layer for AI agents",
            "You review the diff. Nobody reviews the behavior.",
            "Maida shows how your agent behaves, and fails the pull request check when that behavior changes in ways you didn't approve.",
            "Runs on your machine or CI runner. No Maida cloud account required.",
            "Maida's evaluation runs locally and does not upload raw traces to Maida. Your agent's own model and tool calls are a separate flow Maida does not create or remove. Anything you choose to enable states where it sends data and what it sends.",
            "Delegate the work. Keep the responsibility.",
            "Agents will do more work than people can watch. That only works if their behavior is understood well enough to be trusted in advance, not inspected after. Maida starts at the pull request, where a change can still be stopped. We are building toward a standard for how agents should behave, on any model and any harness.",
        ):
            self.assertIn(expected, text)
        description = "Maida shows how your AI agent behaves and fails the pull request check when that behavior changes in ways you didn't approve."
        for attribute in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
            self.assertIn(f'{attribute} content="{description}"', html)
        title = "Maida — You review the diff. Nobody reviews the behavior."
        self.assertIn(f"<title>{title}</title>", html)
        for attribute in ('property="og:title"', 'name="twitter:title"'):
            self.assertIn(f'{attribute} content="{title}"', html)
        for forbidden in ("no telemetry", "telemetry by default", "telemetry is off by default", "everything stays on your machine", "guarantee"):
            self.assertNotIn(forbidden, text.lower())

    def test_install_contains_all_commands_and_policy(self) -> None:
        html = self.client.get("/").get_data(as_text=True)
        before, rest = html.split('<section\n  id="how-it-works"', 1)
        install, after = rest.split("</section>", 1)
        for other in (before, after):
            self.assertNotIn("maida run", other)
            self.assertNotIn("maida demo", other)
            self.assertNotIn("uv tool install", other)
            self.assertNotIn("<pre", other)
            self.assertNotIn("policy.yaml", other)
        for expected in ("maida demo --regression", 'uv tool install "maida-ai==0.6.1"', "maida run my_agent.py", "version: 2", "step_count:", '/docs/reference/policy/'):
            self.assertIn(expected, unescape(install))
        hero = before.split('id="product"', 1)[1].split("</section>", 1)[0]
        self.assertRegex(hero, r'href="/docs/getting-started/">\s*Start with one task')
        self.assertRegex(hero, r'href="https://github.com/maida-ai/maida">\s*View on GitHub')

    def test_homepage_fragments_resolve(self) -> None:
        html = self.client.get("/").get_data(as_text=True)
        ids = set(re.findall(r'\bid="([^"]+)"', html))
        for fragment in re.findall(r'href="/?#([^"]+)"', html):
            self.assertIn(fragment, ids)
        self.assertIn("gate", ids)  # Preserve existing incoming fragments.

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

    def test_verdict_explains_uncertainty_and_shows_real_demo_excerpt(self) -> None:
        html = self.client.get("/").get_data(as_text=True)
        verdict = html.split('id="evidence"', 1)[1].split('</section>', 1)[0]
        self.assertIn("The verdict on your pull request.", verdict)
        for status in ("PASS", "FAIL", "INCONCLUSIVE"):
            self.assertRegex(verdict, rf'<dt[^>]*>{status}</dt>')
        self.assertIn("There is not enough evidence to decide; this is never an approval.", verdict)
        self.assertNotIn("verdict-visual-placeholder", verdict)
        self.assertIn('<article id="verdict-report"', verdict)
        for expected in (
            "Demo PR-comment excerpt", "❌ Maida verdict: fail", "5 of 7 checks failed",
            "Top behavior changes", "Repeated tool call", "New tool",
            "escalate_to_human</code> — new tool, not in baseline",
            "send_reply</code> — no longer called",
            "search_kb</code> — repeated 1 -&gt; 5 calls",
            '<th scope="row">Tool calls</th><td>3</td><td>7</td>', "+133%",
            "tool_call_count_exceeded", "new_tool_path",
        ):
            self.assertIn(expected, verdict)
        self.assertNotIn("<pre", verdict)
        self.assertNotIn("<details", verdict)
        self.assertNotIn("3 of 8 checks failed", verdict)


if __name__ == "__main__":
    unittest.main()
