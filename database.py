import sqlite3

DB_NAME = "kasir.db"


# ================= CONNECT DATABASE =================
def connect():

    return sqlite3.connect(DB_NAME)


# ================= SETUP DATABASE =================
def setup_database():

    conn = connect()

    cur = conn.cursor()

    # ================= USERS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # ================= PRODUCTS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT,
        name TEXT,
        price INTEGER,
        stock INTEGER
    )
    """)

    # ================= TRANSACTIONS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total INTEGER,
        cash INTEGER,
        change INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ================= TRANSACTION ITEMS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transaction_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER,
        product_name TEXT,
        price INTEGER,
        qty INTEGER,
        subtotal INTEGER
    )
    """)

    # ================= HOLD TRANSACTION =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hold_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        items TEXT,
        total INTEGER
    )
    """)

    # ================= DEFAULT OWNER =================
    cur.execute("""
    INSERT OR IGNORE INTO users
    (
        id,
        username,
        password,
        role
    )
    VALUES
    (
        1,
        'admin',
        '123',
        'owner'
    )
    """)

    conn.commit()

    conn.close()