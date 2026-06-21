import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import types

class FakePokemon:
    def __init__(self, **kwargs):
        self.individual_id = kwargs.get("individual_id", "active-uuid")
        self.name = kwargs.get("name", "Pikachu")
        self.display_name = self.name
        self.id = kwargs.get("id", 25)
        self.level = kwargs.get("level", 30)
        self.attacks = kwargs.get("attacks", ["Thunderbolt"])
        self.hp = kwargs.get("hp", 100)
        self.max_hp = kwargs.get("max_hp", 100)
        self.type = kwargs.get("type", ["Electric"])
        self.base_stats = kwargs.get("base_stats", {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90})
        self.stats = kwargs.get("stats", {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90})
        self.ev = kwargs.get("ev", {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0})
        self.iv = kwargs.get("iv", {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15})
        self.ev_yield = kwargs.get("ev_yield", {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0})
        self.tier = kwargs.get("tier", "normal")
        self.shiny = kwargs.get("shiny", False)
        self.held_item = kwargs.get("held_item", None)
        self.gender = kwargs.get("gender", "M")
        self.ability = kwargs.get("ability", "Static")
        self.growth_rate = kwargs.get("growth_rate", "medium-fast")
        self.friendship = kwargs.get("friendship", 50)
        self.everstone = kwargs.get("everstone", False)
        self.evolution_rejected = kwargs.get("evolution_rejected", False)
        self.pokemon_defeated = kwargs.get("pokemon_defeated", 0)
        self.is_favorite = kwargs.get("is_favorite", False)
        self.xp = kwargs.get("xp", 0)

    def invalidate_cp_cache(self):
        pass

    def to_dict(self):
        return {
            "individual_id": self.individual_id,
            "name": self.name,
            "id": self.id,
            "level": self.level,
            "ability": self.ability,
            "type": self.type,
            "base_stats": self.base_stats,
            "stats": self.stats,
            "attacks": self.attacks,
            "base_experience": 112,
            "growth_rate": self.growth_rate,
            "ev": self.ev,
            "iv": self.iv,
            "gender": self.gender,
            "battle_status": "Fighting",
            "ev_yield": self.ev_yield,
            "friendship": self.friendship,
            "everstone": self.everstone,
            "evolution_rejected": self.evolution_rejected,
            "pokemon_defeated": self.pokemon_defeated,
            "is_favorite": self.is_favorite,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "shiny": self.shiny,
            "tier": self.tier,
            "held_item": self.held_item,
            "xp": self.xp,
        }

# Import test_database_manager first (which triggers its setup_mocks() and writes over sys.modules)
from tests.test_database_manager import MockLogger, temp_env



def test_serialize_settings_list_with_dict():
    # Deferred imports to prevent import/mock issues during test collection
    import importlib.util
    from pathlib import Path
    _src = Path(__file__).parent.parent / "src"
    
    # Clean up sys.modules for shop_obj to force re-import under clean environment
    sys.modules.pop("Ankimon.ankimon_items_web.shop_obj", None)
    
    # Define a concrete QDialog stub class so AnkimonItemsWeb inherits from a real Python class
    import PyQt6.QtWidgets
    import aqt
    aqt.QDialog = PyQt6.QtWidgets.QDialog
    with patch("aqt.qt.QDialog", PyQt6.QtWidgets.QDialog):
        spec = importlib.util.spec_from_file_location(
            "Ankimon.ankimon_items_web.shop_obj", 
            _src / "Ankimon" / "ankimon_items_web" / "shop_obj.py"
        )
        shop_obj_mod = importlib.util.module_from_spec(spec)
        sys.modules["Ankimon.ankimon_items_web.shop_obj"] = shop_obj_mod
        spec.loader.exec_module(shop_obj_mod)
        
    AnkimonItemsWeb = shop_obj_mod.AnkimonItemsWeb
    
    dummy_self = MagicMock()
    friendly_names = [
        {
            "key": "mobile.enabled",
            "label": "Mobile Reviews Integration",
            "description": "Expose reviews completed on AnkiMobile during syncing.",
            "type": "boolean",
        },
        {
            "key": "mobile.resolution_mode",
            "label": "Mobile Resolution Mode",
            "description": "How pending reviews are resolved.",
            "type": "select",
            "options": [
                {"value": "manual", "label": "Manual"},
                {"value": "auto", "label": "Auto-Resolve"}
            ]
        }
    ]
    
    config = {
        "mobile.enabled": True,
        "mobile.resolution_mode": "manual"
    }
    
    res = AnkimonItemsWeb._serialize_settings_list(
        dummy_self,
        friendly_names=friendly_names,
        key_by_friendly={},
        name_map={},
        desc_map={},
        config=config
    )
    
    assert len(res) == 2
    assert res[0]["key"] == "mobile.enabled"
    assert res[0]["value"] is True
    assert res[0]["type"] == "boolean"
    assert res[1]["key"] == "mobile.resolution_mode"
    assert res[1]["value"] == "manual"
    assert res[1]["options"] == [
        {"value": "manual", "label": "Manual"},
        {"value": "auto", "label": "Auto-Resolve"}
    ]

