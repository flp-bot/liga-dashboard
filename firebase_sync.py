import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
import config

sys.stdout.reconfigure(encoding='utf-8')

# Firebase RTDB URL (desativado por padrão pois o dashboard utiliza Firebase Hosting com JSONs estáticos)
FIREBASE_RTDB_URL = None

def send_to_firebase(path_suffix, data):
    if not FIREBASE_RTDB_URL:
        return False
    url = f"{FIREBASE_RTDB_URL}/{path_suffix.lstrip('/')}.json"
    json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=json_bytes,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='PUT'
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"[FIREBASE SYNC ERROR] Failed to send {path_suffix}: {e}")
        return False

def sync_all_to_firebase():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 60)
    print(f"      SINCRONIZANDO DADOS COM FIREBASE CLOUD [{now_str}]")
    print("=" * 60)
    
    # 1. Preparar status de sincronização
    status_payload = {
        "app": "LigaPokemon Dashboard",
        "last_sync": now_str,
        "sync_status": "success",
        "hosting_url": "https://ligapokemon-dashboard.web.app"
    }
    sync_status_file = config.DATA_DIR / "sync_status.json"
    try:
        with open(sync_status_file, "w", encoding="utf-8") as f:
            json.dump(status_payload, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"  [AVISO] Falha ao salvar sync_status.json: {e}")

    # 2. Se um RTDB customizado estiver configurado, envia para ele
    if FIREBASE_RTDB_URL:
        for suffix, file_path in [
            ("latest", config.DATA_DIR / "collection_latest.json"),
            ("cards", config.DATA_DIR / "cards_latest.json"),
            ("costs", config.COSTS_FILE),
            ("sales_config", config.SALES_CONFIG_FILE),
            ("card_history", config.CARD_HISTORY_FILE),
            ("registered_stores", config.REGISTERED_STORES_FILE),
            ("store_cards", config.DATA_DIR / "store_cards_latest.json")
        ]:
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        d = json.load(f)
                        send_to_firebase(suffix, d)
                except Exception:
                    pass
        send_to_firebase("status", status_payload)

    # 3. Gerar arquivos estáticos adicionais para Firebase Hosting
    try:
        import csv
        history_csv = config.DATA_DIR / "history_log.csv"
        history_json_file = config.DATA_DIR / "history_log.json"
        if history_csv.exists():
            records = []
            with open(history_csv, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
            with open(history_json_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)

        session_json_file = config.DATA_DIR / "session_status.json"
        session_data = {
            "cookies_exist": True,
            "cookies_count": 6,
            "last_cookie_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "email": "fe0rkut@gmail.com",
            "email_masked": "fe***t@gmail.com",
            "task_state": {
                "is_running": False,
                "current_task": None,
                "last_result": None
            }
        }
        with open(session_json_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        print("  [OK] Arquivos estáticos de dados preparados!")
    except Exception as e:
        print(f"  [AVISO] Erro ao preparar JSONs estáticos: {e}")

    # 4. Deploy to Firebase Hosting so the web app is live online
    print("  [DEPLOY] Enviando atualizações para o Firebase Hosting (https://ligapokemon-dashboard.web.app)...")
    try:
        import subprocess
        res = subprocess.run(["npx.cmd" if subprocess.os.name == 'nt' else "npx", "firebase", "deploy", "--only", "hosting", "--project", "ligapokemon-dashboard"], capture_output=True, text=True)
        if res.returncode == 0:
            print("  [OK] Firebase Hosting atualizado com sucesso!")
            print("  Acesse online em: https://ligapokemon-dashboard.web.app")
        else:
            print(f"  [AVISO] Deploy hosting retornou erro: {res.stderr[:200]}")
    except Exception as e:
        print(f"  [ERRO] Falha ao rodar firebase deploy: {e}")

    print("=" * 60)
    print(f"Sincronização Firebase concluída! Acesse: https://ligapokemon-dashboard.web.app")
    print("=" * 60)
    return True

if __name__ == "__main__":
    sync_all_to_firebase()
