import sqlite3

DB_PATH = "rates.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency TEXT NOT NULL,
            date TEXT NOT NULL,
            rate REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_cached_rate(currency: str, date: str) -> float | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT rate FROM exchange_rates WHERE currency = ? AND date = ?",
        (currency, date)
    )
    row = cursor.fetchone()
    conn.close()
    return row["rate"] if row else None


def store_rate(currency: str, date: str, rate: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO exchange_rates (currency, date, rate) VALUES (?, ?, ?)",
        (currency, date, rate)
    )
    conn.commit()
    conn.close()