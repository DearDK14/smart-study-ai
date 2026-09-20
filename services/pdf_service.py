"""PDF and document processing service."""
import io
from pathlib import Path
from typing import Dict, Any, List
from utils.helpers import clean_extracted_text, calculate_reading_time

class PDFService:
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
        """Extracts text and page metadata from PDF byte stream using pypdf."""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pages_text: List[str] = []
            
            for i, page in enumerate(reader.pages):
                extracted = page.extract_text() or ""
                pages_text.append(clean_extracted_text(extracted))
            
            full_text = "\n\n--- Page Break ---\n\n".join(pages_text)
            page_count = len(reader.pages)
            word_count = len(full_text.split())
            
            return {
                "success": True,
                "text": full_text,
                "page_count": page_count,
                "word_count": word_count,
                "pages": pages_text,
                "reading_time_min": calculate_reading_time(word_count),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "page_count": 0,
                "word_count": 0,
                "pages": [],
                "reading_time_min": 0,
            }

    @staticmethod
    def extract_text_from_txt(file_bytes: bytes) -> Dict[str, Any]:
        """Extract text from plain text or markdown file."""
        try:
            text = file_bytes.decode("utf-8", errors="replace")
            cleaned = clean_extracted_text(text)
            word_count = len(cleaned.split())
            return {
                "success": True,
                "text": cleaned,
                "page_count": max(1, word_count // 300),
                "word_count": word_count,
                "pages": [cleaned],
                "reading_time_min": calculate_reading_time(word_count),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "page_count": 0,
                "word_count": 0,
                "pages": [],
                "reading_time_min": 0,
            }

    @classmethod
    def process_file(cls, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """Dispatcher based on file extension."""
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            return cls.extract_text_from_pdf(file_bytes)
        elif ext in (".txt", ".md"):
            return cls.extract_text_from_txt(file_bytes)
        else:
            return {
                "success": False,
                "error": f"Unsupported extension: {ext}",
                "text": "",
                "page_count": 0,
                "word_count": 0,
                "pages": [],
                "reading_time_min": 0,
            }
