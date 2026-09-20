"""Interactive Flashcards study page with 3D flip effect and spaced repetition."""
import streamlit as st
from services.flashcard_service import FlashcardService
from database.models import FlashcardModel, DocumentModel
from components.cards import render_flashcard_widget

def render_flashcards_page():
    """Renders flashcards deck player and generator."""
    st.markdown("## 🗂️ Interactive Flashcard Decks")
    st.markdown("Master difficult vocabulary, formulas, and concepts with flip cards and active recall.")

    tab_study, tab_gen = st.tabs(["📖 Study Flashcards", "✨ Generate New Deck"])

    with tab_gen:
        docs = DocumentModel.get_all()
        if not docs:
            st.warning("⚠️ Please upload a study document before generating flashcard decks.")
        else:
            doc_map = {d["id"]: d["title"] for d in docs}
            c1, c2 = st.columns([2, 1])
            with c1:
                selected_doc_id = st.selectbox("Source Document", options=list(doc_map.keys()), format_func=lambda x: doc_map[x], key="fc_doc_sel")
                custom_deck_name = st.text_input("Deck Name", placeholder="e.g. Bio-101 Cellular Energy Deck")
            with c2:
                card_count = st.slider("Number of Cards", min_value=3, max_value=15, value=6, key="fc_count")

            if st.button("🚀 Synthesize Flashcards", type="primary", use_container_width=True):
                with st.spinner("Formulating high-yield concept cards..."):
                    res = FlashcardService.generate_flashcards_for_document(
                        document_id=selected_doc_id,
                        deck_name=custom_deck_name.strip() if custom_deck_name.strip() else None,
                        count=card_count,
                    )
                    if res["success"]:
                        st.success(f"🎉 Created deck '{res['deck_name']}' with {res['count']} cards!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed: {res.get('error')}")

    with tab_study:
        decks = FlashcardModel.get_decks()
        if not decks:
            st.info("No flashcard decks created yet. Switch to the 'Generate New Deck' tab to create your first deck!")
            return

        deck_names = [d["deck_name"] for d in decks]
        selected_deck = st.selectbox("Select Flashcard Deck", options=deck_names)

        cards = FlashcardModel.get_by_deck(selected_deck)
        if not cards:
            st.warning("No cards found in this deck.")
            return

        # Initialize deck state in session
        state_key = f"fc_index_{selected_deck}"
        flip_key = f"fc_flipped_{selected_deck}"
        if state_key not in st.session_state:
            st.session_state[state_key] = 0
        if flip_key not in st.session_state:
            st.session_state[flip_key] = False

        idx = st.session_state[state_key]
        if idx >= len(cards):
            idx = 0
            st.session_state[state_key] = 0

        current_card = cards[idx]

        # Progress bar for deck
        progress_val = (idx + 1) / len(cards)
        st.progress(progress_val)
        st.caption(f"Card {idx + 1} of {len(cards)} • Deck: **{selected_deck}**")

        # Flashcard Display
        render_flashcard_widget(
            front=current_card["front_text"],
            back=current_card["back_text"],
            topic=current_card.get("topic", "General"),
            is_flipped=st.session_state[flip_key],
        )

        # Flip & Navigation Controls
        c_prev, c_flip, c_next = st.columns([1, 2, 1])
        with c_prev:
            if st.button("⬅️ Previous", use_container_width=True, disabled=(idx == 0)):
                st.session_state[state_key] = max(0, idx - 1)
                st.session_state[flip_key] = False
                st.rerun()
        with c_flip:
            flip_label = "🔄 Flip to Front" if st.session_state[flip_key] else "🔄 Flip to Answer"
            if st.button(flip_label, type="primary", use_container_width=True):
                st.session_state[flip_key] = not st.session_state[flip_key]
                st.rerun()
        with c_next:
            if st.button("Next ➡️", use_container_width=True, disabled=(idx == len(cards) - 1)):
                st.session_state[state_key] = min(len(cards) - 1, idx + 1)
                st.session_state[flip_key] = False
                st.rerun()

        # Mastery Self-Rating
        st.write("")
        st.markdown("**Rate Your Recall Confidence:**")
        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button("🔴 Hard (Review Again)", use_container_width=True):
                FlashcardService.record_card_review(current_card["id"], "learning")
                st.toast("Marked as Hard (+10 XP) ⚡")
        with r2:
            if st.button("🟡 Medium (Good)", use_container_width=True):
                FlashcardService.record_card_review(current_card["id"], "reviewing")
                st.toast("Marked as Medium (+10 XP) ⚡")
        with r3:
            if st.button("🟢 Mastered! (Easy)", use_container_width=True):
                FlashcardService.record_card_review(current_card["id"], "mastered")
                st.toast("Marked as Mastered! (+10 XP) ⚡")
