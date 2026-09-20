"""Database connection management for SQLite."""
import sqlite3
from pathlib import Path
from config.settings import DATABASE_PATH, BASE_DIR

def get_db_connection():
    """Returns a SQLite connection with dict-like row access and generous timeout."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database using schema.sql and applies any migrations."""
    schema_file = BASE_DIR / "database" / "schema.sql"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found at {schema_file}")
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection()
    try:
        # 1. Check if user_stats has the legacy CHECK (id = 1) constraint
        try:
            tbl_info = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_stats'").fetchone()
            if tbl_info and tbl_info[0] and "CHECK" in tbl_info[0]:
                conn.execute("DROP TABLE IF EXISTS user_stats")
                conn.commit()
        except Exception:
            pass

        # 2. Run standard schema script
        conn.executescript(schema_sql)
        conn.commit()

        # 3. Automatic column migration: ensure user_id column exists on all content tables
        tables_to_check = [
            "documents",
            "summaries",
            "questions",
            "quizzes",
            "quiz_attempts",
            "flashcards",
            "notebook",
            "user_stats",
        ]
        for tbl in tables_to_check:
            try:
                cols = [row["name"] for row in conn.execute(f"PRAGMA table_info({tbl})").fetchall()]
                if "user_id" not in cols:
                    conn.execute(f"ALTER TABLE {tbl} ADD COLUMN user_id INTEGER;")
                    conn.commit()
            except Exception:
                pass

    finally:
        conn.close()

    try:
        from database.models import UserModel
        UserModel.seed_default_user()
    except Exception:
        pass

def clear_all_study_data():
    """Cleans all content data while preserving registered user accounts."""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM quiz_attempts")
        conn.execute("DELETE FROM quizzes")
        conn.execute("DELETE FROM questions")
        conn.execute("DELETE FROM summaries")
        conn.execute("DELETE FROM flashcards")
        conn.execute("DELETE FROM notebook")
        conn.execute("DELETE FROM documents")
        conn.execute("UPDATE user_stats SET xp_total = 0, level = 1, streak_days = 0, gems = 0, tasks_pending = 0, focus_minutes_total = 0")
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DATABASE_PATH)
