import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import json
import csv
import datetime
import config
import database
from logger import log_info, log_error

def mask_email(email):
    if not email or "@" not in email:
        return email
    user, domain = email.split("@", 1)
    masked_user = user[0] + "***" if len(user) <= 3 else user[:2] + "***" + user[-1]
    return f"{masked_user}@{domain}"

def get_session_status(task_state):
    email, _ = config.get_credentials()
    cookies_exist = config.COOKIES_FILE.exists()
    last_modified = None
    cookies_count = 0
    
    if cookies_exist:
        try:
            mtime = config.COOKIES_FILE.stat().st_mtime
            last_modified = datetime.datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")
            with open(config.COOKIES_FILE, "r", encoding="utf-8") as f:
                cookies_list = json.load(f)
                cookies_count = len(cookies_list)
        except Exception as e:
            log_error("Erro ao ler cookies em get_session_status", exc=e)

    return {
        "cookies_exist": cookies_exist,
        "cookies_count": cookies_count,
        "last_cookie_update": last_modified,
        "email": email,
        "email_masked": mask_email(email),
        "task_state": {
            "is_running": task_state.get("is_running", False),
            "current_task": task_state.get("current_task"),
            "last_result": task_state.get("last_result")
        }
    }

def get_latest_data():
    json_file = config.DATA_DIR / "collection_latest.json"
    if json_file.exists():
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {"error": "Nenhum dado encontrado."}

def get_cards_data():
    cards_file = config.DATA_DIR / "cards_latest.json"
    if cards_file.exists():
        try:
            with open(cards_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {"total_cards": 0, "cards": []}

def get_store_cards_data():
    try:
        cards = database.get_all_store_cards()
        if cards:
            return {"total_cards": len(cards), "cards": cards}
    except Exception as e:
        log_error("Erro ao ler banco SQLite em get_store_cards_data", exc=e)

    store_file = config.DATA_DIR / "store_cards_latest.json"
    if store_file.exists():
        try:
            with open(store_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {"total_cards": 0, "cards": []}

def get_registered_stores_data():
    try:
        stores = database.get_registered_stores()
        return {"stores": stores}
    except Exception as e:
        log_error("Erro ao ler banco SQLite em get_registered_stores_data", exc=e)
        
    if config.REGISTERED_STORES_FILE.exists():
        try:
            with open(config.REGISTERED_STORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_error("Erro ao ler registered_stores.json em get_registered_stores_data", exc=e)
    return {"stores": []}

def save_registered_stores_data(body):
    try:
        stores = body.get("stores", [])
        database.save_registered_stores(stores)
        return {"status": "success", "data": body}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_history_data():
    history_csv = config.DATA_DIR / "history_log.csv"
    history_records = []
    if history_csv.exists():
        try:
            with open(history_csv, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    history_records.append(row)
        except Exception as e:
            log_error("Erro ao ler history_log.csv em get_history_data", exc=e)
    return history_records

def get_costs_data():
    if config.COSTS_FILE.exists():
        try:
            with open(config.COSTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_error("Erro ao ler cards_costs.json em get_costs_data", exc=e)
    return {"cards_costs": {}, "total_collection_cost": None}

def save_costs_data(body):
    current = get_costs_data()
    if not isinstance(current, dict):
        current = {"cards_costs": {}, "total_collection_cost": None}

    cards_incoming = body.get("cards_costs")
    if isinstance(cards_incoming, dict):
        if "cards_costs" not in current or not isinstance(current["cards_costs"], dict):
            current["cards_costs"] = {}
        for k, v in cards_incoming.items():
            if v is None or v == "":
                current["cards_costs"].pop(k, None)
            else:
                try:
                    current["cards_costs"][k] = float(v)
                except (ValueError, TypeError):
                    pass

    if "total_collection_cost" in body:
        tot = body["total_collection_cost"]
        if tot is None or tot == "":
            current["total_collection_cost"] = None
        else:
            try:
                current["total_collection_cost"] = float(tot)
            except (ValueError, TypeError):
                pass

    current["updated_at"] = datetime.datetime.now().isoformat()
    try:
        with open(config.COSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
        return {"status": "success", "data": current}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_card_history_data():
    if config.CARD_HISTORY_FILE.exists():
        try:
            with open(config.CARD_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_error("Erro ao ler cards_history.json em get_card_history_data", exc=e)

    cards_payload = get_cards_data()
    cards = cards_payload.get("cards", []) if isinstance(cards_payload, dict) else []
    history_map = {}
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    for card in cards:
        b_id = card.get("binder_id", "")
        name = card.get("card_name_en") or card.get("card_name_pt", "")
        num = card.get("card_number", "")
        set_pt = card.get("set_pt", "")
        quality = card.get("quality", "NM")
        lang = card.get("language", "PT")
        key = f"{b_id}_{name}_{num}_{set_pt}_{quality}_{lang}"

        cur_min = float(card.get("price_min_brl", 0.0) or 0.0)
        cur_avg = float(card.get("price_avg_brl", 0.0) or 0.0)
        cur_max = float(card.get("price_max_brl", 0.0) or 0.0)

        history_map[key] = [{
            "date": date_str,
            "min": cur_min,
            "avg": cur_avg,
            "max": cur_max
        }]

    try:
        with open(config.CARD_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_map, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log_error("Erro ao salvar cards_history.json inicial", exc=e)

    return history_map

def get_sales_config():
    if config.SALES_CONFIG_FILE.exists():
        try:
            with open(config.SALES_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_error("Erro ao ler sales_config.json em get_sales_config", exc=e)
    return {"sale_binder_ids": [], "updated_at": None}

def save_sales_config(body):
    current = get_sales_config()
    if not isinstance(current, dict):
        current = {"sale_binder_ids": [], "updated_at": None}

    if "sale_binder_ids" in body and isinstance(body["sale_binder_ids"], list):
        current["sale_binder_ids"] = [str(x) for x in body["sale_binder_ids"]]

    if "toggle_binder_id" in body:
        b_id = str(body["toggle_binder_id"])
        current_ids = set(current.get("sale_binder_ids", []))
        if b_id in current_ids:
            current_ids.remove(b_id)
        else:
            current_ids.add(b_id)
        current["sale_binder_ids"] = list(current_ids)

    current["updated_at"] = datetime.datetime.now().isoformat()
    try:
        with open(config.SALES_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
        return {"status": "success", "data": current}
    except Exception as e:
        return {"status": "error", "message": str(e)}
