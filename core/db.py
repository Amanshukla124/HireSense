import sqlite3
import json
import os

DB_PATH     = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'hiresense.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')

def init_db():
    """Initializes the database using schema.sql."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())

        # Graceful column migrations for older databases
        for column, definition in [
            ("user_id",     "INTEGER"),
            ("ats_issues",  "TEXT"),
            ("target_role", "TEXT"),
            ("tailored_resumes", "TEXT"),
        ]:
            try:
                conn.execute(f"ALTER TABLE analyses ADD COLUMN {column} {definition}")
            except sqlite3.OperationalError:
                pass

        conn.commit()

def save_analysis(job_desc, resume, result, target_role="", user_id=None):
    """Saves a completed analysis to the database."""
    missing_skills = json.dumps(result.get("missing_skills", []))
    present_skills = json.dumps(result.get("present_skills", []))
    suggestions    = json.dumps(result.get("suggestions", []))
    strengths      = json.dumps(result.get("strengths", []))
    ats_issues     = json.dumps(result.get("ats_issues", []))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analyses (
                user_id, job_desc, resume, score, keyword_score, ai_score,
                missing_skills, present_skills, suggestions, strengths, ats_issues, target_role
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, job_desc, resume,
            result.get("score"),
            result.get("keyword_score"),
            result.get("ai_score"),
            missing_skills, present_skills,
            suggestions, strengths,
            ats_issues, target_role,
        ))
        conn.commit()
        return cursor.lastrowid

def save_tailored_resumes(analysis_id, options):
    """Saves tailored resume options to an existing analysis."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE analyses SET tailored_resumes = ? WHERE id = ?", (json.dumps(options), analysis_id))
        conn.commit()

def get_analyses_for_user(user_id):
    """Retrieves all past analyses for a specific user, most recent first."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        return [
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "job_desc_preview": (row["job_desc"][:100] + "...") if len(row["job_desc"]) > 100 else row["job_desc"],
                "score": row["score"],
                "missing_skills": json.loads(row["missing_skills"] or "[]"),
                "present_skills": json.loads(row["present_skills"] or "[]"),
                "target_role": row["target_role"] if "target_role" in row.keys() else "",
            }
            for row in rows
        ]

def get_analysis_by_id_for_user(analysis_id, user_id):
    """Retrieves a single full analysis record by ID, ensuring it belongs to the user."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id)).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "job_desc": row["job_desc"],
            "resume": row["resume"],
            "score": row["score"],
            "keyword_score": row["keyword_score"],
            "ai_score": row["ai_score"],
            "missing_skills": json.loads(row["missing_skills"] or "[]"),
            "present_skills": json.loads(row["present_skills"] or "[]"),
            "suggestions": json.loads(row["suggestions"] or "[]"),
            "strengths": json.loads(row["strengths"] or "[]"),
            "ats_issues": json.loads(row["ats_issues"]) if row["ats_issues"] else [],
            "target_role": row["target_role"] if "target_role" in row.keys() else "",
            "tailored_resumes": json.loads(row["tailored_resumes"]) if "tailored_resumes" in row.keys() and row["tailored_resumes"] else None,
        }
