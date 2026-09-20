"""StudyForge AI - Main Application Entry Point."""
import sys

def launch_desktop():
    """Launches the modern CustomTkinter desktop application."""
    from gui.main_window import run_app
    run_app()

def launch_web():
    """Launches the Streamlit web dashboard."""
    import streamlit as st
    if not st.runtime.exists():
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", __file__]
        sys.exit(stcli.main())
    
    st.set_page_config(
        page_title="StudyForge AI",
        page_icon="🎓",
        layout="wide",
    )
    from database.connection import init_db
    init_db()
    from components.styles import inject_custom_styles
    from components.sidebar import render_sidebar
    from pages.dashboard import render_dashboard_page
    from pages.documents import render_documents_page
    from pages.summaries import render_summaries_page
    from pages.questions import render_questions_page
    from pages.quiz import render_quiz_page
    from pages.flashcards import render_flashcards_page
    from pages.notebook import render_notebook_page
    from pages.analytics import render_analytics_page
    from pages.settings import render_settings_page

    inject_custom_styles()
    selected_page = render_sidebar()

    views = {
        "📊 Dashboard": render_dashboard_page,
        "📚 Documents": render_documents_page,
        "📑 Summaries": render_summaries_page,
        "❓ Questions": render_questions_page,
        "📝 Quiz Studio": render_quiz_page,
        "🗂️ Flashcards": render_flashcards_page,
        "📓 Notebook": render_notebook_page,
        "📈 Analytics": render_analytics_page,
        "⚙️ Settings": render_settings_page,
    }
    view_fn = views.get(selected_page, render_dashboard_page)
    view_fn()

if __name__ == "__main__":
    # Check for web mode flags
    if "--web" in sys.argv or any("streamlit" in arg for arg in sys.argv):
        launch_web()
    else:
        # Default: Launch modern CustomTkinter desktop application
        launch_desktop()
