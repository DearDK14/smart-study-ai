"""UI Cards and Widgets for StudyGenius / Smart Study AI."""
import streamlit as st
from utils.helpers import calculate_xp_for_level

def render_header_banner(user_name: str = "Tan", motto: str = "Studying hard for finals! 💜", stats: dict = None):
    """Renders the top greeting and Level/XP progress bar matching the screenshot."""
    if not stats:
        stats = {
            "xp_total": 11735,
            "level": 11,
            "streak_days": 1,
            "gems": 250,
        }

    xp_info = calculate_xp_for_level(stats.get("xp_total", 11735))
    level = stats.get("level", 11)
    progress_pct = xp_info["progress_percentage"]
    xp_in_level = xp_info["xp_in_level"]
    xp_needed = xp_info["xp_needed"]
    streak = stats.get("streak_days", 1)
    xp_total = stats.get("xp_total", 11735)

    html = f"""
    <div style="margin-bottom: 1.5rem;">
        <div class="sg-greeting">Good morning 👋</div>
        <div class="sg-subtext">Let's make today count.</div>
        
        <div class="xp-level-card">
            <div class="xp-level-badge">
                <span style="font-size: 1.3rem;">⭐</span> Level {level}
            </div>
            <div class="xp-progress-outer">
                <div class="xp-progress-inner" style="width: {progress_pct}%;"></div>
            </div>
            <div class="xp-stats-right">
                <span class="stat-pill pill-xp">{xp_in_level}/{xp_needed} XP</span>
                <span class="stat-pill pill-streak">🔥 {streak}</span>
                <span class="stat-pill pill-gems">⚡ {xp_total}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_metric_card(title: str, value: str or int, subtitle: str, icon: str, bg_color: str = "#f3e8ff", text_color: str = "#7c3aed"):
    """Renders a single metric card (e.g. Tasks Due, Decks, Subjects, Notes)."""
    html = f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-icon-box" style="background-color: {bg_color}; color: {text_color};">
                {icon}
            </div>
            <span>{title}</span>
        </div>
        <div class="metric-number">{value}</div>
        <div class="metric-label">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_action_card(title: str, icon: str):
    """Renders an action button card (New Note, Study Cards, Focus Timer, Plan Week)."""
    html = f"""
    <div class="action-card">
        <div class="action-icon">{icon}</div>
        <div class="action-title">{title}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_flashcard_widget(front: str, back: str, topic: str = "General", is_flipped: bool = False):
    """Renders an interactive study flashcard."""
    display_text = back if is_flipped else front
    label = "💡 Definition / Answer (Back)" if is_flipped else "❓ Question / Concept (Front)"
    bg_style = "background: linear-gradient(135deg, #faf5ff, #f3e8ff); border-color: #c084fc;" if is_flipped else ""

    html = f"""
    <div class="fc-container">
        <div class="fc-card" style="{bg_style}">
            <div class="fc-badge">{topic.upper()} • {label}</div>
            <div class="fc-text">{display_text}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
