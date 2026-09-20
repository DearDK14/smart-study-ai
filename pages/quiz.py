"""Interactive Quiz Studio page: taking quizzes and receiving instant feedback."""
import streamlit as st
from services.question_service import QuestionService
from database.models import QuizModel, QuestionModel

def render_quiz_page():
    """Renders the interactive quiz testing interface."""
    st.markdown("## 📝 Quiz Studio & Interactive Assessment")
    st.markdown("Test your mastery with interactive MCQs. Earn XP, track topic accuracy, and identify weak areas.")

    quizzes = QuizModel.get_all()
    if not quizzes:
        st.warning("⚠️ No quizzes available yet. Generate questions from a document first!")
        if st.button("❓ Go to Question Studio"):
            st.session_state["current_page"] = "❓ Questions"
            st.rerun()
        return

    quiz_options = {q["id"]: f"{q['title']} ({q['total_questions']} Questions)" for q in quizzes}
    
    default_quiz_id = st.session_state.get("active_quiz_id", quizzes[0]["id"])
    if default_quiz_id not in quiz_options:
        default_quiz_id = quizzes[0]["id"]

    selected_quiz_id = st.selectbox(
        "Choose a Quiz",
        options=list(quiz_options.keys()),
        format_func=lambda x: quiz_options[x],
        index=list(quiz_options.keys()).index(default_quiz_id),
    )

    quiz = QuizModel.get_by_id(selected_quiz_id)
    questions = QuestionModel.get_by_ids(quiz["question_ids"])

    if not questions:
        st.error("No questions found for this quiz.")
        return

    st.markdown(f"### 📋 {quiz['title']}")
    st.caption(f"Total Questions: {len(questions)} • Answer all to complete the quiz.")

    # Form to submit quiz
    with st.form(f"quiz_form_{selected_quiz_id}"):
        user_answers = {}
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}. [{q['topic']}] {q['question_text']}**")
            
            options_dict = {
                "A": f"A) {q['option_a']}",
                "B": f"B) {q['option_b']}",
                "C": f"C) {q['option_c']}",
                "D": f"D) {q['option_d']}",
            }
            
            choice = st.radio(
                f"Select answer for Q{i+1}",
                options=list(options_dict.keys()),
                format_func=lambda k: options_dict[k],
                key=f"q_{q['id']}",
                index=None,
            )
            user_answers[q["id"]] = choice
            st.write("")

        submit_btn = st.form_submit_button("🏁 Submit Quiz & Grade Answers", type="primary", use_container_width=True)

    if submit_btn:
        # Check if all questions were answered
        unanswered = [qid for qid, ans in user_answers.items() if not ans]
        if unanswered:
            st.warning(f"⚠️ Please answer all questions! ({len(unanswered)} remaining)")
            return

        with st.spinner("Grading your quiz and analyzing weak topics..."):
            result = QuestionService.evaluate_quiz_submission(selected_quiz_id, user_answers)

            if not result["success"]:
                st.error("Failed to grade quiz.")
                return

            score = result["score"]
            total = result["total_questions"]
            pct = result["percentage"]
            xp = result["xp_earned"]

            # Results Banner
            st.markdown("---")
            if pct >= 80:
                st.success(f"🏆 **Outstanding Work!** You scored **{score}/{total}** ({pct}%) • **+{xp} XP Earned ⚡**")
                st.balloons()
            elif pct >= 60:
                st.info(f"👍 **Good Effort!** You scored **{score}/{total}** ({pct}%) • **+{xp} XP Earned ⚡**")
            else:
                st.warning(f"📚 **Keep Practicing!** You scored **{score}/{total}** ({pct}%) • **+{xp} XP Earned ⚡**")

            # Weak Topics Detection Alert
            weak_topics = result["weak_topics"]
            if weak_topics:
                st.markdown("### ⚠️ Identified Weak Topics")
                st.markdown("The following topics need extra review (< 60% accuracy):")
                for wt in weak_topics:
                    st.markdown(
                        f"""
                        <div style="background:#fef2f2; border:1px solid #fecaca; padding:0.8rem 1.2rem; border-radius:12px; margin-bottom:0.5rem;">
                            <span class="weak-topic-badge">⚠️ Weak Area</span> 
                            <b>{wt['topic']}</b> — Accuracy: <span style="color:#b91c1c; font-weight:700;">{wt['accuracy']}%</span> ({wt['correct']}/{wt['total']} correct)
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.success("🎯 No weak topics detected! Great mastery across all evaluated concepts.")

            # Detailed Review of Questions
            with st.expander("🔍 Detailed Question Review & Explanations", expanded=True):
                for ans in result["detailed_answers"]:
                    is_c = ans["is_correct"]
                    icon = "✅" if is_c else "❌"
                    color = "#dcfce7" if is_c else "#fee2e2"
                    border = "#86efac" if is_c else "#fca5a5"
                    
                    st.markdown(
                        f"""
                        <div style="background:{color}; border:1px solid {border}; border-radius:12px; padding:1rem; margin-bottom:0.75rem;">
                            <b>{icon} {ans['question_text']}</b><br>
                            Your Answer: <b>{ans['user_choice']}</b> | Correct: <b>{ans['correct_choice']}</b><br>
                            <small style="color:#475569;">Topic: {ans['topic']}</small><br>
                            <span style="font-size:0.9rem; color:#1e293b;">💡 <i>{ans['explanation']}</i></span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