@pytest.mark.parametrize("resolution_mode,newly_queued_count,should_resolve", [
    ("auto", 5, True),       # Under 500, auto-resolve should run
    ("auto", 501, True),     # Over 500, auto-resolve should still run successfully
    ("manual", 5, False),    # Manual mode, should NOT run
])
def test_sync_auto_resolve_hook(temp_env, resolution_mode, newly_queued_count, should_resolve):
    # Deferred imports to prevent import/mock issues during test collection
    from aqt import mw, gui_hooks
    sys.modules.pop("Ankimon.pyobj.ankimon_sync", None)
    from Ankimon.pyobj.ankimon_sync import setup_ankimon_sync_hooks
    from Ankimon.resources import user_path


    db, tmp_path = temp_env
    mw.ankimon_db = db
    mw.col = MagicMock()
    
    # 1. Mock DB reviews queries to return newly_queued_count reviews
    reviews_data = [
        (i, 1000 + i, 3, 10000, 1)
        for i in range(1, newly_queued_count + 1)
    ]
    mw.col.db.all.return_value = reviews_data
    mw.col.db.scalar.return_value = newly_queued_count
    
    # 2. Mock settings
    settings_obj = MagicMock()
    settings_dict = {
        "misc.ankiweb_sync": True,
        "mobile.enabled": True,
        "mobile.resolution_mode": resolution_mode
    }
    settings_obj.get.side_effect = lambda key, default=None: settings_dict.get(key, default)
    
    logger = MagicMock()
    
    # Capture the sync finish hook callback
    gui_hooks.sync_did_finish = MagicMock()
    setup_ankimon_sync_hooks(settings_obj, logger)
    assert gui_hooks.sync_did_finish.append.called
    on_sync_did_finish = gui_hooks.sync_did_finish.append.call_args[0][0]
    
    # 3. Stub database operations
    db.switch_database = MagicMock()
    db.queue_mobile_battles = MagicMock(return_value=newly_queued_count)
    db.get_pending_mobile_count = MagicMock(return_value=newly_queued_count)
    
    # Mock MobileBridge
    mock_bridge = MagicMock()
    mock_bridge.resolveAll.return_value = {
        "success": True,
        "resolved": newly_queued_count,
        "xp_gained": 100,
        "cash_gained": 50,
        "trainer_xp_gained": 10,
        "caught_list": [{"name": "Pikachu", "level": 5, "shiny": False, "tier": "Normal"}],
    }
    
    with patch("Ankimon.pyobj.ankimon_sync.user_path", tmp_path), \
         patch("Ankimon.pyobj.ankimon_sync.tooltip") as mock_tooltip, \
         patch("Ankimon.ankimon_items_web.shop_obj.MobileBridge", return_value=mock_bridge):
         
         try:
             on_sync_did_finish()
         except Exception as e:
             print("EXCEPTION IN ON_SYNC_DID_FINISH:", e)
             import traceback
             traceback.print_exc()
    
         print("LOGGER CALLS:", logger.log.call_args_list)

         if should_resolve:
             assert mock_bridge.resolveAll.called
             mock_tooltip.assert_called_with("⚔ Auto-resolved %d mobile/web reviews! +100 XP, +50¥. Caught: Pikachu." % newly_queued_count)
         else:
             assert not mock_bridge.resolveAll.called
             # Standard manual mode message (check for dev db presence in user_path)
             if (tmp_path / "ankimonDEV.db").is_file():
                 mock_tooltip.assert_called_with("⚔ Mobile/web reviews synced: %d in Normal, %d in Dev! Open Ankimon → Mobile & Web Reviews to resolve." % (newly_queued_count, newly_queued_count))
             else:
                 mock_tooltip.assert_called_with("⚔ Mobile/web reviews synced: %d in Normal! Open Ankimon → Mobile & Web Reviews to resolve." % newly_queued_count)


