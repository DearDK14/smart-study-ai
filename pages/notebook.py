"""Notebook page: student study notes and smart note-taking."""
import streamlit as st
from database.models import NoteModel, DocumentModel

def render_notebook_page():
    """Renders student study notebook."""
    st.markdown("## 📓 Study Notebook & Scratchpad")
    st.markdown("Capture thoughts, organize lecture notes, and synthesize study summaries in one place.")

    tab_new, tab_all = st.tabs(["✍️ New Note", "📚 My Notes"])

    with tab_new:
        title = st.text_input("Note Title", placeholder="e.g. Mitosis vs Meiosis Differences")
        tags = st.text_input("Tags / Subject", placeholder="Biology, Genetics, Exam-Prep")
        
        docs = DocumentModel.get_all()
        doc_map = {None: "None (Standalone Note)"}
        for d in docs:
            doc_map[d["id"]] = d["title"]

        selected_doc = st.selectbox(
            "Associate with Document (Optional)",
            options=list(doc_map.keys()),
            format_func=lambda x: doc_map[x],
        )

        content = st.text_area("Note Content (Markdown supported)", height=220, placeholder="# Core Concepts\n- Key mechanism 1\n- Key mechanism 2...")

        if st.button("💾 Save Note", type="primary", use_container_width=True):
            if not title.strip():
                st.error("Please provide a note title.")
            elif not content.strip():
                st.error("Note content cannot be empty.")
            else:
                note_id = NoteModel.create(
                    title=title.strip(),
                    content=content.strip(),
                    tags=tags.strip() if tags.strip() else "General",
                    document_id=selected_doc,
                )
                st.success(f"✅ Note saved successfully! (ID #{note_id})")
                st.rerun()

    with tab_all:
        notes = NoteModel.get_all()
        if not notes:
            st.info("No notes saved yet. Create your first note in the 'New Note' tab!")
        else:
            st.markdown(f"**Saved Notes ({len(notes)}):**")
            for n in notes:
                with st.expander(f"📌 {n['title']} ({n['tags']}) - {n['created_at']}"):
                    st.markdown(n["content"])
                    if st.button(f"🗑️ Delete Note", key=f"del_note_{n['id']}"):
                        NoteModel.delete(n["id"])
                        st.toast(f"Deleted note '{n['title']}'")
                        st.rerun()
