"""Smart Study AI (StudyGenius) - Main Application Router."""
import streamlit as st

# Streamlit Page Configuration must be the first Streamlit command
st.set_page_config(
    page_title="StudyGenius • Smart Study AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database
from database.connection import init_db
init_db()

# Component Imports
from components.styles import inject_custom_styles
from components.sidebar import render_sidebar

# Page Imports
from pages.dashboard import render_dashboard_page
from pages.documents import render_documents_page
from pages.summaries import render_summaries_page
from pages.questions import render_questions_page
from pages.quiz import render_quiz_page
from pages.flashcards import render_flashcards_page
from pages.notebook import render_notebook_page
from pages.analytics import render_analytics_page
from pages.settings import render_settings_page

def main():
    # Inject Custom CSS matching StudyGenius Design
    inject_custom_styles()

    # Render Sidebar and get active page
    selected_page = render_sidebar()

    # Route to Selected Page
    if selected_page == "📊 Dashboard":
        render_dashboard_page()
    elif selected_page == "📚 Documents":
        render_documents_page()
    elif selected_page == "📑 Summaries":
        render_summaries_page()
    elif selected_page == "❓ Questions":
        render_questions_page()
    elif selected_page == "📝 Quiz Studio":
        render_quiz_page()
    elif selected_page == "🗂️ Flashcards":
        render_flashcards_page()
    elif selected_page == "📓 Notebook":
        render_notebook_page()
    elif selected_page == "📈 Analytics":
        render_analytics_page()
    elif selected_page == "⚙️ Settings":
        render_settings_page()
    else:
        render_dashboard_page()

if __name__ == "__main__":
    main()
