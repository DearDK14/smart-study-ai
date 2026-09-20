"""Learning Analytics page: Weak topic detection and quiz performance insights."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.models import QuizAttemptModel, UserStatsModel
from config.settings import WEAK_TOPIC_ACCURACY_THRESHOLD

def render_analytics_page():
    """Renders analytics dashboard computing real student performance and weak topics."""
    st.markdown("## 📈 Learning Analytics & Weak Topics Diagnostic")
    st.markdown("Automated diagnostic system analyzing quiz results to pinpoint weak topics and guide revision.")

    stats = UserStatsModel.get()
    attempts = QuizAttemptModel.get_all()

    # Top summary metrics
    total_attempts = len(attempts)
    avg_score = round(sum(a["percentage"] for a in attempts) / total_attempts, 1) if total_attempts > 0 else 0.0
    total_xp = stats.get("xp_total", 11735)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quizzes Attempted", total_attempts)
    c2.metric("Average Score", f"{avg_score}%")
    c3.metric("Total XP Earned", f"{total_xp} ⚡")
    c4.metric("Current Level", f"Level {stats.get('level', 11)}")

    st.markdown("---")

    if not attempts:
        st.info("💡 **No quiz attempts recorded yet.** Take a quiz in the **Quiz Studio** to generate real topic diagnostics and identify weak areas!")
        
        # Show simulated preview / demonstration data for initial presentation
        st.markdown("### 📊 Sample Topic Diagnostic Preview")
        demo_topics = pd.DataFrame([
            {"Topic": "Mitochondrial Respiration", "Accuracy": 40.0, "Total Questions": 5, "Status": "⚠️ Weak"},
            {"Topic": "Calvin Cycle & Dark Reactions", "Accuracy": 50.0, "Total Questions": 4, "Status": "⚠️ Weak"},
            {"Topic": "Glycolysis Pathway", "Accuracy": 85.0, "Total Questions": 6, "Status": "✅ Mastered"},
            {"Topic": "Chloroplast Anatomy", "Accuracy": 100.0, "Total Questions": 3, "Status": "✅ Mastered"},
        ])
        fig_demo = px.bar(
            demo_topics,
            x="Topic",
            y="Accuracy",
            color="Status",
            color_discrete_map={"⚠️ Weak": "#ef4444", "✅ Mastered": "#10b981"},
            title="Topic Accuracy Diagnostic (Preview)",
        )
        st.plotly_chart(fig_demo, use_container_width=True)
        return

    # Process Real Quiz Data
    topic_aggregated = {}
    for a in attempts:
        for ans in a.get("answers", []):
            top = ans.get("topic", "General")
            if top not in topic_aggregated:
                topic_aggregated[top] = {"correct": 0, "total": 0}
            topic_aggregated[top]["total"] += 1
            if ans.get("is_correct"):
                topic_aggregated[top]["correct"] += 1

    topic_rows = []
    weak_topics_list = []

    for top, data in topic_aggregated.items():
        acc = round((data["correct"] / data["total"]) * 100, 1) if data["total"] > 0 else 0.0
        status = "⚠️ Weak" if acc < WEAK_TOPIC_ACCURACY_THRESHOLD else "✅ Strong"
        if acc < WEAK_TOPIC_ACCURACY_THRESHOLD:
            weak_topics_list.append({"topic": top, "accuracy": acc, "total": data["total"]})
        topic_rows.append({
            "Topic": top,
            "Accuracy (%)": acc,
            "Correct": data["correct"],
            "Total Questions": data["total"],
            "Status": status,
        })

    df_topics = pd.DataFrame(topic_rows)

    # 1. Weak Topics Priority Alert Card
    st.markdown("### 🎯 Weak Topics Diagnostic (Accuracy < 60%)")
    if weak_topics_list:
        st.markdown(
            f"""
            <div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:16px; padding:1.25rem; margin-bottom:1.5rem;">
                <h4 style="margin:0 0 0.5rem 0; color:#e11d48;">🚨 {len(weak_topics_list)} Weak Topic(s) Identified</h4>
                <p style="color:#4c0519; margin:0; font-size:0.95rem;">
                    Based on your actual test responses, the system recommends dedicating study focus to these subjects before upcoming exams:
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        w_cols = st.columns(min(len(weak_topics_list), 3))
        for idx, wt in enumerate(weak_topics_list):
            with w_cols[idx % 3]:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:2px solid #f87171; border-radius:14px; padding:1rem; text-align:center; box-shadow:0 4px 12px rgba(239,68,68,0.08);">
                        <span style="font-size:1.5rem;">⚠️</span>
                        <div style="font-weight:700; color:#0f172a; margin:0.4rem 0;">{wt['topic']}</div>
                        <div style="font-size:1.2rem; font-weight:800; color:#dc2626;">{wt['accuracy']}%</div>
                        <small style="color:#64748b;">Tested on {wt['total']} questions</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.success("🎉 **Exceptional performance!** No weak topics detected. All tested areas are above the 60% mastery threshold.")

    st.write("")

    # 2. Topic Performance Chart
    st.markdown("### 📊 Performance by Topic Breakdown")
    fig = px.bar(
        df_topics,
        x="Topic",
        y="Accuracy (%)",
        color="Status",
        color_discrete_map={"⚠️ Weak": "#ef4444", "✅ Strong": "#7c3aed"},
        text="Accuracy (%)",
        title="Accuracy Across Evaluated Topics",
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        yaxis=dict(range=[0, 115]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)

    # 3. Quiz History Table
    with st.expander("📜 Full Quiz Attempt History", expanded=False):
        history_rows = []
        for a in attempts:
            history_rows.append({
                "Attempt ID": a["id"],
                "Quiz ID": a["quiz_id"],
                "Score": f"{a['score']}/{a['total_questions']}",
                "Percentage": f"{a['percentage']}%",
                "XP Gained": f"+{a['xp_earned']} ⚡",
                "Date": a["completed_at"],
            })
        st.dataframe(pd.DataFrame(history_rows), use_container_width=True)
