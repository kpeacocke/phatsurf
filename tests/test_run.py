import runpy
import sys
from unittest.mock import patch

import pytest


class FakeApp:
    def run(self, host, port, debug, use_reloader):
        print(
            f"app.run called with host={host}, port={port}, "
            f"debug={debug}, use_reloader={use_reloader}"
        )


def fake_create_app(*args, **kwargs):
    return FakeApp()


@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    # Ensure environment variables are reset between tests.
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("DEBUG_PORT", raising=False)
    monkeypatch.delenv("FLASK_RUN_HOST", raising=False)
    monkeypatch.delenv("FLASK_RUN_PORT", raising=False)
    monkeypatch.delenv("FLASK_DEBUG", raising=False)


def test_run_debug_mode(monkeypatch, capsys):
    """
    Test run.py in development mode (debug mode).
    It should initialize debugpy and call app.run().
    """
    # Set up environment for development.
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("DEBUG_PORT", "5678")
    monkeypatch.setenv("FLASK_RUN_HOST", "0.0.0.0")
    monkeypatch.setenv("FLASK_RUN_PORT", "5001")
    # Also set FLASK_DEBUG to trigger debug behavior.
    monkeypatch.setenv("FLASK_DEBUG", "true")

    # Patch debugpy so that it doesn't actually try to listen.
    fake_debugpy = type("FakeDebugpy", (), {})()
    fake_debugpy._initialized = False

    def fake_listen(address):
        fake_debugpy._initialized = True
        print(f"Debugpy is listening on port {address[1]}")

    fake_debugpy.listen = fake_listen
    monkeypatch.setitem(sys.modules, "debugpy", fake_debugpy)

    # Override create_app to return our fake app.
    monkeypatch.setattr("app.create_app", fake_create_app)

    # Prevent sys.exit from being called in case of failure.
    with patch("sys.exit"):
        runpy.run_path("run.py", run_name="__main__")

    captured = capsys.readouterr().out
    # Check that debugpy was initialized.
    assert "Debugpy is listening on port" in captured
    # Check that the app run call was made.
    assert "app.run called" in captured
    # Also check that a message about starting debug mode is printed.
    assert "Starting Flask app in debug mode" in captured


def test_run_production_mode(monkeypatch, capsys):
    """
    Test run.py in production mode.
    It should NOT call app.run() but instead print a production usage message.
    """
    # Set production environment.
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("FLASK_RUN_HOST", "0.0.0.0")
    monkeypatch.setenv("FLASK_RUN_PORT", "5001")
    # Ensure FLASK_DEBUG is not true.
    monkeypatch.setenv("FLASK_DEBUG", "false")

    # Override create_app to return our fake app.
    monkeypatch.setattr("app.create_app", fake_create_app)

    # Run run.py in production mode.
    runpy.run_path("run.py", run_name="__main__")

    captured = capsys.readouterr().out
    assert "This application is configured for production" in captured
    # Ensure that app.run() was not called.
    assert "app.run called" not in captured


def test_run_debugpy_failure(monkeypatch, capsys):
    """
    Test the branch in run.py where debugpy initialization fails.
    It should print an error and call sys.exit(1).
    """
    # Set up environment for development.
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("DEBUG_PORT", "5678")
    monkeypatch.setenv("FLASK_RUN_HOST", "0.0.0.0")
    monkeypatch.setenv("FLASK_RUN_PORT", "5001")
    monkeypatch.setenv("FLASK_DEBUG", "true")

    # Patch debugpy so that its listen() method fails.
    class FakeDebugpy:
        _initialized = False

        @staticmethod
        def listen(address):
            raise RuntimeError("Forced debugpy failure")

    monkeypatch.setitem(sys.modules, "debugpy", FakeDebugpy)
    monkeypatch.setattr("app.create_app", fake_create_app)

    # Expect run.py to call sys.exit(1) when debugpy initialization fails.
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path("run.py", run_name="__main__")
    assert exc_info.value.code == 1

    captured = capsys.readouterr().out
    assert "Failed to initialize debugpy on port" in captured
