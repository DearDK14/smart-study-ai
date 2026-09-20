"""Left Navigation Sidebar for StudyForge AI."""
import customtkinter as ctk
from gui.theme import COLORS, FONTS

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate, **kwargs):
        super().__init__(
            master,
            width=240,
            corner_radius=0,
            fg_color=(COLORS["sidebar_light"], COLORS["sidebar_dark"]),
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
            **kwargs
        )
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.buttons = {}
        self.active_page = "Dashboard"

        # Brand Header Container
        self.brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.brand_frame.pack(fill="x", padx=18, pady=(20, 24))

        # Brand Logo Badge
        self.logo_badge = ctk.CTkLabel(
            self.brand_frame,
            text="⚡",
            font=("Segoe UI", 18),
            width=38,
            height=38,
            fg_color=COLORS["primary"],
            text_color="white",
            corner_radius=10,
        )
        self.logo_badge.pack(side="left", padx=(0, 10))

        # Brand Title & Tagline
        self.title_box = ctk.CTkFrame(self.brand_frame, fg_color="transparent")
        self.title_box.pack(side="left", fill="x")

        self.brand_title = ctk.CTkLabel(
            self.title_box,
            text="StudyForge AI",
            font=FONTS["header"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.brand_title.pack(anchor="w")

        self.brand_tagline = ctk.CTkLabel(
            self.title_box,
            text="Desktop Learning OS",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
        )
        self.brand_tagline.pack(anchor="w")

        # Navigation Items
        self.nav_items = [
            ("Dashboard", "📊  Dashboard"),
            ("My Documents", "📚  My Documents"),
            ("AI Summaries", "📑  AI Summaries"),
            ("Question Generator", "❓  Question Generator"),
            ("Quiz", "📝  Quiz"),
            ("Flashcards", "🗂️  Flashcards"),
            ("My Notebook", "📓  My Notebook"),
            ("Analytics", "📈  Analytics"),
            ("Settings", "⚙️  Settings"),
        ]

        self.nav_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.nav_container.pack(fill="both", expand=True, padx=12, pady=0)

        for page_id, label in self.nav_items:
            btn = ctk.CTkButton(
                self.nav_container,
                text=label,
                anchor="w",
                font=FONTS["body"],
                height=42,
                corner_radius=10,
                fg_color="transparent",
                text_color=(COLORS["text_dark"], COLORS["text_light"]),
                hover_color=(COLORS["primary_light"], "#334155"),
                command=lambda pid=page_id: self._handle_click(pid),
            )
            btn.pack(fill="x", pady=2)
            self.buttons[page_id] = btn

        # Bottom Footer / Status
        self.footer_frame = ctk.CTkFrame(
            self,
            fg_color=(COLORS["bg_light"], COLORS["bg_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.footer_frame.pack(fill="x", side="bottom", padx=16, pady=16)

        self.footer_status = ctk.CTkLabel(
            self.footer_frame,
            text="🟢 Engine: Ready",
            font=FONTS["small"],
            text_color=(COLORS["success"], COLORS["success"]),
        )
        self.footer_status.pack(anchor="w", padx=12, pady=(8, 2))

        self.footer_version = ctk.CTkLabel(
            self.footer_frame,
            text="StudyForge AI v1.0.0",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
        )
        self.footer_version.pack(anchor="w", padx=12, pady=(0, 8))

        # Initial active button state
        self.set_active("Dashboard")

    def _handle_click(self, page_id: str):
        self.set_active(page_id)
        if self.on_navigate:
            self.on_navigate(page_id)

    def set_active(self, page_id: str):
        """Highlights the active navigation button and de-highlights others."""
        self.active_page = page_id
        for pid, btn in self.buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color="white",
                    font=FONTS["body_bold"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=(COLORS["text_dark"], COLORS["text_light"]),
                    font=FONTS["body"],
                )
