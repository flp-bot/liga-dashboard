import sys
from pathlib import Path

# Add project root and backend to sys.path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
for d in [root_dir, backend_dir]:
    d_str = str(d)
    if d_str not in sys.path:
        sys.path.insert(0, d_str)

import unittest
import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        database.init_db()

    def test_init_db(self):
        stores = database.get_registered_stores()
        self.assertIsInstance(stores, list)
        self.assertGreaterEqual(len(stores), 1)

    def test_save_registered_stores(self):
        stores = database.get_registered_stores()
        res = database.save_registered_stores(stores)
        self.assertEqual(len(res), len(stores))

    def test_store_cards_roundtrip(self):
        sample_cards = [
            {
                "card_name": "Pikachu Test",
                "quantity": 2,
                "price_brl": 15.5,
                "url": "http://example.com",
                "image_url": "http://example.com/img.jpg"
            }
        ]
        database.save_store_cards(sample_cards, store_id="test_store", store_name="Test Store")
        retrieved = database.get_all_store_cards()
        self.assertGreaterEqual(len(retrieved), 1)
        found = any(c["card_name"] == "Pikachu Test" for c in retrieved)
        self.assertTrue(found)

if __name__ == '__main__':
    unittest.main()
