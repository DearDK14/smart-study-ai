"""Notebook View for StudyForge AI."""
from tkinter import messagebox
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from database.models import NoteModel, DocumentModel

class NotebookView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn

        # 1. Top Note Editor Card
        self.editor_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.editor_card.pack(fill="x", padx=16, pady=(10, 16))

        self.editor_title = ctk.CTkLabel(
            self.editor_card,
            text="📓 Personal Study Notes & Scratchpad",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.editor_title.pack(anchor="w", padx=20, pady=(16, 4))

        # Title & Tags Row
        self.meta_row = ctk.CTkFrame(self.editor_card, fg_color="transparent")
        self.meta_row.pack(fill="x", padx=20, pady=(0, 10))

        self.title_entry = ctk.CTkEntry(
            self.meta_row,
            placeholder_text="Note Title (e.g. Krebs Cycle Key Steps)",
            height=38,
            font=FONTS["body"],
        )
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.tag_entry = ctk.CTkEntry(
            self.meta_row,
            placeholder_text="Tags (e.g. Biology, Metabolism)",
            height=38,
            width=220,
            font=FONTS["body"],
        )
        self.tag_entry.pack(side="right")

        # Note Text Content
        self.content_text = ctk.CTkTextbox(
            self.editor_card,
            height=140,
            font=FONTS["body"],
            wrap="word",
        )
        self.content_text.pack(fill="x", padx=20, pady=(0, 12))

        # Save Button Row
        self.btn_row = ctk.CTkFrame(self.editor_card, fg_color="transparent")
        self.btn_row.pack(fill="x", padx=20, pady=(0, 16))

        self.save_btn = ctk.CTkButton(
            self.btn_row,
            text="💾 Save Note to SQLite",
            font=FONTS["body_bold"],
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._save_note,
        )
        self.save_btn.pack(side="right")

        # 2. Search & Saved Notes List
        self.notes_header = ctk.CTkFrame(self, fg_color="transparent")
        self.notes_header.pack(fill="x", padx=16, pady=(4, 8))

        self.list_title = ctk.CTkLabel(
            self.notes_header,
            text="📚 Saved Notes",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.list_title.pack(side="left")

        self.search_entry = ctk.CTkEntry(
            self.notes_header,
            placeholder_text="🔍 Search notes by title or content...",
            width=280,
            height=34,
            font=FONTS["small"],
        )
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_notes())

        self.notes_container = ctk.CTkFrame(self, fg_color="transparent")
        self.notes_container.pack(fill="x", padx=16, pady=(0, 24))

        self.refresh_notes()

    def _save_note(self):
        title = self.title_entry.get().strip()
        tags = self.tag_entry.get().strip() or "General"
        content = self.content_text.get("1.0", "end").strip()

        if not title:
            messagebox.showwarning("Warning", "Please enter a note title.")
            return
        if not content:
            messagebox.showwarning("Warning", "Note content cannot be empty.")
            return

        NoteModel.create(title=title, content=content, tags=tags)
        self.title_entry.delete(0, "end")
        self.tag_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        self.refresh_notes()
        messagebox.showinfo("Saved", f"Note '{title}' saved successfully!")

    def refresh_notes(self):
        for w in self.notes_container.winfo_children():
            w.destroy()

        query = self.search_entry.get().strip().lower()
        all_notes = NoteModel.get_all()

        if query:
            filtered = [n for n in all_notes if query in n["title"].lower() or query in n["content"].lower() or query in n.get("tags", "").lower()]
        else:
            filtered = all_notes

        if not filtered:
            msg = "No matching notes found." if query else "No notes saved yet. Compose your first study note above!"
            lbl = ctk.CTkLabel(self.notes_container, text=msg, font=FONTS["body"], text_color=COLORS["text_muted"])
            lbl.pack(pady=16)
            return

        for note in filtered:
            card = ctk.CTkFrame(
                self.notes_container,
                fg_color=(COLORS["card_light"], COLORS["card_dark"]),
                corner_radius=12,
                border_width=1,
                border_color=(COLORS["border_light"], COLORS["border_dark"]),
            )
            card.pack(fill="x", pady=6)

            hdr = ctk.CTkFrame(card, fg_color="transparent")
            hdr.pack(fill="x", padx=16, pady=(10, 4))

            tag_lbl = ctk.CTkLabel(
                hdr,
                text=f" 🏷️ {note.get('tags', 'General')} ",
                font=FONTS["caption"],
                fg_color=(COLORS["primary_light"], "#1e3a8a"),
                text_color=(COLORS["primary"], "#93c5fd"),
                corner_radius=8,
            )
            tag_lbl.pack(side="left", padx=(0, 10))

            title_lbl = ctk.CTkLabel(hdr, text=note["title"], font=FONTS["body_bold"])
            title_lbl.pack(side="left")

            del_btn = ctk.CTkButton(
                hdr,
                text="🗑️ Delete",
                width=74,
                height=26,
                font=FONTS["caption"],
                fg_color=(COLORS["danger_light"], "#7f1d1d"),
                text_color=COLORS["danger"],
                hover_color=COLORS["danger"],
                command=lambda nid=note["id"], ntitle=note["title"]: self._delete_note(nid, ntitle),
            )
            del_btn.pack(side="right")

            time_lbl = ctk.CTkLabel(hdr, text=str(note.get("created_at"))[:16], font=FONTS["caption"], text_color=COLORS["text_muted"])
            time_lbl.pack(side="right", padx=12)

            cnt_lbl = ctk.CTkLabel(card, text=note["content"], font=FONTS["small"], justify="left", wraplength=720)
            cnt_lbl.pack(anchor="w", padx=16, pady=(0, 12))

    def _delete_note(self, note_id: int, title: str):
        if messagebox.askyesno("Confirm Delete", f"Delete note '{title}'?"):
            NoteModel.delete(note_id)
            self.refresh_notes()
