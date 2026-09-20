"""Database connection management for SQLite."""
import sqlite3
from pathlib import Path
from config.settings import DATABASE_PATH, BASE_DIR

def get_db_connection():
    """Returns a SQLite connection with dict-like row access."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes the database using schema.sql."""
    schema_file = BASE_DIR / "database" / "schema.sql"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found at {schema_file}")
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection()
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()

    try:
        from database.models import UserModel
        UserModel.seed_default_user()
    except Exception:
        pass

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DATABASE_PATH)
