import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import sqlite3
import json
from datetime import datetime
import config
from logger import log_info, log_success, log_error

DB_FILE = config.DATA_DIR / "liga_database.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Stores Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            last_scraped TEXT,
            cards_count INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)
        
        # Store Cards Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id TEXT,
            store_name TEXT,
            store_url TEXT,
            card_name TEXT NOT NULL,
            url TEXT,
            image_url TEXT,
            quantity INTEGER DEFAULT 0,
            price_brl REAL DEFAULT 0.0,
            scraped_at TEXT
        )
        """)
        
        # Seed initial store if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM stores")
        count = cursor.fetchone()["cnt"]
        if count == 0:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            INSERT INTO stores (id, name, url, enabled, last_scraped, cards_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("pacdeck", "PacDeck Store", "https://www.pacdeck.com.br/?view=ecom/itens&id=662762&page=1&tcg=2&txt_estoque=1&ultimas=1", 1, None, 0, now_str))

        conn.commit()
        conn.close()
    except Exception as e:
        log_error("Erro ao inicializar o banco de dados SQLite", exc=e)

def get_registered_stores():
    init_db()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stores ORDER BY created_at ASC")
        rows = cursor.fetchall()
        conn.close()
        
        stores = []
        for r in rows:
            stores.append({
                "id": r["id"],
                "name": r["name"],
                "url": r["url"],
                "enabled": bool(r["enabled"]),
                "last_scraped": r["last_scraped"],
                "cards_count": r["cards_count"]
            })
        return stores
    except Exception as e:
        log_error("Erro ao buscar lojas cadastradas no banco", exc=e)
        return []

def save_registered_stores(stores_list):
    init_db()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Clear existing stores and re-insert
        cursor.execute("DELETE FROM stores")
        for s in stores_list:
            s_id = s.get("id") or s.get("name", "loja").lower().replace(" ", "_")
            cursor.execute("""
            INSERT INTO stores (id, name, url, enabled, last_scraped, cards_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                s_id,
                s.get("name"),
                s.get("url"),
                1 if s.get("enabled", True) else 0,
                s.get("last_scraped"),
                s.get("cards_count", 0),
                now_str
            ))
            
        conn.commit()
        conn.close()
        log_success(f"{len(stores_list)} lojas cadastradas salvas no SQLite com sucesso!")
    except Exception as e:
        log_error("Erro ao salvar lojas no SQLite", exc=e)
        
    # Also sync to JSON backup file
    try:
        with open(config.REGISTERED_STORES_FILE, 'w', encoding='utf-8') as f:
            json.dump({"stores": stores_list}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_error("Erro ao sincronizar backup em JSON das lojas", exc=e)
        
    return stores_list

def save_store_cards(cards, store_id=None, store_name=None, store_url=None):
    init_db()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if store_id:
            cursor.execute("DELETE FROM store_cards WHERE store_id = ?", (store_id,))
        else:
            cursor.execute("DELETE FROM store_cards")

        for c in cards:
            cursor.execute("""
            INSERT INTO store_cards (store_id, store_name, store_url, card_name, url, image_url, quantity, price_brl, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                store_id or c.get("store_id") or "custom",
                store_name or c.get("store_name") or "Loja",
                store_url or c.get("store_url") or "",
                c.get("card_name"),
                c.get("url"),
                c.get("image_url"),
                c.get("quantity", 0),
                c.get("price_brl", 0.0),
                now_str
            ))

        # Update store last_scraped and cards_count in stores table
        if store_id:
            cursor.execute("""
            UPDATE stores SET last_scraped = ?, cards_count = ? WHERE id = ?
            """, (now_str, len(cards), store_id))

        conn.commit()
        conn.close()
        log_success(f"{len(cards)} cartas de loja salvas no SQLite!")
    except Exception as e:
        log_error("Erro ao salvar cartas de loja no banco", exc=e)

def get_all_store_cards():
    init_db()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM store_cards ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        
        cards = []
        for r in rows:
            cards.append({
                "id": r["id"],
                "store_id": r["store_id"],
                "store_name": r["store_name"],
                "store_url": r["store_url"],
                "card_name": r["card_name"],
                "url": r["url"],
                "image_url": r["image_url"],
                "quantity": r["quantity"],
                "price_brl": r["price_brl"],
                "scraped_at": r["scraped_at"]
            })
        return cards
    except Exception as e:
        log_error("Erro ao buscar cartas de loja salvas no banco", exc=e)
        return []

if __name__ == '__main__':
    init_db()
    log_success("Banco de dados SQLite (liga_database.db) inicializado com sucesso!")
    log_info(f"Lojas cadastradas: {get_registered_stores()}")

