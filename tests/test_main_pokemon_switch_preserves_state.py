"""Regression tests for ``pyobj/collection_dialog.py::MainPokemon`` (switch state).

Switching the main Pokemon used to rebuild the incoming Pokemon with a freshly
computed *max* HP stat and to drop ``nature`` / ``evolution_rejected`` on the
floor.  Because the rebuilt object is then written straight back with
``db.save_main_pokemon(main_pokemon.to_dict())``, the silent full-heal and the
reset nature were *persisted* -- a free full restore on every PC-box swap.
These pin the persisted round-trip, not just the in-memory object.

``collection_dialog.py`` is loaded in isolation with its module-level Qt/aqt and
sibling-window dependencies stubbed (mirroring ``test_pc_box_cp_migration.py``),
except that the *real* ``pokemon_obj`` is installed because ``PokemonObject``'s
HP normalisation is exactly what is under test (mirroring that file's use of the
real ``business`` module).  Runs Qt-free in the Tier-1 env.
"""

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_SRC = Path(__file__).resolve().parent.parent / "src"
_MODULE_NAME = "Ankimon.pyobj.collection_dialog"

# A Pokemon whose max HP is comfortably above the fixtures' wounded HP, so a
# silent full-heal is unmistakable.
_BASE_STATS = {"hp": 106, "atk": 110, "def": 90, "spa": 154, "spd": 90, "spe": 130}


class _MockResources:
    """Path-returning stand-in for ``Ankimon.resources`` (any attr -> /tmp/<name>)."""

    pokedex_path = _SRC / "Ankimon" / "data_files" / "pokedex.json"

    def __getattr__(self, name):
        return Path("/tmp") / name


class _FakeDB:
    """The ``mw.ankimon_db`` seam, recording what MainPokemon persists."""

    def __init__(self, existing_main=None):
        self._main = existing_main
        self.saved_main = []
        self.saved_party = []

    def get_main_pokemon(self):
        return self._main

    def save_main_pokemon(self, data):
        self._main = data
        self.saved_main.append(data)

    def save_pokemon(self, data):
        self.saved_party.append(data)


