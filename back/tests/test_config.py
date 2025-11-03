from pathlib import Path

import pytest

from ..src import config


@pytest.fixture
def mock_config(monkeypatch):
    test_values = {
        "data": {
            "rows_to_generate": 100,
            "write_to_csv": False,
        }
    }
    monkeypatch.setattr(config, "_config", test_values)
    return test_values


def test_config_path_is_path():
    assert isinstance(config.CONFIG_PATH, Path)


def test_config_get_returns_value(mock_config):
    assert config.get("data.rows_to_generate") == 100
    assert config.get("data.write_to_csv") is False


def test_empty_key_returns_dict(mock_config):
    assert config.get() == mock_config


def test_nonexistent_path_returns_default(mock_config):
    assert config.get("doesnt.exist", True) is True
