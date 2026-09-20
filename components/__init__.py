"""UI components package for StudyGenius / Smart Study AI."""
from components.styles import inject_custom_styles
from components.sidebar import render_sidebar
from components.cards import (
    render_metric_card,
    render_action_card,
    render_header_banner,
    render_flashcard_widget,
)

__all__ = [
    "inject_custom_styles",
    "render_sidebar",
    "render_metric_card",
    "render_action_card",
    "render_header_banner",
    "render_flashcard_widget",
]
