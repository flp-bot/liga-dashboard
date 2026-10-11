import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import urllib.request
import json
import unicodedata
import re
from concurrent.futures import ThreadPoolExecutor
import config
from logger import log_info, log_success, log_warning, log_error

def clean_text(s):
    if not s:
        return ''
    s = re.sub(r'\(.*?\)', '', str(s))
    s = s.replace('-', ' ').replace('/', ' ')
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').lower().strip()
    return ' '.join(''.join(c for c in s if c.isalnum() or c.isspace()).split())

def extract_num(raw_num):
    if not raw_num:
        return '', '', ''
    num_part = str(raw_num).split('/')[0].strip()
    digits = re.sub(r'\D', '', num_part)
    plain = digits.lstrip('0') or '0'
    padded3 = digits.zfill(3) if digits else num_part
    return num_part, plain, padded3

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def fetch_pokemontcg_io_image(name):
    clean_n = re.sub(r'\(.*?\)', '', name).strip()
    if not clean_n:
        return None
    q = urllib.parse.quote(f'name:"{clean_n}"')
    url = f"https://api.pokemontcg.io/v2/cards?q={q}&pageSize=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            res = json.loads(r.read())
            c_list = res.get('data', [])
            if c_list:
                return c_list[0]['images']['small']
    except Exception:
        pass
    return None

