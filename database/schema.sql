-- Schema for Smart Study AI (StudyGenius)

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    title TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    page_count INTEGER DEFAULT 1,
    word_count INTEGER DEFAULT 0,
    extracted_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    summary_type TEXT DEFAULT 'executive',
    content TEXT NOT NULL,
    key_takeaways TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    topic TEXT NOT NULL DEFAULT 'General',
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT NOT NULL, -- 'A', 'B', 'C', or 'D'
    explanation TEXT,
    difficulty TEXT DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    document_id INTEGER,
    question_ids_json TEXT NOT NULL, -- JSON array of question IDs
    total_questions INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    percentage REAL NOT NULL,
    answers_json TEXT NOT NULL, -- Detailed breakdown per question
    weak_topics_json TEXT,       -- Detected weak topics from this run
    xp_earned INTEGER DEFAULT 0,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    deck_name TEXT NOT NULL DEFAULT 'Default Deck',
    topic TEXT NOT NULL DEFAULT 'General',
    front_text TEXT NOT NULL,
    back_text TEXT NOT NULL,
    mastery_level TEXT DEFAULT 'learning', -- 'learning', 'reviewing', 'mastered'
    reviews_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS user_stats (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    xp_total INTEGER DEFAULT 11735,
    level INTEGER DEFAULT 11,
    streak_days INTEGER DEFAULT 1,
    gems INTEGER DEFAULT 250,
    tasks_pending INTEGER DEFAULT 1,
    focus_minutes_total INTEGER DEFAULT 120,
    last_active_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notebook (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT DEFAULT 'General',
    document_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE SET NULL
);

-- Insert default user stats if not exists (matching the StudyGenius screenshot)
INSERT OR IGNORE INTO user_stats (id, xp_total, level, streak_days, gems, tasks_pending, focus_minutes_total, last_active_date)
VALUES (1, 11735, 11, 1, 250, 1, 120, DATE('now'));
