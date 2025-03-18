import os


class Config:
    """
    Flask configuration class.
    """

    def __init__(self):
        # Load environment variables from .env only if not in testing mode
        if os.getenv("TESTING", "False").lower() != "true":
            from dotenv import load_dotenv

            load_dotenv()

    # General Configuration
    TESTING = os.getenv("TESTING", "False").lower() == "true"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")

    # Database Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/phatsurf")

    # Security Enhancements
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # CSRF Protection
    WTF_CSRF_ENABLED = os.getenv("WTF_CSRF_ENABLED", "True").lower() == "true"

    # Logging Level
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
