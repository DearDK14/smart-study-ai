"""Unit tests for SQLite database layer and CRUD operations."""
import pytest
from database.connection import init_db, get_db_connection
from database.models import (
    DocumentModel,
    SummaryModel,
    QuestionModel,
    QuizModel,
    FlashcardModel,
    UserStatsModel,
)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_document_crud():
    doc_id = DocumentModel.create(
        filename="test_bio.pdf",
        filepath="uploads/test_bio.pdf",
        title="Cellular Biology",
        file_type="PDF",
        file_size=12000,
        page_count=3,
        word_count=500,
        extracted_text="Mitochondria generate ATP through oxidative phosphorylation.",
    )
    assert doc_id is not None

    doc = DocumentModel.get_by_id(doc_id)
    assert doc is not None
    assert doc["title"] == "Cellular Biology"
    assert "Mitochondria" in doc["extracted_text"]

def test_summary_crud():
    doc_id = DocumentModel.create(
        filename="test.txt",
        filepath="uploads/test.txt",
        title="Test Doc",
        file_type="TXT",
        file_size=100,
        page_count=1,
        word_count=20,
        extracted_text="Simple text for summarization testing.",
    )
    s_id = SummaryModel.create(
        document_id=doc_id,
        summary_type="executive",
        content="This is an executive summary.",
        key_takeaways="• Key takeaway 1\n• Key takeaway 2",
    )
    assert s_id is not None

    summaries = SummaryModel.get_by_document(doc_id)
    assert len(summaries) >= 1
    assert "executive summary" in summaries[0]["content"]

def test_flashcard_mastery():
    card_id = FlashcardModel.create(
        document_id=1,
        deck_name="Bio Deck",
        topic="Biochemistry",
        front_text="What is ATP?",
        back_text="Adenosine Triphosphate, energy currency of the cell.",
    )
    assert card_id is not None

    FlashcardModel.update_mastery(card_id, "mastered")
    cards = FlashcardModel.get_by_deck("Bio Deck")
    assert any(c["id"] == card_id and c["mastery_level"] == "mastered" for c in cards)

def test_user_stats_xp_accumulation():
    initial_stats = UserStatsModel.get()
    initial_xp = initial_stats.get("xp_total", 0)

    updated = UserStatsModel.add_xp(150)
    assert updated["xp_total"] == initial_xp + 150
