import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import json
import config
from logger import log_info, log_success

cards_history_file = config.CARD_HISTORY_FILE
cards_latest_file = config.DATA_DIR / "cards_latest.json"

if not cards_history_file.exists() or not cards_latest_file.exists():
    log_info("Arquivos de histórico ou cartas mais recentes não encontrados.")
    sys.exit(0)

with open(cards_history_file, 'r', encoding='utf-8') as f:
    ch = json.load(f)

with open(cards_latest_file, 'r', encoding='utf-8') as f:
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
