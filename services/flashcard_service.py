"""Flashcard creation and mastery tracking service."""
from typing import Dict, Any, List
from services.ai_service import AIService
from database.models import FlashcardModel, DocumentModel, UserStatsModel
from utils.validators import validate_flashcard_data
from config.settings import XP_PER_FLASHCARD_STUDIED

class FlashcardService:
    @classmethod
    def generate_flashcards_for_document(cls, document_id: int, deck_name: str = None, count: int = 6) -> Dict[str, Any]:
        """Generates flashcards for a document and saves them to SQLite."""
        doc = DocumentModel.get_by_id(document_id)
        if not doc:
            return {"success": False, "error": f"Document ID {document_id} not found."}

        text = doc["extracted_text"]
        if not text or len(text.strip()) < 30:
            return {"success": False, "error": "Document does not have sufficient text."}

        if not deck_name:
            deck_name = f"{doc['title']} Deck"

        raw_cards = []

        # Try Gemini API if available
        if AIService.is_api_configured():
            prompt = (
                f"Create {count} high-yield study flashcards from this text.\n"
                f"Return ONLY valid JSON array with keys: topic, front_text, back_text.\n"
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
                        raw_cards = parsed
                except Exception as e:
                    print(f"Error parsing Gemini flashcards JSON: {e}")

        # Fallback to local heuristic generator
        if not raw_cards:
            raw_cards = AIService.generate_local_flashcards(text, count=count)

        # Validate and prepare cards
        valid_cards = []
        for c in raw_cards:
            c["document_id"] = document_id
            c["deck_name"] = deck_name
            is_valid, _ = validate_flashcard_data(c)
            if is_valid:
                valid_cards.append(c)

        if not valid_cards:
            return {"success": False, "error": "Failed to create flashcards."}

        card_ids = FlashcardModel.bulk_create(valid_cards)

        return {
            "success": True,
            "deck_name": deck_name,
            "card_ids": card_ids,
            "count": len(card_ids),
            "cards": valid_cards,
        }

    @classmethod
    def record_card_review(cls, card_id: int, mastery_status: str) -> Dict[str, Any]:
        """Update flashcard mastery status and award XP."""
        valid_statuses = {"learning", "reviewing", "mastered"}
        if mastery_status not in valid_statuses:
            mastery_status = "reviewing"
            
        FlashcardModel.update_mastery(card_id, mastery_status)
        UserStatsModel.add_xp(XP_PER_FLASHCARD_STUDIED)

        return {
            "success": True,
            "card_id": card_id,
            "mastery_level": mastery_status,
            "xp_earned": XP_PER_FLASHCARD_STUDIED,
        }
