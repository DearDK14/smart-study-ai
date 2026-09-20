"""Learning Analytics & Weak Topics Diagnostic View for StudyForge AI."""
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from database.models import QuizAttemptModel, DocumentModel, FlashcardModel, UserStatsModel
from config.settings import WEAK_TOPIC_ACCURACY_THRESHOLD

class AnalyticsView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn

        # 1. Top Diagnostic Header Card
        self.header_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.header_card.pack(fill="x", padx=16, pady=(10, 16))

        self.title_lbl = ctk.CTkLabel(
            self.header_card,
            text="📈 Learning Analytics & Weak Topics Diagnostic",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.title_lbl.pack(anchor="w", padx=20, pady=(16, 4))

        self.desc_lbl = ctk.CTkLabel(
            self.header_card,
            text="Real performance analysis driven by your actual quiz submissions to pinpoint areas needing review.",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
        )
        self.desc_lbl.pack(anchor="w", padx=20, pady=(0, 16))

        # 2. Key Metrics Row (4 Cards)
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=16, pady=(0, 16))
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="analytics_metric")

        attempts = QuizAttemptModel.get_all()
        docs = DocumentModel.get_all()
        cards = FlashcardModel.get_all()
        stats = UserStatsModel.get()

        total_quizzes = len(attempts)
        avg_score = round(sum(a["percentage"] for a in attempts) / total_quizzes, 1) if total_quizzes > 0 else 0.0
        total_xp = stats.get("xp_total", 11735)
        reviewed_cards = sum(c.get("reviews_count", 0) for c in cards)

        self._create_stat_card(0, "Quizzes Completed", str(total_quizzes), "Total Attempts", COLORS["primary"])
        self._create_stat_card(1, "Average Score", f"{avg_score}%", "Overall Accuracy", "#059669")
        self._create_stat_card(2, "Flashcards Reviewed", str(reviewed_cards), "Active Recall Hits", "#d97706")
        self._create_stat_card(3, "Total XP Earned", f"{total_xp:,} ⚡", f"Level {stats.get('level', 11)}", "#7c3aed")

        # 3. Weak Topics Priority Card
        self.weak_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.weak_card.pack(fill="x", padx=16, pady=(0, 16))

        self.weak_title = ctk.CTkLabel(
            self.weak_card,
            text="🎯 Weak Topics Diagnostic (< 60% Accuracy)",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.weak_title.pack(anchor="w", padx=20, pady=(16, 6))

        # Calculate Weak Topics from actual attempts
        topic_stats = {}
        for a in attempts:
            for ans in a.get("answers", []):
                t = ans.get("topic", "General")
                if t not in topic_stats:
                    topic_stats[t] = {"correct": 0, "total": 0}
                topic_stats[t]["total"] += 1
                if ans.get("is_correct"):
                    topic_stats[t]["correct"] += 1

        weak_topics = []
        for t, data in topic_stats.items():
            acc = round((data["correct"] / data["total"]) * 100, 1) if data["total"] > 0 else 0.0
            if acc < WEAK_TOPIC_ACCURACY_THRESHOLD:
                weak_topics.append({"topic": t, "accuracy": acc, "correct": data["correct"], "total": data["total"]})

        if not attempts:
            no_data_lbl = ctk.CTkLabel(
                self.weak_card,
                text="No quiz data available yet. Complete quizzes in the Quiz tab to generate actual topic diagnostics!",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            )
            no_data_lbl.pack(anchor="w", padx=20, pady=(0, 16))
        elif weak_topics:
            for wt in weak_topics:
                wt_frame = ctk.CTkFrame(
                    self.weak_card,
                    fg_color=(COLORS["danger_light"], "#450a0a"),
                    corner_radius=10,
                )
                wt_frame.pack(fill="x", padx=20, pady=4)

                lbl = ctk.CTkLabel(
                    wt_frame,
                    text=f"🚨 {wt['topic']} — Accuracy: {wt['accuracy']}% ({wt['correct']}/{wt['total']} questions correct)",
                    font=FONTS["body_bold"],
                    text_color=COLORS["danger"],
                )
                lbl.pack(side="left", padx=14, pady=8)

                rev_btn = ctk.CTkButton(
                    wt_frame,
                    text="Review in Flashcards",
                    font=FONTS["caption"],
                    height=28,
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["primary_hover"],
                    command=lambda: self.navigate_fn("Flashcards"),
                )
                rev_btn.pack(side="right", padx=14, pady=8)
            ctk.CTkFrame(self.weak_card, height=12, fg_color="transparent").pack()
        else:
            good_lbl = ctk.CTkLabel(
                self.weak_card,
                text="🎉 All tested topics are currently above the 60% mastery threshold! Excellent progress.",
                font=FONTS["body_bold"],
                text_color=COLORS["success"],
            )
            good_lbl.pack(anchor="w", padx=20, pady=(0, 16))

        # 4. Full Topic Mastery Breakdown (Progress Bars)
        self.breakdown_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.breakdown_card.pack(fill="x", padx=16, pady=(0, 16))

        self.bd_title = ctk.CTkLabel(
            self.breakdown_card,
            text="📊 Topic Accuracy Breakdown",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.bd_title.pack(anchor="w", padx=20, pady=(16, 12))

        if topic_stats:
            for t, data in topic_stats.items():
                acc = round((data["correct"] / data["total"]) * 100, 1) if data["total"] > 0 else 0.0
                bar_color = COLORS["danger"] if acc < WEAK_TOPIC_ACCURACY_THRESHOLD else COLORS["primary"]

                row = ctk.CTkFrame(self.breakdown_card, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=4)

                t_lbl = ctk.CTkLabel(row, text=f"{t} ({data['correct']}/{data['total']})", font=FONTS["small"], width=200, anchor="w")
                t_lbl.pack(side="left")

                pb = ctk.CTkProgressBar(row, height=8, corner_radius=4, progress_color=bar_color)
                pb.pack(side="left", fill="x", expand=True, padx=12)
                pb.set(acc / 100.0)

                pct_lbl = ctk.CTkLabel(row, text=f"{acc}%", font=FONTS["small"], width=50, anchor="e")
                pct_lbl.pack(side="right")
            ctk.CTkFrame(self.breakdown_card, height=14, fg_color="transparent").pack()
        else:
            empty_lbl = ctk.CTkLabel(
                self.breakdown_card,
                text="Take a quiz to see your topic accuracy breakdown here.",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            )
            empty_lbl.pack(anchor="w", padx=20, pady=(0, 16))

        # 5. Quiz Attempt History Table
        self.history_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.history_card.pack(fill="x", padx=16, pady=(0, 24))

        self.hist_title = ctk.CTkLabel(
            self.history_card,
            text="📜 Quiz Attempt Log",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.hist_title.pack(anchor="w", padx=20, pady=(16, 10))

        if attempts:
            for a in attempts[:6]:
                item = ctk.CTkFrame(self.history_card, fg_color=(COLORS["bg_light"], COLORS["bg_dark"]), corner_radius=8)
                item.pack(fill="x", padx=20, pady=4)

                q_txt = f"Quiz #{a['quiz_id']} — Score: {a['score']}/{a['total_questions']} ({a['percentage']}%)  •  +{a['xp_earned']} XP"
                lbl = ctk.CTkLabel(item, text=q_txt, font=FONTS["small"])
                lbl.pack(side="left", padx=12, pady=6)

                date_lbl = ctk.CTkLabel(item, text=str(a["completed_at"])[:16], font=FONTS["caption"], text_color=COLORS["text_muted"])
                date_lbl.pack(side="right", padx=12, pady=6)
            ctk.CTkFrame(self.history_card, height=12, fg_color="transparent").pack()
        else:
            no_hist = ctk.CTkLabel(self.history_card, text="No quiz history recorded yet.", font=FONTS["body"], text_color=COLORS["text_muted"])
            no_hist.pack(anchor="w", padx=20, pady=(0, 16))

    def _create_stat_card(self, col: int, title: str, count: str, subtitle: str, color: str):
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

        lbl_count = ctk.CTkLabel(card, text=count, font=("Segoe UI", 22, "bold"), text_color=(COLORS["text_dark"], COLORS["text_light"]))
        lbl_count.pack(anchor="w", padx=16, pady=(0, 2))

        lbl_sub = ctk.CTkLabel(card, text=subtitle, font=FONTS["caption"], text_color=color)
        lbl_sub.pack(anchor="w", padx=16, pady=(0, 14))
