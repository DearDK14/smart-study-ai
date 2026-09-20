"""Theme and styling configuration for StudyForge AI Desktop GUI."""
import customtkinter as ctk

# Color Palette: Modern Light Blue, White & Slate
COLORS = {
    "primary": "#0284c7",          # Sky blue primary accent
    "primary_hover": "#0369a1",    # Darker blue on hover
    "primary_light": "#e0f2fe",    # Soft blue container/badge
    "primary_border": "#bae6fd",   # Light blue border
    
    "bg_light": "#f8fafc",         # Very light slate/white window background
    "bg_dark": "#0f172a",          # Slate 900 for dark mode
    
    "card_light": "#ffffff",       # Pure white cards
    "card_dark": "#1e293b",        # Slate 800 cards for dark mode
    
    "sidebar_light": "#ffffff",    # Clean white sidebar
    "sidebar_dark": "#1e293b",     # Dark sidebar
    
    "header_light": "#ffffff",
    "header_dark": "#1e293b",
    
    "border_light": "#e2e8f0",     # Subtle card border
    "border_dark": "#334155",
    
    "text_dark": "#0f172a",        # Slate 900 high-contrast text
    "text_light": "#f8fafc",       # White text for dark mode
    "text_muted": "#64748b",       # Slate 500 secondary text
    
    "success": "#10b981",          # Emerald green
    "success_light": "#d1fae5",
    "warning": "#f59e0b",          # Amber
    "warning_light": "#fef3c7",
    "danger": "#ef4444",           # Red
    "danger_light": "#fee2e2",
}

# Typography
FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "header": ("Segoe UI", 16, "bold"),
    "subheader": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 12),
    "body_bold": ("Segoe UI", 12, "bold"),
    "small": ("Segoe UI", 10),
    "caption": ("Segoe UI", 9),
    "code": ("Consolas", 11),
}

def init_theme():
    """Initializes CustomTkinter appearance mode and default color theme."""
    ctk.set_appearance_mode("Light")  # Default to Light theme as requested
    ctk.set_default_color_theme("blue")
