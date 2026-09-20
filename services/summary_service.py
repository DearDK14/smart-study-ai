"""Summary generation and management service."""
from typing import Dict, Any, Optional
from services.ai_service import AIService
from database.models import SummaryModel, DocumentModel, UserStatsModel
from config.settings import XP_PER_SUMMARY_READ

class SummaryService:
    @classmethod
    def generate_and_save(cls, document_id: int, summary_type: str = "executive", user_id: Optional[int] = None) -> Dict[str, Any]:
        """Generates summary for a document and persists it in SQLite."""
        doc = DocumentModel.get_by_id(document_id)
        if not doc:
            return {"success": False, "error": f"Document ID {document_id} not found."}

        if user_id is None and "user_id" in doc:
            user_id = doc.get("user_id")

        text = doc["extracted_text"]
        if not text or len(text.strip()) < 30:
            return {"success": False, "error": "Document does not contain sufficient text for summarization."}

        # Try Gemini API first if configured
        summary_result = None
        if AIService.is_api_configured():
            prompt = (
                f"You are an expert academic tutor. Summarize the following study document concisely.\n"
                f"1. Provide a comprehensive Executive Summary paragraph.\n"
                f"2. Provide 4-6 bulleted key takeaways and high-yield exam insights.\n\n"
                f"Document text:\n{text[:6000]}"
            )
            api_resp = AIService.call_gemini(prompt)
            if api_resp:
                parts = api_resp.split("\n\n")
                summary_content = parts[0] if parts else api_resp
                takeaways = "\n\n".join(parts[1:]) if len(parts) > 1 else ""
                summary_result = {
                    "summary": summary_content,
                    "takeaways": takeaways,
                    "model_used": "Gemini 1.5 Flash",
                }

        # If API not configured or failed, use local NLP
        if not summary_result:
            local_res = AIService.generate_local_summary(text)
            summary_result = {
                "summary": local_res["summary"],
                "takeaways": local_res["takeaways"],
                "model_used": local_res["model_used"],
            }

        # Persist in DB
        summary_id = SummaryModel.create(
            document_id=document_id,
            summary_type=summary_type,
            content=summary_result["summary"],
            key_takeaways=summary_result["takeaways"],
            user_id=user_id,
        )

        # Award study XP
        UserStatsModel.add_xp(XP_PER_SUMMARY_READ, user_id=user_id)

        return {
            "success": True,
            "summary_id": summary_id,
            "content": summary_result["summary"],
            "key_takeaways": summary_result["takeaways"],
            "model_used": summary_result["model_used"],
            "xp_awarded": XP_PER_SUMMARY_READ,
        }

    @classmethod
    def get_document_summaries(cls, document_id: int, user_id: Optional[int] = None):
        return SummaryModel.get_by_document(document_id, user_id=user_id)
