from flask import Flask
from app.extensions import mongo

def create_app():
    """
    Application factory for Flask.
    """
    app = Flask(__name__)
    app.config["MONGO_URI"] = "mongodb://localhost:27017/phatsurf"
    mongo.init_app(app)

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