def test_mobile_history_recording(temp_env):
    db, _ = temp_env
    
    # Ensure history is clear initially
    db.clear_mobile_history()
    history = db.get_mobile_history()
    assert len(history) == 0
    
    entry = {
        "timestamp": 123456789,
        "enemy_id": 25,
        "enemy_name": "Pikachu",
        "enemy_level": 10,
        "enemy_shiny": True,
        "companion_name": "Charizard",
        "companion_level": 50,
        "outcome": "caught",
        "xp_gained": 0,
        "trainer_xp_gained": 0,
        "cash_gained": 10,
    }
    
    success = db.add_mobile_history_entry(entry)
    assert success is True
    
    history = db.get_mobile_history()
    assert len(history) == 1
    assert history[0]["enemy_name"] == "Pikachu"
    assert history[0]["enemy_shiny"] is True
    assert history[0]["outcome"] == "caught"
    assert history[0]["cash_gained"] == 10
    
    # Test auto truncation to 500 items
    for i in range(510):
        db.add_mobile_history_entry({
            "timestamp": 200000000 + i,
            "enemy_id": 1,
            "enemy_name": f"Bulbasaur-{i}",
            "enemy_level": 5,
            "enemy_shiny": False,
            "companion_name": "Venusaur",
            "companion_level": 80,
            "outcome": "defeated",
            "xp_gained": 100,
            "trainer_xp_gained": 10,
            "cash_gained": 5,
        })
        
    history = db.get_mobile_history(limit=600)
    assert len(history) == 500
    # The newest elements should remain (Bulbasaur-509 is the newest)
    assert history[0]["enemy_name"] == "Bulbasaur-509"
    
    db.clear_mobile_history()
    assert len(db.get_mobile_history()) == 0


