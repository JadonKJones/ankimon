import sys
import os
import csv
import pytest
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch
import types

_src = Path(__file__).parent.parent / "src"

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

setup_mocks()

# Dynamically load modules to bypass mock pollution from other test files
def force_load_module(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# Retrieve helper globals initially
db_mod = force_load_module("Ankimon.pyobj.database_manager", _src / "Ankimon" / "pyobj" / "database_manager.py")
AnkimonDB = db_mod.AnkimonDB
utils_mod = force_load_module("Ankimon.utils", _src / "Ankimon" / "utils.py")
pokemon_obj_mod = force_load_module("Ankimon.pyobj.pokemon_obj", _src / "Ankimon" / "pyobj" / "pokemon_obj.py")
PokemonObject = pokemon_obj_mod.PokemonObject

class MockLogger:
    def log(self, level, msg): pass
    def log_and_showinfo(self, level, msg): pass
    def _log(self, level, msg): pass

@pytest.fixture
def temp_env(tmp_path):
    """Setup a temporary environment for the DB and its CSV files."""
    setup_mocks()
    db_file_path = tmp_path / "ankimon.db"
    csv_file_path = tmp_path / "items.csv"
    
    # Force reload modules fresh inside the fixture to isolate from other tests
    db_mod_fresh = force_load_module("Ankimon.pyobj.database_manager", _src / "Ankimon" / "pyobj" / "database_manager.py")
    global AnkimonDB
    AnkimonDB = db_mod_fresh.AnkimonDB
    
    utils_mod_fresh = force_load_module("Ankimon.utils", _src / "Ankimon" / "utils.py")
    
    pokemon_obj_mod_fresh = force_load_module("Ankimon.pyobj.pokemon_obj", _src / "Ankimon" / "pyobj" / "pokemon_obj.py")
    global PokemonObject
    PokemonObject = pokemon_obj_mod_fresh.PokemonObject

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
         patch.object(utils_mod_fresh, "csv_file_items_cost", str(csv_file_path)), \
         patch.object(pokemon_obj_mod_fresh, "mw", MagicMock()) as mock_mw:
        
        db = AnkimonDB(MockLogger())
        mock_mw.ankimon_db = db
        sys.modules["aqt"].mw.ankimon_db = db
        
        # Mock give_item to use our temp db
        def mock_give_item(item_name, item_type=None):
            existing = db.get_item(item_name)
            if existing:
                db.update_item_quantity(item_name, 1)
                return
            db.add_item(item_name, 1, {"type": item_type} if item_type else None)
        
        # Inject the mock give_item into utils namespace
        with patch("Ankimon.utils.give_item", side_effect=mock_give_item):
            yield db, mock_mw, mock_give_item

def test_held_item_lifecycle(temp_env):
    db, mock_mw, mock_give_item = temp_env
    
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
    assert item_in_bag is None # Quant = 0 deletes it
    
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
    db, mock_mw, mock_give_item = temp_env
    
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
    
    # Set as the global singleton
    mock_mw.main_pokemon = main_pkm
    from Ankimon.services import services
    services.populate(main_pokemon=main_pkm)
    
    db.save_pokemon(main_pkm.to_dict())
    db.add_item("lucky-egg", 1)
    
    # We instantiate a temporary PokemonObject representing the main Pokémon (simulating UI action)
    temp_pkm_obj = PokemonObject.from_dict(db.get_pokemon("main-uuid"))
    
    # Give the item using the temporary object
    temp_pkm_obj.give_held_item("lucky-egg")
    
    # Verify that the database was updated
    assert db.get_pokemon("main-uuid")["held_item"] == "lucky-egg"
    
    # CRITICAL: Verify that the in-memory main_pokemon singleton was also updated!
    assert mock_mw.main_pokemon.held_item == "lucky-egg"
    
    # Remove the item using another temporary object (simulating UI remove action)
    temp_pkm_obj2 = PokemonObject.from_dict(db.get_pokemon("main-uuid"))
    temp_pkm_obj2.remove_held_item()
    
    # Verify database was updated to None
    assert db.get_pokemon("main-uuid")["held_item"] is None
    
    # CRITICAL: Verify that the in-memory main_pokemon singleton was also updated to None!
    assert mock_mw.main_pokemon.held_item is None

def test_equipped_items_web_serialization_and_unequip(temp_env):
    db, mock_mw, mock_give_item = temp_env
    
    # Mock PyQt6.QtWebChannel to prevent real C++ QWebChannel instantiation with MagicMocks
    sys.modules["PyQt6.QtWebChannel"] = MagicMock()
    # Mock PyQt6.QtWidgets to prevent real QStackedWidget instantiation crashing without QApplication
    sys.modules["PyQt6.QtWidgets"] = MagicMock()
    # Mock Ankimon.singletons locally to override any pollution from other tests
    sys.modules["Ankimon.singletons"] = MagicMock()
    
    # Define a concrete QDialog stub class so AnkimonItemsWeb inherits from a real Python class
    class QDialogStub:
        def __init__(self, *args, **kwargs):
            pass
        def __getattr__(self, name):
            if name.startswith("_"):
                raise AttributeError(name)
            def dummy(*args, **kwargs):
                if name == "windowFlags":
                    return 0
                return None
            return dummy
    sys.modules["aqt"].QDialog = QDialogStub
    
    # 1. Force load shop_obj
    import aqt
    print("AQT QWebEngineView:", getattr(aqt, "QWebEngineView", None), flush=True)
    print("AQT QDialog:", getattr(aqt, "QDialog", None), flush=True)
    print("AQT QVBoxLayout:", getattr(aqt, "QVBoxLayout", None), flush=True)
    
    import traceback
    try:
        shop_obj_mod = force_load_module("Ankimon.ankimon_items_web.shop_obj", _src / "Ankimon" / "ankimon_items_web" / "shop_obj.py")
    except Exception as e:
        print("IMPORT FAILED DURING FORCE LOAD MODULE:", flush=True)
        traceback.print_exc()
        raise e
        
    AnkimonItemsWeb = shop_obj_mod.AnkimonItemsWeb
    
    # Create Pikachu with a held item
    pkm = PokemonObject(
        name="Pikachu",
        id=25,
        shiny=False,
        level=10,
        ability="Static",
        type=["Electric"],
        gender="M",
        growth_rate="medium",
        captured_date=None,
        tier="Normal",
        individual_id="pika-uuid",
        held_item="lucky-egg"
    )
    db.save_pokemon(pkm.to_dict())
    
    # Assert item bag is empty
    assert db.get_item("lucky-egg") is None
    
    # Create the web window instance
    mock_shop_manager = MagicMock()
    mock_shop_manager.todays_daily_items = []
    mock_shop_manager.todays_daily_tms = []
    mock_shop_manager.get_callback.return_value = 0
    mock_shop_manager.tm_price = 0
    mock_shop_manager.daily_items_reroll_cost = 0
    
    print("GLOBAL AQT MW DB:", sys.modules["aqt"].mw.ankimon_db)
    print("SHOP OBJ MOD MW DB:", shop_obj_mod.mw.ankimon_db)
    print("ALL PKMS FROM DB DIRECT:", db.get_all_pokemon())
    print("ALL PKMS FROM SHOP OBJ MW DB:", shop_obj_mod.mw.ankimon_db.get_all_pokemon())
    
    import traceback
    try:
        web_win = AnkimonItemsWeb(
            addon_dir=Path("/tmp"),
            shop_manager=mock_shop_manager,
            item_window=MagicMock(),
            ankimon_tracker=MagicMock(),
            trainer_card=MagicMock(),
            settings_obj=MagicMock(),
            logger=MockLogger()
        )
    except Exception as e:
        traceback.print_exc()
        raise e
    
    # 2. Verify Serialization
    data = web_win.get_inventory_data()
    items = data["items"]
    print("ALL SERIALIZED ITEMS:", items)
    print("ALL SERIALIZED NAMES:", [i["name"] for i in items])
    
    # Find lucky-egg in serialized items
    lucky_egg_entry = next((i for i in items if i["name"] == "lucky-egg"), None)
    assert lucky_egg_entry is not None
    assert lucky_egg_entry["owned_quantity"] == 0
    assert len(lucky_egg_entry["equipped_instances"]) == 1
    assert lucky_egg_entry["equipped_instances"][0]["name"] == "Pikachu"
    assert lucky_egg_entry["equipped_instances"][0]["individual_id"] == "pika-uuid"
    
    # 3. Test handle_unequip_item
    result = web_win.handle_unequip_item("pika-uuid", "lucky-egg")
    assert result["ok"] is True, f"handle_unequip_item failed with: {result}"
    
    # Verify DB was updated
    db_pika = db.get_pokemon("pika-uuid")
    assert db_pika["held_item"] is None
    
    # Verify lucky-egg is back in the bag
    item_in_bag = db.get_item("lucky-egg")
    assert item_in_bag is not None
    assert item_in_bag["quantity"] == 1

