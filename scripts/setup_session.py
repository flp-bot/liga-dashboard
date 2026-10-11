import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import time
import json
from playwright.sync_api import sync_playwright
import config
from logger import log_info, log_success, log_warning, log_error

def run_setup(headless=False, email=None, password=None):
    if not email or not password:
        saved_email, saved_pass = config.get_credentials()
        email = email or saved_email
        password = password or saved_pass

    print("=" * 60)
    print("      LIGAPOKEMON - CONFIGURAÇÃO DE SESSÃO / LOGIN")
    print("=" * 60)
    print(f"Utilizando email: {email}")
    print(f"Modo headless: {headless}")
    print("Iniciando navegador...")

    result = {"success": False, "message": "Iniciando processo..."}

    try:
        with sync_playwright() as p:
            # Launch persistent context to store cookies and site state
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(config.USER_DATA_DIR),
                headless=headless,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = context.pages[0] if context.pages else context.new_page()
            
            print(f"Navegando para: {config.LOGIN_URL}")
            try:
                page.goto(config.LOGIN_URL, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Aviso de navegação: {e}")
            
            # Pre-fill credentials if login fields are present
            try:
                if page.query_selector("input[name='lnick']"):
                    print("Preenchendo credenciais...")
                    page.fill("input[name='lnick']", email)
                    page.fill("input[name='lsenha']", password)
                    
                    print("Efetuando clique no botão de login...")
                    page.click("input[name='Login']")
                    page.wait_for_timeout(3000)
            except Exception as e:
                print(f"Nota na tentativa de auto-preenchimento: {e}")

            # Wait to verify if login succeeded or if manual captcha resolution is required
            print("\nVerificando autenticação...")
            max_wait = 75 if not headless else 25  # Mais tempo se a janela estiver visível para o usuário interagir
            logged_in = False
            
            start_time = time.time()
            while time.time() - start_time < max_wait:
                curr_url = page.url
                try:
                    body_text = page.inner_text("body")
                except Exception:
                    body_text = ""

                # Check URL and body
                if "view=colecao" in curr_url or ("Efetuar Login" not in body_text and "view=logar" not in curr_url and "logar_me" not in curr_url):
                    logged_in = True
                    break
                    
                time.sleep(2)
                
            # Test direct navigation to collection to confirm access
            print("Navegando para a página de coleções para validar a sessão...")
            try:
                page.goto(config.COLLECTION_URL, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2500)
                body_text = page.inner_text("body")
                if "Efetuar Login" not in body_text:
                    logged_in = True
                else:
                    logged_in = False
            except Exception as e:
                print(f"Erro ao testar colecao: {e}")
                
            if logged_in:
                print("\n[SUCESSO] Login autenticado com sucesso!")
                cookies = context.cookies()
                with open(config.COOKIES_FILE, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=2)
                print(f"Cookies salvos em: {config.COOKIES_FILE}")
                result = {"success": True, "message": "Login autenticado com sucesso e sessão salva!"}
            else:
                print("\n[ALERTA] Não foi possível confirmar a autenticação.")
                msg = "Não foi possível confirmar o login. Se houver Captcha na Liga, utilize a opção 'Conexão Assistida (Abrir Navegador)' para resolver."
                result = {"success": False, "message": msg}

            context.close()
            return result
    except Exception as e:
        print(f"Erro geral no setup de sessão: {e}")
        return {"success": False, "message": f"Erro durante o login: {str(e)}"}

def check_session_validity(headless=True):
    """Verifica de forma rápida e silenciosa se a sessão atual salva ainda tem acesso à coleção."""
    if not config.COOKIES_FILE.exists():
        return {"logged_in": False, "message": "Nenhum arquivo de sessão/cookies encontrado."}

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(config.USER_DATA_DIR),
                headless=headless,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            try:
                with open(config.COOKIES_FILE, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                    context.add_cookies(cookies)
            except Exception:
                pass

            page = context.pages[0] if context.pages else context.new_page()
            page.goto(config.COLLECTION_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            
            body_text = page.inner_text("body")
            curr_url = page.url
            
            is_logged = ("Efetuar Login" not in body_text) and ("view=logar" not in curr_url)
            
            if is_logged:
                # Refresh cookies file
                fresh_cookies = context.cookies()
                with open(config.COOKIES_FILE, "w", encoding="utf-8") as f:
                    json.dump(fresh_cookies, f, indent=2)

            context.close()
            
            if is_logged:
                return {"logged_in": True, "message": "Sessão válida e autenticada na Liga."}
            else:
                return {"logged_in": False, "message": "Sessão expirada. É necessário realizar login novamente."}
    except Exception as e:
        return {"logged_in": False, "message": f"Falha ao checar sessão: {str(e)}"}

if __name__ == "__main__":
    headless_flag = "--headless" in sys.argv
    if "--check" in sys.argv:
        res = check_session_validity(headless=headless_flag)
        print(json.dumps(res, indent=2))
    else:
        res = run_setup(headless=headless_flag)
        print(json.dumps(res, indent=2))