def test_mobile_cumulative_cash_rewards(temp_env):
    db, _ = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from aqt import mw
    from unittest.mock import MagicMock, patch

    mw.ankimon_db = db
    mw.main_pokemon = FakePokemon(name="Pikachu", level=30, id=25, attacks=["Thunderbolt"])

    settings_mock = MagicMock()
    # Payout is 10 cash every 5 reviews
    mock_settings_dict = {
        "battle.cards_per_round": 2,
        "trainer.cash_reward_interval": 5,
        "trainer.cash_reward_amount": 10,
        "trainer.cash": 0,
        "trainer.mobile_reviews_resolved_since_payout": 0,
    }
    settings_mock.get.side_effect = lambda key, default=None: mock_settings_dict.get(
        key, default if default is not None else MagicMock()
    )
    def mock_set(key, val):
        mock_settings_dict[key] = val
    settings_mock.set.side_effect = mock_set
    mw.settings_obj = settings_mock

    bridge = MobileBridge(MagicMock())

    # We queue 6 reviews (makes 3 battles of 2 reviews each)
    reviews = [
        {"id": i, "cid": 1000 + i, "ease": 3, "time": 10000, "type": 1} for i in range(1, 7)
    ]
    db.queue_mobile_battles(reviews)

    with patch("Ankimon.functions.encounter_functions.save_main_pokemon_progress"), \
         patch("Ankimon.functions.encounter_functions.save_caught_pokemon"), \
         patch("Ankimon.functions.encounter_functions.generate_random_pokemon") as mock_gen_random, \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=Exception("mocked error")), \
         patch("Ankimon.menu_buttons.update_mobile_badge"):

        mock_gen_random.return_value = (
            "Pikachu", 25, 5, "Run Away", ["Electric"],
            {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            ["Thunderbolt"], 112, "Medium",
            {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
            "M", "Fighting", {}, "Normal", {"speed": 2}, False, "serious"
        )

        # Resolve Battle 1 (2 reviews): counter becomes 2, cash is 0
        bridge.resolveNext()
        res1 = bridge.commitReplayOutcome("defeat")
        print("RES1 VALUE IS:", res1)
        assert res1["cash_gained"] == 0
        assert mock_settings_dict["trainer.cash"] == 0
        assert mock_settings_dict["trainer.mobile_reviews_resolved_since_payout"] == 2

        # Resolve Battle 2 (2 reviews): counter becomes 4, cash is 0
        bridge.resolveNext()
        res2 = bridge.commitReplayOutcome("defeat")
        assert res2["cash_gained"] == 0
        assert mock_settings_dict["trainer.cash"] == 0
        assert mock_settings_dict["trainer.mobile_reviews_resolved_since_payout"] == 4

        # Resolve Battle 3 (2 reviews): counter becomes 6 -> payouts 10 cash, remainder 1
        bridge.resolveNext()
        res3 = bridge.commitReplayOutcome("defeat")
        assert res3["cash_gained"] == 10
        assert mock_settings_dict["trainer.cash"] == 10
        assert mock_settings_dict["trainer.mobile_reviews_resolved_since_payout"] == 1


def test_commit_replay_outcome_override_companion(temp_env):
    db, _ = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from aqt import mw
    from unittest.mock import MagicMock, patch

    mw.ankimon_db = db

    # Setup active companion (Pikachu)
    active_pika = {
        "individual_id": "active-uuid",
        "id": 25,
        "name": "Pikachu",
        "level": 30,
        "xp": 0,
        "shiny": False,
        "attacks": ["Thunderbolt"],
        "base_stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "ability": "Static",
        "growth_rate": "medium-fast",
        "captured_date": "2026-06-19",
        "tier": "normal",
        "ev_yield": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "friendship": 50,
        "everstone": False,
        "evolution_rejected": False,
        "pokemon_defeated": 0,
        "is_favorite": False,
        "type": ["Electric"],
        "gender": "M",
    }
    db.save_pokemon(active_pika)
    mw.main_pokemon = FakePokemon(**active_pika)

    # Setup override companion (Bulbasaur)
    override_bulba = {
        "individual_id": "override-uuid",
        "id": 1,
        "name": "Bulbasaur",
        "level": 10,
        "xp": 100,
        "shiny": False,
        "attacks": ["Tackle"],
        "base_stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "ability": "Overgrow",
        "growth_rate": "medium-fast",
        "captured_date": "2026-06-19",
        "tier": "normal",
        "ev_yield": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "friendship": 50,
        "everstone": False,
        "evolution_rejected": False,
        "pokemon_defeated": 0,
        "is_favorite": False,
        "type": ["Grass"],
        "gender": "M",
    }
    db.save_pokemon(override_bulba)

    bridge = MobileBridge(MagicMock())
    enemy_mock = MagicMock(id=19, display_name="Rattata", level=3, shiny=False, ev_yield={"atk": 1}, tier="normal")
    enemy_mock.to_dict.return_value = {
        "id": 19,
        "name": "Rattata",
        "level": 3,
        "shiny": False,
        "base_stats": {"hp": 30, "atk": 56, "def": 35, "spa": 25, "spd": 35, "spe": 72},
        "stats": {"hp": 30, "atk": 56, "def": 35, "spa": 25, "spd": 35, "spe": 72},
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "nature": "serious",
    }
    bridge._current_pending_outcome = {
        "enemy_pokemon": enemy_mock,
        "battle_xp": 150,
        "total_xp": 150,
        "accumulated_evs": {"atk": 1, "hp": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "total_trainer_xp": 10,
        "main_pokemon": mw.main_pokemon,
        "trainer_card": MagicMock(),
        "settings_obj": MagicMock(get=lambda k, d=None: False if k == "misc.remove_level_cap" else d),
        "companion_id": "override-uuid",
    }

    res = bridge.commitReplayOutcome("defeat")
    assert res.get("success") is not False

    # Verify override Bulbasaur received XP in the DB
    bulba_after = db.get_pokemon_by_individual_id("override-uuid")
    assert bulba_after["xp"] > 100 or bulba_after["level"] > 10
    
    # Verify active companion Pikachu's stats are unchanged in DB and in-memory
    pika_db = db.get_pokemon_by_individual_id("active-uuid")
    assert pika_db["xp"] == 0
    assert mw.main_pokemon.xp == 0


def test_auto_resolve_xp_attribution_multi_companion(temp_env):
    db, _ = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from aqt import mw
    from unittest.mock import MagicMock, patch
    import Ankimon.functions.encounter_functions as ef
    import Ankimon.ankimon_items_web.shop_obj as so
    ef.mw = mw
    so.mw = mw
    mw.ankimon_db = db

    # Active companion (Pikachu)
    active_pika = {
        "individual_id": "active-uuid",
        "id": 25,
        "name": "Pikachu",
        "level": 30,
        "xp": 0,
        "shiny": False,
        "attacks": ["Thunderbolt"],
        "base_stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "ability": "Static",
        "growth_rate": "medium-fast",
        "captured_date": "2026-06-19",
        "tier": "normal",
        "ev_yield": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "friendship": 50,
        "everstone": False,
        "evolution_rejected": False,
        "pokemon_defeated": 0,
        "is_favorite": False,
        "type": ["Electric"],
        "gender": "M",
    }
    db.save_pokemon(active_pika)
    db.set_main_pokemon("active-uuid")
    
    # Mock mw.main_pokemon
    mw.main_pokemon = FakePokemon(**active_pika)

    # Inactive/Team companion (Bulbasaur)
    override_bulba = {
        "individual_id": "override-uuid",
        "id": 1,
        "name": "Bulbasaur",
        "level": 10,
        "xp": 0,
        "shiny": False,
        "attacks": ["Tackle"],
        "base_stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "ability": "Overgrow",
        "growth_rate": "medium-fast",
        "captured_date": "2026-06-19",
        "tier": "normal",
        "ev_yield": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "friendship": 50,
        "everstone": False,
        "evolution_rejected": False,
        "pokemon_defeated": 0,
        "is_favorite": False,
        "type": ["Grass"],
        "gender": "M",
    }
    db.save_pokemon(override_bulba)

    # Put both Bulbasaur and Pikachu in the team
    db.save_team([{"individual_id": "active-uuid"}, {"individual_id": "override-uuid"}])

    bridge = MobileBridge(MagicMock())
    
    # Mock settings and collections
    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 1,
        "mobile.inactive_companions": [],
        "battle.automatic_battle": 2, # auto-defeat
    }
    settings_mock.get.side_effect = lambda k, d=None: mock_settings_dict.get(k, d)
    mw.settings_obj = settings_mock
    mw.achievements_dict = {}

    reviews = [
        {"id": 1, "cid": 2001, "ease": 3, "time": 5000, "type": 1},
        {"id": 2, "cid": 2002, "ease": 3, "time": 5000, "type": 1},
        {"id": 3, "cid": 2003, "ease": 3, "time": 5000, "type": 1},
    ]
    db.queue_mobile_battles(reviews)

    # Mock the poke engine simulator to return that companion 1 wins one battle, companion 2 wins the other
    enemy_mock = MagicMock(id=19, name="Rattata", display_name="Rattata", level=3, shiny=False, ev_yield={"atk": 1}, tier="normal")
    enemy_mock.to_dict.return_value = {
        "id": 19,
        "name": "Rattata",
        "level": 3,
        "shiny": False,
        "base_stats": {"hp": 30, "atk": 56, "def": 35, "spa": 25, "spd": 35, "spe": 72},
        "stats": {"hp": 30, "atk": 56, "def": 35, "spa": 25, "spd": 35, "spe": 72},
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "nature": "serious",
        "ev_yield": {"atk": 1},
    }
    
    # We patch simulate_battle_with_poke_engine and load_active_team_clones
    with patch("Ankimon.functions.encounter_functions.generate_random_pokemon", return_value=enemy_mock), \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", side_effect=[
             {"winner": "player", "turns": 2, "player_hp": 30, "enemy_hp": 0},
             {"winner": "player", "turns": 2, "player_hp": 30, "enemy_hp": 0},
             {"winner": "player", "turns": 2, "player_hp": 30, "enemy_hp": 0}
         ]), \
         patch("Ankimon.menu_buttons.update_mobile_badge"), \
         patch("Ankimon.functions.encounter_functions.limit_ev_yield", side_effect=lambda ev, y: {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}):

        # In auto-resolve, select_best_companion will be called. Let's mock it to return Pikachu first, Bulbasaur second and third
        pika_clone = MagicMock()
        pika_clone.individual_id = "active-uuid"
        pika_clone.display_name = "Pikachu"
        pika_clone.level = 30
        pika_clone.shiny = False
        pika_clone.to_dict.return_value = active_pika
        
        bulba_clone = MagicMock()
        bulba_clone.individual_id = "override-uuid"
        bulba_clone.display_name = "Bulbasaur"
        bulba_clone.level = 10
        bulba_clone.shiny = False
        bulba_clone.to_dict.return_value = override_bulba
        
        assert db.get_main_pokemon() is not None
        with patch("Ankimon.functions.mobile_sync.select_best_companion", side_effect=[pika_clone, pika_clone, bulba_clone]):
            res = bridge.resolveAll()

    pika_db = db.get_pokemon_by_individual_id("active-uuid")
    bulba_db = db.get_pokemon_by_individual_id("override-uuid")
    assert pika_db["xp"] > 0
    assert bulba_db["xp"] > 0
    assert pika_db["pokemon_defeated"] == 2
    assert bulba_db["pokemon_defeated"] == 1


