import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'expensemate-secret-key-super-secure-2026'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'expensemate.db')
    SESSION_COOKIE_NAME = 'expensemate_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit for file uploads
