import json

with open('data/cards_history.json', 'r', encoding='utf-8') as f:
    ch = json.load(f)

with open('data/cards_latest.json', 'r', encoding='utf-8') as f:
    cl = json.load(f)

updated_count = 0
for c in cl.get('cards', []):
    name = c.get('card_name_en') or c.get('card_name_pt', '')
    key = f"{c['binder_id']}_{name}_{c['card_number']}_{c['set_pt']}_{c['quality']}_{c['language']}"
    entries = ch.get(key, [])
    old_trend = c.get('trend')
    if len(entries) >= 2:
        cur_val = entries[-1].get('min', 0.0)
        prev_val = entries[-2].get('min', 0.0)
        if prev_val > 0 and cur_val != prev_val:
            diff = round(cur_val - prev_val, 2)
            pct = round((diff / prev_val) * 100.0, 1)
            c['trend'] = 'up' if diff > 0 else ('down' if diff < 0 else 'stable')
            c['price_change_brl'] = diff
            c['price_change_pct'] = pct
        else:
            c['trend'] = 'stable'
            c['price_change_brl'] = 0.0
            c['price_change_pct'] = 0.0
    else:
        c['trend'] = 'stable'
        c['price_change_brl'] = 0.0
        c['price_change_pct'] = 0.0
    
    if old_trend != c.get('trend'):
        updated_count += 1

with open('data/cards_latest.json', 'w', encoding='utf-8') as f:
    json.dump(cl, f, indent=2, ensure_ascii=False)

print(f'Done! Updated {updated_count} cards in cards_latest.json')
