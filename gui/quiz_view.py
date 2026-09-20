"""Interactive Quiz Studio View for StudyForge AI."""
from tkinter import messagebox
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from database.models import QuizModel, QuestionModel
from services.question_service import QuestionService

class QuizView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, on_stats_updated=None, user=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn
        self.on_stats_updated = on_stats_updated
        self.user = user or {}
        self.user_id = self.user.get("id")

        self.current_quiz = None
        self.questions = []
        self.current_q_idx = 0
        self.user_answers = {}  # {qid: "A"}
        self.quiz_finished = False

        # Top Quiz Selection Row
        self.top_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.top_card.pack(fill="x", padx=16, pady=(10, 16))

        self.top_row = ctk.CTkFrame(self.top_card, fg_color="transparent")
        self.top_row.pack(fill="x", padx=20, pady=16)

        self.quizzes = QuizModel.get_all(user_id=self.user_id)
        self.quiz_map = {q["id"]: q["title"] for q in self.quizzes}
        quiz_titles = [q["title"] for q in self.quizzes] if self.quizzes else ["No quizzes available"]

        self.quiz_lbl = ctk.CTkLabel(self.top_row, text="Select Quiz:", font=FONTS["body_bold"])
        self.quiz_lbl.pack(side="left", padx=(0, 10))

        self.quiz_dropdown = ctk.CTkOptionMenu(
            self.top_row,
            values=quiz_titles,
            height=36,
            width=280,
            font=FONTS["small"],
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"],
            command=self._on_quiz_selected,
        )
        self.quiz_dropdown.pack(side="left", padx=(0, 14))

        self.start_btn = ctk.CTkButton(
            self.top_row,
            text="🔄 Restart Quiz",
            height=36,
            font=FONTS["small"],
            fg_color=(COLORS["primary_light"], "#334155"),
            text_color=COLORS["primary"],
            hover_color=COLORS["primary"],
            command=self._restart_quiz,
        )
        self.start_btn.pack(side="left")

        # Main Quiz Interactive Card
        self.quiz_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.quiz_card.pack(fill="both", expand=True, padx=16, pady=(0, 20))

        # Progress bar
        self.prog_frame = ctk.CTkFrame(self.quiz_card, fg_color="transparent")
        self.prog_frame.pack(fill="x", padx=24, pady=(20, 10))

        self.step_label = ctk.CTkLabel(self.prog_frame, text="Question 1 of 5", font=FONTS["small"], text_color=COLORS["text_muted"])
        self.step_label.pack(side="left")

        self.prog_bar = ctk.CTkProgressBar(
            self.quiz_card,
            height=8,
            corner_radius=4,
            progress_color=COLORS["primary"],
            fg_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.prog_bar.pack(fill="x", padx=24, pady=(0, 16))

        # Topic Badge & Question Text
        self.topic_badge = ctk.CTkLabel(
            self.quiz_card,
            text="General",
            font=FONTS["caption"],
            fg_color=(COLORS["primary_light"], "#1e3a8a"),
            text_color=(COLORS["primary"], "#93c5fd"),
            corner_radius=8,
            padx=8,
            pady=2,
        )
        self.topic_badge.pack(anchor="w", padx=24, pady=(0, 8))

        self.q_text_label = ctk.CTkLabel(
            self.quiz_card,
            text="Upload a study document to automatically create a quiz!",
            font=FONTS["header"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
            wraplength=720,
            justify="left",
        )
        self.q_text_label.pack(anchor="w", padx=24, pady=(0, 20))

        # Radio Options Container
        self.radio_var = ctk.StringVar(value="")
        self.options_frame = ctk.CTkFrame(self.quiz_card, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=24, pady=(0, 20))

        self.radio_btns = {}
        for opt_key in ["A", "B", "C", "D"]:
            r = ctk.CTkRadioButton(
                self.options_frame,
                text=f"Option {opt_key}",
                value=opt_key,
                variable=self.radio_var,
                font=FONTS["body"],
                command=self._on_option_picked,
                border_color=COLORS["primary"],
                fg_color=COLORS["primary"],
            )
            r.pack(anchor="w", pady=6)
            self.radio_btns[opt_key] = r

        # Nav Buttons (Previous, Next, Submit)
        self.nav_btn_row = ctk.CTkFrame(self.quiz_card, fg_color="transparent")
        self.nav_btn_row.pack(fill="x", padx=24, pady=(10, 24))

        self.prev_btn = ctk.CTkButton(
            self.nav_btn_row,
            text="⬅️ Previous",
            width=110,
            height=38,
            font=FONTS["small"],
            fg_color=(COLORS["bg_light"], COLORS["bg_dark"]),
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
            command=self._prev_question,
        )
        self.prev_btn.pack(side="left")

        self.next_btn = ctk.CTkButton(
            self.nav_btn_row,
            text="Next ➡️",
            width=110,
            height=38,
            font=FONTS["small"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._next_question,
        )
        self.next_btn.pack(side="right")

        self.submit_btn = ctk.CTkButton(
            self.nav_btn_row,
            text="🏁 Submit Quiz",
            width=130,
            height=38,
            font=FONTS["body_bold"],
            fg_color="#059669",
            hover_color="#047857",
            command=self._submit_quiz,
        )
        self.submit_btn.pack(side="right", padx=(0, 10))

        # Result Summary Container (hidden until submission)
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.pack(fill="x", padx=16, pady=(0, 24))

        if self.quizzes:
            self._load_quiz(self.quizzes[0]["id"])

    def _on_quiz_selected(self, title):
        for qid, qtitle in self.quiz_map.items():
            if qtitle == title:
                self._load_quiz(qid)
                break

    def _load_quiz(self, quiz_id: int):
        self.current_quiz = QuizModel.get_by_id(quiz_id)
        if not self.current_quiz:
            return
        self.questions = QuestionModel.get_by_ids(self.current_quiz["question_ids"])
        self.current_q_idx = 0
        self.user_answers = {}
        self.quiz_finished = False

        # Clear previous result frames
        for w in self.result_frame.winfo_children():
            w.destroy()

        self._render_current_question()

    def _render_current_question(self):
        if not self.questions:
            self.q_text_label.configure(text="No questions available in this quiz.")
            return

        total = len(self.questions)
        q = self.questions[self.current_q_idx]

        # Update step & progress bar
        self.step_label.configure(text=f"Question {self.current_q_idx + 1} of {total}")
        self.prog_bar.set((self.current_q_idx + 1) / total)

        self.topic_badge.configure(text=f" Topic: {q.get('topic', 'General')} ")
        self.q_text_label.configure(text=f"Q{self.current_q_idx + 1}: {q['question_text']}")

        # Set radio text
        self.radio_btns["A"].configure(text=f"A) {q['option_a']}")
        self.radio_btns["B"].configure(text=f"B) {q['option_b']}")
        self.radio_btns["C"].configure(text=f"C) {q['option_c']}")
        self.radio_btns["D"].configure(text=f"D) {q['option_d']}")

        # Restore previous answer if any
        selected = self.user_answers.get(q["id"], "")
        self.radio_var.set(selected)

        # Nav button states
        self.prev_btn.configure(state="normal" if self.current_q_idx > 0 else "disabled")
        if self.current_q_idx == total - 1:
            self.next_btn.configure(state="disabled")
        else:
            self.next_btn.configure(state="normal")

    def _on_option_picked(self):
        if self.questions:
            q = self.questions[self.current_q_idx]
            self.user_answers[q["id"]] = self.radio_var.get()

    def _prev_question(self):
        if self.current_q_idx > 0:
            self.current_q_idx -= 1
            self._render_current_question()

    def _next_question(self):
        if self.current_q_idx < len(self.questions) - 1:
            self.current_q_idx += 1
            self._render_current_question()

    def _restart_quiz(self):
        if self.current_quiz:
            self._load_quiz(self.current_quiz["id"])

    def _submit_quiz(self):
        if not self.questions:
            return

        # Validate that all questions were answered
        unanswered = len(self.questions) - len(self.user_answers)
        if unanswered > 0:
            if not messagebox.askyesno("Unanswered Questions", f"You have {unanswered} unanswered question(s). Submit anyway?"):
                return

        # Evaluate submission with user_id
        res = QuestionService.evaluate_quiz_submission(self.current_quiz["id"], self.user_answers, user_id=self.user_id)
        if not res.get("success"):
            messagebox.showerror("Error", "Failed to grade quiz.")
            return

        self.quiz_finished = True
        if self.on_stats_updated:
            self.on_stats_updated()

        self._render_results(res)

    def _render_results(self, res: dict):
        for w in self.result_frame.winfo_children():
            w.destroy()

        score = res["score"]
        total = res["total_questions"]
        pct = res["percentage"]
        xp = res["xp_earned"]

        card = ctk.CTkFrame(
            self.result_frame,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        card.pack(fill="x", pady=10)

        title_lbl = ctk.CTkLabel(card, text="🏆 Quiz Completed!", font=FONTS["header"], text_color=COLORS["primary"])
        title_lbl.pack(anchor="w", padx=20, pady=(16, 4))

        score_text = f"You scored {score}/{total} ({pct}%) • Gained +{xp} XP ⚡"
        score_lbl = ctk.CTkLabel(card, text=score_text, font=FONTS["body_bold"])
        score_lbl.pack(anchor="w", padx=20, pady=(0, 10))

        # Weak Topics Diagnostic
        weak_topics = res.get("weak_topics", [])
        if weak_topics:
            wt_frame = ctk.CTkFrame(card, fg_color=(COLORS["danger_light"], "#450a0a"), corner_radius=12)
            wt_frame.pack(fill="x", padx=20, pady=(0, 14))

            wt_title = ctk.CTkLabel(
                wt_frame,
                text=f"⚠️ {len(weak_topics)} Weak Topic(s) Detected (< 60% accuracy):",
                font=FONTS["body_bold"],
                text_color=COLORS["danger"],
            )
            wt_title.pack(anchor="w", padx=16, pady=(10, 4))

            for wt in weak_topics:
                wt_item = ctk.CTkLabel(
                    wt_frame,
                    text=f"• {wt['topic']} — Accuracy: {wt['accuracy']}% ({wt['correct']}/{wt['total']} correct)",
                    font=FONTS["small"],
                    text_color=(COLORS["text_dark"], COLORS["text_light"]),
                )
                wt_item.pack(anchor="w", padx=24, pady=2)
            
            ctk.CTkFrame(wt_frame, height=8, fg_color="transparent").pack()
        else:
            good_lbl = ctk.CTkLabel(card, text="🎯 Perfect Mastery! No weak topics detected.", font=FONTS["small"], text_color=COLORS["success"])
            good_lbl.pack(anchor="w", padx=20, pady=(0, 10))

        # Question by question review
        ctk.CTkLabel(card, text="Detailed Breakdown:", font=FONTS["subheader"]).pack(anchor="w", padx=20, pady=(8, 6))
        for ans in res.get("detailed_answers", []):
            ans_frame = ctk.CTkFrame(card, fg_color=(COLORS["bg_light"], COLORS["bg_dark"]), corner_radius=8)
            ans_frame.pack(fill="x", padx=20, pady=4)

            icon = "✅" if ans["is_correct"] else "❌"
            q_info = f"{icon} {ans['question_text']}\nYour answer: {ans['user_choice'] or 'None'} | Correct: {ans['correct_choice']} (Topic: {ans['topic']})"
            if ans.get("explanation"):
                q_info += f"\n💡 {ans['explanation']}"

            lbl = ctk.CTkLabel(ans_frame, text=q_info, font=FONTS["small"], justify="left", wraplength=700)
            lbl.pack(anchor="w", padx=12, pady=8)

        ctk.CTkFrame(card, height=14, fg_color="transparent").pack()
