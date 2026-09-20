"""Database package for Smart Study AI."""
from database.connection import get_db_connection, init_db
from database.models import (
    DocumentModel,
    SummaryModel,
    QuestionModel,
    QuizModel,
    QuizAttemptModel,
    FlashcardModel,
    UserStatsModel,
)

__all__ = [
    "get_db_connection",
    "init_db",
    "DocumentModel",
    "SummaryModel",
    "QuestionModel",
    "QuizModel",
    "QuizAttemptModel",
    "FlashcardModel",
    "UserStatsModel",
]
