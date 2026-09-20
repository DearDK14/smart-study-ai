"""AI generation service supporting Gemini API with offline local NLP heuristic engine fallback."""
import re
import json
import random
from typing import Dict, Any, List, Optional
from config.settings import GEMINI_API_KEY, DEFAULT_MODEL

class AIService:
    @staticmethod
    def is_api_configured() -> bool:
        """Checks if a valid Gemini API key is provided."""
        return bool(GEMINI_API_KEY and len(GEMINI_API_KEY) > 10)

    @classmethod
    def call_gemini(cls, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Calls Google Gemini API if configured."""
        if not cls.is_api_configured():
            return None
        
        try:
            # Try new google.genai package
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
            )
            return response.text
        except Exception:
            try:
                # Try legacy google.generativeai package
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=GEMINI_API_KEY)
                model = genai_legacy.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"[AIService] Gemini API error: {e}")
                return None

    # =========================================================================
    # Offline Local NLP Pipeline (Heuristic & Statistical Extraction)
    # =========================================================================

    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Split text into distinct sentences."""
        raw_sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 20 and not s.strip().startswith("---")]
        return sentences

    @staticmethod
    def extract_key_terms(text: str, top_n: int = 15) -> List[str]:
        """Extract dominant keywords and technical terms from text."""
        stop_words = {
            "the", "and", "is", "in", "it", "of", "to", "for", "with", "on", "that", "this", "by", "from",
            "as", "an", "are", "be", "at", "which", "or", "was", "were", "can", "will", "has", "have", "had",
            "not", "but", "all", "also", "into", "their", "more", "other", "such", "than", "its", "each",
            "these", "those", "when", "where", "how", "what", "who", "they", "them", "been", "about", "both"
        }
        words = re.findall(r"\b[A-Za-z]{4,}\b", text.lower())
        word_counts: Dict[str, int] = {}
        for w in words:
            if w not in stop_words:
                word_counts[w] = word_counts.get(w, 0) + 1
        
        # Sort by frequency
        sorted_terms = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [term for term, _ in sorted_terms[:top_n]]

    @classmethod
    def generate_local_summary(cls, text: str) -> Dict[str, Any]:
        """Generates executive summary and bullet points locally without external API."""
        sentences = cls.extract_sentences(text)
        if not sentences:
            sentences = [text[:200]]

        # Pick top informative sentences based on length and position
        summary_count = min(4, len(sentences))
        summary_sentences = sentences[:summary_count]
        executive_summary = " ".join(summary_sentences)

        # Generate bullet takeaways
        takeaways = []
        key_terms = cls.extract_key_terms(text, top_n=6)
        
        for s in sentences[summary_count:summary_count + 5]:
            takeaways.append(f"• {s}")
        if not takeaways:
            takeaways = [f"• Focuses on core aspects of {key_terms[0].title() if key_terms else 'the topic'}."]

        return {
            "summary": executive_summary,
            "takeaways": "\n".join(takeaways),
            "key_concepts": [t.title() for t in key_terms[:6]],
            "model_used": "StudyGenius Local NLP Engine",
        }

    @classmethod
    def generate_local_questions(cls, text: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generates multiple choice quiz questions using local heuristic NLP."""
        sentences = cls.extract_sentences(text)
        key_terms = cls.extract_key_terms(text, top_n=20)
        questions = []

        # Find sentences containing key terms
        candidates = []
        for s in sentences:
            for term in key_terms:
                if re.search(rf"\b{re.escape(term)}\b", s, re.IGNORECASE):
                    candidates.append((s, term))
                    break

        if not candidates:
            # Fallback sample questions
            return [
                {
                    "topic": "Fundamentals",
                    "question_text": "What is the primary topic covered in this document?",
                    "option_a": "Core concepts and definitions",
                    "option_b": "Irrelevant historical digression",
                    "option_c": "Unrelated financial theories",
                    "option_d": "System hardware benchmarks",
                    "correct_option": "A",
                    "explanation": "The document primarily introduces foundational knowledge and definitions.",
                    "difficulty": "Easy",
                }
            ]

        # Sample up to `count` candidates
        selected = candidates[:count]
        distractor_pool = [t.title() for t in key_terms] + ["Synthesis", "Regulation", "Propagation", "Homeostasis", "Optimization"]

        for i, (sentence, term) in enumerate(selected):
            # Create a blank or concept question
            blanked = re.sub(rf"\b{re.escape(term)}\b", "______", sentence, flags=re.IGNORECASE, count=1)
            correct_val = term.title()
            
            # Pick 3 unique distractors
            distractors = [d for d in distractor_pool if d.lower() != term.lower()]
            random.shuffle(distractors)
            chosen_distractors = distractors[:3]
            while len(chosen_distractors) < 3:
                chosen_distractors.append(f"Concept-{len(chosen_distractors) + 1}")

            options = [correct_val] + chosen_distractors
            random.shuffle(options)
            correct_letter = ["A", "B", "C", "D"][options.index(correct_val)]

            questions.append({
                "topic": term.title(),
                "question_text": f"Fill in the blank: {blanked}",
                "option_a": options[0],
                "option_b": options[1],
                "option_c": options[2],
                "option_d": options[3],
                "correct_option": correct_letter,
                "explanation": f"According to the source material: '{sentence}'",
                "difficulty": "Medium" if i % 2 == 0 else "Hard",
            })

        return questions

    @classmethod
    def generate_local_flashcards(cls, text: str, count: int = 6) -> List[Dict[str, Any]]:
        """Generates interactive flashcards locally."""
        sentences = cls.extract_sentences(text)
        key_terms = cls.extract_key_terms(text, top_n=20)
        flashcards = []

        seen_terms = set()
        for s in sentences:
            for term in key_terms:
                if term.lower() not in seen_terms and re.search(rf"\b{re.escape(term)}\b", s, re.IGNORECASE):
                    seen_terms.add(term.lower())
                    flashcards.append({
                        "topic": term.title(),
                        "front_text": f"What is the significance of {term.title()} in this context?",
                        "back_text": s,
                    })
                    break
            if len(flashcards) >= count:
                break

        if not flashcards:
            flashcards.append({
                "topic": "Overview",
                "front_text": "Main Objective",
                "back_text": text[:150] + "..." if len(text) > 150 else text,
            })

        return flashcards
