CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    job_desc TEXT NOT NULL,
    resume TEXT NOT NULL,
    score INTEGER,
    keyword_score INTEGER,
    ai_score INTEGER,
    missing_skills TEXT,
    present_skills TEXT,
    suggestions TEXT,
    strengths TEXT,
    tailored_resumes TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    password_hash TEXT,
    google_id TEXT UNIQUE,
    avatar_url TEXT
);
