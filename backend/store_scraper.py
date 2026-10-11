import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import re
import json
import csv
import os
import hashlib
from datetime import datetime
from playwright.sync_api import sync_playwright
import config
import database
from logger import log_info, log_success, log_warning, log_error

sys.stdout.reconfigure(encoding='utf-8')

# MD5 Hash Map of lossless rendered Playwright element screenshots for digits 0-9
HASH_TO_DIGIT = {
    "190b8c56": "0",
    "8ad27acd": "1",
    "9f185b88": "2",
    "7e376c1e": "3",
    "3b8d145e": "3",
    "4f71a92e": "4",
    "92cdf967": "5",
    "6e01a82f": "6",
    "bb1e5341": "7",
    "fc9cc01c": "8",
    "bc828dd3": "9",
    "c1302b5e": "9",
    "2be60713": "9",
    "d5ba399f": "9",
    "038ee206": "9",
    "0a35a3cb": "9"
}

def decode_price(price_tokens, pos_to_digit):
    s = ""
    for t in price_tokens:
        if t.get('type') == 'comma':
            s += "."
        elif t.get('pos'):
            pos = t['pos']
            digit = pos_to_digit.get(pos, "0")
            s += digit
    try:
        return float(s)
    except ValueError:
        return 0.0

def decode_qty(qty_positions, pos_to_digit):
    s = ""
    for pos in qty_positions:
        digit = pos_to_digit.get(pos, "0")
        s += digit
    try:
        return int(s)
    except ValueError:
        return 0

def load_registered_stores():
    try:
        stores = database.get_registered_stores()
        if stores:
            return {"stores": stores}
    except Exception:
        pass
    if config.REGISTERED_STORES_FILE.exists():
        try:
            with open(config.REGISTERED_STORES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "stores": [
            {
                "id": "pacdeck",
                "name": "PacDeck Store",
                "url": "https://www.pacdeck.com.br/?view=ecom/itens&id=662762&page=1&tcg=2&txt_estoque=1&ultimas=1",
                "enabled": True,
                "last_scraped": None,
                "cards_count": 0
            }
        ]
    }

