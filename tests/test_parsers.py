import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
for d in [root_dir, backend_dir]:
    d_str = str(d)
    if d_str not in sys.path:
        sys.path.insert(0, d_str)

import unittest
from backend.parsers import parse_price, parse_price_val, parse_collection_html

class TestParsers(unittest.TestCase):
    def test_parse_price(self):
        self.assertEqual(parse_price("R$ 1.250,50"), 1250.50)
        self.assertEqual(parse_price("Preço: R$ 45,00"), 45.0)
        self.assertEqual(parse_price("Invalido"), 0.0)

    def test_parse_price_val(self):
        self.assertEqual(parse_price_val("R$ 99,90"), 99.90)
        self.assertEqual(parse_price_val("10,00"), 10.0)
        self.assertEqual(parse_price_val(""), 0.0)

    def test_parse_collection_html_sample(self):
        sample_html = """
        <div class="precos">
            <span class="menor-preco">R$ 10,00</span>
            <span class="preco-medio">R$ 20,00</span>
            <span class="maior-preco">R$ 30,00</span>
        </div>
        <div class="blocos-colecao">
            <span class="colecao-nome">Pasta Teste</span>
            <a href="print.php?id=123&tcg=2">Visualizar</a>
            <span>10 cards</span>
            <span>R$ 10,00 - R$ 30,00</span>
        </div>
        """
        parsed = parse_collection_html(sample_html)
        self.assertIn("summary", parsed)
        self.assertEqual(parsed["summary"]["menor_preco_brl"], 10.0)
        self.assertEqual(parsed["summary"]["preco_medio_brl"], 20.0)
        self.assertEqual(parsed["summary"]["maior_preco_brl"], 30.0)
        self.assertEqual(len(parsed["binders"]), 1)
        self.assertEqual(parsed["binders"][0]["id"], "123")

if __name__ == '__main__':
    unittest.main()
