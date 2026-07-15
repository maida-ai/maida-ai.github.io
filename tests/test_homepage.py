import unittest

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


if __name__ == "__main__":
    unittest.main()
