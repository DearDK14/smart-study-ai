"""General helper utilities for formatting, calculations, and text processing."""
import re
import math
from typing import Dict, Any

def format_file_size(size_in_bytes: int) -> str:
    """Format bytes into readable human format (KB, MB, GB)."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

def calculate_reading_time(word_count: int, wpm: int = 200) -> int:
    """Calculates estimated reading time in minutes."""
    if word_count <= 0:
        return 1
    return max(1, math.ceil(word_count / wpm))

def sanitize_filename(filename: str) -> str:
    """Clean filename by removing special chars and spaces."""
    cleaned = re.sub(r"[^\w\s.-]", "", filename).strip()
    return re.sub(r"[\s]+", "_", cleaned)

def calculate_xp_for_level(current_xp: int) -> Dict[str, Any]:
    """Calculate level and progress towards next level.
    Each level requires 1,000 XP.
    Level 1: 0 - 999
    Level 11: 10,000 - 10,999 (or 11,000 - 11,999)
    """
    level = max(1, (current_xp // 1000) + 1)
    current_level_base = (level - 1) * 1000
    xp_in_level = current_xp - current_level_base
    xp_needed = 1000
    progress_percentage = min(100.0, max(0.0, (xp_in_level / xp_needed) * 100.0))
    return {
        "level": level,
        "current_xp": current_xp,
        "xp_in_level": xp_in_level,
        "xp_needed": xp_needed,
        "progress_percentage": round(progress_percentage, 1),
    }

def clean_extracted_text(text: str) -> str:
    """Clean raw extracted text from PDF/documents."""
    if not text:
        return ""
    # Normalize unicode whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove multiple continuous blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove weird null bytes or non-printable chars
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text.strip()
