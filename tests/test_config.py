import importlib

from pytest import MonkeyPatch


def test_default_config(monkeypatch: MonkeyPatch):
    """
    Test the default configuration values.
    """
    # Ensure no environment variable is interfering
    monkeypatch.delenv("MONGO_URI", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)

    # Reimport Config to ensure it picks up the modified environment
    import app.config

    importlib.reload(app.config)
    from app.config import Config

    # Instantiate Config to trigger all code paths
    config = Config()

    assert config.MONGO_URI == "mongodb://localhost:27017/phatsurf"
    assert config.DEBUG is False
    assert config.SECRET_KEY == "default-secret-key"


def test_env_override_config(monkeypatch: MonkeyPatch):
    """
    Test configuration values overridden by environment variables.
    """
    # Override environment variables
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017/test_env")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("SECRET_KEY", "overridden-secret-key")

    # Reimport Config to ensure it picks up the modified environment
    import app.config

    importlib.reload(app.config)
    from app.config import Config

    # Instantiate Config to trigger all code paths
    config = Config()

    assert config.MONGO_URI == "mongodb://localhost:27017/test_env"
    assert config.DEBUG is True
    assert config.SECRET_KEY == "overridden-secret-key"


def test_non_testing_mode(monkeypatch):
    """
    Test that load_dotenv is called when not in testing mode.
    """
    # Ensure TESTING is set to False
    monkeypatch.setenv("TESTING", "False")

    # Mock load_dotenv to check if it's called
    import app.config

    importlib.reload(app.config)
    from unittest.mock import patch

    from app.config import Config

    with patch("dotenv.load_dotenv") as mock_load_dotenv:
        Config()  # noqa: F841

    mock_load_dotenv.assert_called_once()
