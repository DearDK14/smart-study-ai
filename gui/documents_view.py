"""Documents Management View for StudyForge AI with Full Auto-Pipeline."""
import os
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from services.pdf_service import PDFService
from services.summary_service import SummaryService
from services.question_service import QuestionService
from services.flashcard_service import FlashcardService
from database.models import DocumentModel, SummaryModel, QuizModel, FlashcardModel, UserStatsModel
from utils.validators import validate_file_extension, validate_file_size
from utils.helpers import format_file_size, sanitize_filename
from config.settings import UPLOADS_DIR

class DocumentsView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, user=None, on_stats_updated=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn
        self.user = user or {}
        self.user_id = self.user.get("id")
        self.on_stats_updated = on_stats_updated

        # 1. Top Upload Card
        self.upload_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.upload_card.pack(fill="x", padx=16, pady=(10, 16))

        self.upload_title = ctk.CTkLabel(
            self.upload_card,
            text="📚 Upload Study Document (PDF / TXT)",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.upload_title.pack(anchor="w", padx=20, pady=(16, 4))

        self.upload_desc = ctk.CTkLabel(
            self.upload_card,
            text="Select lecture notes, chapters, or textbook PDFs. The AI pipeline will automatically extract content and formulate summaries, exam questions, quizzes, and flashcards in one step.",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
            wraplength=760,
            justify="left",
        )
        self.upload_desc.pack(anchor="w", padx=20, pady=(0, 12))

        # Title Input & File Pick Button
        self.input_row = ctk.CTkFrame(self.upload_card, fg_color="transparent")
        self.input_row.pack(fill="x", padx=20, pady=(0, 10))

        self.title_entry = ctk.CTkEntry(
            self.input_row,
            placeholder_text="Optional custom title (e.g. Bio Chapter 4: Cellular Respiration)",
            height=40,
            font=FONTS["body"],
        )
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.upload_btn = ctk.CTkButton(
            self.input_row,
            text="📂 Choose File & Process All",
            font=FONTS["body_bold"],
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._handle_file_upload,
        )
        self.upload_btn.pack(side="right")

        # Pipeline Options Row
        self.opts_row = ctk.CTkFrame(self.upload_card, fg_color="transparent")
        self.opts_row.pack(fill="x", padx=20, pady=(0, 12))

        self.auto_pipeline_var = ctk.BooleanVar(value=True)
        self.auto_pipeline_cb = ctk.CTkCheckBox(
            self.opts_row,
            text="⚡ Auto-Generate Complete Study Kit (Summary + Questions + Quiz + Flashcards)",
            variable=self.auto_pipeline_var,
            font=FONTS["small"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
            checkbox_height=20,
            checkbox_width=20,
            corner_radius=6,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        self.auto_pipeline_cb.pack(side="left")

        # Loading status bar & progress message
        self.status_label = ctk.CTkLabel(
            self.upload_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["primary"],
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 14))

        # 2. Uploaded Documents Library
        self.lib_header = ctk.CTkFrame(self, fg_color="transparent")
        self.lib_header.pack(fill="x", padx=16, pady=(4, 8))

        self.lib_title = ctk.CTkLabel(
            self.lib_header,
            text="📂 Your Document Library",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.lib_title.pack(side="left")

        self.refresh_btn = ctk.CTkButton(
            self.lib_header,
            text="🔄 Refresh",
            width=80,
            height=30,
            font=FONTS["small"],
            fg_color="transparent",
            text_color=COLORS["primary"],
            hover_color=(COLORS["primary_light"], "#334155"),
            command=self.refresh_list,
        )
        self.refresh_btn.pack(side="right")

        # Container for document list items
        self.list_container = ctk.CTkFrame(self, fg_color="transparent")
        self.list_container.pack(fill="x", padx=16, pady=(0, 24))

        self.refresh_list()

    def _handle_file_upload(self):
        file_path = filedialog.askopenfilename(
            title="Select Study Document",
            filetypes=[("Supported Documents", "*.pdf;*.txt;*.md"), ("PDF Files", "*.pdf"), ("Text Files", "*.txt;*.md")],
        )
        if not file_path:
            return

        custom_title = self.title_entry.get().strip()
        run_full_pipeline = self.auto_pipeline_var.get()

        # Run extraction & full pipeline in background thread
        self.upload_btn.configure(state="disabled", text="⏳ Processing Pipeline...")
        self.status_label.configure(text="⏳ Step 1/4: Extracting text from document...", text_color=COLORS["primary"])

        threading.Thread(
            target=self._process_upload_worker,
            args=(file_path, custom_title, run_full_pipeline),
            daemon=True,
        ).start()

    def _process_upload_worker(self, file_path: str, custom_title: str, run_full_pipeline: bool):
        try:
            filename = os.path.basename(file_path)

            with open(file_path, "rb") as f:
                file_bytes = f.read()

            file_size = len(file_bytes)

            is_valid_ext, err_ext = validate_file_extension(filename)
            if not is_valid_ext:
                self.after(0, lambda: self._on_upload_error(err_ext))
                return

            is_valid_sz, err_sz = validate_file_size(file_size)
            if not is_valid_sz:
                self.after(0, lambda: self._on_upload_error(err_sz))
                return

            # Save local copy
            clean_name = sanitize_filename(filename)
            save_path = UPLOADS_DIR / clean_name
            with open(save_path, "wb") as f:
                f.write(file_bytes)

            # Extract via PDFService
            res = PDFService.process_file(filename, file_bytes)
            if not res["success"]:
                self.after(0, lambda: self._on_upload_error(res.get("error", "Failed to extract text.")))
                return

            title = custom_title if custom_title else filename.rsplit(".", 1)[0]
            file_type = filename.rsplit(".", 1)[-1].upper()

            # Create document row in SQLite with user_id
            doc_id = DocumentModel.create(
                filename=clean_name,
                filepath=save_path,
                title=title,
                file_type=file_type,
                file_size=file_size,
                page_count=res["page_count"],
                word_count=res["word_count"],
                extracted_text=res["text"],
                user_id=self.user_id,
            )

            if not run_full_pipeline:
                self.after(0, lambda: self._on_simple_upload_success(doc_id, title, res["word_count"], res["page_count"]))
                return

            # Run Full Auto-Pipeline: Summary -> Questions/Quiz -> Flashcards
            # Step 2: Summary
            self.after(0, lambda: self.status_label.configure(
                text=f"⏳ Step 2/4: Extracted {res['word_count']:,} words! Synthesizing AI Summary...",
                text_color=COLORS["primary"],
            ))
            sum_res = SummaryService.generate_and_save(doc_id, summary_type="executive", user_id=self.user_id)

            # Step 3: Exam Questions & Quiz
            self.after(0, lambda: self.status_label.configure(
                text="⏳ Step 3/4: Summary generated! Formulating 5 Exam Questions & Quiz...",
                text_color=COLORS["primary"],
            ))
            q_res = QuestionService.generate_questions_for_document(doc_id, count=5, user_id=self.user_id)

            # Step 4: Flashcards Deck
            self.after(0, lambda: self.status_label.configure(
                text="⏳ Step 4/4: Quiz created! Formulating 6 Active Recall Flashcards...",
                text_color=COLORS["primary"],
            ))
            deck_name = f"{title} Deck"
            fc_res = FlashcardService.generate_flashcards_for_document(doc_id, deck_name=deck_name, count=6, user_id=self.user_id)

            # Award bonus study XP
            UserStatsModel.add_xp(50, user_id=self.user_id)

            pipeline_data = {
                "doc_id": doc_id,
                "title": title,
                "words": res["word_count"],
                "pages": res["page_count"],
                "summary": sum_res.get("success", False),
                "quiz_id": q_res.get("quiz_id"),
                "question_count": q_res.get("count", 0),
                "deck_name": deck_name,
                "card_count": fc_res.get("count", 0),
            }

            self.after(0, lambda: self._on_pipeline_success(pipeline_data))

        except Exception as e:
            self.after(0, lambda: self._on_upload_error(str(e)))

    def _on_simple_upload_success(self, doc_id, title, words, pages):
        self.upload_btn.configure(state="normal", text="📂 Choose File & Process All")
        self.status_label.configure(text=f"✅ Successfully processed '{title}' ({words:,} words, {pages} pages)!", text_color=COLORS["success"])
        self.title_entry.delete(0, "end")
        self.refresh_list()
        if self.on_stats_updated:
            self.on_stats_updated()
        messagebox.showinfo("Success", f"Document '{title}' added to your library!")

    def _on_pipeline_success(self, data: dict):
        self.upload_btn.configure(state="normal", text="📂 Choose File & Process All")
        self.status_label.configure(
            text=f"🎉 Full Study Kit Ready! '{data['title']}' ({data['words']:,} words) processed with Summary, Quiz, and Flashcards!",
            text_color=COLORS["success"],
        )
        self.title_entry.delete(0, "end")
        self.refresh_list()
        if self.on_stats_updated:
            self.on_stats_updated()

        self._show_study_kit_modal(data)

    def _show_study_kit_modal(self, data: dict):
        """Displays celebratory modal dialog with instant jump buttons."""
        top = ctk.CTkToplevel(self)
        top.title("StudyForge AI • Study Kit Ready")
        top.geometry("620x460")
        top.grab_set()

        hdr = ctk.CTkLabel(top, text="🎉 Full Study Kit Formulated!", font=FONTS["header"], text_color=COLORS["primary"])
        hdr.pack(anchor="w", padx=24, pady=(20, 4))

        sub = ctk.CTkLabel(
            top,
            text=f"All study assets for '{data['title']}' have been generated and saved to your workspace:",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
        )
        sub.pack(anchor="w", padx=24, pady=(0, 16))

        # Highlights card
        box = ctk.CTkFrame(top, fg_color=(COLORS["bg_light"], COLORS["bg_dark"]), corner_radius=12, border_width=1, border_color=(COLORS["border_light"], COLORS["border_dark"]))
        box.pack(fill="x", padx=24, pady=(0, 20))

        items = [
            f"📄 Document Extracted: {data['pages']} page(s), {data['words']:,} words",
            "📑 High-Yield Executive Summary & Key Concept Glossary ready",
            f"❓ {data['question_count']} Multiple-Choice Questions Formulated (Mastery Quiz #{data['quiz_id']})",
            f"🗂️ {data['card_count']} Active Recall Flashcards ({data['deck_name']})",
            "⚡ +50 Study Kit XP Earned!",
        ]
        for itm in items:
            lbl = ctk.CTkLabel(box, text=f"• {itm}", font=FONTS["body_bold" if "XP" in itm else "small"], text_color=(COLORS["primary"] if "XP" in itm else (COLORS["text_dark"], COLORS["text_light"])))
            lbl.pack(anchor="w", padx=16, pady=4)

        ctk.CTkLabel(top, text="What would you like to do next?", font=FONTS["subheader"]).pack(anchor="w", padx=24, pady=(0, 10))

        btn_row = ctk.CTkFrame(top, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 16))
        btn_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        b1 = ctk.CTkButton(
            btn_row,
            text="🎯 Take Quiz",
            height=38,
            font=FONTS["small"],
            fg_color="#059669",
            hover_color="#047857",
            command=lambda: [top.destroy(), self.navigate_fn("Quiz")],
        )
        b1.grid(row=0, column=0, padx=4, sticky="ew")

        b2 = ctk.CTkButton(
            btn_row,
            text="📑 View Summary",
            height=38,
            font=FONTS["small"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=lambda: [top.destroy(), self.navigate_fn("AI Summaries")],
        )
        b2.grid(row=0, column=1, padx=4, sticky="ew")

        b3 = ctk.CTkButton(
            btn_row,
            text="🗂️ Flashcards",
            height=38,
            font=FONTS["small"],
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            command=lambda: [top.destroy(), self.navigate_fn("Flashcards")],
        )
        b3.grid(row=0, column=2, padx=4, sticky="ew")

        b4 = ctk.CTkButton(
            btn_row,
            text="📊 Dashboard",
            height=38,
            font=FONTS["small"],
            fg_color=(COLORS["primary_light"], "#334155"),
            text_color=COLORS["primary"],
            hover_color=COLORS["primary"],
            command=lambda: [top.destroy(), self.navigate_fn("Dashboard")],
        )
        b4.grid(row=0, column=3, padx=4, sticky="ew")

    def _on_upload_error(self, err_msg):
        self.upload_btn.configure(state="normal", text="📂 Choose File & Process All")
        self.status_label.configure(text=f"❌ {err_msg}", text_color=COLORS["danger"])
        messagebox.showerror("Upload Error", err_msg)

    def refresh_list(self):
        # Clear existing items
        for widget in self.list_container.winfo_children():
            widget.destroy()

        docs = DocumentModel.get_all(user_id=self.user_id)
        if not docs:
            empty_lbl = ctk.CTkLabel(
                self.list_container,
                text="No documents in your library yet. Choose a file above to get started!",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            )
            empty_lbl.pack(pady=24)
            return

        for doc in docs:
            card = ctk.CTkFrame(
                self.list_container,
                fg_color=(COLORS["card_light"], COLORS["card_dark"]),
                corner_radius=12,
                border_width=1,
                border_color=(COLORS["border_light"], COLORS["border_dark"]),
            )
            card.pack(fill="x", pady=6)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=16, pady=12)

            title_lbl = ctk.CTkLabel(
                info_frame,
                text=doc["title"],
                font=FONTS["body_bold"],
                text_color=(COLORS["text_dark"], COLORS["text_light"]),
            )
            title_lbl.pack(anchor="w")

            meta_text = f"Format: {doc['file_type']}  •  Pages: {doc['page_count']}  •  Words: {doc['word_count']:,}  •  Size: {format_file_size(doc['file_size'])}  •  Uploaded: {str(doc['created_at'])[:16]}"
            meta_lbl = ctk.CTkLabel(
                info_frame,
                text=meta_text,
                font=FONTS["caption"],
                text_color=COLORS["text_muted"],
            )
            meta_lbl.pack(anchor="w", pady=(2, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=16, pady=12)

            kit_btn = ctk.CTkButton(
                btn_frame,
                text="⚡ Study Kit",
                width=90,
                height=32,
                font=FONTS["small"],
                fg_color="#059669",
                hover_color="#047857",
                command=lambda d=doc: self._generate_kit_for_doc(d),
            )
            kit_btn.pack(side="left", padx=4)

            view_btn = ctk.CTkButton(
                btn_frame,
                text="🔍 Inspect",
                width=76,
                height=32,
                font=FONTS["small"],
                fg_color=(COLORS["primary_light"], "#334155"),
                text_color=COLORS["primary"],
                hover_color=COLORS["primary"],
                command=lambda d=doc: self._inspect_document(d),
            )
            view_btn.pack(side="left", padx=4)

            del_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️ Delete",
                width=72,
                height=32,
                font=FONTS["small"],
                fg_color=(COLORS["danger_light"], "#7f1d1d"),
                text_color=COLORS["danger"],
                hover_color=COLORS["danger"],
                command=lambda did=doc["id"], dtitle=doc["title"]: self._delete_document(did, dtitle),
            )
            del_btn.pack(side="left", padx=4)

    def _generate_kit_for_doc(self, doc):
        """Generate study kit for an already uploaded document."""
        self.status_label.configure(text=f"⏳ Processing Study Kit for '{doc['title']}'...", text_color=COLORS["primary"])
        
        def _worker():
            try:
                sum_res = SummaryService.generate_and_save(doc["id"], summary_type="executive", user_id=self.user_id)
                q_res = QuestionService.generate_questions_for_document(doc["id"], count=5, user_id=self.user_id)
                deck_name = f"{doc['title']} Deck"
                fc_res = FlashcardService.generate_flashcards_for_document(doc["id"], deck_name=deck_name, count=6, user_id=self.user_id)
                UserStatsModel.add_xp(50, user_id=self.user_id)

                pipeline_data = {
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "words": doc["word_count"],
                    "pages": doc["page_count"],
                    "summary": sum_res.get("success", False),
                    "quiz_id": q_res.get("quiz_id"),
                    "question_count": q_res.get("count", 0),
                    "deck_name": deck_name,
                    "card_count": fc_res.get("count", 0),
                }
                self.after(0, lambda: self._on_pipeline_success(pipeline_data))
            except Exception as e:
                self.after(0, lambda: self._on_upload_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _inspect_document(self, doc):
        """Show full extracted text in a modal viewer."""
        top = ctk.CTkToplevel(self)
        top.title(f"Document Viewer: {doc['title']}")
        top.geometry("750x550")
        top.grab_set()

        hdr = ctk.CTkLabel(top, text=f"📖 {doc['title']}", font=FONTS["header"])
        hdr.pack(anchor="w", padx=20, pady=(16, 4))

        meta = ctk.CTkLabel(top, text=f"Type: {doc['file_type']} | Words: {doc['word_count']:,} | Pages: {doc['page_count']}", font=FONTS["small"], text_color=COLORS["text_muted"])
        meta.pack(anchor="w", padx=20, pady=(0, 10))

        text_box = ctk.CTkTextbox(top, font=FONTS["body"], wrap="word")
        text_box.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        text_box.insert("1.0", doc["extracted_text"])
        text_box.configure(state="disabled")

    def _delete_document(self, doc_id: int, title: str):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{title}'?"):
            DocumentModel.delete(doc_id)
            self.refresh_list()
