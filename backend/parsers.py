import re
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

def parse_price(text):
    if not text:
        return 0.0
    match = re.search(r"R\$\s*([\d\.\,]+)", text)
    if match:
        raw_num = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(raw_num)
        except ValueError:
            return 0.0
    return 0.0

def parse_price_val(val_str):
    if not val_str:
        return 0.0
    cleaned = val_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def parse_collection_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    
    menor_preco = 0.0
    preco_medio = 0.0
    maior_preco = 0.0
    
    precos_div = soup.select_one(".precos")
    if precos_div:
        menor_elem = soup.select_one(".menor-preco")
        medio_elem = soup.select_one(".preco-medio")
        maior_elem = soup.select_one(".maior-preco")
        
        if menor_elem:
            menor_preco = parse_price(menor_elem.get_text())
        if medio_elem:
            preco_medio = parse_price(medio_elem.get_text())
        if maior_elem:
            maior_preco = parse_price(maior_elem.get_text())

    binders = []
    total_cards_all = 0
    
    for block in soup.select(".blocos-colecao"):
        txt = block.get_text(separator=" | ", strip=True)
        name_match = block.find(class_=lambda c: c and 'colecao-nome' in str(c).lower()) or block.find(class_=lambda c: c and 'titulo' in str(c).lower()) or block.find(["h2", "h3", "strong"])
        b_name = name_match.get_text(strip=True) if name_match else ""
        
        b_id = ""
        for a in block.find_all("a", href=True):
            id_match = re.search(r"id=(\d+)", a["href"])
            if id_match:
                b_id = id_match.group(1)
                break

        cards_match = re.search(r"(\d+)\s*cards", txt, re.IGNORECASE)
        b_cards = int(cards_match.group(1)) if cards_match else 0
        
        prices = [parse_price(p) for p in re.findall(r"R\$\s*[\d\.\,]+", txt)]
        b_min_price = prices[0] if len(prices) > 0 else 0.0
        b_max_price = prices[1] if len(prices) > 1 else b_min_price
        
        if b_name and b_id:
            binders.append({
                "id": b_id,
                "name": b_name,
                "cards_count": b_cards,
                "min_price_brl": b_min_price,
                "max_price_brl": b_max_price
            })
            total_cards_all += b_cards

    languages, qualities, rarities, extras, price_ranges, sets = {}, {}, {}, {}, {}, {}
    
    for list_block in soup.select(".colecao-summary-type-list"):
        list_txt = list_block.get_text(strip=True)
        items = list_block.select(".colecao-summary-type-list-item")
        for item in items:
            itxt = item.get_text(strip=True)
            match = re.search(r"^(.*?)\((\d+)\)$", itxt)
            if match:
                key = match.group(1).strip()
                val = int(match.group(2))
                if "Idiomas" in list_txt: languages[key] = val
                elif "Qualidade" in list_txt: qualities[key] = val
                elif "Raridades" in list_txt: rarities[key] = val
                elif "Extras" in list_txt: extras[key] = val
                elif "Faixas de preço" in list_txt: price_ranges[key] = val
                else: sets[key] = val

    if total_cards_all == 0 and languages:
        total_cards_all = sum(languages.values())

    return {
        "summary": {
            "menor_preco_brl": menor_preco,
            "preco_medio_brl": preco_medio,
            "maior_preco_brl": maior_preco,
            "total_cards": total_cards_all
        },
        "binders": binders,
        "breakdowns": {
            "languages": languages,
            "qualities": qualities,
            "rarities": rarities,
            "extras": extras,
            "price_ranges": price_ranges,
            "sets": sets
        }
    }

def parse_binder_html(html_content, b_id, b_name, card_history_map=None):
    if card_history_map is None:
        card_history_map = {}

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    if not table or "Sem acesso" in html_content:
        return None

    rows = table.find_all("tr")
    valid_card_rows = [r for r in rows if len(r.find_all(["td", "th"])) >= 13 and not ("EDIÇÃO" in r.get_text() or "CARD PT" in r.get_text())]

    cards = []
    for tr in valid_card_rows:
        tds = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        qty_str = tds[4] if len(tds) > 4 else "1x"
        qty = int(re.sub(r"\D", "", qty_str)) if re.sub(r"\D", "", qty_str) else 1
        min_p = parse_price_val(tds[10]) if len(tds) > 10 else 0.0
        avg_p = parse_price_val(tds[11]) if len(tds) > 11 else min_p
        max_p = parse_price_val(tds[12]) if len(tds) > 12 else avg_p

        c_name = tds[8] if len(tds) > 8 and tds[8] else (tds[7] if len(tds) > 7 else "")
        c_num = tds[1] if len(tds) > 1 else ""
        c_set = tds[0] if len(tds) > 0 else ""
        c_qual = tds[6] if len(tds) > 6 else "NM"
        c_lang = tds[5] if len(tds) > 5 else "PT"
        hist_key = f"{b_id}_{c_name}_{c_num}_{c_set}_{c_qual}_{c_lang}"
        prev_entries = card_history_map.get(hist_key, [])
        if prev_entries:
            last_known = prev_entries[-1]
            if min_p <= 0.0 and last_known.get("min", 0.0) > 0.0:
                min_p = last_known["min"]
            if avg_p <= 0.0 and last_known.get("avg", 0.0) > 0.0:
                avg_p = last_known["avg"]
            if max_p <= 0.0 and last_known.get("max", 0.0) > 0.0:
                max_p = last_known["max"]

        cards.append({
            "binder_id": b_id,
            "binder_name": b_name,
            "set_pt": c_set,
            "card_number": c_num,
            "color": tds[2] if len(tds) > 2 else "",
            "rarity": tds[3] if len(tds) > 3 else "",
            "quantity": qty,
            "language": c_lang,
            "quality": c_qual,
            "card_name_pt": tds[7] if len(tds) > 7 else "",
            "card_name_en": tds[8] if len(tds) > 8 else "",
            "extras": tds[9] if len(tds) > 9 else "",
            "price_min_brl": min_p,
            "price_avg_brl": avg_p,
            "price_max_brl": max_p,
            "total_value_brl": round(avg_p * qty, 2),
            "price_change_brl": 0.0,
            "price_change_pct": 0.0,
            "trend": "stable"
        })
    return cards

