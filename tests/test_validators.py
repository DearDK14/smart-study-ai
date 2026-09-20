"""Unit tests for input and data validators."""
import pytest
from utils.validators import (
    validate_file_extension,
    validate_file_size,
    validate_question_data,
    validate_flashcard_data,
)

def test_validate_file_extension_valid():
    assert validate_file_extension("notes.pdf")[0] is True
    assert validate_file_extension("slides.txt")[0] is True
    assert validate_file_extension("summary.md")[0] is True

def test_validate_file_extension_invalid():
    is_valid, msg = validate_file_extension("malicious.exe")
    assert is_valid is False
    assert "Unsupported file format" in msg

    is_valid2, _ = validate_file_extension("no_extension")
    assert is_valid2 is False

def test_validate_file_size():
    # 1MB is valid
    assert validate_file_size(1024 * 1024)[0] is True
    # 0 bytes is invalid
    assert validate_file_size(0)[0] is False
    # 50MB exceeds 25MB limit
    assert validate_file_size(50 * 1024 * 1024)[0] is False

def test_validate_question_data_valid():
    q = {
        "question_text": "What is the powerhouse of the cell?",
        "option_a": "Nucleus",
        "option_b": "Mitochondria",
        "option_c": "Ribosome",
        "option_d": "Golgi apparatus",
        "correct_option": "B",
    }
    assert validate_question_data(q)[0] is True

def test_validate_question_data_missing_fields():
    q = {
        "question_text": "What is ATP?",
        "option_a": "Energy carrier",
    }
    is_valid, err = validate_question_data(q)
    assert is_valid is False
    assert "Missing or empty" in err

def test_validate_question_data_invalid_correct_option():
    q = {
        "question_text": "What is ATP?",
        "option_a": "Energy carrier",
        "option_b": "Protein",
        "option_c": "Fat",
        "option_d": "Carbohydrate",
        "correct_option": "Z",
    }
    is_valid, err = validate_question_data(q)
    assert is_valid is False
    assert "Invalid correct_option" in err

def test_validate_flashcard_data():
    card = {"front_text": "Photosynthesis", "back_text": "Process of turning light into glucose."}
    assert validate_flashcard_data(card)[0] is True

    bad_card = {"front_text": "", "back_text": "Some text"}
    assert validate_flashcard_data(bad_card)[0] is False
