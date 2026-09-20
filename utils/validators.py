"""Validation utilities for user input, files, and generated content."""
from pathlib import Path
from typing import Tuple, List, Dict, Any
from config.settings import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB

def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """Check if the uploaded file has a supported extension."""
    if not filename or "." not in filename:
        return False, "File must have an extension (e.g. .pdf, .txt)."
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
    return True, ""

def validate_file_size(size_in_bytes: int) -> Tuple[bool, str]:
    """Check if the file is within maximum permitted size."""
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if size_in_bytes <= 0:
        return False, "File is empty."
    if size_in_bytes > max_bytes:
        return False, f"File size exceeds limit of {MAX_FILE_SIZE_MB}MB."
    return True, ""

def validate_question_data(q: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate question dictionary structure."""
    required_fields = ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_option"]
    for field in required_fields:
        if field not in q or not str(q[field]).strip():
            return False, f"Missing or empty required field: '{field}'"
    
    correct = str(q["correct_option"]).strip().upper()
    if correct not in ("A", "B", "C", "D"):
        return False, f"Invalid correct_option '{correct}'. Must be A, B, C, or D."
        
    return True, ""

def validate_flashcard_data(card: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate flashcard dictionary structure."""
    if not card.get("front_text") or not str(card["front_text"]).strip():
        return False, "Flashcard front text cannot be empty."
    if not card.get("back_text") or not str(card["back_text"]).strip():
        return False, "Flashcard back text cannot be empty."
    return True, ""
