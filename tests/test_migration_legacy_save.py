"""
Unit tests for migrating legacy JSON saves (such as saves without individual_id,
string-formatted items, and deduplicating main Pokemon).
"""

import json
import uuid
from pathlib import Path
import pytest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication

from Ankimon.pyobj.database_manager import AnkimonDB
from Ankimon.pyobj.migration_dialog import MigrationDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


def test_migrate_from_json_legacy_files(tmp_path):
    """Test AnkimonDB.migrate_from_json with legacy JSON structures."""
    db_path = tmp_path / "ankimon.db"
    db = AnkimonDB(db_path=db_path)

    mypokemon_data = [
        {
            "name": "Charizard", "nickname": None, "gender": "M", "level": 59, "id": 6,
            "ability": "Blaze", "type": ["Fire", "Flying"],
            "stats": {"hp": 78, "atk": 84, "def": 78, "spa": 109, "spd": 85, "spe": 100},
            "ev": {"hp": 56, "atk": 73, "def": 63, "spa": 35, "spd": 31, "spe": 43},
            "iv": {"hp": 5, "atk": 11, "def": 2, "spa": 23, "spd": 9, "spe": 31},
            "attacks": ["flamethrower", "airslash"], "base_experience": 267,
            "growth_rate": "medium-slow"
        },
        {
            "name": "Pikachu", "nickname": "Sparky", "gender": "M", "level": 25, "id": 25,
            "ability": "Static", "type": ["Electric"],
            "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "attacks": ["thunderbolt", "quickattack"], "base_experience": 112,
            "growth_rate": "medium-fast"
        }
    ]

    mainpokemon_data = [
        {
            "name": "Charizard", "nickname": None, "gender": "M", "level": 59, "id": 6,
            "ability": "Blaze", "type": ["Fire", "Flying"],
            "stats": {"hp": 78, "atk": 84, "def": 78, "spa": 109, "spd": 85, "spe": 100},
            "ev": {"hp": 56, "atk": 73, "def": 63, "spa": 35, "spd": 31, "spe": 43},
            "iv": {"hp": 5, "atk": 11, "def": 2, "spa": 23, "spd": 9, "spe": 31},
            "attacks": ["flamethrower", "airslash"], "base_experience": 267,
            "growth_rate": "medium-slow"
        }
    ]

    items_data = ["potion", "pp-max", "wide-lens", "wide-lens"]
    badges_data = [1, 2, 3, 4]

    mypokemon_path = tmp_path / "mypokemon.json"
    mainpokemon_path = tmp_path / "mainpokemon.json"
    items_path = tmp_path / "items.json"
    badges_path = tmp_path / "badges.json"

    mypokemon_path.write_text(json.dumps(mypokemon_data), encoding="utf-8")
    mainpokemon_path.write_text(json.dumps(mainpokemon_data), encoding="utf-8")
    items_path.write_text(json.dumps(items_data), encoding="utf-8")
    badges_path.write_text(json.dumps(badges_data), encoding="utf-8")

    stats = db.migrate_from_json(
        mypokemon_path=mypokemon_path,
        mainpokemon_path=mainpokemon_path,
        items_path=items_path,
        badges_path=badges_path
    )

    assert stats["pokemon"] == 2
    assert stats["main"] == 1
    assert db.get_pokemon_count() == 2
    main_p = db.get_main_pokemon()
    assert main_p is not None
    assert main_p["name"] == "Charizard"
    assert main_p["level"] == 59

    # Verify item quantities
    wide_lens = db.get_item("wide-lens")
    assert wide_lens is not None
    assert wide_lens["quantity"] == 2

    # Verify badges
    assert db.execute("SELECT COUNT(*) FROM badges").fetchone()[0] == 4


def test_migration_dialog_legacy_files(qapp, tmp_path):
    """Test MigrationDialog with legacy JSON structures."""
    db_path = tmp_path / "ankimon.db"
    db = AnkimonDB(db_path=db_path)

    mypokemon_data = [
        {
            "name": "Charizard", "nickname": None, "gender": "M", "level": 59, "id": 6,
            "ability": "Blaze", "type": ["Fire", "Flying"],
            "stats": {"hp": 78, "atk": 84, "def": 78, "spa": 109, "spd": 85, "spe": 100},
            "ev": {"hp": 56, "atk": 73, "def": 63, "spa": 35, "spd": 31, "spe": 43},
            "iv": {"hp": 5, "atk": 11, "def": 2, "spa": 23, "spd": 9, "spe": 31},
            "attacks": ["flamethrower", "airslash"], "base_experience": 267,
            "growth_rate": "medium-slow"
        }
    ]
    mainpokemon_data = [mypokemon_data[0]]
    items_data = ["potion", "wide-lens", "wide-lens"]
    badges_data = [1, 2]

    mypokemon_path = tmp_path / "mypokemon.json"
    mainpokemon_path = tmp_path / "mainpokemon.json"
    items_path = tmp_path / "items.json"
    badges_path = tmp_path / "badges.json"

    mypokemon_path.write_text(json.dumps(mypokemon_data), encoding="utf-8")
    mainpokemon_path.write_text(json.dumps(mainpokemon_data), encoding="utf-8")
    items_path.write_text(json.dumps(items_data), encoding="utf-8")
    badges_path.write_text(json.dumps(badges_data), encoding="utf-8")

    dialog = MigrationDialog(
        db,
        mypokemon_path=mypokemon_path,
        mainpokemon_path=mainpokemon_path,
        items_path=items_path,
        badges_path=badges_path
    )

    with patch("PyQt6.QtWidgets.QApplication.processEvents"):
        dialog._run_migration()

    assert dialog.migration_successful
    assert db.get_pokemon_count() == 1
    main_p = db.get_main_pokemon()
    assert main_p is not None
    assert main_p["name"] == "Charizard"
    wide_lens = db.get_item("wide-lens")
    assert wide_lens is not None
    assert wide_lens["quantity"] == 2
