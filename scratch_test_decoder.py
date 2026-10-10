import json

# Permanent digit position mapping for Liga store CSS sprite
DIGIT_POS_MAP = {
    "-216px -2px": "1",
    "-152px -2px": "2",
    "-344px -2px": "3",
    "-552px -2px": "4",
    "-568px -2px": "5",
    "-0px -2px": "0",
    "0px -2px": "9",
    "-264px -23px": "9",
    "-456px -23px": "7",
    "-480px -23px": "0",
    "-120px -23px": "0",
    "-536px -23px": "0",
    "-224px -23px": "0",
    "-200px -44px": "0",
    "-192px -44px": "0",
    "-240px -44px": "0",
    "-560px -44px": "0",
    "-496px -44px": "0"
}

def decode_price(price_tokens):
    s = ""
    for t in price_tokens:
        if t.get('type') == 'comma':
            s += "."
        elif t.get('pos'):
            pos = t['pos']
            digit = DIGIT_POS_MAP.get(pos, "0")
            s += digit
    try:
        return float(s)
    except ValueError:
        return 0.0

def decode_qty(qty_positions):
    s = ""
    for pos in qty_positions:
        digit = DIGIT_POS_MAP.get(pos, "0")
        s += digit
    try:
        return int(s)
    except ValueError:
        return 0

def test():
    with open('data/store_cards_latest.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for c in data.get('cards', [])[:10]:
        price = decode_price(c.get('price_tokens', []))
        qty = decode_qty(c.get('qty_positions', []))
        print(f"#{c['id']} | {c['card_name']} | Qtd: {qty} un. | Preço: R$ {price:.2f}")

if __name__ == '__main__':
    test()
