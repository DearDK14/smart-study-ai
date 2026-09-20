"""Data models and CRUD operations for Smart Study AI."""
import json
from datetime import datetime
from database.connection import get_db_connection

class DocumentModel:
    @staticmethod
    def create(filename, filepath, title, file_type, file_size, page_count, word_count, extracted_text, user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (filename, filepath, title, file_type, file_size, page_count, word_count, extracted_text, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (filename, str(filepath), title, file_type, file_size, page_count, word_count, extracted_text, user_id),
        )
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id

    @staticmethod
    def get_all(user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute("SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        else:
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
    def create(document_id, summary_type, content, key_takeaways="", user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO summaries (document_id, summary_type, content, key_takeaways, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (document_id, summary_type, content, key_takeaways, user_id),
        )
        summary_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return summary_id

    @staticmethod
    def get_by_document(document_id, user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute(
                "SELECT * FROM summaries WHERE document_id = ? AND user_id = ? ORDER BY created_at DESC",
                (document_id, user_id),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM summaries WHERE document_id = ? ORDER BY created_at DESC",
                (document_id,),
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_all(user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute(
                """
                SELECT s.*, d.title as doc_title 
                FROM summaries s 
                LEFT JOIN documents d ON s.document_id = d.id 
                WHERE s.user_id = ?
                ORDER BY s.created_at DESC
                """,
                (user_id,),
            ).fetchall()
        else:
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
    def create(document_id, topic, question_text, option_a, option_b, option_c, option_d, correct_option, explanation="", difficulty="Medium", user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO questions (document_id, topic, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (document_id, topic, question_text, option_a, option_b, option_c, option_d, correct_option.upper(), explanation, difficulty, user_id),
        )
        q_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return q_id

    @staticmethod
    def bulk_create(questions_list, user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        ids = []
        for q in questions_list:
            uid = q.get("user_id", user_id)
            cursor.execute(
                """
                INSERT INTO questions (document_id, topic, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    uid,
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
    def get_all(user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute("SELECT * FROM questions WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM questions ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]


class QuizModel:
    @staticmethod
    def create(title, document_id, question_ids, user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quizzes (title, document_id, question_ids_json, total_questions, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, document_id, json.dumps(question_ids), len(question_ids), user_id),
        )
        quiz_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return quiz_id

    @staticmethod
    def get_all(user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute(
                """
                SELECT q.*, d.title as doc_title 
                FROM quizzes q 
                LEFT JOIN documents d ON q.document_id = d.id 
                WHERE q.user_id = ?
                ORDER BY q.created_at DESC
                """,
                (user_id,),
            ).fetchall()
        else:
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
    def record_attempt(quiz_id, score, total_questions, answers, weak_topics, xp_earned, user_id=None):
        percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0.0
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_attempts (quiz_id, score, total_questions, percentage, answers_json, weak_topics_json, xp_earned, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (quiz_id, score, total_questions, percentage, json.dumps(answers), json.dumps(weak_topics), xp_earned, user_id),
        )
        attempt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return attempt_id

    @staticmethod
    def get_all(user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute("SELECT * FROM quiz_attempts WHERE user_id = ? ORDER BY completed_at DESC", (user_id,)).fetchall()
        else:
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
    def create(document_id, deck_name, topic, front_text, back_text, user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO flashcards (document_id, deck_name, topic, front_text, back_text, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (document_id, deck_name, topic, front_text, back_text, user_id),
        )
        card_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return card_id

    @staticmethod
    def bulk_create(cards_list, user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        ids = []
        for c in cards_list:
            uid = c.get("user_id", user_id)
            cursor.execute(
                """
                INSERT INTO flashcards (document_id, deck_name, topic, front_text, back_text, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (c.get("document_id"), c.get("deck_name", "General"), c.get("topic", "General"), c.get("front_text"), c.get("back_text"), uid),
            )
            ids.append(cursor.lastrowid)
        conn.commit()
        conn.close()
        return ids

    @staticmethod
    def get_decks(user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute(
                """
                SELECT deck_name, COUNT(*) as card_count, 
                       SUM(CASE WHEN mastery_level = 'mastered' THEN 1 ELSE 0 END) as mastered_count
                FROM flashcards 
                WHERE user_id = ?
                GROUP BY deck_name
                """,
                (user_id,),
            ).fetchall()
        else:
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
    def get_by_deck(deck_name, user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute("SELECT * FROM flashcards WHERE deck_name = ? AND user_id = ? ORDER BY id ASC", (deck_name, user_id)).fetchall()
        else:
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
    def get_all(user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute("SELECT * FROM flashcards WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM flashcards ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]


class UserStatsModel:
    @staticmethod
    def get(user_id=None):
        conn = get_db_connection()
        try:
            # Treat 0 or None as general/guest
            if user_id is not None and user_id != 0:
                row = conn.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
                if row:
                    return dict(row)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO user_stats (user_id, xp_total, level, streak_days, gems, tasks_pending, focus_minutes_total, last_active_date)
                    VALUES (?, 0, 1, 0, 0, 0, 0, DATE('now'))
                    """,
                    (user_id,),
                )
                conn.commit()
                new_row = conn.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
                return dict(new_row) if new_row else {"user_id": user_id, "xp_total": 0, "level": 1, "streak_days": 0, "gems": 0, "tasks_pending": 0, "focus_minutes_total": 0}
            else:
                row = conn.execute("SELECT * FROM user_stats WHERE user_id IS NULL OR user_id = 0 LIMIT 1").fetchone()
                if row:
                    return dict(row)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO user_stats (user_id, xp_total, level, streak_days, gems, tasks_pending, focus_minutes_total, last_active_date)
                    VALUES (NULL, 0, 1, 0, 0, 0, 0, DATE('now'))
                    """
                )
                conn.commit()
                return {
                    "id": cursor.lastrowid,
                    "user_id": None,
                    "xp_total": 0,
                    "level": 1,
                    "streak_days": 0,
                    "gems": 0,
                    "tasks_pending": 0,
                    "focus_minutes_total": 0,
                }
        finally:
            conn.close()

    @staticmethod
    def add_xp(xp_to_add, user_id=None):
        stats = UserStatsModel.get(user_id=user_id)
        new_xp = stats.get("xp_total", 0) + xp_to_add
        new_level = max(1, (new_xp // 1000) + 1)
        
        conn = get_db_connection()
        try:
            if user_id is not None and user_id != 0:
                conn.execute(
                    "UPDATE user_stats SET xp_total = ?, level = ? WHERE user_id = ?",
                    (new_xp, new_level, user_id),
                )
            else:
                stat_id = stats.get("id")
                if stat_id:
                    conn.execute(
                        "UPDATE user_stats SET xp_total = ?, level = ? WHERE id = ?",
                        (new_xp, new_level, stat_id),
                    )
                else:
                    conn.execute(
                        "UPDATE user_stats SET xp_total = ?, level = ? WHERE user_id IS NULL OR user_id = 0 OR rowid = 1",
                        (new_xp, new_level),
                    )
            conn.commit()
            return {"xp_total": new_xp, "level": new_level}
        finally:
            conn.close()


class NoteModel:
    @staticmethod
    def create(title, content, tags="General", document_id=None, user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notebook (title, content, tags, document_id, user_id) VALUES (?, ?, ?, ?, ?)",
            (title, content, tags, document_id, user_id),
        )
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return note_id

    @staticmethod
    def get_all(user_id=None):
        conn = get_db_connection()
        if user_id is not None:
            rows = conn.execute("SELECT * FROM notebook WHERE user_id = ? ORDER BY updated_at DESC", (user_id,)).fetchall()
        else:
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
            # Initialize clean zero-stat row for new user
            UserStatsModel.get(user_id=user_id)
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
        try:
            count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if count == 0:
                res = UserModel.create_user("Tan", "tan", "tan@studyforge.ai", "password123")
                if res.get("success"):
                    UserStatsModel.get(user_id=res["user_id"])
        finally:
            conn.close()
