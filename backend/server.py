import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import http.server
import socketserver
import json
import csv
import subprocess
import threading
import mimetypes
import datetime
import config
import scripts.setup_session as setup_session
import database
import services
from logger import log_info, log_success, log_warning, log_error

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

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def read_json_body(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                raw = self.rfile.read(content_length).decode('utf-8')
                return json.loads(raw)
        except Exception as e:
            log_error(f"Erro ao ler corpo JSON: {e}")
        return {}

    def do_GET(self):
        raw_path = self.path
        clean_path = raw_path.split('?')[0]
        if clean_path.endswith('/') and len(clean_path) > 1:
            clean_path = clean_path[:-1]

        if clean_path == "/api/latest":
            self.send_json_response(services.get_latest_data())
        elif clean_path == "/api/history":
            self.send_json_response(services.get_history_data())
        elif clean_path == "/api/cards":
            self.send_json_response(services.get_cards_data())
        elif clean_path == "/api/costs":
            self.send_json_response(services.get_costs_data())
        elif clean_path == "/api/card-history":
            self.send_json_response(services.get_card_history_data())
        elif clean_path == "/api/session-status":
            self.send_json_response(services.get_session_status(task_state))
        elif clean_path == "/api/sales-config":
            self.send_json_response(services.get_sales_config())
        elif clean_path == "/api/store-cards":
            self.send_json_response(services.get_store_cards_data())
        elif clean_path == "/api/registered-stores":
            self.send_json_response(services.get_registered_stores_data())
        elif clean_path in ["/stores", "/stores.html", "/lojas", "/lojas.html"]:
            self.serve_file(config.FRONTEND_DIR / "stores.html")
        elif clean_path in ["/sales", "/sales.html", "/vendas", "/vendas.html"]:
            self.serve_file(config.FRONTEND_DIR / "sales.html")
        elif clean_path in ["/collections", "/collections.html", "/colecoes"]:
            self.serve_file(config.FRONTEND_DIR / "collections.html")
        elif clean_path in ["/dashboard", "/dashboard.html", "/index.html", "/"]:
            self.serve_file(config.FRONTEND_DIR / "dashboard.html")
        else:
            rel_path = clean_path.lstrip('/')
            frontend_file = config.FRONTEND_DIR / rel_path
            root_file = config.BASE_DIR / rel_path
            data_file = config.DATA_DIR / rel_path
            if frontend_file.exists() and frontend_file.is_file():
                self.serve_file(frontend_file)
            elif root_file.exists() and root_file.is_file():
                self.serve_file(root_file)
            elif data_file.exists() and data_file.is_file():
                self.serve_file(data_file)
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
                    subprocess.run(["python", str(config.BACKEND_DIR / "scraper.py")])
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
                    cmd = ["python", str(config.BACKEND_DIR / "store_scraper.py")]
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
            res = services.save_costs_data(body)
            self.send_json_response(res)

        elif clean_path == "/api/sales-config":
            body = self.read_json_body()
            res = services.save_sales_config(body)
            self.send_json_response(res)

        elif clean_path == "/api/registered-stores":
            body = self.read_json_body()
            res = services.save_registered_stores_data(body)
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

def start_server():
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("", PORT), DashboardHandler) as httpd:
        log_info("============================================================")
        log_info(f"   DASHBOARD LIGAPOKEMON RODANDO EM: http://localhost:{PORT}")
        log_info("============================================================")
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()

