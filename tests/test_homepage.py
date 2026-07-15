import unittest
from html import unescape

from app import app


BROKEN_PR_DEMO_URL = (
    "https://github.com/maida-ai/maida-tutorials/tree/main/demos/broken_pr"
)


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
        self.assertIn("repeated 1 -> 4 calls", text)
        self.assertIn(f'href="{BROKEN_PR_DEMO_URL}"', html)


if __name__ == "__main__":
    unittest.main()
