"""Question Generator View for StudyForge AI."""
import threading
from tkinter import messagebox
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from database.models import DocumentModel, QuestionModel
from services.question_service import QuestionService

class QuestionsView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn

        # 1. Top Generator Setup Card
        self.config_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.config_card.pack(fill="x", padx=16, pady=(10, 16))

        self.title_lbl = ctk.CTkLabel(
            self.config_card,
            text="❓ Question Generator & Exam Studio",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.title_lbl.pack(anchor="w", padx=20, pady=(16, 4))

        self.desc_lbl = ctk.CTkLabel(
            self.config_card,
            text="Synthesize multiple-choice exam questions from your course materials with automatic distractor options and explanations.",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
        )
        self.desc_lbl.pack(anchor="w", padx=20, pady=(0, 12))

        # Config Row
        self.cfg_row = ctk.CTkFrame(self.config_card, fg_color="transparent")
        self.cfg_row.pack(fill="x", padx=20, pady=(0, 14))

        self.docs_list = DocumentModel.get_all()
        self.doc_map = {d["id"]: d["title"] for d in self.docs_list}
        options = [d["title"] for d in self.docs_list] if self.docs_list else ["No documents available"]

        # Document Dropdown
        self.doc_lbl = ctk.CTkLabel(self.cfg_row, text="Document:", font=FONTS["small"], text_color=COLORS["text_muted"])
        self.doc_lbl.pack(side="left", padx=(0, 6))

        self.doc_dropdown = ctk.CTkOptionMenu(
            self.cfg_row,
            values=options,
            height=36,
            width=220,
            font=FONTS["small"],
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"],
        )
        self.doc_dropdown.pack(side="left", padx=(0, 16))

        # Difficulty Dropdown
        self.diff_lbl = ctk.CTkLabel(self.cfg_row, text="Difficulty:", font=FONTS["small"], text_color=COLORS["text_muted"])
        self.diff_lbl.pack(side="left", padx=(0, 6))

        self.diff_dropdown = ctk.CTkOptionMenu(
            self.cfg_row,
            values=["Medium", "Easy", "Hard"],
            height=36,
            width=110,
            font=FONTS["small"],
            fg_color=(COLORS["primary_light"], "#334155"),
            text_color=(COLORS["primary"], "white"),
            button_color=COLORS["primary"],
        )
        self.diff_dropdown.pack(side="left", padx=(0, 16))

        # Question Count
        self.count_lbl = ctk.CTkLabel(self.cfg_row, text="Questions:", font=FONTS["small"], text_color=COLORS["text_muted"])
        self.count_lbl.pack(side="left", padx=(0, 6))

        self.count_slider = ctk.CTkSlider(
            self.cfg_row,
            from_=3,
            to=12,
            number_of_steps=9,
            width=120,
            command=self._on_slider_change,
        )
        self.count_slider.set(5)
        self.count_slider.pack(side="left", padx=(0, 6))

        self.slider_val_lbl = ctk.CTkLabel(self.cfg_row, text="5", font=FONTS["body_bold"], text_color=COLORS["primary"])
        self.slider_val_lbl.pack(side="left", padx=(0, 16))

        # Generate Button
        self.gen_btn = ctk.CTkButton(
            self.cfg_row,
            text="⚡ Generate",
            font=FONTS["body_bold"],
            height=36,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._handle_generate_questions,
        )
        self.gen_btn.pack(side="right")

        self.status_lbl = ctk.CTkLabel(
            self.config_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["primary"],
        )
        self.status_lbl.pack(anchor="w", padx=20, pady=(0, 12))

        # 2. Generated Questions Review List
        self.review_header = ctk.CTkFrame(self, fg_color="transparent")
        self.review_header.pack(fill="x", padx=16, pady=(4, 8))

        self.review_title = ctk.CTkLabel(
            self.review_header,
            text="📋 Questions Bank & Preview",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.review_title.pack(side="left")

        self.take_quiz_btn = ctk.CTkButton(
            self.review_header,
            text="🎯 Launch Quiz Mode",
            font=FONTS["small"],
            height=32,
            fg_color="#059669",
            hover_color="#047857",
            command=lambda: self.navigate_fn("Quiz"),
        )
        self.take_quiz_btn.pack(side="right")

        self.questions_container = ctk.CTkFrame(self, fg_color="transparent")
        self.questions_container.pack(fill="x", padx=16, pady=(0, 24))

        self.refresh_questions()

    def _on_slider_change(self, val):
        self.slider_val_lbl.configure(text=str(int(val)))

    def _handle_generate_questions(self):
        selected_title = self.doc_dropdown.get()
        doc_id = None
        for did, title in self.doc_map.items():
            if title == selected_title:
                doc_id = did
                break

        if not doc_id:
            messagebox.showwarning("Warning", "Please upload and select a study document first!")
            return

        count = int(self.count_slider.get())

        self.gen_btn.configure(state="disabled", text="⏳ Synthesizing...")
        self.status_lbl.configure(text=f"AI is synthesizing {count} exam questions...")

        threading.Thread(
            target=self._generate_questions_worker,
            args=(doc_id, count),
            daemon=True,
        ).start()

    def _generate_questions_worker(self, doc_id: int, count: int):
        try:
            res = QuestionService.generate_questions_for_document(doc_id, count=count)
            self.after(0, lambda: self._on_questions_complete(res))
        except Exception as e:
            self.after(0, lambda: self._on_questions_error(str(e)))

    def _on_questions_complete(self, res: dict):
        self.gen_btn.configure(state="normal", text="⚡ Generate")
        if res.get("success"):
            self.status_lbl.configure(text=f"✅ Successfully generated {res.get('count')} questions for Quiz #{res.get('quiz_id')}!", text_color=COLORS["success"])
            self.refresh_questions()
            messagebox.showinfo("Success", f"Generated {res.get('count')} questions! You can now take this assessment in the Quiz tab.")
        else:
            self._on_questions_error(res.get("error", "Failed to generate questions."))

    def _on_questions_error(self, err_msg: str):
        self.gen_btn.configure(state="normal", text="⚡ Generate")
        self.status_lbl.configure(text=f"❌ {err_msg}", text_color=COLORS["danger"])
        messagebox.showerror("Error", f"Question generation error: {err_msg}")

    def refresh_questions(self):
        for w in self.questions_container.winfo_children():
            w.destroy()

        questions = QuestionModel.get_all()
        if not questions:
            lbl = ctk.CTkLabel(
                self.questions_container,
                text="No questions created yet. Select a document above and click 'Generate'!",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            )
            lbl.pack(pady=16)
            return

        for idx, q in enumerate(questions[:8]):
            card = ctk.CTkFrame(
                self.questions_container,
                fg_color=(COLORS["card_light"], COLORS["card_dark"]),
                corner_radius=12,
                border_width=1,
                border_color=(COLORS["border_light"], COLORS["border_dark"]),
            )
            card.pack(fill="x", pady=6)

            hdr = ctk.CTkFrame(card, fg_color="transparent")
            hdr.pack(fill="x", padx=16, pady=(10, 4))

            topic_badge = ctk.CTkLabel(
                hdr,
                text=f" {q.get('topic', 'General')} ",
                font=FONTS["caption"],
                fg_color=(COLORS["primary_light"], "#1e3a8a"),
                text_color=(COLORS["primary"], "#93c5fd"),
                corner_radius=8,
            )
            topic_badge.pack(side="left")

            diff_lbl = ctk.CTkLabel(hdr, text=f"Difficulty: {q.get('difficulty', 'Medium')}", font=FONTS["caption"], text_color=COLORS["text_muted"])
            diff_lbl.pack(side="right")

            q_text = ctk.CTkLabel(card, text=f"Q{idx+1}: {q['question_text']}", font=FONTS["body_bold"], wraplength=700, justify="left")
            q_text.pack(anchor="w", padx=16, pady=(4, 6))

            opts = f"A) {q['option_a']}   |   B) {q['option_b']}   |   C) {q['option_c']}   |   D) {q['option_d']}"
            opt_lbl = ctk.CTkLabel(card, text=opts, font=FONTS["small"], text_color=COLORS["text_muted"], wraplength=700, justify="left")
            opt_lbl.pack(anchor="w", padx=16, pady=(0, 4))

            ans_lbl = ctk.CTkLabel(card, text=f"✅ Correct: Option {q['correct_option']}", font=FONTS["small"], text_color=COLORS["success"])
            ans_lbl.pack(anchor="w", padx=16, pady=(0, 4))

            if q.get("explanation"):
                exp_lbl = ctk.CTkLabel(card, text=f"💡 {q['explanation']}", font=FONTS["caption"], text_color=COLORS["text_muted"], wraplength=700, justify="left")
                exp_lbl.pack(anchor="w", padx=16, pady=(0, 10))
            else:
                ctk.CTkFrame(card, height=6, fg_color="transparent").pack()
