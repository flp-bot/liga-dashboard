import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import json
import csv
import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import config
from logger import log_info, log_success, log_warning, log_error
from backend.parsers import parse_price, parse_price_val, parse_collection_html, parse_binder_html

sys.stdout.reconfigure(encoding='utf-8')

def run_scraper(headless=True):
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now_dt.strftime("%Y-%m-%d")
    
    print("=" * 60)
    print(f"      LIGAPOKEMON - SCRAPER DIÁRIO DA COLEÇÃO [{now_str}]")
    print("=" * 60)
    
    if not config.COOKIES_FILE.exists() and not config.USER_DATA_DIR.exists():
        print("[ERRO] Nenhuma sessão encontrada!")
        return False

    with sync_playwright() as p:
        print("Iniciando navegador...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(config.USER_DATA_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        if config.COOKIES_FILE.exists():
            try:
                with open(config.COOKIES_FILE, "r", encoding="utf-8") as f:
                    context.add_cookies(json.load(f))
            except Exception as e:
                pass

        page = context.pages[0] if context.pages else context.new_page()
        
        print(f"Acessando: {config.COLLECTION_URL}")
        page.goto(config.COLLECTION_URL, wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        html_content = page.content()
        data = parse_collection_html(html_content)
        
        # Save raw HTML dump
        raw_html_path = config.DATA_DIR / f"raw_collection_{date_str}.html"
        with open(raw_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        summary = data["summary"]
        print(f"\n[OK] Métricas Extraídas: {summary['total_cards']} cartas | R$ {summary['maior_preco_brl']:,.2f}")

        # Fetch detailed cards from print pages for all binders found
        binders_to_fetch = data.get("binders") if data.get("binders") else [
            {"id": "563667", "name": "Fofinha 😍"},
            {"id": "559223", "name": "Escuridão absoluta"},
            {"id": "558413", "name": "Caos Ascendente"},
            {"id": "565078", "name": "Escolhas"},
            {"id": "562194", "name": "Equilibrio Perfeito"},
            {"id": "586811", "name": "Promos Mega Evolução"}
        ]
        
        def parse_price_val(val_str):
            if not val_str:
                return 0.0
            cleaned = val_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
            try:
                return float(cleaned)
            except ValueError:
                return 0.0

        # Carrega histórico existente para usar como proteção caso a Liga retorne dados vazios/zerados
        history_file = config.CARD_HISTORY_FILE
        card_history_map = {}
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    card_history_map = json.load(f)
            except Exception:
                card_history_map = {}

        all_cards_flat = []
        for b in binders_to_fetch:
            b_id = b["id"]
            b_name = b["name"]
            url = f"https://www.ligapokemon.com.br/colecao/print.php?id={b_id}&tcg=2"
            print(f"Baixando lista de cartas da pasta '{b_name}' (ID={b_id})...")
            
            binder_cards = []
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    try:
                        page.wait_for_selector("table tr:nth-child(2)", timeout=10000)
                    except Exception:
                        pass
                    # Espera extra de estabilização para garantir injeção de preços e renderização completa
                    page.wait_for_timeout(2500)
                    
                    parsed_cards = parse_binder_html(page.content(), b_id, b_name, card_history_map)
                    if parsed_cards is None:
                        if attempt < max_attempts:
                            log_warning(f"  [RETRY] Tentando recarregar pasta '{b_name}' ({attempt}/{max_attempts})...")
                            page.wait_for_timeout(3000)
                            continue
                        else:
                            log_warning(f"  [AVISO] Tabela não encontrada na pasta '{b_name}' após {max_attempts} tentativas.")
                            break

                    if len(parsed_cards) == 0 and b.get("cards_count", 0) > 0 and attempt < max_attempts:
                        log_warning(f"  [RETRY] Nenhuma linha de carta carregada para '{b_name}', aguardando e tentando novamente...")
                        page.wait_for_timeout(3000)
                        continue

                    binder_cards = parsed_cards
                    log_success(f"  [OK] {len(binder_cards)} cartas lidas na pasta '{b_name}'.")
                    break # Sucesso, sai do loop de tentativas
                except Exception as e:
                    if attempt < max_attempts:
                        print(f"  [RETRY] Erro temporário na pasta {b_name} ({e}), tentando novamente ({attempt}/{max_attempts})...")
                        page.wait_for_timeout(3000)
                    else:
                        print(f"  [ERRO] Falha persistente ao ler pasta {b_name}: {e}")

            all_cards_flat.extend(binder_cards)

        # Checagem de integridade: se leu menos de 60% do total esperado da coleção, não corrompe os dados
        expected_total = summary.get("total_cards", 0)
        if expected_total > 0 and len(all_cards_flat) < (expected_total * 0.6):
            print(f"[ERRO DE INTEGRIDADE] Foram lidas apenas {len(all_cards_flat)} de {expected_total} cartas esperadas. Cancelando atualização para preservar dados corretos.")
            context.close()
            return False

        # Recalculate complete summary and breakdowns from all_cards_flat to include shared collections (e.g. Fofinha 😍)
        tot_cards = sum(c.get("quantity", 1) for c in all_cards_flat)
        tot_min = round(sum((c.get("price_min_brl", 0.0) or 0.0) * c.get("quantity", 1) for c in all_cards_flat), 2)
        tot_avg = round(sum((c.get("price_avg_brl", 0.0) or 0.0) * c.get("quantity", 1) for c in all_cards_flat), 2)
        tot_max = round(sum((c.get("price_max_brl", 0.0) or 0.0) * c.get("quantity", 1) for c in all_cards_flat), 2)

        summary = {
            "menor_preco_brl": tot_min,
            "preco_medio_brl": tot_avg,
            "maior_preco_brl": tot_max,
            "total_cards": tot_cards
        }

        # Build precise binders summary list from all_cards_flat
        binder_map = {}
        for b in binders_to_fetch:
            binder_map[b["id"]] = {
                "id": b["id"],
                "name": b["name"],
                "cards_count": 0,
                "min_price_brl": 0.0,
                "avg_price_brl": 0.0,
                "max_price_brl": 0.0
            }
        
        for c in all_cards_flat:
            b_id = c.get("binder_id")
            b_name = c.get("binder_name", "")
            if b_id and b_id not in binder_map:
                binder_map[b_id] = {
                    "id": b_id,
                    "name": b_name,
                    "cards_count": 0,
                    "min_price_brl": 0.0,
                    "avg_price_brl": 0.0,
                    "max_price_brl": 0.0
                }
            if b_id in binder_map:
                q = c.get("quantity", 1)
                binder_map[b_id]["cards_count"] += q
                binder_map[b_id]["min_price_brl"] += (c.get("price_min_brl", 0.0) or 0.0) * q
                binder_map[b_id]["avg_price_brl"] += (c.get("price_avg_brl", 0.0) or 0.0) * q
                binder_map[b_id]["max_price_brl"] += (c.get("price_max_brl", 0.0) or 0.0) * q

        final_binders = []
        for b_id, b_data in binder_map.items():
            if b_data["cards_count"] >= 0:
                final_binders.append({
                    "id": b_id,
                    "name": b_data["name"],
                    "cards_count": b_data["cards_count"],
                    "min_price_brl": round(b_data["min_price_brl"], 2),
                    "avg_price_brl": round(b_data["avg_price_brl"], 2),
                    "max_price_brl": round(b_data["max_price_brl"], 2)
                })

        # Recalculate breakdowns from all_cards_flat
        languages, qualities, rarities, extras, price_ranges, sets = {}, {}, {}, {}, {}, {}
        for c in all_cards_flat:
            q = c.get("quantity", 1)
            lang = c.get("language", "PT")
            qual = c.get("quality", "NM")
            rar = c.get("rarity", "Comum")
            ext = c.get("extras", "")
            s_pt = c.get("set_pt", "")
            min_p = c.get("price_min_brl", 0.0) or 0.0

            if lang: languages[lang] = languages.get(lang, 0) + q
            if qual: qualities[qual] = qualities.get(qual, 0) + q
            if rar: rarities[rar] = rarities.get(rar, 0) + q
            if ext: extras[ext] = extras.get(ext, 0) + q
            if s_pt: sets[s_pt] = sets.get(s_pt, 0) + q

            if min_p <= 5.0:
                price_ranges["Até R$ 5,00"] = price_ranges.get("Até R$ 5,00", 0) + q
            elif min_p <= 50.0:
                price_ranges["R$ 5,00 a R$ 50,00"] = price_ranges.get("R$ 5,00 a R$ 50,00", 0) + q
            else:
                price_ranges["Acima de R$ 50,00"] = price_ranges.get("Acima de R$ 50,00", 0) + q

        breakdowns = {
            "languages": languages,
            "qualities": qualities,
            "rarities": rarities,
            "extras": extras,
            "price_ranges": price_ranges,
            "sets": sets
        }

        print(f"\n[OK] Métricas Finais (Com Coleções Compartilhadas): {summary['total_cards']} cartas | R$ {summary['preco_medio_brl']:,.2f} (médio)")

        # Save per-card price history first to calculate real trends
        history_file = config.CARD_HISTORY_FILE
        card_history_map = {}
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    card_history_map = json.load(f)
            except Exception:
                card_history_map = {}

        for card in all_cards_flat:
            name = card.get("card_name_en") or card.get("card_name_pt", "")
            key = f"{card['binder_id']}_{name}_{card['card_number']}_{card['set_pt']}_{card['quality']}_{card['language']}"
            if key not in card_history_map:
                card_history_map[key] = []
            
            entries = card_history_map[key]
            existing = next((e for e in entries if e.get("date") == date_str), None)
            if existing:
                existing["min"] = card["price_min_brl"]
                existing["avg"] = card["price_avg_brl"]
                existing["max"] = card["price_max_brl"]
            else:
                entries.append({
                    "date": date_str,
                    "min": card["price_min_brl"],
                    "avg": card["price_avg_brl"],
                    "max": card["price_max_brl"]
                })

            # Real trend calculation: compare latest entry with previous entry based on min price
            if len(entries) >= 2:
                cur_val = entries[-1].get("min", 0.0)
                prev_val = entries[-2].get("min", 0.0)
                if prev_val > 0 and cur_val != prev_val:
                    diff = round(cur_val - prev_val, 2)
                    pct = round((diff / prev_val) * 100.0, 1)
                    if diff > 0:
                        card["trend"] = "up"
                        card["price_change_brl"] = diff
                        card["price_change_pct"] = pct
                    elif diff < 0:
                        card["trend"] = "down"
                        card["price_change_brl"] = diff
                        card["price_change_pct"] = pct
                    else:
                        card["trend"] = "stable"
                        card["price_change_brl"] = 0.0
                        card["price_change_pct"] = 0.0
                else:
                    card["trend"] = "stable"
                    card["price_change_brl"] = 0.0
                    card["price_change_pct"] = 0.0
            else:
                card["trend"] = "stable"
                card["price_change_brl"] = 0.0
                card["price_change_pct"] = 0.0

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(card_history_map, f, indent=2, ensure_ascii=False)

        # Attach cached image URLs from cards_images.json if available
        cards_images_file = config.DATA_DIR / "cards_images.json"
        if cards_images_file.exists():
            try:
                with open(cards_images_file, "r", encoding="utf-8") as f:
                    images_cache = json.load(f)
                for card in all_cards_flat:
                    name = card.get("card_name_en") or card.get("card_name_pt", "")
                    key = f"{card['binder_id']}_{name}_{card['card_number']}_{card['set_pt']}_{card['quality']}_{card['language']}"
                    img_data = images_cache.get(key)
                    if isinstance(img_data, dict):
                        card["image_url"] = img_data.get("low")
                        card["image_high_url"] = img_data.get("high")
                    elif isinstance(img_data, str):
                        card["image_url"] = img_data
                        card["image_high_url"] = img_data
            except Exception as e:
                print(f"Nota ao carregar cache de fotos: {e}")

        # Save cards_latest.json after updating real trends
        cards_export_payload = {
            "timestamp": now_str,
            "date": date_str,
            "total_cards": len(all_cards_flat),
            "cards": all_cards_flat
        }
        
        with open(config.DATA_DIR / "cards_latest.json", "w", encoding="utf-8") as f:
            json.dump(cards_export_payload, f, indent=2, ensure_ascii=False)

        # Save collection_latest.json summary
        export_payload = {
            "timestamp": now_str,
            "date": date_str,
            "summary": summary,
            "binders": final_binders,
            "breakdowns": breakdowns
        }
        
        with open(config.DATA_DIR / "collection_latest.json", "w", encoding="utf-8") as f:
            json.dump(export_payload, f, indent=2, ensure_ascii=False)

        # Save history log CSV
        history_csv = config.DATA_DIR / "history_log.csv"
        file_exists = history_csv.exists()
        with open(history_csv, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Date", "TotalCards", "MinPriceBRL", "AvgPriceBRL", "MaxPriceBRL", "BindersCount"])
            writer.writerow([
                now_str,
                date_str,
                summary["total_cards"],
                summary["menor_preco_brl"],
                summary["preco_medio_brl"],
                summary["maior_preco_brl"],
                len(data["binders"])
            ])

        context.close()
        print("=" * 60)
        print("Scraper concluído com sucesso!")
        print("=" * 60)

        # Trigger Firebase Cloud Sync & Hosting Deploy
        try:
            import firebase_sync
            firebase_sync.sync_all_to_firebase()
        except Exception as e:
            print(f"Nota na sincronização Firebase: {e}")

        # Launch server & open dashboard automatically in default browser
        try:
            import urllib.request
            import subprocess
            import webbrowser
            
            # Check if server is already responding on port 5050
            server_running = False
            try:
                with urllib.request.urlopen("http://127.0.0.1:5050/api/latest", timeout=2) as resp:
                    if resp.status == 200:
                        server_running = True
            except Exception:
                server_running = False

            if not server_running:
                print("Iniciando servidor local do dashboard em http://127.0.0.1:5050...")
                subprocess.Popen(["python", str(config.BASE_DIR / "server.py")], cwd=str(config.BASE_DIR))
                time.sleep(1.5)

            print("Abrindo o Dashboard no navegador...")
            webbrowser.open("http://127.0.0.1:5050")
        except Exception as e:
            print(f"Nota ao abrir o dashboard: {e}")

        return True

if __name__ == "__main__":
    headless_mode = "--show" not in sys.argv
    run_scraper(headless=headless_mode)

