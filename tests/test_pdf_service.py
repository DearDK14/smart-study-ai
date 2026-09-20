"""Unit tests for PDFService document processing."""
import io
import pytest
from services.pdf_service import PDFService

def test_extract_text_from_txt():
    content = "Photosynthesis is the biological process by which plants convert light energy into chemical energy."
    raw_bytes = content.encode("utf-8")
    
    res = PDFService.extract_text_from_txt(raw_bytes)
    assert res["success"] is True
    assert "Photosynthesis" in res["text"]
    assert res["word_count"] > 10
    assert res["page_count"] >= 1

def test_process_file_dispatcher():
    content = "Cell biology lecture notes on cellular respiration and ATP synthase."
    raw_bytes = content.encode("utf-8")
    
    res = PDFService.process_file("lecture.txt", raw_bytes)
    assert res["success"] is True
    assert "ATP synthase" in res["text"]

    # Unsupported format
    unsupported = PDFService.process_file("video.mp4", b"dummy")
    assert unsupported["success"] is False
    assert "Unsupported" in unsupported["error"]

def test_extract_text_from_valid_pdf():
    # Dynamically generate a minimal valid PDF using pypdf's PdfWriter
    import pypdf
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=200, height=200)
    stream = io.BytesIO()
    writer.write(stream)
    pdf_bytes = stream.getvalue()

    res = PDFService.extract_text_from_pdf(pdf_bytes)
    assert res["success"] is True
    assert res["page_count"] == 1
