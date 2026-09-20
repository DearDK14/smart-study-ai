"""Tests for User Data Isolation and the Full Auto-Pipeline."""
import pytest
from database.connection import init_db, get_db_connection
from database.models import (
    UserModel,
    DocumentModel,
    SummaryModel,
    QuizModel,
    FlashcardModel,
    NoteModel,
    UserStatsModel,
)
from services.summary_service import SummaryService
from services.question_service import QuestionService
from services.flashcard_service import FlashcardService

@pytest.fixture(autouse=True)
def setup_test_users():
    init_db()
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE username IN ('user_alpha', 'user_beta')")
    conn.execute("DELETE FROM documents WHERE title LIKE 'Test Pipeline%'")
    conn.commit()
    conn.close()

def test_new_user_empty_state():
    """Verify that a brand new account has zero data and zero XP."""
    res = UserModel.create_user("User Alpha", "user_alpha", "alpha@example.com", "pass123")
    assert res["success"] is True
    uid = res["user_id"]

    # All counts must be 0 for this new user
    assert len(DocumentModel.get_all(user_id=uid)) == 0
    assert len(SummaryModel.get_all(user_id=uid)) == 0
    assert len(QuizModel.get_all(user_id=uid)) == 0
    assert len(FlashcardModel.get_all(user_id=uid)) == 0
    assert len(FlashcardModel.get_decks(user_id=uid)) == 0
    assert len(NoteModel.get_all(user_id=uid)) == 0

    stats = UserStatsModel.get(user_id=uid)
    assert stats["xp_total"] == 0
    assert stats["level"] == 1

def test_auto_pipeline_and_user_isolation():
    """Verify single document upload powers summary, questions, quiz, flashcards, and remains isolated."""
    # User Alpha
    res_a = UserModel.create_user("User Alpha", "user_alpha", "alpha@example.com", "pass123")
    uid_a = res_a["user_id"]

    # User Beta
    res_b = UserModel.create_user("User Beta", "user_beta", "beta@example.com", "pass123")
    uid_b = res_b["user_id"]

    # User Alpha uploads a document
    doc_id = DocumentModel.create(
        filename="bio_notes.pdf",
        filepath="uploads/bio_notes.pdf",
        title="Test Pipeline Bio",
        file_type="PDF",
        file_size=5000,
        page_count=2,
        word_count=120,
        extracted_text="Cell theory states that all biological organisms are composed of cells. Cells are the fundamental unit of life.",
        user_id=uid_a,
    )

    # Pipeline Step 1: Summary
    sum_res = SummaryService.generate_and_save(doc_id, summary_type="executive", user_id=uid_a)
    assert sum_res["success"] is True

    # Pipeline Step 2: Questions & Quiz
    q_res = QuestionService.generate_questions_for_document(doc_id, count=3, user_id=uid_a)
    assert q_res["success"] is True

    # Pipeline Step 3: Flashcards
    fc_res = FlashcardService.generate_flashcards_for_document(doc_id, deck_name="Test Pipeline Deck", count=3, user_id=uid_a)
    assert fc_res["success"] is True

    # Check User Alpha sees their data
    docs_a = DocumentModel.get_all(user_id=uid_a)
    assert len(docs_a) == 1
    assert docs_a[0]["title"] == "Test Pipeline Bio"

    summaries_a = SummaryModel.get_all(user_id=uid_a)
    assert len(summaries_a) == 1

    quizzes_a = QuizModel.get_all(user_id=uid_a)
    assert len(quizzes_a) == 1

    decks_a = FlashcardModel.get_decks(user_id=uid_a)
    assert len(decks_a) == 1

    stats_a = UserStatsModel.get(user_id=uid_a)
    assert stats_a["xp_total"] > 0

    # User Beta should have ZERO documents, ZERO summaries, ZERO quizzes, ZERO flashcards!
    assert len(DocumentModel.get_all(user_id=uid_b)) == 0
    assert len(SummaryModel.get_all(user_id=uid_b)) == 0
    assert len(QuizModel.get_all(user_id=uid_b)) == 0
    assert len(FlashcardModel.get_all(user_id=uid_b)) == 0
    assert len(FlashcardModel.get_decks(user_id=uid_b)) == 0

    stats_b = UserStatsModel.get(user_id=uid_b)
    assert stats_b["xp_total"] == 0
    assert stats_b["level"] == 1