def save_registered_stores(stores_config):
    stores_list = stores_config.get("stores", [])
    try:
        database.save_registered_stores(stores_list)
    except Exception as e:
        print(f"Erro ao salvar lojas no SQLite: {e}")

    with open(config.REGISTERED_STORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(stores_config, f, ensure_ascii=False, indent=2)

def scrape_single_store(page, store_info):
    store_name = store_info.get("name", "Loja")
    store_url = store_info.get("url")

    print("\n" + "-" * 60)
    print(f"  RASPANDO LOJA: {store_name}")
    print(f"  URL: {store_url}")
    print("-" * 60)

    page.goto(store_url, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)

    # Hide banners / consent overlays
    page.evaluate("""() => {
        const banners = document.querySelectorAll('div');
        for (const b of banners) {
            if (b.innerText && (b.innerText.includes('cookies') || b.innerText.includes('LGPD'))) {
                b.style.display = 'none';
            }
        }
    }""")

    # 1. Map CSS backgroundPosition -> Digit by capturing element screenshots & computing MD5
    digit_elements = page.query_selector_all('.price .vidgmi div, .qty .vidgmi div')

    pos_to_digit = {}
    for el in digit_elements:
        style = el.evaluate("e => e.getAttribute('style') || ''")
        bg_pos = el.evaluate("e => window.getComputedStyle(e).backgroundPosition")
        
        if 'v.png' in style or not bg_pos:
            continue

        if bg_pos not in pos_to_digit:
            screenshot_bytes = el.screenshot()
            h = hashlib.md5(screenshot_bytes).hexdigest()[:8]
            digit = HASH_TO_DIGIT.get(h, "9")
            pos_to_digit[bg_pos] = digit

    # 2. Extract Card Items using page.evaluate()
    items_raw = page.evaluate("""() => {
        const items = [];
        document.querySelectorAll('.card-item').forEach((c, idx) => {
            const titleEl = c.querySelector('.title a');
            const title = titleEl ? titleEl.innerText.trim() : '';
            const link = titleEl ? titleEl.href : '';
            const imgEl = c.querySelector('.card-img img');
            const img = imgEl ? (imgEl.src || imgEl.getAttribute('data-src') || '') : '';
            
            // Qty
            const qtyDiv = c.querySelector('.qty .vidgmi');
            const qtyTokens = [];
            if (qtyDiv) {
                qtyDiv.querySelectorAll('div').forEach(d => {
                    const bgPos = window.getComputedStyle(d).backgroundPosition;
                    qtyTokens.push(bgPos);
                });
            }
            
            // Price
            const priceContainer = c.querySelector('.price .vidgmi');
            const priceTokens = [];
            if (priceContainer) {
                priceContainer.childNodes.forEach(child => {
                    if (child.nodeType === 1) {
                        if (child.style && child.style.backgroundImage && child.style.backgroundImage.includes('v.png')) {
                            priceTokens.push({ type: 'comma' });
                        } else {
                            const bgPos = window.getComputedStyle(child).backgroundPosition;
                            priceTokens.push({ type: 'digit', pos: bgPos });
                        }
                    }
                });
            }

            items.push({
                id: idx + 1,
                card_name: title,
                url: link,
                image_url: img,
                qty_positions: qtyTokens,
                price_tokens: priceTokens
            });
        });
        return items;
    }""")

    cards = []
    for item in items_raw:
        price_val = decode_price(item.get("price_tokens", []), pos_to_digit)
        qty_val = decode_qty(item.get("qty_positions", []), pos_to_digit)

        cards.append({
            "id": item["id"],
            "store_id": store_info.get("id"),
            "store_name": store_name,
            "store_url": store_url,
            "card_name": item["card_name"],
            "url": item["url"],
            "image_url": item["image_url"],
            "quantity": qty_val,
            "price_brl": price_val
        })

    print(f"[OK] Extraídos {len(cards)} cards da loja '{store_name}'.")

    # Save directly to SQLite database
    try:
        database.save_store_cards(cards, store_id=store_info.get("id"), store_name=store_name, store_url=store_url)
        print(f"[SQLITE] {len(cards)} cards da loja '{store_name}' salvos no banco de dados!")
    except Exception as e:
        print(f"[AVISO] Erro ao salvar cards no SQLite: {e}")

    return cards

def run_store_scraper(target_url=None, headless=True):
    stores_config = load_registered_stores()
    registered_list = stores_config.get("stores", [])

    print("=" * 60)
    print("      SCRAPER MULTI-LOJAS - ECOMMERCE LIGA")
    print("=" * 60)

    stores_to_scrape = []
    if target_url and target_url != "--all":
        # Scrape specific single URL
        matched = False
        for s in registered_list:
            if s.get("url") == target_url:
                stores_to_scrape.append(s)
                matched = True
                break
        if not matched:
            stores_to_scrape.append({
                "id": "custom",
                "name": "Loja Personalizada",
                "url": target_url,
                "enabled": True
            })
    else:
        # Scrape all enabled stores
        stores_to_scrape = [s for s in registered_list if s.get("enabled", True)]

    if not stores_to_scrape:
        print("[AVISO] Nenhuma loja ativada encontrada para raspagem.")
        return {"total_cards": 0, "cards": []}

    all_cards = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sync_playwright() as p:
        print("Iniciando navegador Playwright...")
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for s_info in stores_to_scrape:
            try:
                cards = scrape_single_store(page, s_info)
                all_cards.extend(cards)

                # Update registered store metadata
                for reg in registered_list:
                    if reg.get("url") == s_info.get("url"):
                        reg["last_scraped"] = now_str
                        reg["cards_count"] = len(cards)
            except Exception as e:
                print(f"[ERRO] Falha ao raspar loja '{s_info.get('name')}': {e}")

        browser.close()

    # Re-index cards sequentially
    for idx, c in enumerate(all_cards):
        c["id"] = idx + 1

    # Save updated registered stores metadata
    save_registered_stores(stores_config)

    # Save aggregated JSON output to data/store_cards_latest.json
    output_data = {
        "last_updated": now_str,
        "total_stores": len(stores_to_scrape),
        "total_cards": len(all_cards),
        "cards": all_cards
    }

    out_path = config.DATA_DIR / "store_cards_latest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Save output to CSV
    csv_path = config.DATA_DIR / "store_cards_latest.csv"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["ID", "Loja", "Nome da Carta", "Quantidade Estoque", "Preço (R$)", "Link", "Imagem"])
        for c in all_cards:
            writer.writerow([c["id"], c.get("store_name", "Loja"), c["card_name"], c["quantity"], f"{c['price_brl']:.2f}".replace('.', ','), c["url"], c["image_url"]])

    print(f"\n[SUCESSO] Raspagem concluída! Total de {len(all_cards)} cards agregados de {len(stores_to_scrape)} loja(s).")
    print(f"  JSON: {out_path}\n  CSV:  {csv_path}")

    # Sincronizar automaticamente com o Firebase Cloud / Firebase Hosting
    try:
        import firebase_sync
        firebase_sync.sync_all_to_firebase()
    except Exception as e:
        print(f"  [AVISO] Falha na sincronização Firebase: {e}")

    return output_data

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    run_store_scraper(target_url=target)
