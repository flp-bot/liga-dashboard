import sys
from pathlib import Path
import unittest
import urllib.request
import json

root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
for d in [root_dir, backend_dir]:
    d_str = str(d)
    if d_str not in sys.path:
        sys.path.insert(0, d_str)

SERVER_URL = "http://127.0.0.1:5050"

class TestServerAPI(unittest.TestCase):
    def test_api_latest(self):
        try:
            url = f"{SERVER_URL}/api/latest"
            req = urllib.request.urlopen(url, timeout=5)
            self.assertEqual(req.status, 200)
            data = json.loads(req.read().decode('utf-8'))
            self.assertTrue(isinstance(data, dict))
            self.assertTrue("summary" in data or "total_cards" in data or "timestamp" in data)
        except Exception as e:
            self.fail(f"Falha ao conectar na API {url}: {e}")

    def test_api_cards(self):
        try:
            url = f"{SERVER_URL}/api/cards"
            req = urllib.request.urlopen(url, timeout=5)
            self.assertEqual(req.status, 200)
            data = json.loads(req.read().decode('utf-8'))
            if isinstance(data, dict):
                self.assertTrue("cards" in data or "total_cards" in data or "error" not in data)
            else:
                self.assertIsInstance(data, list)
        except Exception as e:
            self.fail(f"Falha ao conectar na API {url}: {e}")

    def test_frontend_dashboard_page(self):
        try:
            url = f"{SERVER_URL}/dashboard.html"
            req = urllib.request.urlopen(url, timeout=5)
            self.assertEqual(req.status, 200)
            html = req.read().decode('utf-8')
            self.assertIn("<!doctype html>", html.lower())
        except Exception as e:
            self.fail(f"Falha ao carregar página {url}: {e}")

    def test_frontend_css(self):
        try:
            url = f"{SERVER_URL}/auth.css"
            req = urllib.request.urlopen(url, timeout=5)
            self.assertEqual(req.status, 200)
        except Exception as e:
            self.fail(f"Falha ao carregar CSS {url}: {e}")

if __name__ == '__main__':
    unittest.main()
