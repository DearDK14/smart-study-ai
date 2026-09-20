"""Question generation and Question Bank page."""
import streamlit as st
from services.question_service import QuestionService
from database.models import DocumentModel, QuestionModel

def render_questions_page():
    """Renders Question Generation Studio & Question Bank."""
    st.markdown("## ❓ Question Studio & Question Bank")
    st.markdown("Generate multiple-choice exam questions automatically from uploaded documents with answer explanations and topic tags.")

    docs = DocumentModel.get_all()
    if not docs:
        st.warning("⚠️ No documents uploaded yet. Please upload study materials first!")
        return

    doc_options = {d["id"]: d["title"] for d in docs}
    
    tab_gen, tab_bank = st.tabs(["⚡ Generate New Questions", "📚 Question Bank"])

    with tab_gen:
        c1, c2 = st.columns([2, 1])
        with c1:
            selected_doc_id = st.selectbox(
                "Source Document",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
            )
        with c2:
            q_count = st.slider("Number of Questions", min_value=3, max_value=15, value=5)

        if st.button("🧠 Generate Questions Pipeline", type="primary", use_container_width=True):
            with st.spinner("AI is analyzing document text and synthesizing exam questions..."):
                res = QuestionService.generate_questions_for_document(selected_doc_id, count=q_count)
                if res["success"]:
                    st.success(f"✅ Generated {res['count']} questions! Created Quiz #{res['quiz_id']}.")
                    st.session_state["active_quiz_id"] = res["quiz_id"]
                    
                    # Option to directly take quiz
                    if st.button("📝 Start Quiz Now"):
                        st.session_state["current_page"] = "📝 Quiz Studio"
                        st.rerun()
                else:
                    st.error(f"❌ Generation failed: {res.get('error')}")

    with tab_bank:
        all_q = QuestionModel.get_all()
        if not all_q:
            st.info("No questions in the question bank yet. Generate some questions using the tab above!")
        else:
            st.markdown(f"**Total Questions in Bank:** `{len(all_q)}`")
            for i, q in enumerate(all_q):
                with st.expander(f"Q{i+1}: [{q['topic']}] {q['question_text'][:80]}...", expanded=False):
                    st.markdown(f"**Question**: {q['question_text']}")
                    st.markdown(f"- **A**: {q['option_a']}")
                    st.markdown(f"- **B**: {q['option_b']}")
                    st.markdown(f"- **C**: {q['option_c']}")
                    st.markdown(f"- **D**: {q['option_d']}")
                    st.success(f"**Correct Option**: `{q['correct_option']}`")
                    if q.get("explanation"):
                        st.info(f"💡 **Explanation**: {q['explanation']}")
                    st.caption(f"Topic: {q['topic']} • Difficulty: {q['difficulty']}")
