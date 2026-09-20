"""Dashboard View for StudyForge AI."""
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from database.models import (
    DocumentModel,
    SummaryModel,
    QuizAttemptModel,
    FlashcardModel,
    UserStatsModel,
)
from utils.helpers import calculate_xp_for_level

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn

        # 1. Hero Greeting Banner Card
        self.hero_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.hero_card.pack(fill="x", padx=16, pady=(10, 16))

        self.hero_title = ctk.CTkLabel(
            self.hero_card,
            text="Good morning, Tan 👋",
            font=FONTS["title"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.hero_title.pack(anchor="w", padx=24, pady=(20, 4))

        self.hero_subtitle = ctk.CTkLabel(
            self.hero_card,
            text="Welcome to StudyForge AI. Review your progress, study flashcards, and master exam topics today.",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
        )
        self.hero_subtitle.pack(anchor="w", padx=24, pady=(0, 16))

        # XP Level Progress Bar inside hero card
        self.xp_container = ctk.CTkFrame(
            self.hero_card,
            fg_color=(COLORS["bg_light"], COLORS["bg_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.xp_container.pack(fill="x", padx=24, pady=(0, 20))

        stats = UserStatsModel.get()
        xp_info = calculate_xp_for_level(stats.get("xp_total", 11735))

        self.xp_header = ctk.CTkFrame(self.xp_container, fg_color="transparent")
        self.xp_header.pack(fill="x", padx=16, pady=(12, 6))

        self.level_badge = ctk.CTkLabel(
            self.xp_header,
            text=f"⭐ Level {stats.get('level', 11)} Student",
            font=FONTS["body_bold"],
            text_color=COLORS["primary"],
        )
        self.level_badge.pack(side="left")

        self.xp_fraction = ctk.CTkLabel(
            self.xp_header,
            text=f"{xp_info['xp_in_level']} / {xp_info['xp_needed']} XP to Level {stats.get('level', 11) + 1}",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        )
        self.xp_fraction.pack(side="right")

        self.xp_bar = ctk.CTkProgressBar(
            self.xp_container,
            height=10,
            corner_radius=6,
            progress_color=COLORS["primary"],
            fg_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.xp_bar.pack(fill="x", padx=16, pady=(0, 14))
        self.xp_bar.set(xp_info["progress_percentage"] / 100.0)

        # 2. Key Metrics Grid (4 Stat Cards)
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=16, pady=(0, 16))
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="metric")

        docs = DocumentModel.get_all()
        summaries = SummaryModel.get_all()
        attempts = QuizAttemptModel.get_all()
        cards = FlashcardModel.get_all()

        self._create_stat_card(0, "📚 Documents", len(docs), "Processed Notes", COLORS["primary"], COLORS["primary_light"])
        self._create_stat_card(1, "📑 Summaries", len(summaries), "AI Insights", "#059669", "#d1fae5")
        self._create_stat_card(2, "📝 Quizzes", len(attempts), "Assessments Done", "#d97706", "#fef3c7")
        self._create_stat_card(3, "🗂️ Flashcards", len(cards), "Active Cards", "#7c3aed", "#ede9fe")

        # 3. Quick Action Buttons Row
        self.actions_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.actions_card.pack(fill="x", padx=16, pady=(0, 16))

        self.actions_title = ctk.CTkLabel(
            self.actions_card,
            text="⚡ Quick Actions",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.actions_title.pack(anchor="w", padx=20, pady=(16, 12))

        self.btn_row = ctk.CTkFrame(self.actions_card, fg_color="transparent")
        self.btn_row.pack(fill="x", padx=20, pady=(0, 18))
        self.btn_row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="action")

        actions = [
            ("📤 Upload Notes", "My Documents", COLORS["primary"]),
            ("✨ Generate Summary", "AI Summaries", "#059669"),
            ("❓ Create Questions", "Question Generator", "#d97706"),
            ("🎯 Start Quiz", "Quiz", "#7c3aed"),
        ]

        for col_idx, (text, page_target, btn_color) in enumerate(actions):
            b = ctk.CTkButton(
                self.btn_row,
                text=text,
                font=FONTS["body_bold"],
                height=42,
                corner_radius=10,
                fg_color=btn_color,
                hover_color=COLORS["primary_hover"],
                command=lambda pt=page_target: self.navigate_fn(pt),
            )
            b.grid(row=0, column=col_idx, padx=6, sticky="ew")

        # 4. Recent Activity Feed
        self.activity_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.activity_card.pack(fill="x", padx=16, pady=(0, 24))

        self.activity_title = ctk.CTkLabel(
            self.activity_card,
            text="🕒 Recent Study Activity",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.activity_title.pack(anchor="w", padx=20, pady=(16, 10))

        if not attempts and not docs:
            self.empty_label = ctk.CTkLabel(
                self.activity_card,
                text="No recent activity yet. Upload a document or take a quiz to start building your study history!",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            )
            self.empty_label.pack(anchor="w", padx=20, pady=(0, 18))
        else:
            # Display last 3 attempts or documents
            for a in attempts[:3]:
                item_frame = ctk.CTkFrame(
                    self.activity_card,
                    fg_color=(COLORS["bg_light"], COLORS["bg_dark"]),
                    corner_radius=8,
                )
                item_frame.pack(fill="x", padx=20, pady=4)
                
                txt = f"📝 Completed Quiz #{a['quiz_id']} — Score: {a['score']}/{a['total_questions']} ({a['percentage']}%) • +{a['xp_earned']} XP"
                lbl = ctk.CTkLabel(item_frame, text=txt, font=FONTS["small"], text_color=(COLORS["text_dark"], COLORS["text_light"]))
                lbl.pack(side="left", padx=12, pady=8)

                time_lbl = ctk.CTkLabel(item_frame, text=str(a['completed_at'])[:16], font=FONTS["caption"], text_color=COLORS["text_muted"])
                time_lbl.pack(side="right", padx=12, pady=8)

            for d in docs[:2]:
                item_frame = ctk.CTkFrame(
                    self.activity_card,
                    fg_color=(COLORS["bg_light"], COLORS["bg_dark"]),
                    corner_radius=8,
                )
                item_frame.pack(fill="x", padx=20, pady=4)
                
                txt = f"📚 Uploaded '{d['title']}' ({d['word_count']} words, {d['page_count']} pages)"
                lbl = ctk.CTkLabel(item_frame, text=txt, font=FONTS["small"], text_color=(COLORS["text_dark"], COLORS["text_light"]))
                lbl.pack(side="left", padx=12, pady=8)

                time_lbl = ctk.CTkLabel(item_frame, text=str(d['created_at'])[:16], font=FONTS["caption"], text_color=COLORS["text_muted"])
                time_lbl.pack(side="right", padx=12, pady=8)

            ctk.CTkFrame(self.activity_card, height=12, fg_color="transparent").pack()

    def _create_stat_card(self, col: int, title: str, count: int, subtitle: str, color: str, light_bg: str):
        card = ctk.CTkFrame(
            self.metrics_frame,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=14,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        lbl_title = ctk.CTkLabel(card, text=title, font=FONTS["small"], text_color=COLORS["text_muted"])
        lbl_title.pack(anchor="w", padx=16, pady=(14, 2))

        lbl_count = ctk.CTkLabel(card, text=str(count), font=("Segoe UI", 24, "bold"), text_color=(COLORS["text_dark"], COLORS["text_light"]))
        lbl_count.pack(anchor="w", padx=16, pady=(0, 2))

        lbl_sub = ctk.CTkLabel(card, text=subtitle, font=FONTS["caption"], text_color=color)
        lbl_sub.pack(anchor="w", padx=16, pady=(0, 14))
