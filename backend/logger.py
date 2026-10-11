import logging
import sys
import io
from pathlib import Path
import config

# Logger setup
LOGGER_NAME = "LigaDashboard"
log_file = config.DATA_DIR / "app.log"

def setup_logger():
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # File Handler (UTF-8)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler (reconfigured UTF-8 stream for Windows compatibility)
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        stream = sys.stdout
    except Exception:
        stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    console_handler = logging.StreamHandler(stream)
    console_formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

def log_info(msg):
    logger.info(f"[INFO] {msg}")

def log_success(msg):
    logger.info(f"[OK] {msg}")

def log_warning(msg):
    logger.warning(f"[AVISO] {msg}")

def log_error(msg, exc=None):
    if exc:
        logger.error(f"[ERRO] {msg} - Detalhes: {exc}", exc_info=True)
    else:
        logger.error(f"[ERRO] {msg}")

