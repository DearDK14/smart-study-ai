"""Document management page: PDF upload, extraction, and inspection."""
import streamlit as st
from services.pdf_service import PDFService
from database.models import DocumentModel
from utils.validators import validate_file_extension, validate_file_size
from utils.helpers import format_file_size, sanitize_filename
from config.settings import UPLOADS_DIR

def render_documents_page():
    """Renders document upload and extraction interface."""
    st.markdown("## 📚 Document Management & PDF Extraction")
    st.markdown("Upload course textbooks, lecture slides, or study notes (PDF, TXT, MD) to extract and process study materials.")

    tab_upload, tab_library = st.tabs(["📤 Upload New Document", "📂 Document Library"])

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Choose a study document",
            type=["pdf", "txt", "md"],
            help="Upload a PDF syllabus, notes, or chapter (up to 25MB).",
        )

        doc_title = st.text_input("Document Title", placeholder="e.g. Chapter 4: Photosynthesis & Cellular Respiration")

        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            file_size = len(file_bytes)
            filename = uploaded_file.name

            # Validations
            ext_valid, ext_err = validate_file_extension(filename)
            size_valid, size_err = validate_file_size(file_size)

            if not ext_valid:
                st.error(f"❌ {ext_err}")
                return
            if not size_valid:
                st.error(f"❌ {size_err}")
                return

            st.info(f"📄 **Selected**: `{filename}` ({format_file_size(file_size)})")

            if st.button("🚀 Extract & Save Document", type="primary", use_container_width=True):
                with st.spinner("Extracting text and analyzing document structure..."):
                    # Save local copy
                    clean_name = sanitize_filename(filename)
                    save_path = UPLOADS_DIR / clean_name
                    with open(save_path, "wb") as f:
                        f.write(file_bytes)

                    # Extract text via PDFService
                    res = PDFService.process_file(filename, file_bytes)

                    if not res["success"]:
                        st.error(f"❌ Extraction failed: {res.get('error', 'Unknown error')}")
                        return

                    title = doc_title.strip() if doc_title.strip() else filename.rsplit(".", 1)[0]
                    file_type = filename.rsplit(".", 1)[-1].upper()

                    doc_id = DocumentModel.create(
                        filename=clean_name,
                        filepath=save_path,
                        title=title,
                        file_type=file_type,
                        file_size=file_size,
                        page_count=res["page_count"],
                        word_count=res["word_count"],
                        extracted_text=res["text"],
                    )

                    st.success(f"✅ Document successfully processed! (ID: {doc_id})")
                    
                    # Quick Stats display
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Pages Extracted", res["page_count"])
                    c2.metric("Total Words", res["word_count"])
                    c3.metric("Est. Reading Time", f"{res['reading_time_min']} mins")

                    # Preview of extracted text
                    with st.expander("🔍 Preview Extracted Text (First 1,000 characters)"):
                        st.text_area("Extracted Content", res["text"][:1500], height=250)

    with tab_library:
        docs = DocumentModel.get_all()
        if not docs:
            st.info("No documents uploaded yet. Upload a PDF or TXT document to get started!")
        else:
            st.markdown(f"**Found {len(docs)} study documents in your library:**")
            for doc in docs:
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:1.2rem; margin-bottom:1rem; box-shadow:0 2px 6px rgba(0,0,0,0.02);">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <h4 style="margin:0; color:#0f172a; font-weight:700;">{doc['title']}</h4>
                                    <p style="margin:4px 0 0 0; color:#64748b; font-size:0.85rem;">
                                        Format: <span style="font-weight:600; color:#7c3aed;">{doc['file_type']}</span> • 
                                        Pages: <b>{doc['page_count']}</b> • 
                                        Words: <b>{doc['word_count']}</b> • 
                                        Size: <b>{format_file_size(doc['file_size'])}</b> • 
                                        Uploaded: {doc['created_at']}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    col_view, col_sum, col_del = st.columns([1, 1, 1])
                    with col_view:
                        with st.expander(f"📖 Read {doc['title']}"):
                            st.text_area(f"Full Text - {doc['title']}", doc["extracted_text"], height=300)
                    with col_sum:
                        if st.button(f"⚡ Generate AI Summary", key=f"sum_{doc['id']}"):
                            st.session_state["selected_doc_id"] = doc["id"]
                            st.session_state["current_page"] = "📑 Summaries"
                            st.rerun()
                    with col_del:
                        if st.button(f"🗑️ Delete", key=f"del_{doc['id']}"):
                            DocumentModel.delete(doc["id"])
                            st.toast(f"Deleted {doc['title']}")
                            st.rerun()
