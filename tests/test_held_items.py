"""Held-item lifecycle tests (F12).

These self-mock ``aqt``/``anki`` and force-load the real ``database_manager`` /
``utils`` / ``pokemon_obj`` modules so the held-item give/remove logic can be
exercised without an Anki runtime. On main's org that logic runs through the
service seam (``services.db`` / ``services.main_pokemon``), so the fixture wires
the temp DB onto ``services`` with auto-reverting ``patch.object``.

IMPORTANT (blast-radius): all ``sys.modules`` mutation and module force-loading
happens **inside the fixture**, never at import time, and is snapshot/restored on
teardown. Doing it at module scope would leave a mock-bound ``Ankimon.utils`` in
``sys.modules`` at collection time and break unrelated Tier-1 tests
(e.g. test_ankimon_tracker) that later import the real module.
"""

import sys
import csv
import pytest
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch
import types

_src = Path(__file__).parent.parent / "src"

# sys.modules keys this file mocks / force-loads. Snapshotted and restored around
# the fixture so nothing leaks into the rest of the Tier-1 suite.
_MANAGED_KEYS = (
    "aqt", "aqt.qt", "aqt.utils", "aqt.gui_hooks", "aqt.operations",
    "aqt.reviewer", "aqt.webview", "aqt.main", "aqt.operations.QueryOp", "aqt.theme",
    "anki", "anki.hooks", "anki.collection", "anki.models", "anki.notes",
    "anki.template", "anki.buildinfo",
    "Ankimon.resources", "Ankimon.singletons", "Ankimon.business",
    "Ankimon.pyobj.database_manager", "Ankimon.utils", "Ankimon.pyobj.pokemon_obj",
)

# Module-global class handles, (re)assigned by the fixture. Placeholders only —
# no module is imported at collection time.
AnkimonDB = None
PokemonObject = None


def _snapshot_modules():
    return {k: sys.modules.get(k) for k in _MANAGED_KEYS}


def _restore_modules(snap):
    for k, v in snap.items():
        if v is None:
            sys.modules.pop(k, None)
        else:
            sys.modules[k] = v


def setup_mocks():
    # Mock aqt/anki namespaces force unconditionally
    for name in [
        "aqt", "aqt.qt", "aqt.utils", "aqt.gui_hooks", "aqt.operations",
        "aqt.reviewer", "aqt.webview", "aqt.main", "aqt.operations.QueryOp", "aqt.theme",
        "anki", "anki.hooks", "anki.collection", "anki.models", "anki.notes", "anki.template", "anki.buildinfo"
    ]:
        sys.modules[name] = MagicMock()

    # 1. Force Register packages with __path__ so relative imports resolve
    for _pkg in ("Ankimon", "Ankimon.functions", "Ankimon.pyobj"):
        _mod = sys.modules.get(_pkg)
        if not _mod or isinstance(_mod, MagicMock) or not hasattr(_mod, "__path__"):
            _mod = types.ModuleType(_pkg)
            sys.modules[_pkg] = _mod

        # Always ensure package settings are set
        _mod.__path__ = [str(_src / _pkg.replace(".", "/"))]
        _mod.__package__ = _pkg

    # Define a robust mock for resources
    class MockResources:
        user_path = Path("/tmp")
        csv_file_items_cost = Path("/tmp/items.csv")
        items_path = Path("/tmp/items.json")
        badges_path = Path("/tmp/badges.json")
        mypokemon_path = Path("/tmp/mypokemon.json")
        mainpokemon_path = Path("/tmp/mainpokemon.json")
        pokedex_path = _src / "Ankimon" / "data_files" / "pokedex.json"
        def __getattr__(self, name): return Path("/tmp") / name

    sys.modules["Ankimon.resources"] = MockResources()
    sys.modules["Ankimon.singletons"] = MagicMock()

    # Pre-configure Ankimon.business Mock unconditionally
    business_mock = MagicMock()
    business_mock.pokemon_go_raw_stats.return_value = (100, 100, 100)
    business_mock.calculate_pokemon_go_cp.return_value = 500
    sys.modules["Ankimon.business"] = business_mock


