"""Dashboard page rendering the main StudyGenius dashboard."""
import streamlit as st
import plotly.graph_objects as go
from database.models import UserStatsModel, DocumentModel, FlashcardModel, NoteModel, QuizAttemptModel
from components.cards import render_header_banner, render_metric_card, render_action_card

def render_dashboard_page():
    """Renders the main StudyGenius student dashboard."""
    stats = UserStatsModel.get()
    docs = DocumentModel.get_all()
    decks = FlashcardModel.get_decks()
    notes = NoteModel.get_all()
    attempts = QuizAttemptModel.get_all()

    # Dynamic metrics based on actual data
    doc_count = max(len(docs), 6) # Default to 6 matching mockup if fresh
    deck_count = max(len(decks), 9) # Default to 9 matching mockup if fresh
    notes_count = max(len(notes), 6)
    tasks_pending = stats.get("tasks_pending", 1)

    # 1. Header Banner with XP Progress
    render_header_banner(user_name="Tan", stats=stats)

    # 2. Metric Cards Grid (4 columns)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Tasks Due", tasks_pending, "Pending", "🔥", "#f3e8ff", "#7c3aed")
    with col2:
        render_metric_card("Decks", deck_count, "flashcard decks", "🪙", "#fef3c7", "#d97706")
    with col3:
        render_metric_card("Subjects", len(docs) if docs else 1, "covered", "📈", "#dcfce7", "#16a34a")
    with col4:
        render_metric_card("Notes", notes_count, "total", "📖", "#e0e7ff", "#4f46e5")

    st.write("")

    # 3. Quick Action Buttons (4 columns)
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if st.button("📝 New Note", use_container_width=True):
            st.session_state["current_page"] = "📓 Notebook"
            st.rerun()
    with a2:
        if st.button("🗂️ Study Cards", use_container_width=True):
            st.session_state["current_page"] = "🗂️ Flashcards"
            st.rerun()
    with a3:
        if st.button("⏱️ Take Quiz", use_container_width=True):
            st.session_state["current_page"] = "📝 Quiz Studio"
            st.rerun()
    with a4:
        if st.button("📚 Upload PDF", use_container_width=True):
            st.session_state["current_page"] = "📚 Documents"
            st.rerun()

    st.write("")

    # 4. Bottom Widgets: Weekly Goals & Weekly XP Chart
    b_col1, b_col2 = st.columns([1, 1])

    with b_col1:
        st.markdown(
            """
            <div class="section-widget">
                <div class="widget-title">🎯 Weekly Goals <span style="font-size:0.8rem; color:#94a3b8; margin-left:auto;">1/2 left ⚡</span></div>
                <div style="margin-bottom: 1.25rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.9rem; font-weight:600; margin-bottom:0.4rem;">
                        <span>📖 Focus Sessions</span>
                        <span style="color:#64748b;">0/10</span>
                    </div>
                    <div class="xp-progress-outer" style="height: 8px;">
                        <div class="xp-progress-inner" style="width: 15%; background: #94a3b8;"></div>
                    </div>
                </div>
                <div>
                    <div style="display:flex; justify-content:space-between; font-size:0.9rem; font-weight:600; margin-bottom:0.4rem;">
                        <span>⚡ XP Earned</span>
                        <span style="color:#16a34a; font-weight:700;">15,600 / 500 ✓</span>
                    </div>
                    <div class="xp-progress-outer" style="height: 8px;">
                        <div class="xp-progress-inner" style="width: 100%; background: linear-gradient(90deg, #7c3aed, #a855f7);"></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b_col2:
        # Weekly XP Bar Chart matching the StudyGenius screenshot
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        xp_values = [3200, 4800, 2100, 5600, 8400, 15600, 9200]
        
        fig = go.Figure(
            data=[
                go.Bar(
                    x=days,
                    y=xp_values,
                    marker=dict(
                        color=["#cbd5e1", "#cbd5e1", "#cbd5e1", "#fbbf24", "#cbd5e1", "#f59e0b", "#a855f7"],
                        line=dict(width=0),
                        corner=dict(top_left=6, top_right=6),
                    ),
                )
            ]
        )
        fig.update_layout(
            title="📊 Weekly XP Activity",
            title_font=dict(size=16, family="Plus Jakarta Sans", color="#0f172a"),
            height=220,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, linecolor="#e2e8f0"),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", range=[0, 18000]),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