def _make_module(name, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


def _force_load(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def collection_dialog():
    """Load ``collection_dialog.py`` with a stubbed runtime + the real PokemonObject."""
    parent_pkgs = ("Ankimon", "Ankimon.functions", "Ankimon.pyobj")

    class _Stub:
        def __init__(self, *a, **k):
            pass

    # to_dict() lazily computes CP via ``..business``; a functional stub keeps the
    # round-trip cheap and independent of the CP formula.
    business = MagicMock()
    business.pokemon_go_raw_stats.return_value = (100, 100, 100)
    business.calculate_pokemon_go_cp.return_value = 500

    singletons = _make_module(
        "Ankimon.singletons", pokemon_pc=MagicMock(name="pokemon_pc")
    )

    to_install = {
        # Qt/aqt runtime: MagicMock modules satisfy `from PyQt6.QtWidgets import *`
        # and `from aqt import mw` without a real Anki or a QApplication.
        "aqt": _make_module("aqt", mw=MagicMock(name="mw")),
        "aqt.utils": MagicMock(),
        "PyQt6": MagicMock(),
        "PyQt6.QtWidgets": MagicMock(),
        "PyQt6.QtGui": MagicMock(),
        "PyQt6.QtCore": MagicMock(),
        # Sibling windows/services touched only by the type hints.
        "Ankimon.pyobj.error_handler": _make_module(
            "Ankimon.pyobj.error_handler", show_warning_with_traceback=MagicMock()
        ),
        "Ankimon.pyobj.InfoLogger": _make_module(
            "Ankimon.pyobj.InfoLogger", ShowInfoLogger=_Stub
        ),
        "Ankimon.pyobj.translator": _make_module(
            "Ankimon.pyobj.translator", Translator=_Stub
        ),
        "Ankimon.pyobj.test_window": _make_module(
            "Ankimon.pyobj.test_window", TestWindow=_Stub
        ),
        "Ankimon.pyobj.reviewer_obj": _make_module(
            "Ankimon.pyobj.reviewer_obj", Reviewer_Manager=_Stub
        ),
        "Ankimon.functions.pokedex_functions": _make_module(
            "Ankimon.functions.pokedex_functions",
            search_pokedex_by_id=lambda pkmn_id: "mewtwo",
            search_pokedex=lambda name, key: dict(_BASE_STATS),
        ),
        # Imported (unused) at the top of MainPokemon's body.
        "Ankimon.functions.migration": _make_module(
            "Ankimon.functions.migration", migrate_starter_individual_id=MagicMock()
        ),
        # Imported at the very END of MainPokemon's body.
        "Ankimon.singletons": singletons,
        "Ankimon.business": business,
        "Ankimon.resources": _MockResources(),
        _MODULE_NAME: None,
        "Ankimon.pyobj.pokemon_obj": None,
    }
    saved = {name: sys.modules.get(name) for name in (*to_install, *parent_pkgs)}

    for pkg in parent_pkgs:
        mod = types.ModuleType(pkg)
        mod.__path__ = [str(_SRC / pkg.replace(".", "/"))]
        mod.__package__ = pkg
        sys.modules[pkg] = mod
    for name, mod in to_install.items():
        if mod is not None:
            sys.modules[name] = mod

    try:
        # The real PokemonObject -- its HP normalisation is the subject.
        pokemon_obj = _force_load(
            "Ankimon.pyobj.pokemon_obj", _SRC / "Ankimon" / "pyobj" / "pokemon_obj.py"
        )
        module = _force_load(
            _MODULE_NAME, _SRC / "Ankimon" / "pyobj" / "collection_dialog.py"
        )
        module._PokemonObject = pokemon_obj.PokemonObject
        module._singletons = singletons
        yield module
    finally:
        for name, val in saved.items():
            if val is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = val


def _stored_pokemon(**overrides):
    """A PC-box row for the *incoming* main, wounded and mid-evolution-refusal."""
    row = {
        "id": 150,
        "name": "mewtwo",
        "nickname": "",
        "level": 50,
        "ability": "Pressure",
        "type": ["Psychic"],
        "gender": "N",
        "growth_rate": "slow",
        "base_experience": 306,
        "attacks": ["psychic"],
        "ev": {k: 0 for k in _BASE_STATS},
        "iv": {k: 31 for k in _BASE_STATS},
        "nature": "adamant",
        "hp": 7,
        "current_hp": 7,
        "evolution_rejected": True,
        "everstone": False,
        "shiny": False,
        "individual_id": "incoming-uuid",
        "xp": 120,
        "friendship": 70,
        "pokemon_defeated": 3,
        "tier": "Legendary",
        "captured_date": None,
        "is_favorite": False,
        "held_item": None,
    }
    row.update(overrides)
    return row


def _call(module, stored, db=None):
    """Drive MainPokemon against stubbed collaborators; return (main, db)."""
    PokemonObject = module._PokemonObject
    outgoing = PokemonObject(
        name="pikachu", id=25, shiny=False, level=5, ability="Static",
        type=["Electric"], gender="M", growth_rate="medium", captured_date=None,
        tier="Normal", individual_id="outgoing-uuid", base_stats=dict(_BASE_STATS),
    )
    db = db or _FakeDB(existing_main=outgoing.to_dict())
    module.mw.ankimon_db = db

    logger = MagicMock()
    translator = MagicMock()
    translator.translate.return_value = "picked"
    reviewer_obj = MagicMock()
    test_window = MagicMock()
    test_window.isVisible.return_value = False

    module.MainPokemon(stored, outgoing, logger, translator, reviewer_obj, test_window)
    return outgoing, db


def test_switch_preserves_wounded_hp(collection_dialog):
    """A wounded Pokemon is not silently full-healed by being made main."""
    main, db = _call(collection_dialog, _stored_pokemon())

    assert main.hp == 7
    assert main.hp != main.max_hp, "the incoming main was full-healed"
    assert db.saved_main, "the new main must be persisted"
    assert db.saved_main[-1]["hp"] == 7
    assert db.saved_main[-1]["current_hp"] == 7


def test_switch_preserves_nature_and_evolution_rejected(collection_dialog):
    """``nature`` and ``evolution_rejected`` survive the rebuild."""
    main, db = _call(collection_dialog, _stored_pokemon())

    assert main.nature == "adamant"
    assert main.evolution_rejected is True
    assert db.saved_main[-1]["nature"] == "adamant"
    assert db.saved_main[-1]["evolution_rejected"] is True


def test_hp_and_current_hp_stay_consistent(collection_dialog):
    """Both HP fields agree and stay inside the valid range."""
    main, db = _call(collection_dialog, _stored_pokemon())

    assert main.hp == main.current_hp == 7
    assert 0 <= main.hp <= main.max_hp
    saved = db.saved_main[-1]
    assert saved["hp"] == saved["current_hp"]


def test_stale_hp_key_does_not_resurrect_a_full_heal(collection_dialog):
    """``current_hp`` wins over a stale ``hp``.

    ``encounter_functions.save_main_pokemon_progress`` refreshes only
    ``current_hp`` on the main's row after every enemy defeat, leaving ``hp`` at
    whatever it was when the row was last written whole.  Reading ``hp`` first
    would hand that stale full-HP value back, so re-picking the current main as
    main straight after a win would still be a free heal.
    """
    stored = _stored_pokemon(hp=181, current_hp=12)  # stale full HP / fresh live HP
    main, db = _call(collection_dialog, stored)

    assert main.hp == 12, "a stale ``hp`` key full-healed the incoming main"
    assert main.current_hp == 12
    assert db.saved_main[-1]["hp"] == 12
    assert db.saved_main[-1]["current_hp"] == 12


def test_stone_evolved_record_keeps_its_post_evolution_hp(collection_dialog):
    """``evolution_window`` writes only ``current_hp`` when a Pokemon evolves.

    Its row therefore carries the pre-evolution ``hp`` alongside the correct
    post-evolution ``current_hp``.  Preferring ``hp`` would pin the evolved
    Pokemon at its old, much smaller HP and then persist that.
    """
    stored = _stored_pokemon(hp=5, current_hp=160)
    main, db = _call(collection_dialog, stored)

    assert main.hp == 160
    assert db.saved_main[-1]["hp"] == 160


def test_persisted_hp_keys_never_disagree(collection_dialog):
    """Whatever the row shape, the round-trip must not write a split record.

    ``to_dict()`` persists ``hp`` and ``current_hp`` independently, so a
    disagreement here is silently resolved -- in the other direction -- by
    ``_normalize_loaded_hp`` at the next launch.
    """
    for row in (
        _stored_pokemon(hp=181, current_hp=12),
        _stored_pokemon(hp=5, current_hp=160),
        _stored_pokemon(hp=None, current_hp=9),
        _stored_pokemon(hp=9, current_hp=None),
        _stored_pokemon(hp=0, current_hp=0),
    ):
        main, db = _call(collection_dialog, row)
        saved = db.saved_main[-1]
        assert saved["hp"] == saved["current_hp"] == main.hp
        assert 0 <= main.hp <= main.max_hp


def test_fainted_pokemon_stays_fainted(collection_dialog):
    """0 HP must survive the switch rather than being read as a falsy miss."""
    main, db = _call(collection_dialog, _stored_pokemon(hp=0, current_hp=0))

    assert main.hp == 0
    assert db.saved_main[-1]["hp"] == 0


def test_special_form_does_not_leak_from_the_outgoing_main(collection_dialog):
    """``mega``/``special_form`` are the only fields __init__ drops.

    ``__dict__.update()`` cannot clear an attribute the new object never set, so
    assigning them only when the key is present let the outgoing Pokemon's value
    survive onto the incoming Pokemon -- and get persisted.
    """
    outgoing_kwargs = dict(
        name="pikachu", id=25, shiny=False, level=5, ability="Static",
        type=["Electric"], gender="M", growth_rate="medium", captured_date=None,
        tier="Normal", individual_id="outgoing-uuid", base_stats=dict(_BASE_STATS),
    )
    PokemonObject = collection_dialog._PokemonObject
    outgoing = PokemonObject(**outgoing_kwargs)
    outgoing.mega = True
    outgoing.special_form = "gmax"

    db = _FakeDB(existing_main=outgoing.to_dict())
    collection_dialog.mw.ankimon_db = db
    test_window = MagicMock()
    test_window.isVisible.return_value = False
    stored = _stored_pokemon()
    stored.pop("mega", None)
    stored.pop("special_form", None)

    collection_dialog.MainPokemon(
        stored, outgoing, MagicMock(), MagicMock(), MagicMock(), test_window
    )

    assert outgoing.mega is False, "mega leaked from the outgoing main"
    assert outgoing.special_form is None
    assert db.saved_main[-1]["mega"] is False
    assert db.saved_main[-1]["special_form"] is None


def test_outgoing_save_failure_is_logged_not_swallowed(collection_dialog):
    """This save is now the only thing preserving the outgoing Pokemon's HP."""
    class _BoomDB(_FakeDB):
        def save_pokemon(self, data):
            raise RuntimeError("disk on fire")

    PokemonObject = collection_dialog._PokemonObject
    outgoing = PokemonObject(
        name="pikachu", id=25, shiny=False, level=5, ability="Static",
        type=["Electric"], gender="M", growth_rate="medium", captured_date=None,
        tier="Normal", individual_id="outgoing-uuid", base_stats=dict(_BASE_STATS),
    )
    db = _BoomDB(existing_main=outgoing.to_dict())
    collection_dialog.mw.ankimon_db = db
    logger = MagicMock()
    test_window = MagicMock()
    test_window.isVisible.return_value = False

    collection_dialog.MainPokemon(
        _stored_pokemon(), outgoing, logger, MagicMock(), MagicMock(), test_window
    )

    assert logger.log.called, "the swallowed save failure was never reported"
    assert db.saved_main, "the switch itself must still complete"


def test_missing_hp_falls_back_to_current_hp(collection_dialog):
    """A partially migrated row carrying only ``current_hp`` is not healed."""
    row = _stored_pokemon()
    del row["hp"]
    row["current_hp"] = 9

    main, _db = _call(collection_dialog, row)

    assert main.hp == main.current_hp == 9


def test_null_nature_falls_back_to_serious(collection_dialog):
    """An explicit null nature must not reach ``get_nature_stat_mult``."""
    main, _db = _call(collection_dialog, _stored_pokemon(nature=None))

    assert main.nature == "serious"
    assert isinstance(main.stats, dict)  # nature maths did not blow up


def test_outgoing_main_is_saved_before_replacement(collection_dialog):
    """The previous main's in-memory state is written to the party first."""
    _main, db = _call(collection_dialog, _stored_pokemon())

    assert [row["individual_id"] for row in db.saved_party] == ["outgoing-uuid"]


def test_hud_refresh_and_grid_refresh_are_triggered(collection_dialog):
    """The HUD repaint goes through the guarded ``refresh_hud`` seam."""
    PokemonObject = collection_dialog._PokemonObject
    outgoing = PokemonObject(
        name="pikachu", id=25, shiny=False, level=5, ability="Static",
        type=["Electric"], gender="M", growth_rate="medium", captured_date=None,
        tier="Normal", individual_id="outgoing-uuid", base_stats=dict(_BASE_STATS),
    )
    db = _FakeDB(existing_main=outgoing.to_dict())
    collection_dialog.mw.ankimon_db = db
    reviewer_obj = MagicMock()
    test_window = MagicMock()
    test_window.isVisible.return_value = False

    collection_dialog.MainPokemon(
        _stored_pokemon(), outgoing, MagicMock(), MagicMock(), reviewer_obj, test_window
    )

    reviewer_obj.refresh_hud.assert_called_once_with()
    collection_dialog._singletons.pokemon_pc.refresh_pokemon_grid.assert_called_once_with()
