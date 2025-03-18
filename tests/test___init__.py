import logging
import os

from flask import Flask

from app import configure_logging, create_app, run_app


def test_create_app():
    """Test that the Flask app is created properly."""
    app = create_app()
    assert isinstance(app, Flask)
    assert app.config["WTF_CSRF_ENABLED"]  # CSRF should be enabled by default
    assert "main" in app.blueprints  # Ensure blueprint is registered


def test_create_app_testing():
    """Test that the app is properly configured for testing."""
    app = create_app(testing=True)
    assert app.config["TESTING"] is True
    # CSRF should be disabled in tests.
    assert app.config["WTF_CSRF_ENABLED"] is False


def test_create_app_development(monkeypatch):
    """Test that CSRF is disabled in development mode."""
    monkeypatch.setenv("FLASK_ENV", "development")
    app = create_app()
    # In development, CSRF is disabled.
    assert app.config["WTF_CSRF_ENABLED"] is False


def test_configure_logging(caplog, monkeypatch):
    """Test that logging is correctly configured."""
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    app = Flask(__name__)
    configure_logging(app)
    # DEBUG level is 10.
    assert app.logger.level == 10
    app.logger.debug("Test debug message")
    assert "Test debug message" in caplog.text


def test_logging_output(caplog):
    """Ensure that log messages are recorded correctly."""
    app = create_app()
    with caplog.at_level(logging.INFO):
        app.logger.info("Test log entry")
    assert "Test log entry" in caplog.text


def test_mongo_initialization(monkeypatch):
    """Ensure MongoDB initialization is called."""
    calls = []

    def fake_init_app(app):
        calls.append(app)

    monkeypatch.setattr("app.extensions.mongo.init_app", fake_init_app)
    app = create_app()
    assert len(calls) == 1
    assert calls[0] is app


def test_login_manager_initialization(monkeypatch):
    """Ensure Flask-Login is properly initialized."""
    calls = []

    def fake_init_app(app):
        calls.append(app)

    monkeypatch.setattr("app.routes.login_manager.init_app", fake_init_app)
    app = create_app()
    assert len(calls) == 1
    assert calls[0] is app


def test_bcrypt_initialization(monkeypatch):
    """Ensure Flask-Bcrypt is properly initialized."""
    calls = []

    def fake_init_app(app):
        calls.append(app)

    monkeypatch.setattr("app.routes.bcrypt.init_app", fake_init_app)
    app = create_app()
    assert len(calls) == 1
    assert calls[0] is app


def test_csrf_disabled_in_testing():
    """Ensure CSRF is disabled in testing mode."""
    app = create_app(testing=True)
    assert not app.config["WTF_CSRF_ENABLED"]


def test_main_run(monkeypatch):
    """
    Test the __main__ block in __init__.py using runpy.

    This test monkeypatches create_app to return a fake app with a run() method.
    When the __main__ block is executed via run_app, it should call app.run().
    """
    run_called = {"flag": False}

    class FakeApp:
        def run(self, **kwargs):
            run_called["flag"] = True
            debug_env = os.getenv("FLASK_DEBUG", "False").lower() == "true"
            assert kwargs.get("debug") == debug_env
            assert kwargs.get("host") == "0.0.0.0"
            assert kwargs.get("port") == 5000

    def fake_create_app(*args, **kwargs):
        return FakeApp()

    monkeypatch.setattr("app.create_app", fake_create_app)
    run_app()
    assert run_called["flag"]
