import importlib

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


def test_testing_config(monkeypatch: MonkeyPatch):
    """
    Test configuration values when TESTING is set to True and False.
    """
    # Set environment variables
    monkeypatch.setenv("TESTING", "True")

    # Reload the Config class to reflect environment changes
    import app.config
    importlib.reload(app.config)
    from app.config import Config

    # Verify TESTING is True
    config = Config()
    assert config.TESTING is True

    # Set environment variables
    monkeypatch.setenv("TESTING", "False")

    # Reload the Config class to reflect environment changes
    importlib.reload(app.config)
    from app.config import Config

    # Verify TESTING is False
    config = Config()
    assert config.TESTING is False
