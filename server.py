import http.server
import socketserver
import json
import csv
import subprocess
import threading
import mimetypes
import sys
import datetime
from pathlib import Path
import config
import setup_session
import database

sys.stdout.reconfigure(encoding='utf-8')
PORT = 5050

# Global lock and execution status to prevent concurrent Playwright tasks
task_lock = threading.Lock()
task_state = {
    "is_running": False,
    "current_task": None,  # 'scraper', 'login', 'check'
    "started_at": None,
    "last_result": None
}

def mask_email(email):
    if not email or "@" not in email:
        return email
    user, domain = email.split("@", 1)
    if len(user) <= 3:
        masked_user = user[0] + "***"
    else:
        masked_user = user[:2] + "***" + user[-1]
    return f"{masked_user}@{domain}"


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def read_json_body(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                raw = self.rfile.read(content_length).decode('utf-8')
                return json.loads(raw)
        except Exception as e:
            print(f"Erro ao ler corpo JSON: {e}")
        return {}

    def do_GET(self):
        raw_path = self.path
        clean_path = raw_path.split('?')[0]
        if clean_path.endswith('/') and len(clean_path) > 1:
            clean_path = clean_path[:-1]
            
        print(f"[SERVER GET] raw='{raw_path}' -> clean='{clean_path}'", flush=True)

        if clean_path == "/api/latest":
            self.send_json_response(self.get_latest_data())
        elif clean_path == "/api/history":
            self.send_json_response(self.get_history_data())
        elif clean_path == "/api/cards":
            self.send_json_response(self.get_cards_data())
        elif clean_path == "/api/costs":
            self.send_json_response(self.get_costs_data())
        elif clean_path == "/api/card-history":
            self.send_json_response(self.get_card_history_data())
        elif clean_path == "/api/session-status":
            self.send_json_response(self.get_session_status())
        elif clean_path == "/api/sales-config":
            self.send_json_response(self.get_sales_config())
        elif clean_path == "/api/store-cards":
            self.send_json_response(self.get_store_cards_data())
        elif clean_path == "/api/registered-stores":
            self.send_json_response(self.get_registered_stores_data())
        elif clean_path in ["/stores", "/stores.html", "/lojas", "/lojas.html"]:
            self.serve_file(config.BASE_DIR / "stores.html")
        elif clean_path in ["/sales", "/sales.html", "/vendas", "/vendas.html"]:
            self.serve_file(config.BASE_DIR / "sales.html")
        elif clean_path in ["/collections", "/collections.html", "/colecoes"]:
            self.serve_file(config.BASE_DIR / "collections.html")
        elif clean_path in ["/dashboard", "/dashboard.html", "/index.html", "/"]:
            self.serve_file(config.BASE_DIR / "dashboard.html")
        else:
            rel_file = config.BASE_DIR / clean_path.lstrip('/')
            if rel_file.exists() and rel_file.is_file():
                self.serve_file(rel_file)
            else:
                print(f"[SERVER 404] File not found for clean='{clean_path}'", flush=True)
                self.send_error(404, "Arquivo nao encontrado")

    def do_POST(self):
        raw_path = self.path
        clean_path = raw_path.split('?')[0]
        if clean_path.endswith('/') and len(clean_path) > 1:
            clean_path = clean_path[:-1]

        print(f"[SERVER POST] clean='{clean_path}'", flush=True)
            
        if clean_path == "/api/run-scraper":
            if task_state["is_running"]:
                self.send_json_response({
                    "status": "busy",
                    "message": f"Já existe uma tarefa em execução ({task_state['current_task']}). Aguarde finalizar."
                }, status_code=409)
                return

            def run():
                with task_lock:
                    task_state["is_running"] = True
                    task_state["current_task"] = "scraper"
                    task_state["started_at"] = datetime.datetime.now().isoformat()
                try:
                    subprocess.run(["python", str(config.BASE_DIR / "scraper.py")])
                finally:
                    with task_lock:
                        task_state["is_running"] = False
                        task_state["current_task"] = None
            
            thread = threading.Thread(target=run, daemon=True)
            thread.start()
            self.send_json_response({"status": "success", "message": "Scraper iniciado com sucesso!"})

        elif clean_path == "/api/run-store-scraper":
            if task_state["is_running"]:
                self.send_json_response({
                    "status": "busy",
                    "message": f"Já existe uma tarefa em execução ({task_state['current_task']}). Aguarde finalizar."
                }, status_code=409)
                return

            body = self.read_json_body()
            store_url = body.get("url")

            def run_store():
                with task_lock:
                    task_state["is_running"] = True
                    task_state["current_task"] = "store_scraper"
                    task_state["started_at"] = datetime.datetime.now().isoformat()
                try:
                    cmd = ["python", str(config.BASE_DIR / "store_scraper.py")]
                    if store_url:
                        cmd.append(store_url)
                    subprocess.run(cmd)
                finally:
                    with task_lock:
                        task_state["is_running"] = False
                        task_state["current_task"] = None
            
            thread = threading.Thread(target=run_store, daemon=True)
            thread.start()
            self.send_json_response({"status": "success", "message": "Scraper de loja iniciado com sucesso!"})

        elif clean_path == "/api/login":
            if task_state["is_running"]:
                self.send_json_response({
                    "status": "busy",
                    "message": f"Já existe uma operação em andamento ({task_state['current_task']})."
                }, status_code=409)
                return

            body = self.read_json_body()
            headless = body.get("headless", True)
            email = body.get("email")
            password = body.get("password")

            # Update credentials if provided
            if email and password:
                config.save_credentials(email, password)

            def run_login():
                with task_lock:
                    task_state["is_running"] = True
                    task_state["current_task"] = "login"
                    task_state["started_at"] = datetime.datetime.now().isoformat()
                try:
                    res = setup_session.run_setup(headless=headless, email=email, password=password)
                    task_state["last_result"] = res
                except Exception as e:
                    task_state["last_result"] = {"success": False, "message": str(e)}
                finally:
                    with task_lock:
                        task_state["is_running"] = False
                        task_state["current_task"] = None

            # If headless=False (assisted login with browser UI), run in thread and respond
            thread = threading.Thread(target=run_login, daemon=True)
            thread.start()
            self.send_json_response({
                "status": "success",
                "message": "Processo de login iniciado! " + ("A janela do navegador foi aberta na sua tela." if not headless else "Autenticando em segundo plano...")
            })

        elif clean_path == "/api/check-session":
            if task_state["is_running"]:
                self.send_json_response({
                    "status": "busy",
                    "message": f"Sistema ocupado com: {task_state['current_task']}."
                }, status_code=409)
                return

            def run_check():
                with task_lock:
                    task_state["is_running"] = True
                    task_state["current_task"] = "check"
                try:
                    res = setup_session.check_session_validity(headless=True)
                    task_state["last_result"] = res
                finally:
                    with task_lock:
                        task_state["is_running"] = False
                        task_state["current_task"] = None

            thread = threading.Thread(target=run_check, daemon=True)
            thread.start()
            self.send_json_response({"status": "success", "message": "Verificação de sessão iniciada em segundo plano..."})

        elif clean_path == "/api/costs":
            body = self.read_json_body()
            res = self.save_costs_data(body)
            self.send_json_response(res)

        elif clean_path == "/api/sales-config":
            body = self.read_json_body()
            res = self.save_sales_config(body)
            self.send_json_response(res)

        elif clean_path == "/api/registered-stores":
            body = self.read_json_body()
            res = self.save_registered_stores_data(body)
            self.send_json_response(res)

        elif clean_path == "/api/save-credentials":
            body = self.read_json_body()
            email = body.get("email", "").strip()
            password = body.get("password", "").strip()

            if not email or not password:
                self.send_json_response({"status": "error", "message": "Email e senha são obrigatórios."}, status_code=400)
                return

            config.save_credentials(email, password)
            self.send_json_response({"status": "success", "message": "Credenciais atualizadas com sucesso!"})

        else:
            self.send_error(404, "Endpoint nao encontrado")

    def serve_file(self, file_path):
        try:
            content_type, _ = mimetypes.guess_type(str(file_path))
            if not content_type:
                content_type = "text/html"
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Erro ao ler arquivo: {e}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def send_json_response(self, data, status_code=200):
        content = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def get_session_status(self):
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
            except Exception:
                pass

        return {
            "cookies_exist": cookies_exist,
            "cookies_count": cookies_count,
            "last_cookie_update": last_modified,
            "email": email,
            "email_masked": mask_email(email),
            "task_state": {
                "is_running": task_state["is_running"],
                "current_task": task_state["current_task"],
                "last_result": task_state["last_result"]
            }
        }

    def get_latest_data(self):
        json_file = config.DATA_DIR / "collection_latest.json"
        if json_file.exists():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                return {"error": str(e)}
        return {"error": "Nenhum dado encontrado."}

    def get_cards_data(self):
        cards_file = config.DATA_DIR / "cards_latest.json"
        if cards_file.exists():
            try:
                with open(cards_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                return {"error": str(e)}
        return {"total_cards": 0, "cards": []}

    def get_store_cards_data(self):
        try:
            cards = database.get_all_store_cards()
            if cards:
                return {"total_cards": len(cards), "cards": cards}
        except Exception as e:
            print(f"Erro ao ler banco SQLite para store_cards: {e}")

        store_file = config.DATA_DIR / "store_cards_latest.json"
        if store_file.exists():
            try:
                with open(store_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                return {"error": str(e)}
        return {"total_cards": 0, "cards": []}

    def get_registered_stores_data(self):
        try:
            stores = database.get_registered_stores()
            return {"stores": stores}
        except Exception as e:
            print(f"Erro ao ler banco SQLite para lojas: {e}")
            
        if config.REGISTERED_STORES_FILE.exists():
            try:
                with open(config.REGISTERED_STORES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao ler registered_stores.json: {e}")
        return {"stores": []}

    def save_registered_stores_data(self, body):
        try:
            stores = body.get("stores", [])
            database.save_registered_stores(stores)
            return {"status": "success", "data": body}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_history_data(self):
        history_csv = config.DATA_DIR / "history_log.csv"
        history_records = []
        if history_csv.exists():
            try:
                with open(history_csv, "r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        history_records.append(row)
            except Exception as e:
                print(f"Erro ao ler historico: {e}")
        return history_records

    def get_costs_data(self):
        if config.COSTS_FILE.exists():
            try:
                with open(config.COSTS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao ler cards_costs.json: {e}")
        return {"cards_costs": {}, "total_collection_cost": None}

    def save_costs_data(self, body):
        current = self.get_costs_data()
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

    def get_card_history_data(self):
        if config.CARD_HISTORY_FILE.exists():
            try:
                with open(config.CARD_HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao ler cards_history.json: {e}")

        # If file doesn't exist, initialize 1 single history point (today) for all cards
        cards_payload = self.get_cards_data()
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
            print(f"Erro ao salvar cards_history.json inicial: {e}")

        return history_map

    def get_sales_config(self):
        if config.SALES_CONFIG_FILE.exists():
            try:
                with open(config.SALES_CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao ler sales_config.json: {e}")
        return {"sale_binder_ids": [], "updated_at": None}

    def save_sales_config(self, body):
        current = self.get_sales_config()
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

def start_server():
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("", PORT), DashboardHandler) as httpd:
        print(f"============================================================")
        print(f"   DASHBOARD LIGAPOKEMON RODANDO EM: http://localhost:{PORT}")
        print(f"============================================================")
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()
