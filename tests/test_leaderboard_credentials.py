"""Security and migration contracts for leaderboard credentials."""

import importlib.util
import json
from pathlib import Path


_SCHEMA_PATH = (
    Path(__file__).parent.parent
    / "src"
    / "Ankimon"
    / "ankimon_items_web"
    / "settings_schema.py"
)


def _load_settings_schema():
    spec = importlib.util.spec_from_file_location(
        "ankimon_settings_schema_credentials_test", _SCHEMA_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_secret_setting_serialization_never_exposes_stored_value():
    schema = _load_settings_schema()

    serialized = schema.serialize_secret_setting("actual-secret-api-key")

    assert "actual-secret-api-key" not in json.dumps(serialized)
    assert serialized == {
        "type": "password",
        "value": schema.SECRET_SETTING_PLACEHOLDER,
        "secret_configured": True,
        "secret_placeholder": schema.SECRET_SETTING_PLACEHOLDER,
    }


def test_empty_secret_serializes_as_unconfigured():
    schema = _load_settings_schema()

    serialized = schema.serialize_secret_setting("")

    assert serialized["value"] == ""
    assert serialized["secret_configured"] is False


def test_secret_placeholder_and_summary_redaction_contract():
    schema = _load_settings_schema()

    assert schema.is_unchanged_secret_placeholder(
        schema.SECRET_SETTING_PLACEHOLDER
    )
    assert not schema.is_unchanged_secret_placeholder("replacement-key")
    assert (
        schema.display_setting_value("leaderboard.api_key", "actual-secret-api-key")
        == schema.SECRET_SETTING_PLACEHOLDER
    )
    assert schema.display_setting_value("leaderboard.username", "Nuz") == "Nuz"
