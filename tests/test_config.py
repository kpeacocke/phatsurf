import importlib
from unittest.mock import patch

from pytest import MonkeyPatch


def test_default_config(monkeypatch: MonkeyPatch):
    """
    Test the default configuration values without environment overrides.
    """
    # Clear relevant environment variables to simulate defaults
    monkeypatch.delenv("MONGO_URI", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)

    # Reload the Config class to reflect environment changes
    import app.config

    importlib.reload(app.config)
    from app.config import Config

    # Verify default values
    config = Config()
    assert config.MONGO_URI == "mongodb://localhost:27017/phatsurf"
    assert config.DEBUG is False
    assert config.SECRET_KEY == "default-secret-key"


def test_env_override_config(monkeypatch: MonkeyPatch):
    """
    Test configuration values overridden by environment variables.
    """
    # Set environment variables
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017/test_env")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("SECRET_KEY", "overridden-secret-key")

    # Reload the Config class to reflect environment changes
    import app.config

    importlib.reload(app.config)
    from app.config import Config

    # Verify overridden values
    config = Config()
    assert config.MONGO_URI == "mongodb://localhost:27017/test_env"
    assert config.DEBUG is True
    assert config.SECRET_KEY == "overridden-secret-key"


def test_non_testing_mode(monkeypatch: MonkeyPatch):
    """
    Test that `load_dotenv` is called when the application is not in testing mode.
    """
    # Ensure TESTING is set to False
    monkeypatch.setenv("TESTING", "False")

    # Mock `load_dotenv` to verify if it gets called
    import app.config

    importlib.reload(app.config)
    from app.config import Config

    with patch("dotenv.load_dotenv") as mock_load_dotenv:
        Config()  # Instantiate Config to trigger `load_dotenv`
        mock_load_dotenv.assert_called_once()