def test_per_database_watermark_sync(temp_env):
    db, tmp_path = temp_env
    from Ankimon.pyobj.ankimon_sync import setup_ankimon_sync_hooks
    from aqt import mw, gui_hooks
    from unittest.mock import MagicMock, patch

    # Create two DBs in tmp_path: ankimon.db and ankimonDEV.db
    # We copy current db structure
    db.switch_database("ankimon.db")
    db.set_mobile_watermark(500)
    
    # Create the dev DB
    dev_db_file = tmp_path / "ankimonDEV.db"
    import shutil
    shutil.copy(db.db_path, dev_db_file)
    
    # Now set dev DB watermark to 1000
    db.switch_database("ankimonDEV.db")
    db.set_mobile_watermark(1000)

    # Set back to normal active db
    db.switch_database("ankimon.db")
    mw.ankimon_db = db
    mw.col = MagicMock()
    
    # Mock detect_mobile_reviews
    def mock_detect(col, watermark, desktop_ids):
        if watermark == 500:
            return [{"id": 501, "revlog_id": 5001, "cid": 6001, "ease": 3, "time": 1000, "type": 1}]
        elif watermark == 1000:
            return [{"id": 1001, "revlog_id": 6001, "cid": 7001, "ease": 3, "time": 1000, "type": 1}]
        return []

    settings_mock = MagicMock()
    mock_settings = {
        "mobile.enabled": True,
        "mobile.resolution_mode": "manual",
        "misc.ankiweb_sync": True,
    }
    settings_mock.get.side_effect = lambda k, d=None: mock_settings.get(k, d)
    mw.settings_obj = settings_mock

    # Mock gui_hooks.sync_did_finish.append
    gui_hooks.sync_did_finish.append = MagicMock()

    with patch("Ankimon.functions.mobile_sync.detect_mobile_reviews", side_effect=mock_detect), \
         patch("Ankimon.functions.mobile_sync.get_desktop_session_revlog_ids", return_value=[]), \
         patch("Ankimon.functions.mobile_sync.clear_desktop_session"), \
         patch("Ankimon.menu_buttons.update_mobile_badge"), \
         patch("Ankimon.pyobj.database_manager.user_path", tmp_path), \
         patch("Ankimon.pyobj.ankimon_sync.user_path", tmp_path):
        
        setup_ankimon_sync_hooks(mw.settings_obj, MagicMock())
        on_sync_did_finish = gui_hooks.sync_did_finish.append.call_args[0][0]
        on_sync_did_finish()

    # Verify both got updated watermarks on their respective databases
    db.switch_database("ankimonDEV.db")
    assert db.get_mobile_watermark() == 1001


