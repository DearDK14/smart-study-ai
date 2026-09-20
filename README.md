# 🎓 StudyGenius • Smart Study AI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Framework: Streamlit](https://img.shields.io/badge/framework-Streamlit-red.svg)](https://streamlit.io/)
[![Database: SQLite](https://img.shields.io/badge/database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Tests: Pytest](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![CodeMyFYP Hack 26](https://img.shields.io/badge/Hackathon-CodeMyFYP%20Hack%2026-purple.svg)](https://hackathon.codemyfyp.com)

An AI-powered academic learning operating system that turns dense textbooks, lecture notes, and syllabi into executive summaries, interactive quizzes, 3D flashcard decks, and weak-topic learning analytics.

---

## 🌟 Key Features & Architecture

### 1. 🔍 Framework & Architecture Audit
- **Core Framework**: **Streamlit** (Python) with a custom modern CSS design system matching the **StudyGenius** macOS purple-dashboard aesthetic.
- **Database**: Thread-safe **SQLite** persistent storage (`data/study_genius.db`) with normalized models for documents, summaries, question banks, quizzes, attempts, flashcard decks, and gamified XP stats.
- **AI Pipeline**: Dual-mode engine:
  - **Online**: Google Gemini API (`gemini-1.5-flash`) via `google-genai`.
  - **Offline Fallback**: Built-in heuristic NLP processor (TF/statistical keyword extractor, semantic summarizer, distractor generator) ensuring the application is **100% functional out of the box** even without an API key.

### 2. 📚 Document Management & PDF Extraction
- High-fidelity PDF document parser powered by `pypdf`.
- Supports PDF, TXT, and Markdown documents up to 25MB.
- Automatic page-by-page extraction, word count computation, and estimated reading time calculation.

### 3. 📑 AI Summaries & Content Pipeline
- Generates structured Executive Summaries and bulleted high-yield exam takeaways.
- Automated Key Concepts glossary generation.
- Awards study XP for engaging with course materials.

### 4. 📝 Interactive Quiz Studio & Assessment
- Multiple-choice questions with 4 distinct options, explanations, and topic categorization.
- Real-time instant grading with celebratory feedback and detailed rationale.

### 5. 🗂️ 3D Animated Flashcards & Spaced Repetition
- Dynamic flashcard decks generated from uploaded documents.
- Interactive front/back flip cards with self-rated recall ("Hard", "Medium", "Mastered") for active recall reinforcement.

### 6. 📈 Weak Topics Diagnostic & Learning Analytics
- Aggregates actual student quiz submissions across specific topics.
- Automatically flags **Weak Topics** ($<60\%$ accuracy threshold) to guide exam revision.
- Interactive Plotly charts displaying mastery distribution, XP velocity, and full attempt history.

---

## 📁 Repository Structure

```text
Hack 26/
│
├── app.py                     # Main application entry point & router
├── requirements.txt           # Project dependencies
├── .env                       # Environment variables (API keys)
├── .env.example               # Template environment configuration
├── .gitignore                 # Ignored files and directories
├── README.md                  # Comprehensive documentation
│
├── config/
│   ├── __init__.py
│   └── settings.py            # App settings, paths, thresholds
│
├── database/
│   ├── __init__.py
│   ├── connection.py          # SQLite connection and initialization
│   ├── models.py              # CRUD models for documents, quizzes, flashcards
│   └── schema.sql             # Relational database schema
│
├── services/
│   ├── __init__.py
│   ├── ai_service.py          # Dual AI engine (Gemini + Local NLP fallback)
│   ├── pdf_service.py         # PDF text extraction and document parsing
│   ├── summary_service.py     # Summary generation and persistence
│   ├── question_service.py    # MCQ generation, grading, weak topic analysis
│   └── flashcard_service.py   # Flashcard generation and mastery tracking
│
├── pages/
│   ├── __init__.py
│   ├── dashboard.py           # StudyGenius dashboard with XP & stat cards
│   ├── documents.py           # Document upload & text extraction
│   ├── summaries.py           # AI summaries studio
│   ├── questions.py           # Question generation & Question Bank
│   ├── quiz.py                # Interactive quiz testing
│   ├── flashcards.py          # 3D flip study flashcards
│   ├── notebook.py            # Student study notes
│   ├── analytics.py           # Weak topics diagnosis & charts
│   └── settings.py            # System settings & API key manager
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py             # Navigation sidebar matching design
│   ├── cards.py               # Metric cards, action buttons, flashcard widget
│   └── styles.py              # Custom CSS matching StudyGenius mockup
│
├── utils/
│   ├── __init__.py
│   ├── validators.py          # File and data schema validation
│   └── helpers.py             # Text cleaning, XP math, file formatting
│
├── tests/
│   ├── __init__.py
│   ├── test_database.py       # Database CRUD unit tests
│   ├── test_pdf_service.py    # PDF extraction unit tests
│   ├── test_quiz.py           # Quiz grading & weak topic detection tests
│   └── test_validators.py     # Input validator unit tests
│
├── data/
│   └── .gitkeep               # SQLite database directory
│
└── uploads/
    └── biology_cellular_respiration.txt  # Sample study materials
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/DearDK14/smart-study-ai.git
cd smart-study-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Gemini API Key
Create or update `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
> *Note: If no API key is provided, the platform automatically runs on the built-in offline Local NLP Engine!*

### 4. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the full automated test suite covering database models, PDF extraction, quiz grading, and weak topic analytics:

```bash
pytest tests/ -v
```

All 15 test cases pass out-of-the-box!

---

## 🌐 Live Demo & Deployment Guide

### Deploying to Streamlit Community Cloud (1-Click Free Hosting)
1. Push your repository to GitHub: `https://github.com/DearDK14/smart-study-ai`.
2. Visit [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub account and select repository `DearDK14/smart-study-ai`.
4. Set Main file path to `app.py`.
5. Under **Advanced settings**, add your `GEMINI_API_KEY` (optional).
6. Click **Deploy!**

---

## 👨‍💻 Author
- **Team**: DearDK14
- **Hackathon**: CodeMyFYP Hack 26
