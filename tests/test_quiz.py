"""Unit tests for Quiz evaluation and Weak Topic analytics engine."""
import pytest
from database.connection import init_db
from database.models import DocumentModel, QuestionModel, QuizModel
from services.question_service import QuestionService

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_quiz_evaluation_and_weak_topic_detection():
    # 1. Create a dummy document
    doc_id = DocumentModel.create(
        filename="genetics.txt",
        filepath="uploads/genetics.txt",
        title="Genetics 101",
        file_type="TXT",
        file_size=200,
        page_count=1,
        word_count=50,
        extracted_text="Genetics involves DNA replication, transcription, and translation.",
    )

    # 2. Insert questions for two distinct topics:
    # Topic A: "Replication" (will get 100% correct)
    # Topic B: "Translation" (will get 0% correct -> should be flagged as weak!)
    q1_id = QuestionModel.create(
        document_id=doc_id,
        topic="Replication",
        question_text="Which enzyme unzips DNA?",
        option_a="Helicase",
        option_b="Polymerase",
        option_c="Ligase",
        option_d="Primase",
        correct_option="A",
    )
    q2_id = QuestionModel.create(
        document_id=doc_id,
        topic="Translation",
        question_text="Where does translation occur?",
        option_a="Nucleus",
        option_b="Ribosome",
        option_c="Lysosome",
        option_d="Vacuole",
        correct_option="B",
    )

    # 3. Create a Quiz
    quiz_id = QuizModel.create("Genetics Exam", doc_id, [q1_id, q2_id])

    # 4. User submits answers: Correct for Q1 ('A'), Incorrect for Q2 ('C')
    user_answers = {
        q1_id: "A", # Correct
        q2_id: "C", # Wrong (Correct is B)
    }

    result = QuestionService.evaluate_quiz_submission(quiz_id, user_answers)

    assert result["success"] is True
    assert result["score"] == 1
    assert result["total_questions"] == 2
    assert result["percentage"] == 50.0

    # Topic A should be 100%
    assert result["topic_accuracy"]["Replication"] == 100.0
    # Topic B should be 0%
    assert result["topic_accuracy"]["Translation"] == 0.0

    # Weak topics should specifically contain "Translation"
    weak_topic_names = [wt["topic"] for wt in result["weak_topics"]]
    assert "Translation" in weak_topic_names
    assert "Replication" not in weak_topic_names
