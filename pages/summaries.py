"""AI Summaries page: generation and reading of study summaries."""
import streamlit as st
from services.summary_service import SummaryService
from database.models import DocumentModel, SummaryModel

def render_summaries_page():
    """Renders AI summarization studio."""
    st.markdown("## 📑 AI Study Summaries")
    st.markdown("Transform long textbook chapters and complex lecture notes into high-yield executive summaries and bullet points.")

    docs = DocumentModel.get_all()
    if not docs:
        st.warning("⚠️ No documents uploaded yet. Please upload a study document first!")
        if st.button("📤 Go to Documents Upload"):
            st.session_state["current_page"] = "📚 Documents"
            st.rerun()
        return

    # Select document
    doc_options = {d["id"]: f"{d['title']} ({d['file_type']} - {d['word_count']} words)" for d in docs}
    
    default_doc_id = st.session_state.get("selected_doc_id", docs[0]["id"])
    if default_doc_id not in doc_options:
        default_doc_id = docs[0]["id"]

    selected_id = st.selectbox(
        "Select Document to Summarize",
        options=list(doc_options.keys()),
        format_func=lambda x: doc_options[x],
        index=list(doc_options.keys()).index(default_doc_id),
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        sum_type = st.selectbox("Summary Focus", ["Comprehensive Executive Summary", "High-Yield Exam Cram", "Key Concepts & Glossary"])
    with c2:
        st.write("")
        st.write("")
        generate_btn = st.button("✨ Generate AI Summary", type="primary", use_container_width=True)

    if generate_btn:
        with st.spinner("AI is analyzing key concepts and drafting summary..."):
            res = SummaryService.generate_and_save(selected_id, summary_type=sum_type)
            if res["success"]:
                st.success(f"🎉 Summary generated! (+{res['xp_awarded']} XP earned ⚡)")
                st.balloons()
            else:
                st.error(f"❌ Failed to generate summary: {res.get('error')}")

    # Display Existing Summaries for Selected Document
    st.markdown("---")
    summaries = SummaryModel.get_by_document(selected_id)
    if summaries:
        st.markdown(f"### 📋 Generated Summaries ({len(summaries)})")
        for i, s in enumerate(summaries):
            with st.container():
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #ede9fe; border-radius:18px; padding:1.5rem; margin-bottom:1.5rem; box-shadow:0 4px 12px rgba(124, 58, 237, 0.05);">
                        <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                            <span style="font-weight:700; color:#7c3aed; font-size:0.9rem; text-transform:uppercase;">{s['summary_type']}</span>
                            <span style="color:#94a3b8; font-size:0.8rem;">{s['created_at']}</span>
                        </div>
                        <h4 style="color:#0f172a; margin-top:0;">Executive Summary</h4>
                        <p style="color:#334155; line-height:1.7; font-size:1.02rem;">{s['content']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if s.get("key_takeaways"):
                    with st.expander("📌 Key Exam Takeaways & Concepts", expanded=True):
                        st.markdown(s["key_takeaways"])
    else:
        st.info("No summaries generated yet for this document. Click **'Generate AI Summary'** above!")
