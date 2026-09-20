"""Automated tests for CustomTkinter Desktop GUI initialization and navigation."""
import pytest
from gui.main_window import MainWindow

def test_gui_window_and_navigation():
    app = MainWindow(start_authenticated=True)
    app.withdraw()  # Keep hidden during automated test run

    pages = [
        "Dashboard",
        "My Documents",
        "AI Summaries",
        "Question Generator",
        "Quiz",
        "Flashcards",
        "My Notebook",
        "Analytics",
        "Settings",
    ]

    for page in pages:
        app.navigate(page)
        app.update()
        assert app.sidebar.active_page == page
        assert app.current_view is not None

    app.destroy()