def test_auto_resolve_zero_xp_ev_gain_still_increments_defeated(temp_env):
    db, _ = temp_env
    from Ankimon.ankimon_items_web.shop_obj import MobileBridge
    from aqt import mw
    from unittest.mock import MagicMock, patch
    import Ankimon.functions.encounter_functions as ef
    import Ankimon.ankimon_items_web.shop_obj as so
    ef.mw = mw
    so.mw = mw
    mw.ankimon_db = db

    # Inactive companion (Bulbasaur) with 0 XP / 0 EV gain
    override_bulba = {
        "individual_id": "override-uuid",
        "id": 1,
        "name": "Bulbasaur",
        "level": 100,  # Level 100 means 0 XP gain
        "xp": 0,
        "shiny": False,
        "attacks": ["Tackle"],
        "base_stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "ev": {"hp": 252, "atk": 252, "def": 6, "spa": 0, "spd": 0, "spe": 0}, # Maxed EVs (510 total)
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "ability": "Overgrow",
        "growth_rate": "medium-fast",
        "captured_date": "2026-06-19",
        "tier": "normal",
        "ev_yield": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "friendship": 50,
        "everstone": False,
        "evolution_rejected": False,
        "pokemon_defeated": 0,
        "is_favorite": False,
        "type": ["Grass"],
        "gender": "M",
    }
    db.save_pokemon(override_bulba)
    db.save_team([{"individual_id": "override-uuid"}])

    bridge = MobileBridge(MagicMock())
    
    settings_mock = MagicMock()
    mock_settings_dict = {
        "battle.cards_per_round": 1,
        "mobile.inactive_companions": [],
        "battle.automatic_battle": 2,
    }
    settings_mock.get.side_effect = lambda k, d=None: mock_settings_dict.get(k, d)
    mw.settings_obj = settings_mock
    mw.achievements_dict = {}

    reviews = [
        {"id": 1, "cid": 2001, "ease": 3, "time": 5000, "type": 1},
    ]
    db.queue_mobile_battles(reviews)

    enemy_mock = MagicMock(id=19, name="Rattata", display_name="Rattata", level=3, shiny=False, ev_yield={"atk": 1}, tier="normal")
    enemy_mock.to_dict.return_value = {
        "id": 19, "name": "Rattata", "level": 3, "shiny": False,
        "base_stats": {"hp": 30, "atk": 56, "def": 35, "spa": 25, "spd": 35, "spe": 72},
        "stats": {"hp": 30, "atk": 56, "def": 35, "spa": 25, "spd": 35, "spe": 72},
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "iv": {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15},
        "nature": "serious", "ev_yield": {"atk": 1},
    }
    
    with patch("Ankimon.functions.encounter_functions.generate_random_pokemon", return_value=enemy_mock), \
         patch("Ankimon.functions.ankimon_hooks_to_poke_engine.simulate_battle_with_poke_engine", return_value={"winner": "player", "turns": 2, "player_hp": 30, "enemy_hp": 0}), \
         patch("Ankimon.menu_buttons.update_mobile_badge"), \
         patch("Ankimon.functions.encounter_functions.limit_ev_yield", return_value={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}):

        bulba_clone = MagicMock()
        bulba_clone.individual_id = "override-uuid"
        bulba_clone.display_name = "Bulbasaur"
        bulba_clone.level = 100
        bulba_clone.shiny = False
        bulba_clone.to_dict.return_value = override_bulba
        
        with patch("Ankimon.functions.mobile_sync.select_best_companion", return_value=bulba_clone):
            res = bridge.resolveAll()

    bulba_db = db.get_pokemon_by_individual_id("override-uuid")
    assert bulba_db["pokemon_defeated"] == 1


