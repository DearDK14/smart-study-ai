"""Application settings and configuration parameters."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# App Metadata
APP_NAME = os.getenv("APP_NAME", "StudyGenius (Smart Study AI)")
VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Directories
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "data/study_genius.db")

# Ensure required runtime folders exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Upload Constraints
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 25))
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

# AI Service Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
DEFAULT_MODEL = "gemini-1.5-flash"
USE_LOCAL_FALLBACK = True

# Gamification Thresholds
XP_PER_SUMMARY_READ = 25
XP_PER_QUIZ_COMPLETED = 50
XP_PER_CORRECT_ANSWER = 20
XP_PER_FLASHCARD_STUDIED = 10
LEVEL_XP_MULTIPLIER = 200  # Level = XP / 200 + 1
WEAK_TOPIC_ACCURACY_THRESHOLD = 60.0  # Percentage below which a topic is considered "weak"
