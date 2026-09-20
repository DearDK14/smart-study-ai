"""Sidebar navigation component matching StudyGenius layout."""
import streamlit as st

def render_sidebar():
    """Renders the left navigation sidebar and returns selected page name."""
    with st.sidebar:
        # User & Brand Avatar Header
        st.markdown(
            """
            <div class="brand-container">
                <div class="brand-avatar">T</div>
                <div class="brand-text">
                    <h2>StudyGenius</h2>
                    <p>Tan • Studying hard 💜</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_options = [
            "📊 Dashboard",
            "📚 Documents",
            "📑 Summaries",
            "❓ Questions",
            "📝 Quiz Studio",
            "🗂️ Flashcards",
            "📓 Notebook",
            "📈 Analytics",
            "⚙️ Settings",
        ]

        # Determine current selection from session_state
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = nav_options[0]

        default_idx = 0
        if st.session_state["current_page"] in nav_options:
            default_idx = nav_options.index(st.session_state["current_page"])

        selected_page = st.radio(
            "Navigation Menu",
            options=nav_options,
            index=default_idx,
            label_visibility="collapsed",
        )
        st.session_state["current_page"] = selected_page

        st.markdown("---")
        st.caption("🚀 **CodeMyFYP Hack 26 Edition**\nSmart Study AI v1.0.0")

        return selected_page
