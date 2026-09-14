import json
import os
import subprocess
import sys

from filetools.questions import ask_multichoice
from filetools.settings import AppConfig


def test_ask_multichoice_shows_prompt(monkeypatch, caplog):
    # Regression: callers passed a prompt that ask_multichoice didn't accept (TypeError).
    monkeypatch.setattr("builtins.input", lambda _prompt="": "2")
    with caplog.at_level("INFO", logger="filetools"):
        assert ask_multichoice(["Movies", "Movies 4K"], "Select a movie library:") == "Movies 4K"
    assert "Select a movie library: (1, 2):" in caplog.text


def test_settings_path_from_environment(tmp_path, monkeypatch):
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({"metadata": {"year_range": {"min": 1950, "max": 2040}}}))
    monkeypatch.setenv("FILETOOLS_SETTINGS", str(settings))

    config = AppConfig()

    assert config.settings_path == settings
    assert (config.year_min, config.year_max) == (1950, 2040)


def test_package_config_honours_environment(tmp_path):
    # Regression: filetools/__init__.py always passed an explicit path, ignoring the variable.
    settings = tmp_path / "settings.json"
    settings.write_text("{}")
    result = subprocess.run(
        [sys.executable, "-c", "import filetools; print(filetools.CONFIG.settings_path)"],
        env={**os.environ, "FILETOOLS_SETTINGS": str(settings)},
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == str(settings)
