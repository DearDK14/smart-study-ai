"""AI Summaries View for StudyForge AI."""
import threading
from tkinter import messagebox
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from database.models import DocumentModel, SummaryModel
from services.summary_service import SummaryService

class SummariesView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn

        # 1. Top Control Card
        self.control_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.control_card.pack(fill="x", padx=16, pady=(10, 16))

        self.title_lbl = ctk.CTkLabel(
            self.control_card,
            text="📑 AI Study Summaries & Exam Cram",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.title_lbl.pack(anchor="w", padx=20, pady=(16, 4))

        self.desc_lbl = ctk.CTkLabel(
            self.control_card,
            text="Transform detailed textbook chapters into high-yield executive summaries, bullet points, and exam takeaways.",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
        )
        self.desc_lbl.pack(anchor="w", padx=20, pady=(0, 12))

        # Selectors row
        self.sel_row = ctk.CTkFrame(self.control_card, fg_color="transparent")
        self.sel_row.pack(fill="x", padx=20, pady=(0, 14))

        self.docs_list = DocumentModel.get_all()
        self.doc_map = {d["id"]: d["title"] for d in self.docs_list}
        options = [d["title"] for d in self.docs_list] if self.docs_list else ["No documents available"]

        self.doc_dropdown = ctk.CTkOptionMenu(
            self.sel_row,
            values=options,
            height=40,
            width=280,
            font=FONTS["body"],
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"],
        )
        self.doc_dropdown.pack(side="left", padx=(0, 12))

        self.type_dropdown = ctk.CTkOptionMenu(
            self.sel_row,
            values=["Comprehensive Executive Summary", "High-Yield Exam Cram", "Key Concepts & Glossary"],
            height=40,
            width=260,
            font=FONTS["body"],
            fg_color=(COLORS["primary_light"], "#334155"),
            text_color=(COLORS["primary"], "white"),
            button_color=COLORS["primary"],
        )
        self.type_dropdown.pack(side="left", padx=(0, 12))

        self.gen_btn = ctk.CTkButton(
            self.sel_row,
            text="✨ Generate AI Summary",
            font=FONTS["body_bold"],
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._handle_generate,
        )
        self.gen_btn.pack(side="right")

        # Loading / Status label
        self.status_lbl = ctk.CTkLabel(
            self.control_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["primary"],
        )
        self.status_lbl.pack(anchor="w", padx=20, pady=(0, 12))

        # 2. Summary Display Card
        self.display_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.display_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.display_header = ctk.CTkFrame(self.display_card, fg_color="transparent")
        self.display_header.pack(fill="x", padx=20, pady=(16, 8))

        self.display_title = ctk.CTkLabel(
            self.display_header,
            text="📋 Generated Summary Content",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.display_title.pack(side="left")

        self.copy_btn = ctk.CTkButton(
            self.display_header,
            text="📋 Copy to Clipboard",
            height=32,
            width=140,
            font=FONTS["small"],
            fg_color=(COLORS["primary_light"], "#334155"),
            text_color=COLORS["primary"],
            hover_color=COLORS["primary"],
            command=self._copy_to_clipboard,
        )
        self.copy_btn.pack(side="right")

        self.summary_text = ctk.CTkTextbox(
            self.display_card,
            font=FONTS["body"],
            height=260,
            wrap="word",
        )
        self.summary_text.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # 3. Previously Saved Summaries Section
        self.history_header = ctk.CTkFrame(self, fg_color="transparent")
        self.history_header.pack(fill="x", padx=16, pady=(8, 8))

        self.history_title = ctk.CTkLabel(
            self.history_header,
            text="📜 Saved Summaries History",
            font=FONTS["subheader"],
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.history_title.pack(side="left")

        self.history_container = ctk.CTkFrame(self, fg_color="transparent")
        self.history_container.pack(fill="x", padx=16, pady=(0, 24))

        self.refresh_history()

    def _handle_generate(self):
        selected_title = self.doc_dropdown.get()
        doc_id = None
        for did, title in self.doc_map.items():
            if title == selected_title:
                doc_id = did
                break

        if not doc_id:
            messagebox.showwarning("Warning", "Please upload and select a study document first!")
            return

        summary_type = self.type_dropdown.get()

        self.gen_btn.configure(state="disabled", text="⏳ Synthesizing...")
        self.status_lbl.configure(text="AI is analyzing concepts and creating high-yield summary...")

        threading.Thread(
            target=self._generate_worker,
            args=(doc_id, summary_type),
            daemon=True,
        ).start()

    def _generate_worker(self, doc_id: int, summary_type: str):
        try:
            res = SummaryService.generate_and_save(doc_id, summary_type)
            self.after(0, lambda: self._on_generate_complete(res))
        except Exception as e:
            self.after(0, lambda: self._on_generate_error(str(e)))

    def _on_generate_complete(self, res: dict):
        self.gen_btn.configure(state="normal", text="✨ Generate AI Summary")
        if res.get("success"):
            content = res.get("content", "")
            takeaways = res.get("key_takeaways", "")
            full_display = f"EXECUTIVE SUMMARY:\n{content}\n\n"
            if takeaways:
                full_display += f"KEY EXAM TAKEAWAYS & CONCEPTS:\n{takeaways}\n\n"
            full_display += f"[Generated with {res.get('model_used', 'AI Engine')} • +{res.get('xp_awarded', 25)} XP Earned ⚡]"

            self.summary_text.delete("1.0", "end")
            self.summary_text.insert("1.0", full_display)
            self.status_lbl.configure(text="✅ Summary generated successfully!", text_color=COLORS["success"])
            self.refresh_history()
            messagebox.showinfo("Success", "AI summary successfully generated and saved to your database!")
        else:
            self._on_generate_error(res.get("error", "Failed to generate summary."))

    def _on_generate_error(self, err_msg: str):
        self.gen_btn.configure(state="normal", text="✨ Generate AI Summary")
        self.status_lbl.configure(text=f"❌ {err_msg}", text_color=COLORS["danger"])
        messagebox.showerror("Error", f"Summary generation error: {err_msg}")

    def _copy_to_clipboard(self):
        txt = self.summary_text.get("1.0", "end").strip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            messagebox.showinfo("Copied", "Summary copied to clipboard!")

    def refresh_history(self):
        for w in self.history_container.winfo_children():
            w.destroy()

        summaries = SummaryModel.get_all()
        if not summaries:
            lbl = ctk.CTkLabel(
                self.history_container,
                text="No summaries generated yet. Choose a document above and click 'Generate'!",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            )
            lbl.pack(pady=12)
            return

        for s in summaries[:5]:
            card = ctk.CTkFrame(
                self.history_container,
                fg_color=(COLORS["card_light"], COLORS["card_dark"]),
                corner_radius=12,
                border_width=1,
                border_color=(COLORS["border_light"], COLORS["border_dark"]),
            )
            card.pack(fill="x", pady=5)

            hdr = ctk.CTkFrame(card, fg_color="transparent")
            hdr.pack(fill="x", padx=16, pady=(10, 4))

            doc_title = s.get("doc_title") or "Document"
            lbl = ctk.CTkLabel(hdr, text=f"📑 {doc_title} ({s.get('summary_type', 'General')})", font=FONTS["body_bold"])
            lbl.pack(side="left")

            time_lbl = ctk.CTkLabel(hdr, text=str(s.get("created_at"))[:16], font=FONTS["caption"], text_color=COLORS["text_muted"])
            time_lbl.pack(side="right")

            preview = s.get("content", "")[:200] + "..."
            txt = ctk.CTkLabel(card, text=preview, font=FONTS["small"], text_color=COLORS["text_muted"], justify="left", wraplength=700)
            txt.pack(anchor="w", padx=16, pady=(0, 8))

            btn = ctk.CTkButton(
                card,
                text="View Full Summary",
                height=28,
                width=130,
                font=FONTS["caption"],
                fg_color=(COLORS["primary_light"], "#334155"),
                text_color=COLORS["primary"],
                hover_color=COLORS["primary"],
                command=lambda summary=s: self._load_summary_into_view(summary),
            )
            btn.pack(anchor="e", padx=16, pady=(0, 10))

    def _load_summary_into_view(self, s: dict):
        text = f"EXECUTIVE SUMMARY:\n{s.get('content', '')}\n\n"
        if s.get("key_takeaways"):
            text += f"KEY EXAM TAKEAWAYS:\n{s.get('key_takeaways')}\n\n"
        text += f"[Created: {s.get('created_at')}]"
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", text)
