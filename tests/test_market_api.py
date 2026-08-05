import os
import unittest

from src.market_api import fetch_ebay_sales, fetch_tcgplayer_sales


class TestMarketAPI(unittest.TestCase):

    def test_ebay_requires_credentials(self):
        os.environ.pop("EBAY_CLIENT_ID", None)
        os.environ.pop("EBAY_CLIENT_SECRET", None)

        with self.assertRaises(ValueError):
            fetch_ebay_sales("Charizard", limit=1)

    def test_tcgplayer_requires_credentials(self):
        os.environ.pop("TCGPLAYER_CLIENT_ID", None)
        os.environ.pop("TCGPLAYER_CLIENT_SECRET", None)

        with self.assertRaises(ValueError):
            fetch_tcgplayer_sales("Pikachu", limit=1)


if __name__ == "__main__":
    unittest.main()
