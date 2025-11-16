import sqlite3
import pandas as pd

class UserProfileManager:
    def __init__(self, db_name="users.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                risk_tolerance REAL,
                preferred_assets TEXT,
                created_at TEXT
            )
        """)
        self.conn.commit()

    def create_user(self, username, risk_tolerance=0.1, preferred_assets=''):
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO users (username, risk_tolerance, preferred_assets, created_at) VALUES (?, ?, ?, ?)",
            (username, risk_tolerance, preferred_assets, pd.Timestamp.now()))
        self.conn.commit()

    def get_user(self, username):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if not row:
            return None
        return dict(zip([desc[0] for desc in c.description], row))

    def set_preference(self, username, risk_tolerance=None, preferred_assets=None):
        c = self.conn.cursor()
        if risk_tolerance is not None:
            c.execute("UPDATE users SET risk_tolerance = ? WHERE username = ?", (risk_tolerance, username))
        if preferred_assets is not None:
            c.execute("UPDATE users SET preferred_assets = ? WHERE username = ?", (preferred_assets, username))
        self.conn.commit()