# Dynamically load modules to bypass mock pollution from other test files
def force_load_module(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class MockLogger:
    def log(self, level, msg): pass
    def log_and_showinfo(self, level, msg): pass
    def _log(self, level, msg): pass


@pytest.fixture
def temp_env(tmp_path):
    """Temporary DB + service-seam wiring for held-item logic.

    On main's org, ``PokemonObject.give_held_item`` / ``remove_held_item`` and
    ``utils.give_item`` reach the database and the in-memory main-Pokemon through
    the service seam (``services.db`` / ``services.main_pokemon``), not through
    ``aqt.mw``. So this wires the temp DB onto ``services`` with ``patch.object``
    (auto-reverting, so the temp DB never leaks into the rest of the Tier-1 suite)
    rather than monkeypatching ``mw`` (pokemon_obj no longer imports ``mw`` at all).
    """
    snap = _snapshot_modules()
    setup_mocks()
    try:
        csv_file_path = tmp_path / "items.csv"

        # Force reload the real modules fresh, isolated from other tests.
        db_mod_fresh = force_load_module("Ankimon.pyobj.database_manager", _src / "Ankimon" / "pyobj" / "database_manager.py")
        global AnkimonDB
        AnkimonDB = db_mod_fresh.AnkimonDB

        utils_mod_fresh = force_load_module("Ankimon.utils", _src / "Ankimon" / "utils.py")

        pokemon_obj_mod_fresh = force_load_module("Ankimon.pyobj.pokemon_obj", _src / "Ankimon" / "pyobj" / "pokemon_obj.py")
        global PokemonObject
        PokemonObject = pokemon_obj_mod_fresh.PokemonObject

        # The shared service registry that give_held_item / remove_held_item / give_item read.
        from Ankimon.services import services

        # Create mock items.csv
        headers = ["id", "identifier", "category_id", "cost", "fling_power", "fling_effect_id"]
        rows = [
            ["100", "lucky-egg", "1", "200", "", ""],
        ]
        with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        with patch.object(db_mod_fresh, "user_path", tmp_path), \
             patch.object(db_mod_fresh, "csv_file_items_cost", str(csv_file_path)), \
             patch.object(utils_mod_fresh, "csv_file_items_cost", str(csv_file_path)):

            db = AnkimonDB(MockLogger())
            # Keep the global aqt mock consistent for any incidental mw.ankimon_db reader.
            sys.modules["aqt"].mw.ankimon_db = db

            # Route the seam at the shared registry. patch.object reverts on exit so
            # the temp DB / main_pokemon never leak into the other Tier-1 tests. The
            # real give_item / give_held_item now operate against this temp DB.
            with patch.object(services, "db", db), \
                 patch.object(services, "main_pokemon", None):
                yield db
    finally:
        _restore_modules(snap)


def test_held_item_lifecycle(temp_env):
    db = temp_env

    # 1. Give the player a lucky-egg in their bag
    db.add_item("lucky-egg", 1)

    # Verify it exists and quantity is 1
    item = db.get_item("lucky-egg")
    assert item is not None
    assert item["quantity"] == 1

    # 2. Create a Pokémon
    pkm = PokemonObject(
        name="Pikachu",
        id=25,
        shiny=False,
        level=5,
        ability="Static",
        type=["Electric"],
        gender="M",
        growth_rate="medium",
        captured_date=None,
        tier="Normal",
        individual_id="test-uuid",
        held_item=None
    )

    # Save the Pokémon to database
    db.save_pokemon(pkm.to_dict())

    # Verify Pokémon in DB has no held item
    db_pkm = db.get_pokemon("test-uuid")
    assert db_pkm["held_item"] is None

    # 3. Give the held item to Pokémon
    pkm.give_held_item("lucky-egg")

    # Check that item quantity decremented to 0 and got deleted from inventory
    item_in_bag = db.get_item("lucky-egg")
    assert item_in_bag is None  # Quant = 0 deletes it

    # Check that Pokémon in DB holds the item
    db_pkm = db.get_pokemon("test-uuid")
    assert db_pkm["held_item"] == "lucky-egg"

    # 4. Remove held item from Pokémon
    pkm.remove_held_item()

    # Check that item is back in bag with quantity 1
    item_in_bag = db.get_item("lucky-egg")
    assert item_in_bag is not None
    assert item_in_bag["quantity"] == 1

    # Check that Pokémon in DB no longer holds it
    db_pkm = db.get_pokemon("test-uuid")
    assert db_pkm["held_item"] is None


def test_main_pokemon_singleton_sync(temp_env):
    db = temp_env
    from Ankimon.services import services

    # Create the main Pokémon in the database and as an in-memory singleton
    main_pkm = PokemonObject(
        name="Charizard",
        id=6,
        shiny=False,
        level=50,
        ability="Blaze",
        type=["Fire", "Flying"],
        gender="M",
        growth_rate="medium",
        captured_date=None,
        tier="Normal",
        individual_id="main-uuid",
        held_item=None
    )

    # Set as the global singleton on the service seam (reverted by the fixture's
    # patch.object(services, "main_pokemon", None) on teardown).
    services.main_pokemon = main_pkm

    db.save_pokemon(main_pkm.to_dict())
    db.add_item("lucky-egg", 1)

    # We instantiate a temporary PokemonObject representing the main Pokémon (simulating UI action)
    temp_pkm_obj = PokemonObject.from_dict(db.get_pokemon("main-uuid"))

    # Give the item using the temporary object
    temp_pkm_obj.give_held_item("lucky-egg")

    # Verify that the database was updated
    assert db.get_pokemon("main-uuid")["held_item"] == "lucky-egg"

    # CRITICAL: Verify that the in-memory main_pokemon singleton was also updated!
    assert services.main_pokemon.held_item == "lucky-egg"

    # Remove the item using another temporary object (simulating UI remove action)
    temp_pkm_obj2 = PokemonObject.from_dict(db.get_pokemon("main-uuid"))
    temp_pkm_obj2.remove_held_item()

    # Verify database was updated to None
    assert db.get_pokemon("main-uuid")["held_item"] is None

    # CRITICAL: Verify that the in-memory main_pokemon singleton was also updated to None!
    assert services.main_pokemon.held_item is None


def test_equipped_items_web_serialization_and_unequip(temp_env):
    # This portion exercises AnkimonItemsWeb from ankimon_items_web/shop_obj.py —
    # the web-shell HOST feature, which is NOT part of the F12 Items/Bag seam unit
    # and is absent on this branch (src/Ankimon/ankimon_items_web/ does not exist on
    # main yet). Skip just this portion so the rest of the file still validates the
    # held-item give/remove lifecycle and main_pokemon singleton sync.
    pytest.skip(
        "AnkimonItemsWeb host (ankimon_items_web/shop_obj.py) absent in F12 unit; "
        "web equipped-items serialize/unequip lands with the web-shell HOST leaf."
    )
