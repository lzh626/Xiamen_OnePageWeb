import sqlite3
from pathlib import Path

from config.settings import DB_PATH


INIT_SQL_PATH = Path(__file__).resolve().parent / "init.sql"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(force_reset: bool = False):
    if force_reset and DB_PATH.exists():
        DB_PATH.unlink()

    if DB_PATH.exists():
        return

    conn = get_db_connection()
    with INIT_SQL_PATH.open("r", encoding="utf-8") as sql_file:
        conn.executescript(sql_file.read())
    conn.commit()
    conn.close()


def reset_db():
    init_db(force_reset=True)
