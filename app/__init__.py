import os
import logging
from flask import Flask
from app.extensions import mongo


def create_app():
    """
    Application factory for Flask.
    """
    app = Flask(__name__)

    # Configure MongoDB URI
    app.config["MONGO_URI"] = os.getenv(
        "MONGO_URI", "mongodb://localhost:27017/phatsurf"
    )
    mongo.init_app(app)

    # Set up logging
    configure_logging(app)

    # Register blueprints
    from app.routes import main

    app.register_blueprint(main)

    return app


def configure_logging(app):
    """
    Configures logging for the Flask app.
    """
    # Set log level to DEBUG for detailed output during development
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
    )

    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)

    # Log the current configuration
    app.logger.debug(f"App initialized with MONGO_URI: {app.config['MONGO_URI']}")