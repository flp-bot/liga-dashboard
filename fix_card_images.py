import json
import unicodedata
import re
from pathlib import Path
import config

def clean_text(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').lower().strip()
    return ''.join(c for c in s if c.isalnum() or c.isspace())

def run_fix():
    sets_map_file = Path('c:/liga/card-sets-map.json')
    if not sets_map_file.exists():
        print("card-sets-map.json nao encontrado!")
        return

    with open(sets_map_file, 'r', encoding='utf-8') as f:
        sets_map = json.load(f)

    cards_file = config.DATA_DIR / 'cards_latest.json'
    images_file = config.DATA_DIR / 'cards_images.json'

    with open(cards_file, 'r', encoding='utf-8') as f:
        cl = json.load(f)

    images = {}
    if images_file.exists():
        try:
            with open(images_file, 'r', encoding='utf-8') as f:
                images = json.load(f)
        except Exception:
            images = {}

    updated = 0
    for c in cl.get('cards', []):
        s_clean = clean_text(c.get('set_pt', ''))
        cfg = sets_map.get(s_clean)
        num_part = str(c.get('card_number', '')).split('/')[0].strip()
        digits = re.sub(r'\D', '', num_part)
        padded3 = digits.zfill(3) if digits else num_part
        plain = digits.lstrip('0') or '0'
        
        name_for_key = c.get('card_name_en') or c.get('card_name_pt', '')
        key = f"{c['binder_id']}_{name_for_key}_{c['card_number']}_{c['set_pt']}_{c['quality']}_{c['language']}"

        if cfg:
            serie = cfg['serie']
            sid = cfg['set']
            fmt = padded3 if (serie in ['sv', 'me'] or sid.startswith('swsh9') or sid.startswith('swsh10') or sid.startswith('swsh11') or sid.startswith('swsh12')) else plain
            new_url = f"https://assets.tcgdex.net/pt/{serie}/{sid}/{fmt}/low.webp"
            new_high = f"https://assets.tcgdex.net/pt/{serie}/{sid}/{fmt}/high.webp"
            
            c['image_url'] = new_url
            c['image_high_url'] = new_high
            images[key] = {'low': new_url, 'high': new_high}
            updated += 1
        elif 'promo' in s_clean or 'mega' in s_clean:
            if 'mega' in s_clean:
                new_url = f"https://assets.tcgdex.net/en/me/mep/{padded3}/low.webp"
                new_high = f"https://assets.tcgdex.net/en/me/mep/{padded3}/high.webp"
            elif 'escarlate' in s_clean or 'violeta' in s_clean or 'sv' in s_clean:
                new_url = f"https://assets.tcgdex.net/pt/sv/svp/{padded3}/low.webp"
                new_high = f"https://assets.tcgdex.net/pt/sv/svp/{padded3}/high.webp"
            elif 'espada' in s_clean or 'escudo' in s_clean or 'swsh' in s_clean:
                new_url = f"https://assets.tcgdex.net/pt/swsh/swshp/SWSH{padded3}/low.webp"
                new_high = f"https://assets.tcgdex.net/pt/swsh/swshp/SWSH{padded3}/high.webp"
            else:
                new_url = None
                new_high = None
            if new_url:
                c['image_url'] = new_url
                c['image_high_url'] = new_high
                images[key] = {'low': new_url, 'high': new_high}
                updated += 1

    print(f"Total de {updated}/{len(cl.get('cards', []))} cartas atualizadas com URLs assertivas de Colecao + Numero!")

    with open(cards_file, 'w', encoding='utf-8') as f:
        json.dump(cl, f, ensure_ascii=False, indent=2)

    with open(images_file, 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=2)

    print("cards_latest.json e cards_images.json salvos com sucesso!")

if __name__ == '__main__':
    run_fix()