def generate_images_cache():
    print("Baixando base de cartas do TCGdex (PT, EN, JA, ZH-TW, KO)...")
    tcgdex_cards = []
    for lang in ['pt', 'en', 'ja', 'zh-tw', 'ko']:
        try:
            cards = fetch_json(f'https://api.tcgdex.net/v2/{lang}/cards')
            for c in cards:
                c['_lang'] = lang
            tcgdex_cards.extend(cards)
            print(f"  [OK] {len(cards)} cartas carregadas ({lang.upper()}).")
        except Exception as e:
            print(f"  [AVISO] Erro ao carregar TCGdex {lang.upper()}: {e}")

    sets_map_file = Path('c:/liga/card-sets-map.json')
    sets_map = {}
    if sets_map_file.exists():
        with open(sets_map_file, 'r', encoding='utf-8') as f:
            sets_map = json.load(f)

    # Carrega custom overrides (para cartas asiáticas raras/promos)
    custom_map = {}
    custom_file = config.DATA_DIR / 'custom_card_images.json'
    if custom_file.exists():
        try:
            with open(custom_file, 'r', encoding='utf-8') as f:
                custom_map = json.load(f)
            print(f"  [OK] {len(custom_map)} URLs customizadas carregadas de custom_card_images.json.")
        except Exception as e:
            print(f"  [AVISO] Erro ao carregar custom_card_images.json: {e}")

    # Indexação por CONJUNTO + NÚMERO e por NOME + NÚMERO
    by_set_localid = {}
    by_name_localid = {}

    for c in tcgdex_cards:
        img = c.get('image')
        if not img:
            continue
        c_id = c.get('id', '')
        local_id = str(c.get('localId', ''))
        name = clean_text(c.get('name', ''))
        set_id = c_id.rsplit('-', 1)[0] if '-' in c_id else ''
        set_clean = clean_text(set_id)
        _, plain_num, padded3_num = extract_num(local_id)
        
        card_info = {
            'name': name,
            'image': img,
            'id': c_id,
            'set_id': set_id,
            'local_id': local_id,
            'lang': c['_lang']
        }
        
        if set_clean:
            by_set_localid.setdefault((set_clean, plain_num), []).append(card_info)
            by_set_localid.setdefault((set_clean, padded3_num), []).append(card_info)
        
        if name:
            by_name_localid.setdefault((name, plain_num), []).append(card_info)
            by_name_localid.setdefault((name, padded3_num), []).append(card_info)

    cards_file = config.DATA_DIR / 'cards_latest.json'
    if not cards_file.exists():
        print("[ERRO] cards_latest.json não encontrado.")
        return

    with open(cards_file, 'r', encoding='utf-8') as f:
        cl = json.load(f)

    cards = cl.get('cards', [])
    card_images_map = {}

    matched = 0
    unmatched_cards = []

    for c in cards:
        name_for_key = c.get('card_name_en') or c.get('card_name_pt', '')
        key = f"{c['binder_id']}_{name_for_key}_{c['card_number']}_{c['set_pt']}_{c['quality']}_{c['language']}"
        simple_custom_key = f"{name_for_key}_{c['card_number']}_{c['set_pt']}"

        selected_img = None

        # 0. PRIORIDADE 0: Override Customizado
        if key in custom_map:
            selected_img = custom_map[key]
        elif simple_custom_key in custom_map:
            selected_img = custom_map[simple_custom_key]

        n_pt = clean_text(c.get('card_name_pt'))
        n_en = clean_text(c.get('card_name_en'))
        s_clean = clean_text(c.get('set_pt'))
        raw_num, plain_num, padded3_num = extract_num(c.get('card_number'))

        # 1. PRIORIDADE 1: Manter a consistência do CONJUNTO DA CARTA (Set Match)
        cfg = sets_map.get(s_clean)
        is_classic_set = ('classicas' in s_clean or 'classic' in s_clean)

        if not selected_img and cfg:
            sid_clean = clean_text(cfg['set'])
            candidates = by_set_localid.get((sid_clean, plain_num), []) + by_set_localid.get((sid_clean, padded3_num), [])
            for cand in candidates:
                if is_classic_set or cand['name'] == n_pt or cand['name'] == n_en or (n_pt and n_pt in cand['name']) or (n_en and n_en in cand['name']):
                    selected_img = cand['image']
                    break

            # Se a coleção está no sets_map, constrói a URL ESPECÍFICA DELE (Garante que a carta NUNCA mude para outra coleção aleatória!)
            if not selected_img and not is_classic_set:
                serie = cfg['serie']
                sid = cfg['set']
                lang = cfg.get('lang', 'pt')
                fmt = padded3_num if (serie.lower() in ['sv', 'me'] or sid.lower().startswith('swsh9') or sid.lower().startswith('swsh10') or sid.lower().startswith('swsh11') or sid.lower().startswith('swsh12')) else plain_num
                selected_img = f"https://assets.tcgdex.net/{lang}/{serie}/{sid}/{fmt}"

        # 2. PRIORIDADE 2: Para cartas clássicas/reprints (ex: 30 Anos Cartas Clássicas), busca por nome+número
        if not selected_img and is_classic_set:
            name_cands = (by_name_localid.get((n_pt, plain_num), []) + 
                          by_name_localid.get((n_pt, padded3_num), []) +
                          by_name_localid.get((n_en, plain_num), []) +
                          by_name_localid.get((n_en, padded3_num), []))
            if name_cands:
                selected_img = name_cands[0]['image']

        if selected_img:
            low_url = f"{selected_img}/low.webp" if not (selected_img.endswith('.webp') or selected_img.endswith('.png') or selected_img.endswith('.jpg')) else selected_img
            high_url = f"{selected_img}/high.webp" if not (selected_img.endswith('.webp') or selected_img.endswith('.png') or selected_img.endswith('.jpg')) else selected_img
            card_images_map[key] = {
                "low": low_url,
                "high": high_url
            }
            c["image_url"] = low_url
            c["image_high_url"] = high_url
            matched += 1
        else:
            unmatched_cards.append((c, key))

    # 3. Fallback secundário para cartas restantes via Pokémon TCG API (pokemontcg.io)
    if unmatched_cards:
        print(f"Buscando {len(unmatched_cards)} cartas restantes na Pokémon TCG API secundária...")
        def resolve_secondary(item):
            card, key = item
            name = card.get('card_name_en') or card.get('card_name_pt', '')
            img = fetch_pokemontcg_io_image(name)
            return card, key, img

        with ThreadPoolExecutor(max_workers=5) as executor:
            sec_results = list(executor.map(resolve_secondary, unmatched_cards))

        for card, key, img in sec_results:
            if img:
                card_images_map[key] = {
                    "low": img,
                    "high": img
                }
                card["image_url"] = img
                card["image_high_url"] = img
                matched += 1
            else:
                card["image_url"] = None
                card["image_high_url"] = None

    print(f"Mapeamento Consistente por Coleção concluído: {matched}/{len(cards)} cartas encontradas ({matched/len(cards)*100:.1f}%)")

    images_file = config.DATA_DIR / 'cards_images.json'
    with open(images_file, 'w', encoding='utf-8') as f:
        json.dump(card_images_map, f, indent=2, ensure_ascii=False)
    print(f"Arquivo {images_file} salvo com sucesso!")

    with open(cards_file, 'w', encoding='utf-8') as f:
        json.dump(cl, f, indent=2, ensure_ascii=False)
    print("Atualizado cards_latest.json com consistência total de coleção!")

if __name__ == '__main__':
    generate_images_cache()
