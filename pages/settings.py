"""Settings page: API configuration, system diagnostic, and reset tools."""
import os
import streamlit as st
from config.settings import GEMINI_API_KEY, APP_NAME, VERSION, DATABASE_PATH
from database.connection import init_db
from database.models import UserStatsModel

def render_settings_page():
    """Renders application settings and system configuration."""
    st.markdown("## ⚙️ System Settings & AI Configuration")

    tab_ai, tab_db = st.tabs(["🤖 AI Model & Keys", "🗄️ Database & Profile"])

    with tab_ai:
        st.markdown("### Google Gemini API Key")
        st.markdown("Configure your Gemini API key to enable online LLM models. If no key is set, StudyGenius automatically uses its **built-in offline local NLP heuristic engine**!")

        current_key = GEMINI_API_KEY
        key_input = st.text_input(
            "Gemini API Key",
            value=current_key,
            type="password",
            placeholder="AIzaSy...",
            help="Get an API key from Google AI Studio (https://aistudio.google.com)",
        )

        if st.button("💾 Save API Key", type="primary"):
            # Update .env
            env_file = DATABASE_PATH.parent.parent / ".env"
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"GEMINI_API_KEY={key_input.strip()}\n")
                f.write(f"APP_NAME={APP_NAME}\n")
                f.write(f"DATABASE_PATH=data/study_genius.db\n")
                f.write(f"MAX_FILE_SIZE_MB=25\n")
            st.success("✅ Settings updated! Please restart the app for changes to take effect.")

        if key_input:
            st.success("🟢 Online AI Mode Active (Gemini API)")
        else:
            st.info("🔵 Offline Local NLP Mode Active (No API key needed)")

    with tab_db:
        st.markdown("### App & Profile Diagnostics")
        st.markdown(f"- **App Name**: {APP_NAME}")
        st.markdown(f"- **Version**: {VERSION}")
        st.markdown(f"- **Database**: `{DATABASE_PATH}`")

        stats = UserStatsModel.get()
        st.json(stats)

        st.markdown("---")
        st.markdown("### Reset Database")
        st.caption("Clear all documents, quiz attempts, and restore default state.")
        if st.button("⚠️ Reset & Reinitialize Database", type="secondary"):
            init_db()
            st.success("Database reinitialized successfully!")
            st.rerun()
