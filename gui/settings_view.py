"""Settings View for StudyForge AI."""
from tkinter import messagebox
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from config.settings import GEMINI_API_KEY, APP_NAME, VERSION, DATABASE_PATH
from database.connection import init_db

class SettingsView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, on_theme_toggle=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn
        self.on_theme_toggle = on_theme_toggle

        # 1. AI Configuration Card
        self.ai_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.ai_card.pack(fill="x", padx=16, pady=(10, 16))

        self.ai_title = ctk.CTkLabel(
            self.ai_card,
            text="🤖 AI Model & API Configuration",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.ai_title.pack(anchor="w", padx=20, pady=(16, 4))

        self.ai_desc = ctk.CTkLabel(
            self.ai_card,
            text="StudyForge AI features a dual-mode engine: it automatically uses Google Gemini if a key is provided, or the built-in offline local NLP engine if omitted.",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
            wraplength=700,
            justify="left",
        )
        self.ai_desc.pack(anchor="w", padx=20, pady=(0, 12))

        # API Key Entry
        self.key_row = ctk.CTkFrame(self.ai_card, fg_color="transparent")
        self.key_row.pack(fill="x", padx=20, pady=(0, 14))

        self.key_entry = ctk.CTkEntry(
            self.key_row,
            placeholder_text="Enter Gemini API Key (e.g. AIzaSy...)",
            height=38,
            width=360,
            font=FONTS["small"],
            show="•",
        )
        if GEMINI_API_KEY:
            self.key_entry.insert(0, GEMINI_API_KEY)
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.save_key_btn = ctk.CTkButton(
            self.key_row,
            text="💾 Save Key",
            font=FONTS["body_bold"],
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._save_api_key,
        )
        self.save_key_btn.pack(side="right")

        # Engine Status Indicator
        status_text = "🟢 Engine Status: Online (Google Gemini API)" if GEMINI_API_KEY else "🔵 Engine Status: Offline Local NLP Engine (Zero API Key Needed)"
        self.engine_status = ctk.CTkLabel(
            self.ai_card,
            text=status_text,
            font=FONTS["small"],
            text_color=(COLORS["success"] if GEMINI_API_KEY else COLORS["primary"]),
        )
        self.engine_status.pack(anchor="w", padx=20, pady=(0, 16))

        # 2. Appearance & Theme Selection Card
        self.theme_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.theme_card.pack(fill="x", padx=16, pady=(0, 16))

        self.theme_title = ctk.CTkLabel(
            self.theme_card,
            text="🎨 Interface Appearance & Theme",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.theme_title.pack(anchor="w", padx=20, pady=(16, 4))

        self.theme_row = ctk.CTkFrame(self.theme_card, fg_color="transparent")
        self.theme_row.pack(fill="x", padx=20, pady=(0, 16))

        self.theme_lbl = ctk.CTkLabel(self.theme_row, text="Theme Mode:", font=FONTS["body"])
        self.theme_lbl.pack(side="left", padx=(0, 10))

        self.theme_dropdown = ctk.CTkOptionMenu(
            self.theme_row,
            values=["Light", "Dark", "System"],
            font=FONTS["small"],
            height=36,
            width=140,
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"],
            command=self._set_theme,
        )
        self.theme_dropdown.set(ctk.get_appearance_mode())
        self.theme_dropdown.pack(side="left")

        # 3. Application Info & System Diagnostics Card
        self.info_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.info_card.pack(fill="x", padx=16, pady=(0, 16))

        self.info_title = ctk.CTkLabel(
            self.info_card,
            text="ℹ️ Application Information",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.info_title.pack(anchor="w", padx=20, pady=(16, 8))

        diag_text = (
            f"• Application: {APP_NAME}\n"
            f"• Version: {VERSION}\n"
            f"• Desktop Framework: CustomTkinter v6.0.0\n"
            f"• Database Engine: SQLite 3 ({DATABASE_PATH})\n"
            f"• Hackathon Edition: CodeMyFYP Hack 26\n"
        )
        self.diag_lbl = ctk.CTkLabel(
            self.info_card,
            text=diag_text,
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            justify="left",
        )
        self.diag_lbl.pack(anchor="w", padx=20, pady=(0, 16))

        # 4. Data Management & Reset
        self.reset_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.reset_card.pack(fill="x", padx=16, pady=(0, 24))

        self.reset_title = ctk.CTkLabel(
            self.reset_card,
            text="⚠️ Database & Data Management",
            font=FONTS["subheader"],
            text_color=COLORS["danger"],
        )
        self.reset_title.pack(anchor="w", padx=20, pady=(16, 4))

        self.reset_desc = ctk.CTkLabel(
            self.reset_card,
            text="Reinitialize local SQLite tables and reset test documents, quizzes, and notes to clean initial state.",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        )
        self.reset_desc.pack(anchor="w", padx=20, pady=(0, 12))

        self.reset_btn = ctk.CTkButton(
            self.reset_card,
            text="🗑️ Clear & Reset Database",
            font=FONTS["small"],
            height=36,
            fg_color=(COLORS["danger_light"], "#7f1d1d"),
            text_color=COLORS["danger"],
            hover_color=COLORS["danger"],
            command=self._reset_database,
        )
        self.reset_btn.pack(anchor="w", padx=20, pady=(0, 16))

    def _save_api_key(self):
        new_key = self.key_entry.get().strip()
        env_file = DATABASE_PATH.parent.parent / ".env"
        try:
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"GEMINI_API_KEY={new_key}\n")
                f.write(f"APP_NAME={APP_NAME}\n")
                f.write(f"DATABASE_PATH=data/study_genius.db\n")
                f.write(f"MAX_FILE_SIZE_MB=25\n")
            
            msg = "🟢 Online AI Mode Active!" if new_key else "🔵 Offline Local NLP Mode Active!"
            self.engine_status.configure(text=msg)
            messagebox.showinfo("Success", "API key saved! Changes will apply to new generations.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save key: {e}")

    def _set_theme(self, mode: str):
        ctk.set_appearance_mode(mode)
        if self.on_theme_toggle:
            self.on_theme_toggle(mode)

    def _reset_database(self):
        if messagebox.askyesno("Confirm Database Reset", "Are you sure you want to reset the database? All documents, quizzes, notes, and study stats will be restored to defaults."):
            try:
                init_db()
                messagebox.showinfo("Reset Complete", "Database successfully reinitialized!")
                self.navigate_fn("Dashboard")
            except Exception as e:
                messagebox.showerror("Reset Error", str(e))
