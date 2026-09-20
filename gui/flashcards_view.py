"""Flashcards Study View for StudyForge AI."""
import threading
from tkinter import messagebox
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from database.models import FlashcardModel, DocumentModel
from services.flashcard_service import FlashcardService

class FlashcardsView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_fn, on_stats_updated=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn
        self.on_stats_updated = on_stats_updated

        self.cards = []
        self.current_idx = 0
        self.is_flipped = False

        # 1. Deck Selector & Generator Row
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

        self.decks = FlashcardModel.get_decks()
        deck_names = [d["deck_name"] for d in self.decks] if self.decks else ["No decks available"]

        self.deck_lbl = ctk.CTkLabel(self.top_row, text="Select Deck:", font=FONTS["body_bold"])
        self.deck_lbl.pack(side="left", padx=(0, 8))

        self.deck_dropdown = ctk.CTkOptionMenu(
            self.top_row,
            values=deck_names,
            height=36,
            width=260,
            font=FONTS["small"],
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"],
            command=self._on_deck_selected,
        )
        self.deck_dropdown.pack(side="left", padx=(0, 14))

        self.new_deck_btn = ctk.CTkButton(
            self.top_row,
            text="✨ Generate New Deck",
            height=36,
            font=FONTS["small"],
            fg_color="#059669",
            hover_color="#047857",
            command=self._open_generator_dialog,
        )
        self.new_deck_btn.pack(side="right")

        # 2. Main Flashcard Flip Area
        self.card_container = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=20,
            border_width=2,
            border_color=(COLORS["primary_border"], "#334155"),
            height=320,
        )
        self.card_container.pack(fill="x", padx=16, pady=(0, 16))
        self.card_container.pack_propagate(False)

        # Header inside card: Topic & Side indicator
        self.card_header = ctk.CTkFrame(self.card_container, fg_color="transparent")
        self.card_header.pack(fill="x", padx=24, pady=(20, 10))

        self.topic_badge = ctk.CTkLabel(
            self.card_header,
            text="TOPIC",
            font=FONTS["caption"],
            fg_color=(COLORS["primary_light"], "#1e3a8a"),
            text_color=(COLORS["primary"], "#93c5fd"),
            corner_radius=8,
            padx=10,
            pady=3,
        )
        self.topic_badge.pack(side="left")

        self.side_badge = ctk.CTkLabel(
            self.card_header,
            text="❓ Front: Concept / Question",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
        )
        self.side_badge.pack(side="right")

        # Central Card Text
        self.card_text = ctk.CTkLabel(
            self.card_container,
            text="Select or generate a flashcard deck to begin active recall.",
            font=("Segoe UI", 16, "bold"),
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
            wraplength=680,
            justify="center",
        )
        self.card_text.pack(expand=True, fill="both", padx=30, pady=20)

        # Bottom flip hint
        self.flip_hint = ctk.CTkLabel(
            self.card_container,
            text="💡 Click 'Flip Card' below to reveal answer",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
        )
        self.flip_hint.pack(side="bottom", pady=(0, 16))

        # 3. Card Action Controls
        self.controls_card = ctk.CTkFrame(
            self,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
        )
        self.controls_card.pack(fill="x", padx=16, pady=(0, 16))

        # Nav row
        self.nav_row = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        self.nav_row.pack(fill="x", padx=24, pady=(16, 12))

        self.prev_btn = ctk.CTkButton(
            self.nav_row,
            text="⬅️ Previous",
            width=110,
            height=38,
            font=FONTS["small"],
            fg_color=(COLORS["bg_light"], COLORS["bg_dark"]),
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
            command=self._prev_card,
        )
        self.prev_btn.pack(side="left")

        self.flip_btn = ctk.CTkButton(
            self.nav_row,
            text="🔄 Flip Card",
            width=140,
            height=38,
            font=FONTS["body_bold"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._flip_card,
        )
        self.flip_btn.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(
            self.nav_row,
            text="Next ➡️",
            width=110,
            height=38,
            font=FONTS["small"],
            fg_color=(COLORS["bg_light"], COLORS["bg_dark"]),
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
            command=self._next_card,
        )
        self.next_btn.pack(side="right")

        # Spaced Repetition Rating Buttons
        self.rate_label = ctk.CTkLabel(self.controls_card, text="Rate Your Recall Mastery:", font=FONTS["small"], text_color=COLORS["text_muted"])
        self.rate_label.pack(anchor="w", padx=24, pady=(4, 6))

        self.rate_row = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        self.rate_row.pack(fill="x", padx=24, pady=(0, 16))
        self.rate_row.grid_columnconfigure((0, 1, 2), weight=1)

        self.hard_btn = ctk.CTkButton(
            self.rate_row,
            text="🔴 Hard (Review Again)",
            font=FONTS["small"],
            height=34,
            fg_color=(COLORS["danger_light"], "#7f1d1d"),
            text_color=COLORS["danger"],
            hover_color=COLORS["danger"],
            command=lambda: self._rate_mastery("learning"),
        )
        self.hard_btn.grid(row=0, column=0, padx=4, sticky="ew")

        self.med_btn = ctk.CTkButton(
            self.rate_row,
            text="🟡 Medium (Good)",
            font=FONTS["small"],
            height=34,
            fg_color=(COLORS["warning_light"], "#78350f"),
            text_color=COLORS["warning"],
            hover_color=COLORS["warning"],
            command=lambda: self._rate_mastery("reviewing"),
        )
        self.med_btn.grid(row=0, column=1, padx=4, sticky="ew")

        self.easy_btn = ctk.CTkButton(
            self.rate_row,
            text="🟢 Mastered! (+10 XP)",
            font=FONTS["small"],
            height=34,
            fg_color=(COLORS["success_light"], "#064e3b"),
            text_color=COLORS["success"],
            hover_color=COLORS["success"],
            command=lambda: self._rate_mastery("mastered"),
        )
        self.easy_btn.grid(row=0, column=2, padx=4, sticky="ew")

        # Load initial deck if exists
        if self.decks:
            self._load_deck(self.decks[0]["deck_name"])

    def _on_deck_selected(self, deck_name):
        self._load_deck(deck_name)

    def _load_deck(self, deck_name: str):
        self.cards = FlashcardModel.get_by_deck(deck_name)
        self.current_idx = 0
        self.is_flipped = False
        self._render_card()

    def _render_card(self):
        if not self.cards:
            self.card_text.configure(text="No cards found in this deck.")
            return

        card = self.cards[self.current_idx]
        total = len(self.cards)

        self.topic_badge.configure(text=f" {card.get('topic', 'General').upper()} ({self.current_idx + 1}/{total}) ")

        if self.is_flipped:
            self.side_badge.configure(text="💡 Back: Answer / Explanation")
            self.card_text.configure(text=card["back_text"])
            self.flip_btn.configure(text="🔄 Flip to Question")
            self.card_container.configure(fg_color=(COLORS["primary_light"], "#1e293b"))
        else:
            self.side_badge.configure(text="❓ Front: Concept / Question")
            self.card_text.configure(text=card["front_text"])
            self.flip_btn.configure(text="🔄 Flip to Answer")
            self.card_container.configure(fg_color=(COLORS["card_light"], COLORS["card_dark"]))

        self.prev_btn.configure(state="normal" if self.current_idx > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_idx < len(self.cards) - 1 else "disabled")

    def _flip_card(self):
        self.is_flipped = not self.is_flipped
        self._render_card()

    def _prev_card(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.is_flipped = False
            self._render_card()

    def _next_card(self):
        if self.current_idx < len(self.cards) - 1:
            self.current_idx += 1
            self.is_flipped = False
            self._render_card()

    def _rate_mastery(self, mastery_level: str):
        if not self.cards:
            return
        card = self.cards[self.current_idx]
        FlashcardService.record_card_review(card["id"], mastery_level)
        if self.on_stats_updated:
            self.on_stats_updated()
        # Automatically advance to next card
        if self.current_idx < len(self.cards) - 1:
            self._next_card()

    def _open_generator_dialog(self):
        docs = DocumentModel.get_all()
        if not docs:
            messagebox.showwarning("Warning", "Please upload a study document first before generating flashcards!")
            return

        top = ctk.CTkToplevel(self)
        top.title("Generate Flashcard Deck")
        top.geometry("480x360")
        top.grab_set()

        hdr = ctk.CTkLabel(top, text="✨ Synthesize Flashcard Deck", font=FONTS["header"])
        hdr.pack(anchor="w", padx=24, pady=(20, 6))

        doc_map = {d["id"]: d["title"] for d in docs}
        doc_drop = ctk.CTkOptionMenu(top, values=[d["title"] for d in docs], width=300, font=FONTS["body"])
        doc_drop.pack(anchor="w", padx=24, pady=8)

        deck_entry = ctk.CTkEntry(top, placeholder_text="Deck Name (e.g. Bio 101 Exam Deck)", width=300, font=FONTS["body"])
        deck_entry.pack(anchor="w", padx=24, pady=8)

        def _generate():
            sel_title = doc_drop.get()
            did = next((k for k, v in doc_map.items() if v == sel_title), None)
            dname = deck_entry.get().strip() or f"{sel_title} Deck"
            top.destroy()

            threading.Thread(
                target=lambda: self._generate_cards_worker(did, dname),
                daemon=True,
            ).start()

        btn = ctk.CTkButton(top, text="🚀 Generate Deck", font=FONTS["body_bold"], fg_color=COLORS["primary"], command=_generate)
        btn.pack(anchor="w", padx=24, pady=16)

    def _generate_cards_worker(self, doc_id: int, deck_name: str):
        res = FlashcardService.generate_flashcards_for_document(doc_id, deck_name=deck_name, count=6)
        if res.get("success"):
            self.after(0, lambda: self._on_deck_generated(deck_name))
        else:
            self.after(0, lambda: messagebox.showerror("Error", res.get("error", "Failed to generate deck.")))

    def _on_deck_generated(self, deck_name: str):
        self.decks = FlashcardModel.get_decks()
        deck_names = [d["deck_name"] for d in self.decks]
        self.deck_dropdown.configure(values=deck_names)
        self.deck_dropdown.set(deck_name)
        self._load_deck(deck_name)
        messagebox.showinfo("Success", f"Created deck '{deck_name}'!")
