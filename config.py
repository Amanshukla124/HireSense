import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-me-to-a-random-secret'
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL') or 'google/gemma-3-4b-it:free'

    # Google OAuth 2.0
    GOOGLE_CLIENT_ID     = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI  = os.environ.get('GOOGLE_REDIRECT_URI') or 'http://localhost:5001/auth/google/callback'
