import logging
import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from app.config import Config
from app.extensions import mongo
from app.routes import bcrypt, login_manager, main


def create_app(testing: bool = False):
    """
    Application factory for Flask.
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    if testing:
        app.config["TESTING"] = True
    if testing or os.getenv("FLASK_ENV") == "development":
        app.config["TESTING"] = True
    if testing or os.getenv("FLASK_ENV") == "development":
        # Disable CSRF for testing and development
        app.config["WTF_CSRF_ENABLED"] = False

    # Enable CSRF protection in production
    csrf = CSRFProtect()
    if not testing and app.config.get("WTF_CSRF_ENABLED", True):
        csrf.init_app(app)

    # Initialize database and extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Set up logging
    configure_logging(app)

    # Register blueprints
    app.register_blueprint(main)

    return app


def configure_logging(app):
    """
    Configures logging for the Flask app.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    )
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    app.logger.info(
        f"App initialized with MONGO_URI: {app.config.get('MONGO_URI', 'Not Set')}"
    )


def run_app():
    """
    Main entry point for running the Flask app.
    """
    app = create_app()
    app.run(
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true",
        host="0.0.0.0",
        port=5000,
    )


if __name__ == "__main__":  # pragma: no cover
    run_app()  # pragma: no cover
