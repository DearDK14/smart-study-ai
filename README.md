# ⚡ StudyForge AI • Modern Student Learning OS

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GUI: CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter%206.0-0284c7.svg)](https://customtkinter.tomschimansky.com/)
[![Database: SQLite](https://img.shields.io/badge/database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Tests: Pytest](https://img.shields.io/badge/tests-16%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![Theme: Light Blue & White](https://img.shields.io/badge/theme-Light%20Blue%20%26%20White-sky.svg)](https://customtkinter.tomschimansky.com/)

**StudyForge AI** is a modern, responsive Python desktop application designed for students and educators. Built with **CustomTkinter**, it converts dense lecture notes and textbook PDFs into structured executive summaries, multiple-choice quiz assessments, 3D study flashcards, personal study notes, and diagnostic weak-topic learning analytics.

---

## 🌟 Key Features

### 1. 🖥️ Modern Desktop GUI (CustomTkinter)
- **Design Style**: Sleek light-blue and white card interface (`#0284c7`, `#e0f2fe`, `#ffffff`) with rounded cards, smooth hover states, and native Dark Mode support.
- **Single Window Architecture**: Left sidebar navigation, responsive top header with live XP and Level badges, and dynamic content frames that switch smoothly without popup clutter.
- **Asynchronous Threading**: AI processing and document extractions run in dedicated background threads (`threading.Thread`) so the user interface never freezes.

### 2. 📚 Document Management & PDF Extraction
- Powered by `pypdf` with support for `.pdf`, `.txt`, and `.md` files up to 25MB.
- Automatic page-by-page extraction, word count computation, and estimated reading time calculation.
- Built-in document viewer with full extracted text inspection and safe deletion.

### 3. 📑 AI Summaries & Content Pipeline
- Synthesizes comprehensive Executive Summaries, high-yield exam crams, and concept glossaries.
- Dual-engine architecture:
  - **Online**: Google Gemini API (`gemini-1.5-flash`).
  - **Offline Local NLP**: Built-in statistical term extractor and heuristic synthesizer that **works 100% offline with zero API key**.
- One-click copy to clipboard and SQLite history log.

### 4. ❓ Question Generator & Question Bank
- Customizable question generation: choose difficulty (*Easy*, *Medium*, *Hard*) and question count (3 to 12).
- Automatic distractor formulation, correct answer keys, and pedagogical explanations.
- Searchable Question Bank with direct links to assessment mode.

### 5. 📝 Interactive Quiz Assessment
- Full multiple-choice testing interface with radio options (A, B, C, D) and progress bar.
- Instant automated scoring, question-by-question review, and celebratory feedback.
- Automated **Weak Topics Diagnostic**: identifies subjects with $<60\%$ accuracy from real student answers.

### 6. 🗂️ Interactive Study Flashcards
- 3D-styled flip cards with front concept/question and back definition/answer.
- Spaced repetition recall ratings (*Hard*, *Medium*, *Mastered*) that award XP and update mastery tracking in SQLite.

### 7. 📓 Personal Study Notebook
- Rich note creator with title, content, tags, and document linking.
- Real-time search filter and instant note deletion.

### 8. 📈 Diagnostic Learning Analytics
- Analyzes actual quiz attempt history from SQLite.
- Categorizes topics into Strong vs Weak ($<60\%$ accuracy).
- Progress bar visualizer for topic mastery and full quiz attempt log.

### 9. ⚙️ Settings & Theme Customization
- One-click Light / Dark / System theme switching.
- Gemini API key manager with live online/offline engine status.
- Safe database reset tool with confirmation dialog.

---

## 📁 Project Architecture

```text
Hack 26/
├── app.py                     # Main application entry point (launches Desktop GUI)
├── requirements.txt           # Python package dependencies
├── .env                       # Environment variables (API keys)
├── .env.example               # Template environment configuration
├── .gitignore                 # Version control exclusions
├── README.md                  # Comprehensive documentation
│
├── gui/                       # CustomTkinter Desktop GUI Framework
│   ├── __init__.py            # GUI package exports
│   ├── main_window.py         # Main CTk root window & page router
│   ├── theme.py               # Palette tokens, typography, CTk theme setup
│   ├── sidebar.py             # Left navigation sidebar
│   ├── header.py              # Top header with XP pill, level, user badge
│   ├── dashboard_view.py      # Student dashboard view
│   ├── documents_view.py      # PDF/document upload & manager view
│   ├── summaries_view.py      # AI summaries view
│   ├── questions_view.py      # Question generator view
│   ├── quiz_view.py           # Interactive quiz player view
│   ├── flashcards_view.py     # Flashcards study view
│   ├── notebook_view.py       # Personal notebook view
│   ├── analytics_view.py      # Weak topics & learning analytics view
│   └── settings_view.py       # Settings & theme configuration view
│
├── database/                  # SQLite Persistent Storage
│   ├── __init__.py
│   ├── connection.py          # SQLite connection manager
│   ├── models.py              # CRUD models for documents, quizzes, flashcards, stats
│   └── schema.sql             # Relational schema
│
├── services/                  # Business Logic & AI Engines
│   ├── __init__.py
│   ├── ai_service.py          # Gemini API + Local Heuristic NLP fallback
│   ├── pdf_service.py         # PDF text extraction and document parsing
│   ├── summary_service.py     # Summary generation and persistence
│   ├── question_service.py    # MCQ generation, grading, weak topic analysis
│   └── flashcard_service.py   # Flashcard generation and mastery tracking
│
├── config/
│   ├── __init__.py
│   └── settings.py            # App settings, paths, thresholds
│
├── utils/
│   ├── __init__.py
│   ├── validators.py          # File and data schema validation
│   └── helpers.py             # Text processing, reading time, XP math
│
├── tests/                     # Automated Test Suite (Pytest)
│   ├── __init__.py
│   ├── test_database.py       # Database CRUD tests
│   ├── test_pdf_service.py    # PDF text extraction tests
│   ├── test_quiz.py           # Quiz grading & weak topic detection tests
│   ├── test_validators.py     # Input validation tests
│   └── test_gui_navigation.py # CustomTkinter GUI startup & navigation tests
│
├── data/
│   └── .gitkeep               # SQLite database directory
└── uploads/
    ├── .gitkeep
    └── biology_cellular_respiration.txt  # Sample study materials
```

---

## 🚀 Installation & Running

### 1. Install Dependencies
Ensure Python 3.10+ is installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Launch the Desktop Application
Run the main application script:
```bash
python app.py
```
The **StudyForge AI** desktop window will open immediately!

*(Optional) To launch the Streamlit web dashboard instead:*
```bash
python app.py --web
# or
streamlit run app.py
```

---

## 🧪 Running Automated Tests

Run the full Pytest test suite:
```bash
python -m pytest tests/ -v
```
**Result**: 16/16 test cases passing!

---

## 👨‍💻 Author & Credits
- **Project**: StudyForge AI (Hack 26 Edition)
- **Repository**: [https://github.com/DearDK14/smart-study-ai](https://github.com/DearDK14/smart-study-ai)
