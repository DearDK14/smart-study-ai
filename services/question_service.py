"""Question and Quiz management service."""
from typing import Dict, Any, List, Optional
from services.ai_service import AIService
from database.models import QuestionModel, QuizModel, QuizAttemptModel, DocumentModel, UserStatsModel
from utils.validators import validate_question_data
from config.settings import (
    XP_PER_QUIZ_COMPLETED,
    XP_PER_CORRECT_ANSWER,
    WEAK_TOPIC_ACCURACY_THRESHOLD,
)

class QuestionService:
    @classmethod
    def generate_questions_for_document(cls, document_id: int, count: int = 5, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Generates quiz questions for a document and saves them to the DB."""
        doc = DocumentModel.get_by_id(document_id)
        if not doc:
            return {"success": False, "error": f"Document ID {document_id} not found."}

        if user_id is None and "user_id" in doc:
            user_id = doc.get("user_id")

        text = doc["extracted_text"]
        if not text or len(text.strip()) < 30:
            return {"success": False, "error": "Document does not contain enough text."}

        raw_questions = []

        # Try Gemini first if configured
        if AIService.is_api_configured():
            prompt = (
                f"You are an expert exam creator. Generate {count} multiple-choice questions from this text.\n"
                f"Return ONLY valid JSON array with keys: topic, question_text, option_a, option_b, option_c, option_d, correct_option ('A','B','C','D'), explanation, difficulty ('Easy','Medium','Hard').\n"
                f"Text:\n{text[:6000]}"
            )
            api_resp = AIService.call_gemini(prompt)
            if api_resp:
                try:
                    cleaned_json = api_resp.strip()
                    if cleaned_json.startswith("```json"):
                        cleaned_json = cleaned_json[7:]
                    if cleaned_json.startswith("```"):
                        cleaned_json = cleaned_json[3:]
                    if cleaned_json.endswith("```"):
                        cleaned_json = cleaned_json[:-3]
                    import json
                    parsed = json.loads(cleaned_json.strip())
                    if isinstance(parsed, list):
                        raw_questions = parsed
                except Exception as e:
                    print(f"Error parsing Gemini questions JSON: {e}")

        # Fallback to local heuristic question generator
        if not raw_questions:
            raw_questions = AIService.generate_local_questions(text, count=count)

        # Validate and sanitize questions
        valid_questions = []
        for q in raw_questions:
            q["document_id"] = document_id
            q["user_id"] = user_id
            is_valid, _ = validate_question_data(q)
            if is_valid:
                valid_questions.append(q)

        if not valid_questions:
            return {"success": False, "error": "Failed to formulate valid questions from document."}

        # Save to database
        q_ids = QuestionModel.bulk_create(valid_questions, user_id=user_id)
        
        # Create an associated Quiz
        quiz_title = f"{doc['title']} Mastery Quiz"
        quiz_id = QuizModel.create(quiz_title, document_id, q_ids, user_id=user_id)

        return {
            "success": True,
            "quiz_id": quiz_id,
            "question_ids": q_ids,
            "count": len(q_ids),
            "questions": valid_questions,
        }

    @classmethod
    def evaluate_quiz_submission(cls, quiz_id: int, user_answers: Dict[int, str], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Evaluates submitted answers, detects weak topics, and records attempt."""
        quiz = QuizModel.get_by_id(quiz_id)
        if not quiz:
            return {"success": False, "error": "Quiz not found."}

        if user_id is None and "user_id" in quiz:
            user_id = quiz.get("user_id")

        questions = QuestionModel.get_by_ids(quiz["question_ids"])
        score = 0
        total = len(questions)
        topic_stats: Dict[str, Dict[str, int]] = {}
        detailed_answers = []

        for q in questions:
            qid = q["id"]
            correct = q["correct_option"].upper()
            user_choice = user_answers.get(qid, "").upper()
            is_correct = (user_choice == correct)

            if is_correct:
                score += 1

            topic = q.get("topic", "General")
            if topic not in topic_stats:
                topic_stats[topic] = {"correct": 0, "total": 0}
            topic_stats[topic]["total"] += 1
            if is_correct:
                topic_stats[topic]["correct"] += 1

            detailed_answers.append({
                "question_id": qid,
                "question_text": q["question_text"],
                "user_choice": user_choice,
                "correct_choice": correct,
                "is_correct": is_correct,
                "topic": topic,
                "explanation": q.get("explanation", ""),
            })

        # Identify Weak Topics (< WEAK_TOPIC_ACCURACY_THRESHOLD %)
        weak_topics = []
        topic_accuracy = {}
        for topic, stat in topic_stats.items():
            acc = round((stat["correct"] / stat["total"]) * 100, 1) if stat["total"] > 0 else 0.0
            topic_accuracy[topic] = acc
            if acc < WEAK_TOPIC_ACCURACY_THRESHOLD:
                weak_topics.append({
                    "topic": topic,
                    "accuracy": acc,
                    "correct": stat["correct"],
                    "total": stat["total"],
                })

        # Calculate XP gained
        xp_earned = XP_PER_QUIZ_COMPLETED + (score * XP_PER_CORRECT_ANSWER)
        UserStatsModel.add_xp(xp_earned, user_id=user_id)

        # Save Attempt Record
        attempt_id = QuizAttemptModel.record_attempt(
            quiz_id=quiz_id,
            score=score,
            total_questions=total,
            answers=detailed_answers,
            weak_topics=weak_topics,
            xp_earned=xp_earned,
            user_id=user_id,
        )

        percentage = round((score / total) * 100, 1) if total > 0 else 0.0

        return {
            "success": True,
            "attempt_id": attempt_id,
            "score": score,
            "total_questions": total,
            "percentage": percentage,
            "xp_earned": xp_earned,
            "topic_accuracy": topic_accuracy,
            "weak_topics": weak_topics,
            "detailed_answers": detailed_answers,
        }
