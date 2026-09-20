"""Data models and CRUD operations for Smart Study AI."""
import json
from datetime import datetime
from database.connection import get_db_connection

class DocumentModel:
    @staticmethod
    def create(filename, filepath, title, file_type, file_size, page_count, word_count, extracted_text):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (filename, filepath, title, file_type, file_size, page_count, word_count, extracted_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (filename, str(filepath), title, file_type, file_size, page_count, word_count, extracted_text),
        )
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(doc_id):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def delete(doc_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()


class SummaryModel:
    @staticmethod
    def create(document_id, summary_type, content, key_takeaways=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO summaries (document_id, summary_type, content, key_takeaways)
            VALUES (?, ?, ?, ?)
            """,
            (document_id, summary_type, content, key_takeaways),
        )
        summary_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return summary_id

    @staticmethod
    def get_by_document(document_id):
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM summaries WHERE document_id = ? ORDER BY created_at DESC",
            (document_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT s.*, d.title as doc_title 
            FROM summaries s 
            LEFT JOIN documents d ON s.document_id = d.id 
            ORDER BY s.created_at DESC
            """
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class QuestionModel:
    @staticmethod
    def create(document_id, topic, question_text, option_a, option_b, option_c, option_d, correct_option, explanation="", difficulty="Medium"):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO questions (document_id, topic, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (document_id, topic, question_text, option_a, option_b, option_c, option_d, correct_option.upper(), explanation, difficulty),
        )
        q_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return q_id

    @staticmethod
    def bulk_create(questions_list):
        conn = get_db_connection()
        cursor = conn.cursor()
        ids = []
        for q in questions_list:
            cursor.execute(
                """
                INSERT INTO questions (document_id, topic, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    q.get("document_id"),
                    q.get("topic", "General"),
                    q.get("question_text"),
                    q.get("option_a"),
                    q.get("option_b"),
                    q.get("option_c"),
                    q.get("option_d"),
                    q.get("correct_option", "A").upper(),
                    q.get("explanation", ""),
                    q.get("difficulty", "Medium"),
                ),
            )
            ids.append(cursor.lastrowid)
        conn.commit()
        conn.close()
        return ids

    @staticmethod
    def get_by_document(document_id):
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM questions WHERE document_id = ? ORDER BY id ASC", (document_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_ids(id_list):
        if not id_list:
            return []
        placeholders = ",".join("?" for _ in id_list)
        conn = get_db_connection()
        rows = conn.execute(f"SELECT * FROM questions WHERE id IN ({placeholders})", tuple(id_list)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM questions ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]


class QuizModel:
    @staticmethod
    def create(title, document_id, question_ids):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quizzes (title, document_id, question_ids_json, total_questions)
            VALUES (?, ?, ?, ?)
            """,
            (title, document_id, json.dumps(question_ids), len(question_ids)),
        )
        quiz_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return quiz_id

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT q.*, d.title as doc_title 
            FROM quizzes q 
            LEFT JOIN documents d ON q.document_id = d.id 
            ORDER BY q.created_at DESC
            """
        ).fetchall()
        conn.close()
        result = []
        for r in rows:
            d = dict(r)
            d["question_ids"] = json.loads(d["question_ids_json"]) if d["question_ids_json"] else []
            result.append(d)
        return result

    @staticmethod
    def get_by_id(quiz_id):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        d["question_ids"] = json.loads(d["question_ids_json"]) if d["question_ids_json"] else []
        return d


class QuizAttemptModel:
    @staticmethod
    def record_attempt(quiz_id, score, total_questions, answers, weak_topics, xp_earned):
        percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0.0
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_attempts (quiz_id, score, total_questions, percentage, answers_json, weak_topics_json, xp_earned)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (quiz_id, score, total_questions, percentage, json.dumps(answers), json.dumps(weak_topics), xp_earned),
        )
        attempt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return attempt_id

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM quiz_attempts ORDER BY completed_at DESC").fetchall()
        conn.close()
        results = []
        for r in rows:
            d = dict(r)
            d["answers"] = json.loads(d["answers_json"]) if d["answers_json"] else []
            d["weak_topics"] = json.loads(d["weak_topics_json"]) if d["weak_topics_json"] else []
            results.append(d)
        return results


class FlashcardModel:
    @staticmethod
    def create(document_id, deck_name, topic, front_text, back_text):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO flashcards (document_id, deck_name, topic, front_text, back_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (document_id, deck_name, topic, front_text, back_text),
        )
        card_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return card_id

    @staticmethod
    def bulk_create(cards_list):
        conn = get_db_connection()
        cursor = conn.cursor()
        ids = []
        for c in cards_list:
            cursor.execute(
                """
                INSERT INTO flashcards (document_id, deck_name, topic, front_text, back_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (c.get("document_id"), c.get("deck_name", "General"), c.get("topic", "General"), c.get("front_text"), c.get("back_text")),
            )
            ids.append(cursor.lastrowid)
        conn.commit()
        conn.close()
        return ids

    @staticmethod
    def get_decks():
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT deck_name, COUNT(*) as card_count, 
                   SUM(CASE WHEN mastery_level = 'mastered' THEN 1 ELSE 0 END) as mastered_count
            FROM flashcards 
            GROUP BY deck_name
            """
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_deck(deck_name):
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM flashcards WHERE deck_name = ? ORDER BY id ASC", (deck_name,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update_mastery(card_id, mastery_level):
        conn = get_db_connection()
        conn.execute(
            "UPDATE flashcards SET mastery_level = ?, reviews_count = reviews_count + 1 WHERE id = ?",
            (mastery_level, card_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM flashcards ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]


class UserStatsModel:
    @staticmethod
    def get():
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM user_stats WHERE id = 1").fetchone()
        conn.close()
        return dict(row) if row else {
            "id": 1,
            "xp_total": 11735,
            "level": 11,
            "streak_days": 1,
            "gems": 250,
            "tasks_pending": 1,
            "focus_minutes_total": 120,
        }

    @staticmethod
    def add_xp(xp_to_add):
        stats = UserStatsModel.get()
        new_xp = stats.get("xp_total", 0) + xp_to_add
        # Level formula: Level 1 starts at 0, each level requires 1000 XP
        new_level = max(1, (new_xp // 1000) + 1)
        conn = get_db_connection()
        conn.execute(
            "UPDATE user_stats SET xp_total = ?, level = ? WHERE id = 1",
            (new_xp, new_level),
        )
        conn.commit()
        conn.close()
        return {"xp_total": new_xp, "level": new_level}


class NoteModel:
    @staticmethod
    def create(title, content, tags="General", document_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notebook (title, content, tags, document_id) VALUES (?, ?, ?, ?)",
            (title, content, tags, document_id),
        )
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return note_id

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM notebook ORDER BY updated_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def delete(note_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM notebook WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()


class UserModel:
    @staticmethod
    def _hash_password(password: str) -> str:
        import hashlib
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def create_user(name: str, username: str, email: str, password: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        pwd_hash = UserModel._hash_password(password)
        try:
            cursor.execute(
                """
                INSERT INTO users (name, username, email, password_hash)
                VALUES (?, ?, ?, ?)
                """,
                (name.strip(), username.strip().lower(), email.strip().lower(), pwd_hash),
            )
            user_id = cursor.lastrowid
            conn.commit()
            return {"success": True, "user_id": user_id, "name": name, "username": username}
        except Exception as e:
            err = str(e)
            if "UNIQUE constraint failed" in err:
                if "username" in err:
                    return {"success": False, "error": "Username is already registered."}
                elif "email" in err:
                    return {"success": False, "error": "Email is already registered."}
            return {"success": False, "error": f"Failed to register user: {err}"}
        finally:
            conn.close()

    @staticmethod
    def authenticate(username_or_email: str, password: str):
        conn = get_db_connection()
        ident = username_or_email.strip().lower()
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (ident, ident),
        ).fetchone()
        conn.close()

        if not row:
            return {"success": False, "error": "User account not found."}

        pwd_hash = UserModel._hash_password(password)
        if row["password_hash"] != pwd_hash:
            return {"success": False, "error": "Invalid password."}

        return {
            "success": True,
            "user": {
                "id": row["id"],
                "name": row["name"],
                "username": row["username"],
                "email": row["email"],
            },
        }

    @staticmethod
    def seed_default_user():
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()
        if count == 0:
            UserModel.create_user("Tan", "tan", "tan@studyforge.ai", "password123")

