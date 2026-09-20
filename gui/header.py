"""Top Header component for StudyForge AI."""
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from database.models import UserStatsModel

class Header(ctk.CTkFrame):
    def __init__(self, master, on_theme_toggle=None, on_logout=None, **kwargs):
        super().__init__(
            master,
            fg_color=(COLORS["header_light"], COLORS["header_dark"]),
            corner_radius=0,
            height=64,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
            **kwargs
        )
        self.pack_propagate(False)
        self.on_theme_toggle = on_theme_toggle
        self.on_logout = on_logout
        self.user_id = None
        self.user_name = "Student"
        
        # Left side: Current Page Title & Subtitle
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.pack(side="left", fill="y", padx=24)
        
        self.title_label = ctk.CTkLabel(
            self.left_frame,
            text="Dashboard",
            font=FONTS["header"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.title_label.pack(side="top", anchor="w", pady=(10, 0))
        
        self.subtitle_label = ctk.CTkLabel(
            self.left_frame,
            text="Welcome back! Let's make today count.",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        )
        self.subtitle_label.pack(side="top", anchor="w")

        # Right side: Logout, Theme toggle, User avatar, Level badge, XP pill
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.pack(side="right", fill="y", padx=20)

        # Logout Button
        self.logout_btn = ctk.CTkButton(
            self.right_frame,
            text="🚪 Logout",
            width=76,
            height=32,
            font=FONTS["small"],
            fg_color=(COLORS["danger_light"], "#7f1d1d"),
            text_color=COLORS["danger"],
            hover_color=COLORS["danger"],
            command=self._handle_logout,
        )
        self.logout_btn.pack(side="right", padx=(12, 0), pady=16)

        # Theme Switcher
        self.theme_switch = ctk.CTkSwitch(
            self.right_frame,
            text="Dark",
            font=FONTS["small"],
            command=self._handle_theme_toggle,
            width=46,
            progress_color=COLORS["primary"],
        )
        self.theme_switch.pack(side="right", padx=(10, 0), pady=18)

        # User Avatar Pill
        self.user_pill = ctk.CTkFrame(
            self.right_frame,
            fg_color=(COLORS["primary_light"], COLORS["card_dark"]),
            border_width=1,
            border_color=(COLORS["primary_border"], COLORS["border_dark"]),
            corner_radius=20,
            height=36,
        )
        self.user_pill.pack(side="right", padx=(12, 0), pady=14)
        
        self.avatar_label = ctk.CTkLabel(
            self.user_pill,
            text=" 👤 Student ",
            font=FONTS["body_bold"],
            text_color=(COLORS["primary"], COLORS["text_light"]),
        )
        self.avatar_label.pack(side="left", padx=10, pady=4)

        # Level Pill
        self.level_label = ctk.CTkLabel(
            self.right_frame,
            text="⭐ Level 1",
            font=FONTS["small"],
            fg_color=(COLORS["warning_light"], "#78350f"),
            text_color=(COLORS["warning"], "#fef3c7"),
            corner_radius=12,
            padx=10,
            pady=4,
        )
        self.level_label.pack(side="right", padx=(10, 0), pady=16)

        # XP Pill
        self.xp_label = ctk.CTkLabel(
            self.right_frame,
            text="⚡ 0 XP",
            font=FONTS["small"],
            fg_color=(COLORS["primary_light"], "#1e3a8a"),
            text_color=(COLORS["primary"], "#93c5fd"),
            corner_radius=12,
            padx=10,
            pady=4,
        )
        self.xp_label.pack(side="right", padx=(0, 0), pady=16)

    def set_title(self, title: str, subtitle: str = ""):
        """Update active section title and subtitle."""
        self.title_label.configure(text=title)
        if subtitle:
            self.subtitle_label.configure(text=subtitle)

    def set_user(self, user: dict):
        """Update active user state, avatar label and refresh stats."""
        if not user:
            return
        self.user_id = user.get("id")
        self.user_name = user.get("name", "Student")
        self.avatar_label.configure(text=f" 👤 {self.user_name} ")
        self.update_user_stats(self.user_id)

    def set_user_name(self, name: str):
        """Update user avatar pill with logged in user name."""
        self.user_name = name
        self.avatar_label.configure(text=f" 👤 {name} ")

    def update_user_stats(self, user_id=None):
        """Fetch real user stats from SQLite and refresh labels."""
        try:
            uid = user_id if user_id is not None else self.user_id
            stats = UserStatsModel.get(user_id=uid)
            xp = stats.get("xp_total", 0)
            level = stats.get("level", 1)
            self.xp_label.configure(text=f"⚡ {xp:,} XP")
            self.level_label.configure(text=f"⭐ Level {level}")
        except Exception:
            pass

    def _handle_logout(self):
        if self.on_logout:
            self.on_logout()

    def _handle_theme_toggle(self):
        is_dark = self.theme_switch.get() == 1
        new_mode = "Dark" if is_dark else "Light"
        ctk.set_appearance_mode(new_mode)
        if self.on_theme_toggle:
            self.on_theme_toggle(new_mode)
