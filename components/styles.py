"""Custom CSS injected into Streamlit to match the StudyGenius dashboard design."""
import streamlit as st

def inject_custom_styles():
    """Injects high-fidelity CSS styling to replicate StudyGenius UI."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global reset and font */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #f8fafc !important;
        color: #1e293b;
    }

    /* Streamlit top header adjustment */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    .stMainBlockContainer {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* Left Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 8px rgba(0,0,0,0.02);
    }
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 0.35rem;
    }
    section[data-testid="stSidebar"] .stRadio label {
        padding: 0.6rem 0.9rem;
        border-radius: 12px;
        transition: all 0.2s ease;
        font-weight: 500;
        color: #475569;
        font-size: 0.95rem;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background-color: #f1f5f9;
        color: #6366f1;
    }

    /* StudyGenius Brand Logo in Sidebar */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0.25rem 1.5rem 0.25rem;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 1rem;
    }
    .brand-avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: linear-gradient(135deg, #a855f7, #ec4899);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 10px rgba(168, 85, 247, 0.25);
    }
    .brand-text h2 {
        font-size: 1.15rem;
        font-weight: 800;
        margin: 0;
        color: #0f172a;
        letter-spacing: -0.02em;
    }
    .brand-text p {
        font-size: 0.75rem;
        color: #94a3b8;
        margin: 0;
    }

    /* Hero Header Banner */
    .sg-greeting {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.25rem;
        letter-spacing: -0.03em;
    }
    .sg-subtext {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }

    /* Level and XP Bar */
    .xp-level-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.25rem 1.75rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04);
        border: 1px solid #edf2f7;
        margin-bottom: 1.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
    }
    .xp-level-badge {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-weight: 700;
        color: #7c3aed;
        font-size: 1.05rem;
        min-width: 110px;
    }
    .xp-progress-outer {
        flex: 1;
        background-color: #f1f5f9;
        height: 10px;
        border-radius: 10px;
        overflow: hidden;
        position: relative;
    }
    .xp-progress-inner {
        height: 100%;
        background: linear-gradient(90deg, #8b5cf6, #a855f7);
        border-radius: 10px;
        transition: width 0.4s ease;
    }
    .xp-stats-right {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stat-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
    }
    .pill-xp {
        color: #64748b;
    }
    .pill-streak {
        color: #ea580c;
        background-color: #fff7ed;
        border-color: #ffedd5;
    }
    .pill-gems {
        color: #7c3aed;
        background-color: #f5f3ff;
        border-color: #ede9fe;
    }

    /* Metric Cards Grid */
    .metric-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 1.4rem;
        box-shadow: 0 4px 18px -2px rgba(0, 0, 0, 0.04);
        border: 1px solid #f1f5f9;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.08);
    }
    .metric-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .metric-icon-box {
        width: 32px;
        height: 32px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }
    .metric-number {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    /* Quick Action Buttons */
    .action-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.25rem;
        text-align: center;
        border: 1px solid #f1f5f9;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .action-card:hover {
        border-color: #c4b5fd;
        background-color: #faf5ff;
        transform: translateY(-2px);
    }
    .action-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    .action-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: #1e293b;
    }

    /* Bottom Widgets (Goals & Analytics) */
    .section-widget {
        background: #ffffff;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04);
        border: 1px solid #f1f5f9;
        height: 100%;
    }
    .widget-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Flashcard Flip Card Styling */
    .fc-container {
        perspective: 1000px;
        margin: 1.5rem 0;
    }
    .fc-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 2.5rem;
        min-height: 260px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 10px 30px -5px rgba(124, 58, 237, 0.1);
        border: 2px solid #ede9fe;
        position: relative;
    }
    .fc-badge {
        position: absolute;
        top: 1.25rem;
        left: 1.5rem;
        font-size: 0.75rem;
        font-weight: 700;
        color: #7c3aed;
        background: #f5f3ff;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
    }
    .fc-text {
        font-size: 1.35rem;
        font-weight: 600;
        color: #1e293b;
        line-height: 1.5;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(124, 58, 237, 0.35) !important;
    }

    /* Weak topic alert badge */
    .weak-topic-badge {
        display: inline-block;
        background-color: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fca5a5;
        padding: 0.25rem 0.6rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
