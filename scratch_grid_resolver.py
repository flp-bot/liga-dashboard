import json
import re

def resolve_digit_from_pos(pos):
    m = re.match(r"(-?\d+)px\s+(-?\d+)px", pos)
    if not m:
        return 0
    x = int(m[1])
    y = int(m[2])

    # The sprite image has digits 0..9 placed at X offsets.
    # Digits are spaced horizontally by 8px or 12px columns, or 24px columns per row.
    # Let's inspect the modulo mapping:
    abs_x = abs(x)
    
    # Grid formula: (abs_x // 8) % 10 or (abs_x // 24) % 10
    digit = (abs_x // 8) % 10
    return digit

def test():
    with open('data/store_cards_latest.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for c in data.get('cards', [])[:8]:
        card_name = c['card_name']
        price_str = ""
        for t in c.get('price_tokens', []):
            if t.get('type') == 'comma':
                price_str += "."
            elif t.get('pos'):
                pos = t['pos']
                d = resolve_digit_from_pos(pos)
                price_str += str(d)
        
        try:
            val = float(price_str)
        except ValueError:
            val = 0.0
            
        print(f"{card_name} -> R$ {val:.2f} (raw='{price_str}')")

if __name__ == '__main__':
    test()
