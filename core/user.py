import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from core.db import DB_PATH


class User(UserMixin):
    """Flask-Login compatible User model backed by SQLite."""

    def __init__(self, id, email, first_name, last_name,
                 password_hash, google_id, avatar_url, created_at):
        self.id = id
        self.email = email
        self.first_name = first_name or ""
        self.last_name = last_name or ""
        self.password_hash = password_hash
        self.google_id = google_id
        self.avatar_url = avatar_url
        self.created_at = created_at

    @property
    def display_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.email

    @property
    def initials(self):
        parts = self.display_name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.display_name[:2].upper()

    # ── DB helpers ──────────────────────────────────

    @staticmethod
    def _row_to_user(row):
        if not row:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            password_hash=row["password_hash"],
            google_id=row["google_id"],
            avatar_url=row["avatar_url"],
            created_at=row["created_at"],
        )

    @staticmethod
    def get_by_id(user_id):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return User._row_to_user(row)

    @staticmethod
    def get_by_email(email):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
            return User._row_to_user(row)

    @staticmethod
    def get_by_google_id(google_id):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE google_id = ?", (google_id,)
            ).fetchone()
            return User._row_to_user(row)

    @staticmethod
    def create_with_password(email, password, first_name="", last_name=""):
        """Register a new email/password user. Returns User or raises ValueError."""
        if User.get_by_email(email):
            raise ValueError("An account with this email already exists.")
        pw_hash = generate_password_hash(password)
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """INSERT INTO users (email, first_name, last_name, password_hash)
                   VALUES (?, ?, ?, ?)""",
                (email, first_name, last_name, pw_hash),
            )
            conn.commit()
            return User.get_by_id(cur.lastrowid)

    @staticmethod
    def create_or_update_from_google(google_id, email, first_name, last_name, avatar_url):
        """Upsert a user coming from Google OAuth. Returns User."""
        existing = User.get_by_google_id(google_id)
        if existing:
            # Update avatar/name in case they changed
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    """UPDATE users SET first_name=?, last_name=?, avatar_url=?
                       WHERE google_id=?""",
                    (first_name, last_name, avatar_url, google_id),
                )
                conn.commit()
            return User.get_by_google_id(google_id)

        # Maybe the email already exists (they registered with password first)
        by_email = User.get_by_email(email)
        if by_email:
            # Link Google ID to the existing account
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "UPDATE users SET google_id=?, avatar_url=? WHERE id=?",
                    (google_id, avatar_url, by_email.id),
                )
                conn.commit()
            return User.get_by_id(by_email.id)

        # Brand new user via Google
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """INSERT INTO users (email, first_name, last_name, google_id, avatar_url)
                   VALUES (?, ?, ?, ?, ?)""",
                (email, first_name, last_name, google_id, avatar_url),
            )
            conn.commit()
            return User.get_by_id(cur.lastrowid)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
