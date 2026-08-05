import unittest

from src.main import app


class TestMain(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_index_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Collector Sales Data", response.data)


if __name__ == "__main__":
    unittest.main()
