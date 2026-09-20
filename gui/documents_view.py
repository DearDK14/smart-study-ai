"""Documents Management View for StudyForge AI."""
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from services.pdf_service import PDFService
from database.models import DocumentModel
from utils.validators import validate_file_extension, validate_file_size
from utils.helpers import format_file_size, sanitize_filename
from config.settings import UPLOADS_DIR

class DocumentsView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn

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
            text="Select lecture notes, chapters, or articles to extract content and power AI summaries, quizzes, and flashcards.",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
        )
        self.upload_desc.pack(anchor="w", padx=20, pady=(0, 12))

        # Title Input & File Pick Button
        self.input_row = ctk.CTkFrame(self.upload_card, fg_color="transparent")
        self.input_row.pack(fill="x", padx=20, pady=(0, 14))

        self.title_entry = ctk.CTkEntry(
            self.input_row,
            placeholder_text="Optional custom title (e.g. Bio Chapter 4: Cellular Respiration)",
            height=40,
            font=FONTS["body"],
        )
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.upload_btn = ctk.CTkButton(
            self.input_row,
            text="📂 Choose File & Process",
            font=FONTS["body_bold"],
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._handle_file_upload,
        )
        self.upload_btn.pack(side="right")

        # Loading status bar
        self.status_label = ctk.CTkLabel(
            self.upload_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["primary"],
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 12))

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

        # Run extraction in background thread to keep GUI responsive
        self.upload_btn.configure(state="disabled", text="⏳ Extracting...")
        self.status_label.configure(text="Extracting text and analyzing document structure...")

        threading.Thread(
            target=self._process_upload_worker,
            args=(file_path, custom_title),
            daemon=True,
        ).start()

    def _process_upload_worker(self, file_path: str, custom_title: str):
        try:
            import os
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

            doc_id = DocumentModel.create(
                filename=clean_name,
                filepath=save_path,
                title=title,
                file_type=file_type,
                file_size=file_size,
                page_count=res["page_count"],
                word_count=res["word_count"],
                extracted_text=res["text"],
            )

            self.after(0, lambda: self._on_upload_success(doc_id, title, res["word_count"], res["page_count"]))

        except Exception as e:
            self.after(0, lambda: self._on_upload_error(str(e)))

    def _on_upload_success(self, doc_id, title, words, pages):
        self.upload_btn.configure(state="normal", text="📂 Choose File & Process")
        self.status_label.configure(text=f"✅ Successfully processed '{title}' ({words:,} words, {pages} pages)!", text_color=COLORS["success"])
        self.title_entry.delete(0, "end")
        self.refresh_list()
        messagebox.showinfo("Success", f"Document '{title}' successfully added to your library!")

    def _on_upload_error(self, err_msg):
        self.upload_btn.configure(state="normal", text="📂 Choose File & Process")
        self.status_label.configure(text=f"❌ {err_msg}", text_color=COLORS["danger"])
        messagebox.showerror("Upload Error", err_msg)

    def refresh_list(self):
        # Clear existing items
        for widget in self.list_container.winfo_children():
            widget.destroy()

        docs = DocumentModel.get_all()
        if not docs:
            empty_lbl = ctk.CTkLabel(
                self.list_container,
                text="No documents in your library yet. Choose a file above to get started!",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            )
            empty_lbl.pack(pady=20)
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

            view_btn = ctk.CTkButton(
                btn_frame,
                text="🔍 Inspect",
                width=80,
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
                width=76,
                height=32,
                font=FONTS["small"],
                fg_color=(COLORS["danger_light"], "#7f1d1d"),
                text_color=COLORS["danger"],
                hover_color=COLORS["danger"],
                command=lambda did=doc["id"], dtitle=doc["title"]: self._delete_document(did, dtitle),
            )
            del_btn.pack(side="left", padx=4)

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
