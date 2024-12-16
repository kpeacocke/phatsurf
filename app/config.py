import os


class Config:
    """
    Flask configuration class.
    """

    TESTING = os.getenv("TESTING", "False") == "True"

    def __init__(self):
        # Load environment variables only if not in testing mode
        if not self.TESTING:
            from dotenv import load_dotenv

            load_dotenv()

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/phatsurf")
    DEBUG = os.getenv("DEBUG", "False") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
