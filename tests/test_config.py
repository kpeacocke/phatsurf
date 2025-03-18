import importlib

import pytest


def get_config():
    """
    Reloads and returns the Config class instance so that changes to
    environment variables are picked up.
    """
    import app.config

    importlib.reload(app.config)
    from app.config import Config

    return Config()


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    """
    Clear relevant environment variables before each test.
    """
    for key in ["MONGO_URI", "DEBUG", "SECRET_KEY", "TESTING", "WTF_CSRF_ENABLED"]:
        monkeypatch.delenv(key, raising=False)
    yield


def test_default_config(monkeypatch):
    """
    Test the default configuration values without environment overrides.
    """
    config = get_config()
    assert config.MONGO_URI == "mongodb://localhost:27017/phatsurf"
    assert config.DEBUG is False
    assert config.SECRET_KEY == "default-secret-key"


def test_env_override_config(monkeypatch):
    """
    Test configuration values overridden by environment variables.
    """
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017/test_env")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("SECRET_KEY", "overridden-secret-key")

    config = get_config()
    assert config.MONGO_URI == "mongodb://localhost:27017/test_env"
    assert config.DEBUG is True
    assert config.SECRET_KEY == "overridden-secret-key"


def test_testing_config(monkeypatch):
    """
    Test configuration values when TESTING is set to True and then False.
    """
    monkeypatch.setenv("TESTING", "True")
    config = get_config()
    assert config.TESTING is True

    monkeypatch.setenv("TESTING", "False")
    config = get_config()
    assert config.TESTING is False
