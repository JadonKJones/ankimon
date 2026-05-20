[1]. src/Ankimon/__init__.py
Why this file is critical: Primary entrypoint configuring Anki hooks and initializing the addon lifecycle.

# -*- coding: utf-8 -*-

# Ankimon
# Copyright (C) 2024 Unlucky-Life

# This program is free software: you can redistribute it and/or modify
# by the Free Software Foundation
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# Important - If you redistribute it and/or modify this addon - must give contribution in Title and Code
# aswell as ask for permission to modify / redistribute this addon or the code itself

try:
    from .debug_console import show_ankimon_dev_console
except ModuleNotFoundError:
    pass

import aqt
from aqt import gui_hooks, mw
from aqt.gui_hooks import webview_will_set_content
from aqt.webview import WebContent

from .resources import ensure_ankimon_infrastructure, user_path, addon_dir
ensure_ankimon_infrastructure(addon_dir, user_path)

from .singletons import (
    settings_obj,
    settings_window,
    logger,
    translator,
    reviewer_obj,
    ankimon_tracker_obj,
    test_window,
    achievement_bag,
    shop_manager,
    ankimon_tracker_window,
    pokedex_window,
    eff_chart,
    gen_id_chart,
    license,
    credits,
    evo_window,
    starter_window,
    item_window,
    version_dialog,
    pokemon_pc,
    trainer_card,
)
from .functions.url_functions import (
    open_team_builder,
    rate_addon_url,
    report_bug,
    join_discord_url,
    open_leaderboard_url,
)
from .functions.pokemon_showdown_functions import (
    export_to_pkmn_showdown,
    export_all_pkmn_showdown,
    flex_pokemon_collection,
)
from .utils import test_online_connectivity
from .menu_buttons import create_menu_actions
from .hooks import setupHooks
from .pyobj.error_handler import show_warning_with_traceback

# --- Register singletons on mw for global access ---
mw.settings_ankimon = settings_window
mw.logger = logger
mw.translator = translator
mw.settings_obj = settings_obj

from .gui_classes import overview_team

# --- Startup: backup, migration, assets, first enemy ---
from .startup import run_startup_sequence
database_complete, collected_pokemon_ids, backup_manager = run_startup_sequence()

# --- Web exports for reviewer UI ---
mw.addonManager.setWebExports(
    __name__, r"user_files/.*\.(css|js|jpg|gif|html|ttf|png|mp3)"
)

def on_webview_will_set_content(web_content: WebContent, context) -> None:
    if not isinstance(context, aqt.reviewer.Reviewer):
        return
    ankimon_package = mw.addonManager.addonFromModule(__name__)
    web_content.js.append(
        f"/_addons/{ankimon_package}/user_files/web/ankimon_hud_portal.js"
    )

webview_will_set_content.append(on_webview_will_set_content)

# --- Card timer and answer hooks ---
from .card_hooks import register_card_hooks
register_card_hooks()

setupHooks(None, ankimon_tracker_obj)

# --- Changelog check ---
online_connectivity = test_online_connectivity()
no_more_news = settings_obj.get("misc.YouShallNotPass_Ankimon_News")
ssh = settings_obj.get("misc.ssh")

from .changelog import check_and_show_changelog, open_help_window
check_and_show_changelog(online_connectivity, ssh, no_more_news)

# --- Battle loop ---
from .battle_loop import on_review_card, init_battle_state
init_battle_state(collected_pokemon_ids)
gui_hooks.reviewer_did_answer_card.append(on_review_card)

# --- Menu ---
create_menu_actions(
    database_complete,
    online_connectivity,
    item_window,
    test_window,
    achievement_bag,
    open_team_builder,
    export_to_pkmn_showdown,
    export_all_pkmn_showdown,
    flex_pokemon_collection,
    eff_chart,
    gen_id_chart,
    credits,
    license,
    open_help_window,
    report_bug,
    rate_addon_url,
    version_dialog,
    trainer_card,
    ankimon_tracker_window,
    logger,
    settings_window,
    shop_manager,
    pokedex_window,
    settings_obj.get("controls.key_for_opening_closing_ankimon"),
    join_discord_url,
    open_leaderboard_url,
    settings_obj,
    addon_dir,
    pokemon_pc,
    backup_manager,
)

# --- Hook registry, profile hooks, reviewer UI, discord ---
from .hook_registry import (
    CatchPokemonHook,
    DefeatPokemonHook,
    add_catch_pokemon_hook,
    add_defeat_pokemon_hook,
)

from .profile_hooks import register_profile_hooks
register_profile_hooks(
    online_connectivity,
    backup_manager,
    CatchPokemonHook,
    DefeatPokemonHook,
    add_catch_pokemon_hook,
    add_defeat_pokemon_hook,
    collected_pokemon_ids,
)

from .reviewer_ui import setup_reviewer_ui, set_collected_ids
set_collected_ids(collected_pokemon_ids)
setup_reviewer_ui(
    settings_obj.get("controls.catch_key"),
    settings_obj.get("controls.defeat_key"),
    settings_obj.get("controls.pokemon_buttons"),
)

from .discord_integration import setup_discord_hooks
setup_discord_hooks()


---

[2]. src/Ankimon/singletons.py
Why this file is critical: Central repository for all global application state and major singleton instances.

"""
singletons.py

This module groups up some of the global variables that originally wer ein the __init__.py.
This module, hopefully, does not have vocation to remain permanently. This is but a transition step
in the splitting of the __init__.py file.

More detailed explanation if needed:
- Any important classes/functions
- Special behaviors, assumptions, or usage notes

Author: Axil
Created: 2025-06-03 (YYY-MM-DD)
"""

import json
import uuid

from aqt import mw

from .pyobj.ankimon_tracker import AnkimonTracker
from .pyobj.settings import Settings
from .pyobj.settings_window import SettingsWindow
from .pyobj.pokemon_obj import PokemonObject
from .pyobj.InfoLogger import ShowInfoLogger
from .pyobj.trainer_card import TrainerCard
from .pyobj.translator import Translator
from .pyobj.test_window import TestWindow
from .pyobj.achievement_window import AchievementWindow
from .pyobj.settings_window import SettingsWindow
from .pyobj.ankimon_tracker_window import AnkimonTrackerWindow
from .pyobj.ankimon_shop import PokemonShopManager
from .pokedex.pokedex_obj import Pokedex
from .pyobj.reviewer_obj import Reviewer_Manager
from .pyobj.evolution_window import EvoWindow
from .pyobj.starter_window import StarterWindow
from .pyobj.item_window import ItemWindow
from .pyobj.pc_box import PokemonPC
from .pyobj.database_manager import get_db
from .gui_entities import (
    License,
    Credits,
    TableWidget,
    IDTableWidget,
    Pokedex_Widget,
    Version_Dialog,
)
from .functions.update_main_pokemon import update_main_pokemon
from .functions.badges_functions import populate_achievements_from_badges
from .resources import addon_dir

# start loggerobject for Ankimon
logger = ShowInfoLogger()

# Initialize the database (this also runs migrations on first startup)
ankimon_db = get_db(logger)

# Create the Settings object
settings_obj = Settings()

# Pass the correct attributes to SettingsWindow
settings_window = SettingsWindow(
    config=settings_obj.config,  # Use settings_obj.config instead of settings_obj.settings.config
    set_config_callback=settings_obj.set,
    save_config_callback=settings_obj.save_config,
    load_config_callback=settings_obj.load_config,
)

# Init Translator
translator = Translator(language=int(settings_obj.get("misc.language")))

# Not sure what this does, but from afar it looks like a bad idea
mw.settings_ankimon = settings_window
mw.logger = logger
mw.translator = translator
mw.settings_obj = settings_obj
mw.ankimon_db = ankimon_db  # Database singleton for global access

main_pokemon, mainpokemon_empty = update_main_pokemon()

enemy_pokemon = PokemonObject(
    name="Rattata",  # Name of the Pokémon
    shiny=False,  # Shiny status (False for normal appearance)
    id=19,  # ID number
    level=5,  # Level
    ability="Run Away",  # Ability specific to Rattata
    type=["Normal"],  # Type (Normal type for Rattata)
    stats={  # Base stats for Rattata
        "hp": 39,
        "atk": 52,
        "def": 43,
        "spa": 60,
        "spd": 50,
        "spe": 65,
        "xp": 101,
    },
    attacks=["Quick Attack", "Tackle", "Tail Whip"],  # Typical moves for Rattata
    base_experience=58,  # Base experience points
    growth_rate="medium-slow",  # Growth rate
    hp=30,  # Hit points (HP)
    ev={
        "hp": 3,
        "atk": 5,
        "def": 4,
        "spa": 1,
        "spd": 2,
        "spe": 3,
    },  # EVs (Effort Values) for stats
    iv={
        "hp": 27,
        "atk": 24,
        "def": 3,
        "spa": 24,
        "spd": 16,
        "spe": 21,
    },  # IVs (Individual Values) for stats
    gender="M",  # Gender
    battle_status="Fighting",  # Status during battle
    xp=0,  # XP (experience points)
    position=(5, 5),  # Position in battle
    tier="Normal",
    captured_date=None,
    individual_id=str(uuid.uuid4()),
)

# Create a sample trainer card to test
trainer_card = TrainerCard(
    logger,
    main_pokemon,
    settings_obj,
    trainer_name=settings_obj.get("trainer.name"),
    trainer_id="".join(filter(str.isdigit, str(uuid.uuid4()).replace("-", ""))),
    team="Pikachu (Level 25), Charizard (Level 50), Bulbasaur (Level 15)",
    league="Unranked",
)

ankimon_tracker_obj = AnkimonTracker(
    trainer_card=trainer_card,
)
# Set Pokémon in the tracker
ankimon_tracker_obj.set_main_pokemon(main_pokemon)
ankimon_tracker_obj.set_enemy_pokemon(enemy_pokemon)

# Create an instance of the MainWindow
test_window = TestWindow(
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    settings_obj=settings_obj,
    ankimon_tracker_obj=ankimon_tracker_obj,
    translator=translator,
    parent=mw,
    logger=logger,
)

achievement_bag = AchievementWindow()

# Initialize the Pokémon Shop Manager
shop_manager = PokemonShopManager(
    logger=logger,
    settings_obj=settings_obj,
    set_callback=settings_obj.set,
    get_callback=settings_obj.get,
)

ankimon_tracker_window = AnkimonTrackerWindow(tracker=ankimon_tracker_obj)
pokedex_window = Pokedex(addon_dir, ankimon_tracker=ankimon_tracker_obj)
reviewer_obj = Reviewer_Manager(
    settings_obj=settings_obj,
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    ankimon_tracker=ankimon_tracker_obj,
)

eff_chart = TableWidget()
pokedex = Pokedex_Widget()
gen_id_chart = IDTableWidget()
license = License()
credits = Credits()
version_dialog = Version_Dialog()

achievements = populate_achievements_from_badges({str(i): False for i in range(1, 69)})

evo_window = EvoWindow(
    logger,
    settings_obj,
    main_pokemon,
    translator,
    reviewer_obj,
    test_window,
    achievements,
)
starter_window = StarterWindow(logger, settings_obj)
item_window = ItemWindow(  # Create an instance of the MainWindow
    logger=logger,
    settings_obj=settings_obj,
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    achievements=achievements,
    starter_window=starter_window,
    evo_window=evo_window,
)

pokemon_pc = PokemonPC(
    logger=logger,
    translator=translator,
    reviewer_obj=reviewer_obj,
    test_window=test_window,
    settings=settings_obj,
    main_pokemon=main_pokemon,
)


---

[3]. src/Ankimon/battle_loop.py
Why this file is critical: Orchestrates the core gameplay loop executing when flashcards are reviewed.

import copy
import random
from dataclasses import dataclass, field
from typing import Any, Optional

from aqt import mw
from aqt.qt import QDialog

from .singletons import (
    main_pokemon,
    enemy_pokemon,
    settings_obj,
    reviewer_obj,
    ankimon_tracker_obj,
    test_window,
    evo_window,
    logger,
    achievements,
    trainer_card,
    translator,
)
from .functions.encounter_functions import handle_enemy_faint, handle_main_pokemon_faint
from .functions.badges_functions import (
    handle_review_count_achievement,
    check_for_badge,
    receive_badge,
)
from .functions.battle_functions import (
    update_pokemon_battle_status,
    validate_pokemon_status,
    process_battle_data,
)
from .functions.drawing_utils import tooltipWithColour
from .utils import safe_get_random_move, play_effect_sound, play_sound
from .functions.ankimon_hooks_to_poke_engine import simulate_battle_with_poke_engine
from .classes.choose_move_dialog import MoveSelectionDialog
from .pyobj.error_handler import show_warning_with_traceback


@dataclass
class BattleState:
    new_state: Any = None
    mutator_full_reset: int = 1
    user_hp_after: int = 0
    opponent_hp_after: int = 0
    dmg_from_enemy_move: int = 0
    dmg_from_user_move: int = 0
    item_receive_value: int = 0
    collected_pokemon_ids: set = field(default_factory=set)


_state = BattleState()


def init_battle_state(collected_pokemon_ids: set):
    _state.item_receive_value = random.randint(3, 385)
    _state.collected_pokemon_ids = collected_pokemon_ids


def _get_cards_per_round() -> int:
    cards_per_round = settings_obj.get("battle.cards_per_round")
    if isinstance(cards_per_round, int):
        return cards_per_round
    if isinstance(cards_per_round, str) and "-" in cards_per_round:
        try:
            min_val, max_val = map(int, cards_per_round.split("-"))
            return random.randint(min_val, max_val)
        except (ValueError, IndexError):
            return 2
    return 2


def on_review_card(*args):
    global _state
    s = _state

    try:
        multiplier = ankimon_tracker_obj.multiplier
        user_attack = random.choice(main_pokemon.attacks) if main_pokemon.attacks else "splash"
        enemy_attack = random.choice(enemy_pokemon.attacks) if enemy_pokemon.attacks else "splash"

        battle_sounds = settings_obj.get("audio.battle_sounds")

        ankimon_tracker_obj.cards_battle_round += 1
        ankimon_tracker_obj.cry_counter += 1
        cry_counter = ankimon_tracker_obj.cry_counter
        total_reviews = ankimon_tracker_obj.get_total_reviews()
        reviewer_obj.seconds = 0
        reviewer_obj.myseconds = 0
        ankimon_tracker_obj.general_card_count_for_battle += 1

        color = "#F0B27A"

        handle_review_count_achievement(total_reviews, achievements)

        s.item_receive_value -= 1
        if s.item_receive_value <= 0:
            s.item_receive_value = random.randint(3, 385)
            test_window.display_item()
            if not check_for_badge(achievements, 6):
                receive_badge(6, achievements)

        if total_reviews == settings_obj.get("battle.daily_average"):
            settings_obj.set("trainer.cash", settings_obj.get("trainer.cash") + 200)
            trainer_card.cash = settings_obj.get("trainer.cash")

        if battle_sounds == True and ankimon_tracker_obj.general_card_count_for_battle == 1:
            play_sound(enemy_pokemon.id, settings_obj)

        if ankimon_tracker_obj.cards_battle_round >= _get_cards_per_round():
            ankimon_tracker_obj.cards_battle_round = 0
            ankimon_tracker_obj.attack_counter = 0
            ankimon_tracker_obj.pokemon_encounter += 1
            multiplier = ankimon_tracker_obj.multiplier

            if (
                ankimon_tracker_obj.pokemon_encounter > 0
                and enemy_pokemon.hp > 0
                and multiplier < 1
            ):
                enemy_move = safe_get_random_move(enemy_pokemon.attacks, logger=logger)
                enemy_move_category = enemy_move.get("category")
                if enemy_move_category == "Status":
                    color = "#F7DC6F"
                elif enemy_move_category == "Special":
                    color = "#D2B4DE"
                else:
                    color = "#F0B27A"
            else:
                enemy_attack = "splash"

            move = safe_get_random_move(main_pokemon.attacks, logger=logger)
            category = move.get("category")

            if (
                ankimon_tracker_obj.pokemon_encounter > 0
                and main_pokemon.hp > 0
                and enemy_pokemon.hp > 0
            ):
                if settings_obj.get("controls.allow_to_choose_moves") == True:
                    dialog = MoveSelectionDialog(main_pokemon.attacks)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        if dialog.selected_move:
                            user_attack = dialog.selected_move

                if category == "Status":
                    color = "#F7DC6F"
                elif category == "Special":
                    color = "#D2B4DE"
                else:
                    color = "#F0B27A"

            results = simulate_battle_with_poke_engine(
                main_pokemon,
                enemy_pokemon,
                user_attack,
                enemy_attack,
                s.mutator_full_reset,
                s.new_state,
            )

            battle_info = results[0]
            s.new_state = copy.deepcopy(results[1])
            s.dmg_from_enemy_move = results[2]
            s.dmg_from_user_move = results[3]
            s.mutator_full_reset = results[4]
            current_battle_info_changes = results[5]
            instructions = results[0]["instructions"]
            heals_to_user = sum(
                inst[2] for inst in instructions if inst[0:2] == ["heal", "user"]
            )
            heals_to_opponent = sum(
                inst[2] for inst in instructions if inst[0:2] == ["heal", "opponent"]
            )
            true_dmg_from_enemy_move = sum(
                inst[2] for inst in instructions if inst[0:2] == ["damage", "user"]
            )
            true_dmg_from_user_move = sum(
                inst[2] for inst in instructions if inst[0:2] == ["damage", "opponent"]
            )

            if true_dmg_from_enemy_move < 0:
                true_dmg_from_enemy_move = 0
                heals_to_user += abs(true_dmg_from_enemy_move)
            if true_dmg_from_user_move < 0:
                true_dmg_from_user_move = 0
                heals_to_opponent += abs(true_dmg_from_user_move)

            main_pokemon.hp = s.new_state.user.active.hp
            main_pokemon.current_hp = s.new_state.user.active.hp
            enemy_pokemon.hp = s.new_state.opponent.active.hp
            enemy_pokemon.current_hp = s.new_state.opponent.active.hp

            enemy_status_changed, main_status_changed = update_pokemon_battle_status(
                battle_info, enemy_pokemon, main_pokemon
            )
            enemy_pokemon.battle_status = validate_pokemon_status(enemy_pokemon)
            main_pokemon.battle_status = validate_pokemon_status(main_pokemon)

            formatted_battle_log = process_battle_data(
                battle_info=battle_info,
                multiplier=multiplier,
                main_pokemon=main_pokemon,
                enemy_pokemon=enemy_pokemon,
                user_attack=user_attack,
                enemy_attack=enemy_attack,
                dmg_from_user_move=true_dmg_from_user_move,
                dmg_from_enemy_move=true_dmg_from_enemy_move,
                user_hp_after=main_pokemon.hp,
                opponent_hp_after=enemy_pokemon.hp,
                battle_status=main_pokemon.battle_status,
                pokemon_encounter=ankimon_tracker_obj.pokemon_encounter,
                translator=translator,
                changes=current_battle_info_changes,
            )

            tooltipWithColour(formatted_battle_log, color)

            if true_dmg_from_enemy_move > 0 and multiplier < 1:
                reviewer_obj.myseconds = settings_obj.compute_special_variable("animate_time")
                tooltipWithColour(f" -{true_dmg_from_enemy_move} HP ", "#F06060", x=-200)
                play_effect_sound(settings_obj, "HurtNormal")

            if true_dmg_from_user_move > 0:
                reviewer_obj.seconds = settings_obj.compute_special_variable("animate_time")
                tooltipWithColour(f" -{true_dmg_from_user_move} HP ", "#F06060", x=200)
                if multiplier == 1:
                    play_effect_sound(settings_obj, "HurtNormal")
                elif multiplier < 1:
                    play_effect_sound(settings_obj, "HurtNotEffective")
                elif multiplier > 1:
                    play_effect_sound(settings_obj, "HurtSuper")
            else:
                reviewer_obj.seconds = 0

            if int(heals_to_user) != 0:
                heal_color = "#68FA94" if heals_to_user > 0 else "#F06060"
                sign = "+" if heals_to_user > 0 else ""
                tooltipWithColour(f" {sign}{int(heals_to_user)} HP ", heal_color, x=-250)

            if int(heals_to_opponent) != 0:
                heal_color = "#68FA94" if heals_to_opponent > 0 else "#F06060"
                sign = "+" if heals_to_opponent > 0 else ""
                tooltipWithColour(f" {sign}{int(heals_to_opponent)} HP ", heal_color, x=250)

            if enemy_pokemon.hp < 1:
                enemy_pokemon.hp = 0
                test_window.display_battle()
                handle_enemy_faint(
                    main_pokemon,
                    enemy_pokemon,
                    s.collected_pokemon_ids,
                    test_window,
                    evo_window,
                    reviewer_obj,
                    logger,
                    achievements,
                )
                s.mutator_full_reset = 1

        if cry_counter == 10 and battle_sounds is True:
            play_sound(enemy_pokemon.id, settings_obj)

        if main_pokemon.hp < 1:
            handle_main_pokemon_faint(
                main_pokemon, enemy_pokemon, test_window, reviewer_obj, translator
            )
            s.mutator_full_reset = 1

        class Container:
            pass

        reviewer = Container()
        reviewer.web = mw.reviewer.web
        reviewer_obj.update_life_bar(reviewer, 0, 0)
        if test_window is not None:
            if enemy_pokemon.hp > 0:
                test_window.display_battle()
    except Exception as e:
        show_warning_with_traceback(
            parent=mw, exception=e, message="An error occurred in reviewer:"
        )


---

[4]. src/Ankimon/pyobj/database_manager.py
Why this file is critical: Definitive source of truth and abstraction layer for all SQLite database persistence.

"""
AnkimonDB - Consolidated Database Manager for Ankimon

This module provides a SQLite-based storage solution for all Ankimon game data,
replacing multiple JSON files with a single, obfuscated database file.
"""

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import csv
from ..resources import user_path, csv_file_items_cost, mypokemon_path, mainpokemon_path, items_path, badges_path, team_pokemon_path as team_path


class AnkimonDB:
    """Handles all database operations for Ankimon. Stores data in SQLite."""

    DB_FILENAME = "ankimon.db"

    def __init__(self, logger=None):
        self.logger = logger
        self.db_path = user_path / self.DB_FILENAME
        self._connection: Optional[sqlite3.Connection] = None
        self._setup_database()

    def _log(self, level: str, message: str):
        """Helper for logging."""
        if self.logger:
            self.logger.log(level, message)
        else:
            print(f"[{level}] {message}")

    # --- Connection Management ---

    def _get_connection(self) -> sqlite3.Connection:
        """Gets or creates a database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row  # Access columns by name
        return self._connection

    def close(self):
        """Closes the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    # --- Obfuscation / De-obfuscation ---

    def _obfuscate(self, data: Any) -> str:
        """Serializes a Python object to a JSON string. (Formerly obfuscated)"""
        return json.dumps(data, ensure_ascii=False)

    def _deobfuscate(self, data_str: str) -> Optional[Any]:
        """Deserializes a JSON string to a Python object. (Formerly deobfuscated)"""
        if not data_str:
            return None
        try:
            return json.loads(data_str)
        except Exception as e:
            self._log("error", f"Failed to load json data: {e}")
            return None

    # --- Database Setup ---

    def _setup_database(self):
        """Creates all necessary tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Table for captured pokemon (replaces mypokemon.json AND mainpokemon.json)
        # is_main flag: 0 = not main, 1 = main pokemon
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS captured_pokemon (
                individual_id TEXT PRIMARY KEY,
                is_main INTEGER DEFAULT 0,
                data TEXT NOT NULL,
                name TEXT GENERATED ALWAYS AS (json_extract(data, '$.name')) VIRTUAL,
                pokedex_id INTEGER GENERATED ALWAYS AS (json_extract(data, '$.id')) VIRTUAL,
                shiny BOOLEAN GENERATED ALWAYS AS (json_extract(data, '$.shiny')) VIRTUAL,
                level INTEGER GENERATED ALWAYS AS (json_extract(data, '$.level')) VIRTUAL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_name ON captured_pokemon(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_pokedex_id ON captured_pokemon(pokedex_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_shiny ON captured_pokemon(shiny)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_level ON captured_pokemon(level)")

        # Check if is_main column exists (for migration from old schema)
        cursor.execute("PRAGMA table_info(captured_pokemon)")
        columns = [row[1] for row in cursor.fetchall()]
        if "is_main" not in columns:
            self._log("info", "Migrating schema: adding is_main column...")
            cursor.execute("ALTER TABLE captured_pokemon ADD COLUMN is_main INTEGER DEFAULT 0")
            # Migrate data from old main_pokemon table if it exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='main_pokemon'")
            if cursor.fetchone():
                cursor.execute("SELECT individual_id, data FROM main_pokemon WHERE id = 1")
                row = cursor.fetchone()
                if row:
                    main_id = row[0]
                    main_data = row[1]
                    # Update the existing pokemon to be main, or insert if not exists
                    cursor.execute(
                        "INSERT OR REPLACE INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 1, ?)",
                        (main_id, main_data)
                    )
                cursor.execute("DROP TABLE main_pokemon")
                self._log("info", "Migrated main_pokemon table to is_main flag")

        # Table for items (replaces items.json) - using PokeAPI integer ID as PK
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                item_name TEXT UNIQUE,
                quantity INTEGER DEFAULT 0,
                data TEXT,
                category_id INTEGER,
                cost INTEGER,
                fling_power INTEGER,
                fling_effect_id INTEGER
            )
        """)

        # Table for badges (replaces badges.json)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS badges (
                badge_id TEXT PRIMARY KEY,
                achieved BOOLEAN DEFAULT 0
            )
        """)

        # Metadata table for tracking migration status, etc.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Table for team composition (replaces team.json)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team (
                slot_position INTEGER PRIMARY KEY,
                individual_id TEXT NOT NULL
            )
        """)

        # Table for released pokemon history (replaces pokemon_history.json)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                individual_id TEXT UNIQUE,
                data TEXT NOT NULL
            )
        """)

        # Table for user data/credentials (replaces data.json)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Table for config settings (replaces config.obf)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.commit()
        self._log("info", "AnkimonDB: Database schema initialized.")

    # --- Captured Pokemon Operations ---

    def save_pokemon(self, pokemon_data: Dict[str, Any]):
        """Saves or updates a captured pokemon. Preserves is_main flag if pokemon already exists."""
        individual_id = pokemon_data.get("individual_id")
        if not individual_id:
            self._log("error", "Cannot save pokemon without individual_id")
            return False

        obfuscated_data = self._obfuscate(pokemon_data)
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check if pokemon already exists to preserve is_main flag
        cursor.execute("SELECT is_main FROM captured_pokemon WHERE individual_id = ?", (individual_id,))
        row = cursor.fetchone()

        if row:
            # Update existing - preserve is_main
            cursor.execute(
                "UPDATE captured_pokemon SET data = ? WHERE individual_id = ?",
                (obfuscated_data, individual_id)
            )
        else:
            # Insert new with is_main = 0
            cursor.execute(
                "INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 0, ?)",
                (individual_id, obfuscated_data)
            )
        conn.commit()
        return True

    def get_pokemon(self, individual_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific pokemon by its individual_id."""
        cursor = self.execute(
            "SELECT data FROM captured_pokemon WHERE individual_id = ?",
            (individual_id,)
        )
        row = cursor.fetchone()
        if row:
            return self._deobfuscate(row["data"])
        return None

    def get_all_pokemon(self) -> List[Dict[str, Any]]:
        """Retrieves all captured pokemon."""
        cursor = self.execute("SELECT data FROM captured_pokemon")
        results = []
        for row in cursor.fetchall():
            pokemon = self._deobfuscate(row["data"])
            if pokemon:
                results.append(pokemon)

        return results

    def has_pokemon_by_name(self, name: str) -> bool:
        """
        Efficiently checks if a pokemon with the given name exists in the collection.
        Uses a direct SQL query on the virtual name index.
        """
        cursor = self.execute("SELECT 1 FROM captured_pokemon WHERE LOWER(name) = LOWER(?) LIMIT 1", (name,))
        return cursor.fetchone() is not None

    def delete_pokemon(self, individual_id: str) -> bool:
        """Deletes a pokemon from the captured collection."""
        cursor = self.execute(
            "DELETE FROM captured_pokemon WHERE individual_id = ?",
            (individual_id,)
        )
        self._get_connection().commit()
        return cursor.rowcount > 0

    def replace_pokemon(self, pokemon_data: Dict[str, Any], old_individual_id: str) -> bool:
        """Replaces a pokemon with the given individual_id with the given pokemon_data."""

        obfuscated_data = self._obfuscate(pokemon_data)
        conn = self._get_connection()
        cursor = conn.cursor()

        new_individual_id = pokemon_data["individual_id"]

        # Are we trying to replace ourselves?
        if new_individual_id == old_individual_id:
            self._log("error", f"You already have this {pokemon_data['name']} in your collection!")
            return False


        # Does the pokemon being replaced exist?
        cursor.execute(
            "SELECT is_main FROM captured_pokemon WHERE individual_id = ?",
            (old_individual_id,)
        )
        row = cursor.fetchone()

        if row is None:
            self._log("error", f"No Pokémon found with individual_id {old_individual_id}")
            return False

        is_main = row[0]

        # Does the incoming Pokémon already exist somewhere else?
        cursor.execute(
            "SELECT 1 FROM captured_pokemon WHERE individual_id = ?",
            (new_individual_id,)
        )
        if cursor.fetchone() is not None:
            self._log("error", f"You already have this {pokemon_data['name']} in your collection!")
            return False

        # You passed all the checks. Full steam ahead!
        # Replace the row in-place
        cursor.execute(
            """
            UPDATE captured_pokemon
            SET individual_id = ?, is_main = ?, data = ?
            WHERE individual_id = ?
            """,
            (new_individual_id, is_main, obfuscated_data, old_individual_id)
        )

        conn.commit()

        return cursor.rowcount > 0

    def get_pokemon_count(self) -> int:
        """Returns the count of captured pokemon."""
        cursor = self.execute("SELECT COUNT(*) FROM captured_pokemon")
        return cursor.fetchone()[0]

    def get_shiny_count(self) -> int:
        """Returns the count of shiny pokemon."""
        cursor = self.execute("SELECT COUNT(*) FROM captured_pokemon WHERE shiny = 1")
        return cursor.fetchone()[0]

    def execute(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """Executes a custom SQL query and returns the cursor.
        Useful for caller-specific fast-path queries without cluttering the manager."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        return cursor

    def get_pokemons_by_individual_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Retrieves multiple pokemon by their individual_ids."""
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        cursor = self.execute(f"SELECT data FROM captured_pokemon WHERE individual_id IN ({placeholders})", ids)
        results = []
        for row in cursor.fetchall():
            pokemon = self._deobfuscate(row["data"])
            if pokemon:
                results.append(pokemon)
        return results

    def get_all_pokemon_ids(self) -> set:
        """Returns a set of all captured pokemon's pokedex IDs using the virtual index."""
        cursor = self.execute("SELECT pokedex_id FROM captured_pokemon WHERE pokedex_id IS NOT NULL")
        return {row[0] for row in cursor.fetchall()}

    # --- Main Pokemon Operations ---

    def save_main_pokemon(self, pokemon_data: Dict[str, Any]):
        """Saves/updates the main pokemon. Sets is_main=1 on this pokemon, is_main=0 on all others."""
        individual_id = pokemon_data.get("individual_id")
        if not individual_id:
            self._log("error", "Cannot save main pokemon without individual_id")
            return False

        obfuscated_data = self._obfuscate(pokemon_data)
        conn = self._get_connection()
        cursor = conn.cursor()

        # Clear the main flag from all pokemon first
        cursor.execute("UPDATE captured_pokemon SET is_main = 0 WHERE is_main = 1")

        # Save/update this pokemon and set as main
        cursor.execute(
            "INSERT OR REPLACE INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 1, ?)",
            (individual_id, obfuscated_data)
        )
        conn.commit()
        return True

    def get_main_pokemon(self) -> Optional[Dict[str, Any]]:
        """Retrieves the main pokemon (the one with is_main=1)."""
        cursor = self.execute("SELECT data FROM captured_pokemon WHERE is_main = 1")
        row = cursor.fetchone()
        if row:
            return self._deobfuscate(row["data"])
        return None

    def set_main_pokemon(self, individual_id: str) -> bool:
        """Sets a pokemon as the main pokemon by individual_id. Returns False if pokemon not found."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check if pokemon exists
        cursor.execute("SELECT individual_id FROM captured_pokemon WHERE individual_id = ?", (individual_id,))
        if not cursor.fetchone():
            return False

        # Clear old main
        cursor.execute("UPDATE captured_pokemon SET is_main = 0 WHERE is_main = 1")
        # Set new main
        cursor.execute("UPDATE captured_pokemon SET is_main = 1 WHERE individual_id = ?", (individual_id,))
        conn.commit()
        return True

    # --- Item Operations ---

    def add_item(self, item_name: str, quantity: int = 1, extra_data: Optional[Dict] = None, commit: bool = True) -> bool:
        """
        Adds a new item to the database with metadata discovery from items.csv.
        Use this for the first time an item is introduced (e.g. migration, looting).
        """
        item_id = None
        category_id = None
        cost = None
        fling_power = None
        fling_effect_id = None

        # Look up metadata from items.csv
        if Path(csv_file_items_cost).is_file():
            try:
                with open(csv_file_items_cost, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if r['identifier'] == item_name:
                            item_id = int(r['id'])
                            if r.get('category_id'): category_id = int(r['category_id'])
                            if r.get('cost'): cost = int(r['cost'])
                            if r.get('fling_power'): fling_power = int(r['fling_power'])
                            if r.get('fling_effect_id'): fling_effect_id = int(r['fling_effect_id'])
                            break
            except Exception as e:
                self._log("error", f"Failed to look up item '{item_name}' in items.csv: {e}")

        return self.save_item(
            item_id, item_name, quantity, extra_data,
            category_id=category_id, cost=cost,
            fling_power=fling_power, fling_effect_id=fling_effect_id,
            commit=commit
        )

    def save_item(self, item_id: Optional[int], item_name: str, quantity: int, extra_data: Optional[Dict] = None,
                  category_id: Optional[int] = None, cost: Optional[int] = None,
                  fling_power: Optional[int] = None, fling_effect_id: Optional[int] = None,
                  commit: bool = True) -> bool:
        """
        Low-level upsert for items. Lenient with metadata: if missing, tries to fetch from
        existing DB records but DOES NOT perform CSV lookups.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Lenient metadata resolution: try to fetch existing metadata from DB if NOT provided
        if item_name and (item_id is None or cost is None or category_id is None):
            cursor.execute("SELECT id, category_id, cost, fling_power, fling_effect_id FROM items WHERE item_name = ?", (item_name,))
            row = cursor.fetchone()
            if row:
                if item_id is None: item_id = row["id"]
                if category_id is None: category_id = row["category_id"]
                if cost is None: cost = row["cost"]
                if fling_power is None: fling_power = row["fling_power"]
                if fling_effect_id is None: fling_effect_id = row["fling_effect_id"]

        # Ensure type: "TM" for UI filtering if applicable
        if category_id == 37:
            if extra_data is None: extra_data = {}
            if extra_data.get("type") != "TM": extra_data["type"] = "TM"

        obfuscated_data = self._obfuscate(extra_data) if extra_data else None
        cursor.execute(
            """INSERT OR REPLACE INTO items
               (id, item_name, quantity, data, category_id, cost, fling_power, fling_effect_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (item_id, item_name, quantity, obfuscated_data, category_id, cost, fling_power, fling_effect_id)
        )
        if commit:
            conn.commit()
        return True

    def get_item(self, identifier: Any) -> Optional[Dict[str, Any]]:
        """Retrieves an item by name (identifier) or integer ID."""
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            field = "id"
        else:
            field = "item_name"

        cursor = self.execute(
            f"SELECT id, item_name, quantity, data, category_id, cost, fling_power, fling_effect_id FROM items WHERE {field} = ?",
            (identifier,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "item_name": row["item_name"],
                "quantity": row["quantity"],
                "extra_data": self._deobfuscate(row["data"]) if row["data"] else {},
                "category_id": row["category_id"],
                "cost": row["cost"],
                "fling_power": row["fling_power"],
                "fling_effect_id": row["fling_effect_id"]
            }
        return None

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Retrieves all items."""
        cursor = self.execute("SELECT id, item_name, quantity, data, category_id, cost, fling_power, fling_effect_id FROM items")
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "item_name": row["item_name"],
                "quantity": row["quantity"],
                "extra_data": self._deobfuscate(row["data"]) if row["data"] else {},
                "category_id": row["category_id"],
                "cost": row["cost"],
                "fling_power": row["fling_power"],
                "fling_effect_id": row["fling_effect_id"]
            })
        return results

    def update_item_quantity(self, item_name: str, delta: int) -> int:
        """Updates item quantity by delta. Returns new quantity."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get current quantity
        cursor.execute("SELECT quantity FROM items WHERE item_name = ?", (item_name,))
        row = cursor.fetchone()
        current_qty = row["quantity"] if row else 0
        if current_qty == 0:
            self._log("warning", f"Item '{item_name}' not found in inventory.")
            return 0
        new_qty = current_qty + delta
        if new_qty < 0:
            self._log("warning", f"Item '{item_name}' has insufficient quantity.")
            return current_qty

        if new_qty > 0:
            cursor.execute(
                "UPDATE items SET quantity = ? WHERE item_name = ?",
                (new_qty, item_name)
            )
        else:
            cursor.execute("DELETE FROM items WHERE item_name = ?", (item_name,))

        conn.commit()
        return new_qty

    # --- Badge Operations ---

    def save_badge(self, badge_id: str, badge_data: Dict[str, Any]):
        """Saves or updates a badge."""
        achieved = badge_data.get("achieved", "false")
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO badges (badge_id, achieved) VALUES (?, ?)",
            (badge_id, achieved)
        )
        conn.commit()
        return True

    def get_badge(self, badge_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a badge by ID."""
        cursor = self.execute("SELECT * FROM badges WHERE badge_id = ?", (badge_id,))
        row = cursor.fetchone()
        if row:
            return {
                "badge_id": row["badge_id"],
                "achieved": row["achieved"]
            }
        return None

    def get_all_badges(self) -> List[Dict[str, Any]]:
        """Retrieves all badges."""
        cursor = self.execute("SELECT badge_id, achieved FROM badges")
        results = []
        for row in cursor.fetchall():
            badge = {
                "badge_id": row["badge_id"],
                "achieved": row["achieved"]
            }
            results.append(badge)
        return results

    # --- Team Operations ---

    def save_team(self, team_list: List[Dict[str, Any]]):
        """Saves the team composition. Replaces existing team."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # clear existing team
        cursor.execute("DELETE FROM team")

        for i, member in enumerate(team_list):
            individual_id = member.get("individual_id")
            if individual_id:
                cursor.execute(
                    "INSERT INTO team (slot_position, individual_id) VALUES (?, ?)",
                    (i + 1, individual_id)
                )
        conn.commit()
        return True

    def get_team(self) -> List[Dict[str, Any]]:
        """Retrieves the current team as a list of dicts with individual_id."""
        cursor = self.execute("SELECT individual_id FROM team ORDER BY slot_position ASC")
        results = []
        for row in cursor.fetchall():
            results.append({"individual_id": row["individual_id"]})
        return results

    # --- Pokemon History Operations ---

    def add_to_history(self, pokemon_data: Dict[str, Any]):
        """Adds a released pokemon to history."""
        # Ensure individual_id exists to avoid duplicates if possible, or just generate one
        individual_id = pokemon_data.get("individual_id") or str(uuid.uuid4())

        obfuscated_data = self._obfuscate(pokemon_data)
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO pokemon_history (individual_id, data) VALUES (?, ?)",
                (individual_id, obfuscated_data)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            self._log("warning", f"Pokemon {individual_id} already in history.")
            return False

    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieves all released pokemon history."""
        cursor = self.execute("SELECT data FROM pokemon_history")
        results = []
        for row in cursor.fetchall():
            data = self._deobfuscate(row["data"])
            if data:
                results.append(data)
        return results

    # --- User Data Operations ---

    def set_user_data(self, key: str, value: Any):
        """Sets a user data key-value pair."""
        # Store as simple string if possible, or JSON string for complex objects
        str_value = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_data (key, value) VALUES (?, ?)",
            (key, str_value)
        )
        conn.commit()
        return True

    def get_user_data(self, key: str, default: Any = None) -> Any:
        """Retrieves user data by key."""
        cursor = self.execute("SELECT value FROM user_data WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            val = row["value"]
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(val)
            except:
                return val
        return default

    def get_all_user_data(self) -> Dict[str, Any]:
        """Retrieves all user data as a dictionary."""
        cursor = self.execute("SELECT key, value FROM user_data")
        result = {}
        for row in cursor.fetchall():
            key = row["key"]
            val = row["value"]
            try:
                result[key] = json.loads(val)
            except:
                result[key] = val
        return result

    # --- Config Operations (replaces config.obf) ---

    def set_config_value(self, key: str, value: Any):
        """Sets a config key-value pair."""
        # Store as JSON string to preserve type information
        str_value = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (key, str_value)
        )
        conn.commit()
        return True

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Retrieves a config value by key."""
        cursor = self.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            val = row["value"]
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(val)
            except:
                return val
        return default

    def get_all_config(self) -> Dict[str, Any]:
        """Retrieves all config settings as a dictionary."""
        cursor = self.execute("SELECT key, value FROM config")
        result = {}
        for row in cursor.fetchall():
            key = row["key"]
            val = row["value"]
            try:
                result[key] = json.loads(val)
            except:
                result[key] = val
        return result

    def save_all_config(self, config_dict: Dict[str, Any]):
        """Bulk saves a config dictionary to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        for key, value in config_dict.items():
            str_value = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)
            cursor.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (key, str_value)
            )
        conn.commit()
        return True

    def has_config(self) -> bool:
        """Checks if config data exists in the database."""
        cursor = self.execute("SELECT COUNT(*) FROM config")
        return cursor.fetchone()[0] > 0

    def get_stats(self) -> Dict[str, int]:
        """Returns a summary of database contents for synchronization/backup comparison."""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        # Count pokemon
        cursor.execute("SELECT COUNT(*) as count FROM captured_pokemon")
        stats["pokemon"] = cursor.fetchone()["count"]

        # Count items
        cursor.execute("SELECT COUNT(*) as count FROM items")
        stats["items"] = cursor.fetchone()["count"]

        # Count history
        cursor.execute("SELECT COUNT(*) as count FROM pokemon_history")
        stats["history"] = cursor.fetchone()["count"]

        # Count badges
        cursor.execute("SELECT COUNT(*) as count FROM badges")
        stats["badges"] = cursor.fetchone()["count"]

        return stats

    # --- Migration from JSON Files ---

    def migrate_from_json(self, mypokemon_path: Path, mainpokemon_path: Path,
                          items_path: Path, badges_path: Path,
                          team_path: Path = None, history_path: Path = None,
                          data_path: Path = None, rate_path: Path = None) -> Dict[str, int]:
        """
        Migrates data from JSON files to the database.
        Returns a dict with counts of migrated items.
        """
        stats = {"pokemon": 0, "main": 0, "items": 0, "badges": 0,
                 "team": 0, "history": 0, "userdata": 0}

        # Check if already migrated
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'migrated_phase2'")
        if cursor.fetchone():
            self._log("info", "Database Phase 2 (full) already migrated. Checking Phase 1...")
            # If Phase 2 is done, Phase 1 is definitely done.
            return stats

        # Check Phase 1 migration (captured, items, badges)
        cursor.execute("SELECT value FROM metadata WHERE key = 'migrated'")
        phase1_done = cursor.fetchone() is not None

        if not phase1_done:
            # Migrate mypokemon.json
            if mypokemon_path.is_file():
                try:
                    with open(mypokemon_path, 'r', encoding='utf-8') as f:
                        pokemon_list = json.load(f)
                    for pokemon in pokemon_list:
                        if self.save_pokemon(pokemon):
                            stats["pokemon"] += 1
                    self._log("info", f"Migrated {stats['pokemon']} pokemon from mypokemon.json")
                except Exception as e:
                    self._log("error", f"Failed to migrate mypokemon.json: {e}")

            # Migrate mainpokemon.json
            if mainpokemon_path.is_file():
                try:
                    with open(mainpokemon_path, 'r', encoding='utf-8') as f:
                        main_data = json.load(f)
                    if main_data:
                        # mainpokemon.json is a list with one item
                        main_pokemon = main_data[0] if isinstance(main_data, list) else main_data
                        if self.save_main_pokemon(main_pokemon):
                            stats["main"] = 1
                    self._log("info", "Migrated main pokemon from mainpokemon.json")
                except Exception as e:
                    self._log("error", f"Failed to migrate mainpokemon.json: {e}")

            # Migrate items.json
            if items_path.is_file():
                try:
                    with open(items_path, 'r', encoding='utf-8') as f:
                        items_list = json.load(f)

                    for item in items_list:
                        if not item: continue
                        # Support multiple legacy keys for item name
                        item_name = item.get("item") or item.get("name") or item.get("item_name")
                        quantity = item.get("quantity", item.get("amount", 1))
                        if item_name:
                            if self.add_item(item_name, quantity, extra_data=item, commit=False):
                                stats["items"] += 1

                    self._get_connection().commit()
                    self._log("info", f"Migrated {stats['items']} items from items.json")
                except Exception as e:
                    self._log("error", f"Failed to migrate items.json: {e}")

            # Migrate badges.json - handles both [1, 2, 3] and [{"id": 1}, ...] formats
            if badges_path.is_file():
                try:
                    with open(badges_path, 'r', encoding='utf-8') as f:
                        badges_list = json.load(f)
                    for badge in badges_list:
                        # Handle both integer, string, and dict formats
                        if isinstance(badge, (int, str)):
                            badge_id = str(badge)
                            badge_data = {"achieved": True}
                        else:
                            badge_id = str(badge.get("id", badge.get("badge_id", "")))
                            # Ensure we have achieved status preserved
                            badge_data = badge
                            badge_data["achieved"] = True

                        if badge_id:
                            self.save_badge(badge_id, badge_data)
                            stats["badges"] += 1
                    self._log("info", f"Migrated {stats['badges']} badges from badges.json")
                except Exception as e:
                    self._log("error", f"Failed to migrate badges.json: {e}")

            # Mark Phase 1 as done
            cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('migrated', 'true')")

        # --- Phase 2 Migration (Team, History, UserData) ---

        # Migrate team.json
        if team_path and team_path.is_file():
            try:
                with open(team_path, 'r', encoding='utf-8') as f:
                    team_list = json.load(f)
                if self.save_team(team_list):
                    stats["team"] = len(team_list)
                self._log("info", f"Migrated {stats['team']} team members from team.json")
            except Exception as e:
                self._log("error", f"Failed to migrate team.json: {e}")

        # Migrate pokemon_history.json
        if history_path and history_path.is_file():
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    history_list = json.load(f)
                for pokemon in history_list:
                    if self.add_to_history(pokemon):
                        stats["history"] += 1
                self._log("info", f"Migrated {stats['history']} history entries from pokemon_history.json")
            except Exception as e:
                self._log("error", f"Failed to migrate pokemon_history.json: {e}")

        # Migrate data.json (User Credentials)
        if data_path and data_path.is_file():
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                count = 0
                for key, value in user_data.items():
                    self.set_user_data(key, value)
                    count += 1
                stats["userdata"] = count
                self._log("info", f"Migrated {stats['userdata']} keys from data.json")
            except Exception as e:
                self._log("error", f"Failed to migrate data.json: {e}")

        # Step 8: Migrate rate_this.json
        if rate_path and rate_path.is_file():
            try:
                with open(rate_path, 'r', encoding='utf-8') as f:
                    rate_data = json.load(f)

                if isinstance(rate_data, dict) and rate_data.get("rate_this"):
                    self.set_user_data("rate_this", "true")
                    self._log("info", "Migrated rate_this.json")
            except Exception as e:
                self._log("error", f"Failed to migrate rate_this.json: {e}")

        # Mark Phase 2 as done
        cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('migrated_phase2', 'true')")
        conn.commit()

        # --- Integrity Check ---
        # Verify that database counts match expected counts from JSON files
        integrity_issues = []

        # Count JSON entries
        json_counts = {"pokemon": 0, "items": 0, "badges": 0}
        try:
            if mypokemon_path.is_file():
                with open(mypokemon_path, 'r', encoding='utf-8') as f:
                    json_counts["pokemon"] = len(json.load(f))
            if items_path.is_file():
                with open(items_path, 'r', encoding='utf-8') as f:
                    json_counts["items"] = len(json.load(f))
            if badges_path.is_file():
                with open(badges_path, 'r', encoding='utf-8') as f:
                    json_counts["badges"] = len(json.load(f))
        except Exception as e:
            self._log("warning", f"Could not read JSON files for integrity check: {e}")

        # Count database entries
        db_counts = {"pokemon": 0, "items": 0, "badges": 0}
        cursor.execute("SELECT COUNT(*) FROM captured_pokemon")
        db_counts["pokemon"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM items")
        db_counts["items"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM badges")
        db_counts["badges"] = cursor.fetchone()[0]

        # Compare counts
        for key in ["pokemon", "items", "badges"]:
            if json_counts[key] > 0 and db_counts[key] < json_counts[key]:
                integrity_issues.append(
                    f"{key}: JSON has {json_counts[key]} entries but DB only has {db_counts[key]}"
                )

        if integrity_issues:
            self._log("warning", f"Migration integrity issues detected: {integrity_issues}")
            stats["integrity_issues"] = integrity_issues
        else:
            self._log("info", "Migration integrity check passed - all counts match.")

        self._log("info", f"Migration complete: {stats}")
        return stats

    # --- Utility ---

    def is_migrated(self) -> bool:
        """Checks if ALL JSON data (Phase 1 & 2) has been migrated to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'migrated_phase2'")
        row = cursor.fetchone()
        return row is not None and row["value"] == "true"

    def is_migrated_phase1(self) -> bool:
        """Checks if Phase 1 data (pokemon, items, badges) has been migrated."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'migrated'")
        row = cursor.fetchone()
        return row is not None and row["value"] == "true"


# Singleton instance for use throughout the addon
_db_instance: Optional[AnkimonDB] = None


def get_db(logger=None) -> AnkimonDB:
    """Gets the singleton database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = AnkimonDB(logger)
    return _db_instance


---

[5]. src/Ankimon/startup.py
Why this file is critical: Handles initial bootstrap processes like migrations, asset checks, and first-run setup.

import json
import random

from aqt import mw

from .resources import (
    pkmnimgfolder,
    sound_list_path,
)
from .utils import (
    check_folders_exist,
    get_main_pokemon_data,
    load_collected_pokemon_ids,
    count_items_and_rewrite,
)
from .functions.encounter_functions import generate_random_pokemon
from .functions.badges_functions import get_achieved_badges
from .functions.rate_addon_functions import rate_this_addon
from .gui_entities import CheckFiles
from .pyobj.download_sprites import show_agreement_and_download_dialog
from .pyobj.backup_files import run_backup
from .pyobj.backup_manager import BackupManager
from .pyobj.error_handler import show_warning_with_traceback
from .singletons import (
    logger,
    translator,
    settings_obj,
    ankimon_tracker_obj,
    main_pokemon,
    enemy_pokemon,
    starter_window,
    ankimon_db,
)


def run_startup_sequence():
    logger.log_and_showinfo("game", translator.translate("startup"))
    logger.log_and_showinfo("game", translator.translate("backing_up_files"))

    try:
        run_backup()
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="Backup error:")

    backup_manager = BackupManager(logger, settings_obj)

    if not ankimon_db.is_migrated():
        from .pyobj.migration_dialog import show_migration_dialog_if_needed
        from .resources import (
            mypokemon_path, mainpokemon_path, itembag_path, badgebag_path,
            team_pokemon_path, pokemon_history_path, user_path_credentials,
            rate_path
        )
        show_migration_dialog_if_needed(
            ankimon_db, mypokemon_path, mainpokemon_path, itembag_path, badgebag_path, mw,
            team_pokemon_path, pokemon_history_path, user_path_credentials, rate_path
        )

    if settings_obj.get("misc.developer_mode"):
        backup_manager.create_backup(manual=False)

    collected_pokemon_ids = load_collected_pokemon_ids()

    with open(sound_list_path, "r", encoding="utf-8") as json_file:
        sound_list = json.load(json_file)

    ankimon_tracker_obj.pokemon_encounter = 0

    database_complete = _check_assets()

    if database_complete:
        _init_first_enemy()
        _check_starter()
        badge_list = get_achieved_badges()
        if len(badge_list) > 1:
            rate_this_addon()

    count_items_and_rewrite()

    return database_complete, collected_pokemon_ids, backup_manager


def _check_assets():
    back_sprites = check_folders_exist(pkmnimgfolder, "back_default")
    back_default_gif = check_folders_exist(pkmnimgfolder, "back_default_gif")
    front_sprites = check_folders_exist(pkmnimgfolder, "front_default")
    front_default_gif = check_folders_exist(pkmnimgfolder, "front_default_gif")
    item_sprites = check_folders_exist(pkmnimgfolder, "items")
    badges_sprites = check_folders_exist(pkmnimgfolder, "badges")

    database_complete = all([
        back_sprites,
        front_sprites,
        front_default_gif,
        back_default_gif,
        item_sprites,
        badges_sprites,
    ])

    if not database_complete:
        show_agreement_and_download_dialog(force_download=True)
        dialog = CheckFiles()
        dialog.show()

    return database_complete


def _init_first_enemy():
    try:
        get_main_pokemon_data()
    except Exception:
        pass

    (
        name, id, level, ability, type, base_stats, enemy_attacks,
        base_experience, growth_rate, ev, iv, gender,
        battle_status, battle_stats, tier, ev_yield, shiny,
    ) = generate_random_pokemon(main_pokemon.level, ankimon_tracker_obj)

    enemy_pokemon.update_stats(
        name=name, id=id, level=level, ability=ability, type=type,
        base_stats=base_stats, attacks=enemy_attacks,
        base_experience=base_experience, growth_rate=growth_rate,
        ev=ev, iv=iv, gender=gender, battle_status=battle_status,
        battle_stats=battle_stats, tier=tier, ev_yield=ev_yield, shiny=shiny,
    )
    max_hp = enemy_pokemon.calculate_max_hp()
    enemy_pokemon.current_hp = max_hp
    enemy_pokemon.hp = max_hp
    enemy_pokemon.max_hp = max_hp
    ankimon_tracker_obj.randomize_battle_scene()


def _check_starter():
    from .pyobj.database_manager import get_db
    db = get_db()
    if db.get_pokemon_count() == 0:
        starter_window.display_starter_pokemon()


---

[6]. src/Ankimon/card_hooks.py
Why this file is critical: Directly interfaces with Anki's card review hooks to trigger gameloop events.

import aqt
from aqt import gui_hooks, mw, utils
from aqt.utils import tooltip

from .singletons import ankimon_tracker_obj, reviewer_obj


def on_show_question(Card):
    ankimon_tracker_obj.start_card_timer()


def on_show_answer(Card):
    ankimon_tracker_obj.stop_card_timer()


def on_reviewer_did_show_question(card):
    reviewer_obj.update_life_bar(mw.reviewer, None, None)


def answerCard_before(filter, reviewer, card):
    utils.answBtnAmt = reviewer.mw.col.sched.answerButtons(card)
    return filter


def answerCard_after(rev, card, ease):
    maxEase = rev.mw.col.sched.answerButtons(card)
    if ease == 1:
        ankimon_tracker_obj.review("again")
    elif ease == maxEase - 2:
        ankimon_tracker_obj.review("hard")
    elif ease == maxEase - 1:
        ankimon_tracker_obj.review("good")
    elif ease == maxEase:
        ankimon_tracker_obj.review("easy")
    else:
        tooltip("Error in ColorConfirmation: Couldn't interpret ease")
    ankimon_tracker_obj.reset_card_timer()


def register_card_hooks():
    gui_hooks.reviewer_did_show_question.append(on_show_question)
    gui_hooks.reviewer_did_show_answer.append(on_show_answer)
    gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
    aqt.gui_hooks.reviewer_will_answer_card.append(answerCard_before)
    aqt.gui_hooks.reviewer_did_answer_card.append(answerCard_after)


---

[7]. src/Ankimon/pyobj/pokemon_obj.py
Why this file is critical: Defines the core data model and state structure for in-memory Pokémon instances.

from typing import Union
import uuid
import json
import os
from typing import Optional
from aqt import mw

from ..functions.sprite_functions import get_sprite_path

from ..poke_engine.objects import Pokemon
from ..resources import pkmnimgfolder, mainpokemon_path, mypokemon_path
from ..utils import give_item

class PokemonObject:
    def __init__(
        self,

        type,
        name: str,
        id: int,
        shiny: bool,
        level: int,
        ability,
        gender: str,
        growth_rate: str,
        captured_date: Optional[str],
        tier: str,
        individual_id: str,

        current_hp=15,
        base_stats=None,
        attacks=None,
        base_experience=0,
        hp=16,
        ev=None,
        iv=None,
        battle_status="Fighting",
        xp=0,
        position=(0, 0),
        nickname="",
        moves=None,
        ev_yield=None,
        friendship=0,
        everstone=False,
        pokemon_defeated=0,
        is_favorite=False,
        held_item: Union[str, None]=None,
        **kwargs
    ):
        # Unique identifier
        self.individual_id = individual_id
        self.name = name
        self.nickname = nickname
        self.shiny = shiny
        self.id = id
        self.level = level
        self.ability = ability
        self.type = type
        self.gender = gender
        self.tier = tier
        self.everstone = everstone
        self.pokemon_defeated = pokemon_defeated

        if not ability or str(ability).strip().lower() in ("none", "no ability", ""):
            self.ability = "Run Away"
        else:
            self.ability = ability

        # Stats
        self.base_stats = base_stats or {"hp": 1, "atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 1}
        self.ev = {k: int(v) for k, v in (ev or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}).items()}
        self.iv = {k: int(v) for k, v in (iv or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}).items()}
        self.ev_yield = {k: int(v) for k, v in (ev_yield or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}).items()}

        # Attacks and moves
        self.attacks = list(attacks) if attacks else ["Struggle"]
        self.moves = list(moves) if moves else []

        # Experience and growth
        self.base_experience = base_experience
        self.growth_rate = growth_rate
        self.xp = xp
        self.friendship = friendship

        # Battle and status
        self.battle_status = str(battle_status)
        self.position = tuple(position) if isinstance(position, (list, tuple)) else (0, 0)
        self.stat_stages = kwargs.get('stat_stages', {
            'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0
        })
        self.volatile_status = set(kwargs.get('volatile_status', []))
        self.nature = kwargs.get('nature', 'serious')
        self.held_item = held_item

        # HP calculation
        self.max_hp = self.calculate_max_hp()
        self.hp = int(kwargs.get('hp', self.max_hp))
        self.current_hp = current_hp or 15

        self.is_favorite = is_favorite
        self.captured_date = captured_date

    @classmethod
    def calc_stat(
        cls,
        stat_name: str,
        base_stat_val: int,
        level: int,
        iv: int,
        ev: int,
        nature: str
        ) -> int:
        if stat_name == "hp":
            hp = 10 + level + int((2 * base_stat_val + iv + int(ev / 4)) * level / 100)  # Formula found on bulbapedia
            return int(hp)
        elif stat_name in ("atk", "def", "spa", "spd", "spe"):
            nature_mult = PokemonObject.get_nature_stat_mult(stat_name, nature)  # Formula found on bulbapedia
            stat = (5 + int((2 * base_stat_val + iv + int(ev / 4)) * level / 100)) * nature_mult
            return int(stat)
        raise ValueError(f"Received an unknown stat_name : {stat_name}")

    @property
    def stats(self) -> dict:
        _dict = {}
        for key, val in self.base_stats.items():
            if key not in ("hp", "atk", "def", "spa", "spd", "spe"):
                continue
            _dict[key] = PokemonObject.calc_stat(
                key, val, self.level, self.iv[key], self.ev[key], self.nature
                )
        return _dict

    @stats.setter
    def stats(self, value):
        raise AttributeError("Setting the value of the stats of a Pokemon is forbidden as they are automatically calculated using their base stats. You can instead set the base_stats of the Pokemon.")

    @property
    def cp(self) -> int:
        """Combat Power — Pokemon GO style formula.

        ``CP = floor(Attack × √Defense × √Stamina × CPM² / 10)``

        Uses raw stats (base + IV + EV/4) so CPM is the sole level
        multiplier.  See :func:`business.calculate_pokemon_go_cp`.

        Memoized: attribute assignment to ``level``, ``ev``, ``iv``, or
        ``base_stats`` invalidates the cache via ``__setattr__``. Mutating
        those containers in-place (e.g. ``self.ev["atk"] += 1``) does not,
        so call :meth:`invalidate_cp_cache` explicitly at those sites.
        """
        cached = getattr(self, "_cached_cp", None)
        if cached is not None:
            return cached
        # Local import to avoid a circular dependency with ``business``.
        from ..business import calculate_pokemon_go_cp, pokemon_go_raw_stats

        attack, defense, stamina = pokemon_go_raw_stats(
            self.base_stats, self.iv, self.ev
        )
        cp_val = calculate_pokemon_go_cp(attack, defense, stamina, self.level)
        object.__setattr__(self, "_cached_cp", cp_val)
        return cp_val

    def invalidate_cp_cache(self) -> None:
        """Drop memoized CP so the next ``cp`` access recomputes.

        Call after mutating ``ev``/``iv``/``base_stats`` dict contents
        in place (attribute reassignment is caught automatically by
        ``__setattr__``).
        """
        object.__setattr__(self, "_cached_cp", None)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in ("level", "ev", "iv", "base_stats"):
            object.__setattr__(self, "_cached_cp", None)

    @classmethod
    def get_nature_stat_mult(cls, stat_name: str, nature: str) -> float:
        if stat_name == "atk":
            if nature.lower() in ("lonely", "brave", "adamant", "naughty"):
                return 1.1
            if nature.lower() in ("bold", "timid", "modest", "calm"):
                return 0.9
        elif stat_name == "def":
            if nature.lower() in ("bold", "relaxed", "impish", "lax"):
                return 1.1
            if nature.lower() in ("lonely", "hasty", "mild", "gentle"):
                return 0.9
        elif stat_name == "spa":
            if nature.lower() in ("modest", "mild", "quiet", "rash"):
                return 1.1
            if nature.lower() in ("adamant", "impish", "jolly", "careful"):
                return 0.9
        elif stat_name == "spd":
            if nature.lower() in ("calm", "gentle", "sassy", "careful"):
                return 1.1
            if nature.lower() in ("naughty", "lax", "naive", "rash"):
                return 0.9
        elif stat_name == "spe":
            if nature.lower() in ("timid", "hasty", "jolly", "naive"):
                return 1.1
            if nature.lower() in ("brave", "relaxed", "quiet", "sassy"):
                return 0.9
        return 1.0

    def to_dict(self):
        return {
            "name": self.name,
            "nickname": self.nickname,
            "level": self.level,
            "gender": self.gender,
            "id": self.id,
            "ability": self.ability,
            "type": self.type,
            "base_stats": self.base_stats,
            "stats": self.stats,  # Calculated stats
            "cp": self.cp,
            "nature": self.nature,
            "ev": self.ev,
            "iv": self.iv,
            "attacks": self.attacks,
            "base_experience": self.base_experience,
            "growth_rate": self.growth_rate,
            "everstone": self.everstone,
            "shiny": self.shiny,
            "captured_date": getattr(self, "captured_date", None),
            "individual_id": self.individual_id,
            "mega": getattr(self, "mega", False),
            "special_form": getattr(self, "special_form", None),
            "xp": self.xp,
            "hp": self.hp,  # Current HP
            "friendship": self.friendship,
            "pokemon_defeated": self.pokemon_defeated,
            "tier": self.tier,  # Added tier
            "is_favorite": getattr(self, "is_favorite", False),  # Added with default
            # Additional fields from your example
            "current_hp": getattr(self, "current_hp", self.hp),
            "held_item": self.held_item,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def get_stats(self):
        """Return the stats of the Pokémon."""
        return vars(self)

    # Derived/read-only attributes to skip in update_stats. ``cp`` and
    # ``stats`` are @property getters whose setattr raises
    # AttributeError (silently swallowed by the caller's bare
    # `except Exception`). ``max_hp`` is a plain cache field — setattr
    # would succeed, but the splatted value is almost certainly stale
    # relative to the new ``level``/``base_stats``, so we skip it and
    # recompute it ourselves below.
    _READONLY_ATTRS = frozenset({"cp", "stats", "max_hp"})

    def update_stats(self, **kwargs):
        """Update the attributes of the Pokémon object with keyword arguments."""
        for key, value in kwargs.items():
            if key in self._READONLY_ATTRS:
                continue
            if hasattr(self, key):
                setattr(self, key, value)
        # Derived caches — recompute from the (possibly updated)
        # base_stats/level/iv/ev so they don't go stale.
        self.max_hp = self.calculate_max_hp()
        self._update_battle_stats()  # Update battle stats

    def reset_stats(self):
        """Reset the stats of the Pokémon to default values."""
        self.hp = self.max_hp
        self.battle_status = "Fighting"
        self._update_battle_stats()

    def _update_battle_stats(self):
        """Update battle stats with current stats, EVs, and IVs."""
        self._battle_stats = {}
        # Only update battle stats with valid keys
        for d in [self.stats, self.iv, self.ev]:
            for key, value in d.items():
                self._battle_stats[key] = value

    def calculate_max_hp(self):
        ev, iv = self.ev["hp"], self.iv["hp"]
        hp = 10 + self.level + int((2 * self.base_stats["hp"] + iv + int(ev / 4)) * self.level / 100)
        hp = int(hp)
        return hp

    def get_sprite_path(self, side, sprite_type):
        return get_sprite_path(side, sprite_type, self.id, self.shiny, self.gender)

    def to_engine_format(self):
        from ..poke_engine.helpers import normalize_name
        return {
            'identifier': normalize_name(self.name),
            'level': self.level,
            'nature': getattr(self, 'nature', 'serious'),
            'evs': (
                self.ev.get('hp', 0),
                self.ev.get('atk', 0),
                self.ev.get('def', 0),
                self.ev.get('spa', 0),
                self.ev.get('spd', 0),
                self.ev.get('spe', 0)
            ),
            'types': [normalize_name(t) for t in self.type],
            'hp': self.hp,
            'maxhp': self.max_hp,
            'ability': normalize_name(self.ability) if self.ability else 'none',
            'item': normalize_name(self.held_item) if self.held_item else None,
            'attack': self.stats.get('atk', 0),
            'defense': self.stats.get('def', 0),
            'special_attack': self.stats.get('spa', 0),
            'special_defense': self.stats.get('spd', 0),
            'speed': self.stats.get('spe', 0),
            'ivs': (
                self.iv.get('hp', 0),
                self.iv.get('atk', 0),
                self.iv.get('def', 0),
                self.iv.get('spa', 0),
                self.iv.get('spd', 0),
                self.iv.get('spe', 0)
            ),
            'attack_boost': self.stat_stages.get('atk', 0),
            'defense_boost': self.stat_stages.get('def', 0),
            'special_attack_boost': self.stat_stages.get('spa', 0),
            'special_defense_boost': self.stat_stages.get('spd', 0),
            'speed_boost': self.stat_stages.get('spe', 0),
            'accuracy_boost': self.stat_stages.get('accuracy', 0),
            'evasion_boost': self.stat_stages.get('evasion', 0),
            'status': self.battle_status if self.battle_status != "fighting" else None,
            'volatile_status': set(normalize_name(vs) for vs in self.volatile_status),
            'moves': [{'id': normalize_name(move)} for move in self.attacks]
        }

    @classmethod
    def from_engine_format(cls, engine_data):
        """Create PokemonObject from poke-engine data"""
        return cls(
            name=engine_data['identifier'].capitalize(),
            level=engine_data['level'],
            hp=engine_data['hp'],
            base_stats={
                'hp': engine_data.get('maxhp', 0),
                'atk': engine_data['attack'],
                'def': engine_data['defense'],
                'spa': engine_data['special_attack'],
                'spd': engine_data['special_defense'],
                'spe': engine_data['speed']
            },
            ev={k: v for k, v in zip(['hp','atk','def','spa','spd','spe'], engine_data['evs'])},
            iv={k: v for k, v in zip(['hp','atk','def','spa','spd','spe'], engine_data['ivs'])},
            battlestatus=engine_data.get('status', 'fighting'),
            moves=engine_data['moves'],
            stat_stages={
                'atk': engine_data['stat_stages']['attack'],
                'def': engine_data['stat_stages']['defense'],
                'spa': engine_data['stat_stages']['special_attack'],
                'spd': engine_data['stat_stages']['special_defense'],
                'spe': engine_data['stat_stages']['speed'],
                'accuracy': engine_data['stat_stages']['accuracy'],
                'evasion': engine_data['stat_stages']['evasion']
            },
            volatile_status=set(engine_data.get('volatile_status', [])),
            nature=engine_data.get('nature', 'serious'),
            held_item=engine_data.get('item', '')
        )

    def to_poke_engine_Pokemon(self) -> Pokemon:
        _dict = self.to_engine_format()
        pokemon = Pokemon(
            identifier=_dict['identifier'],
            level=_dict['level'],
            types=_dict['types'],
            hp=_dict['hp'],
            maxhp=_dict['maxhp'],
            ability=_dict['ability'],
            item=_dict['item'],
            attack=_dict['attack'],
            defense=_dict['defense'],
            special_attack=_dict['special_attack'],
            special_defense=_dict['special_defense'],
            speed=_dict['speed'],
            nature=_dict.get('nature', 'serious'),
            evs=_dict.get('evs', (85,) * 6),
            attack_boost=_dict.get('attack_boost', 0),
            defense_boost=_dict.get('defense_boost', 0),
            special_attack_boost=_dict.get('special_attack_boost', 0),
            special_defense_boost=_dict.get('special_defense_boost', 0),
            speed_boost=_dict.get('speed_boost', 0),
            accuracy_boost=_dict.get('accuracy_boost', 0),
            evasion_boost=_dict.get('evasion_boost', 0),
            status=_dict.get('status', None),
            terastallized=_dict.get('terastallized', False),
            volatile_status=_dict.get('volatile_status', set()),
            moves=_dict.get('moves', [])
        )
        return pokemon

    def reset_bonuses(self):
        """
        This method resets various bonuses and status effects currently applied
        to the pokemon.

        This method is typically used to reset the stat boosts of the main
        Pokemon when the opponent gets KOed, preventing the user from
        steamrolling every wild pokemon once the main pokemon is setup with
        stat boosts.

        Args:
            None

        Returns:
            None
        """
        self.stat_stages = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'accuracy': 0,
            'evasion': 0
            }

    def give_held_item(self, held_item: str) -> None:
        """
        Assigns a held item to the Pokémon and updates the database.

        If the Pokémon is already holding an item, it is removed first.
        """
        db = mw.ankimon_db

        # If the pokemon already holds an object, we remove it to make room for the new one.
        if self.held_item:
            self.remove_held_item()

        db.update_item_quantity(held_item, -1)
        self.held_item = held_item

        # Save to captured_pokemon in database
        pokemon_data = db.get_pokemon(self.individual_id)
        if pokemon_data:
            pokemon_data["held_item"] = held_item
            db.save_pokemon(pokemon_data)

        # Also update main_pokemon if this is the main pokemon
        main_pokemon = db.get_main_pokemon()
        if main_pokemon and main_pokemon.get("individual_id") == self.individual_id:
            main_pokemon["held_item"] = held_item
            db.save_main_pokemon(main_pokemon)

    def remove_held_item(self) -> None:
        """
        Removes the held item from the Pokémon and updates the database.
        """
        if self.held_item is None:
            return

        db = mw.ankimon_db

        give_item(self.held_item)  # We put the item back in the item bag
        self.held_item = None

        # Save to captured_pokemon in database
        pokemon_data = db.get_pokemon(self.individual_id)
        if pokemon_data:
            pokemon_data["held_item"] = None
            db.save_pokemon(pokemon_data)

        # Also update main_pokemon if this is the main pokemon
        main_pokemon = db.get_main_pokemon()
        if main_pokemon and main_pokemon.get("individual_id") == self.individual_id:
            main_pokemon["held_item"] = None
            db.save_main_pokemon(main_pokemon)


class PokemonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PokemonObject):
            data = obj.__dict__.copy()
            # Convert complex types to serializable formats
            data['volatile_status'] = list(data['volatile_status'])
            data['stat_stages'] = data.get('stat_stages', {})
            data['moves'] = data.get('attacks', [])
            return data
        return super().default(obj)


---

[8]. src/Ankimon/functions/ankimon_hooks_to_poke_engine.py
Why this file is critical: Acts as the crucial bridge translating Ankimon state objects into poke_engine simulation state.

import random
from collections import defaultdict
import copy
import traceback
from typing import Union

from ..poke_engine import constants
from ..singletons import ankimon_tracker_obj, settings_obj
import math

from ..poke_engine.battle import Move
from ..poke_engine.objects import Pokemon, State, StateMutator, Side
from ..poke_engine.helpers import normalize_name
from ..poke_engine.find_state_instructions import get_all_state_instructions
from ..pyobj.error_handler import show_warning_with_traceback

def reset_stat_boosts(pokemon: Pokemon) -> Pokemon:
    """
    Resets all stat boosts of a given Pokemon to zero.

    Args:
        pokemon (Pokemon): The Pokemon whose stat boosts will be reset.

    Returns:
        Pokemon: The same Pokemon object with all stat boosts reset to zero.
    """
    pokemon.attack_boost = 0
    pokemon.defense_boost = 0
    pokemon.special_attack_boost = 0
    pokemon.special_defense_boost = 0
    pokemon.speed_boost = 0
    pokemon.accuracy_boost = 0
    pokemon.evasion_boost = 0
    return pokemon

def reset_side(pokemon: Pokemon, side_conditions: Union[dict, None]=None) -> Side:
    """
    Resets and returns a new Side object for the given Pokemon with default or provided side conditions.

    If no side conditions are provided, a default set with all conditions initialized to zero is used.

    Args:
        pokemon (Pokemon): The active Pokemon for the side.
        side_conditions (Union[dict, None], optional): A dictionary of side conditions to apply.
            If None, defaults to all conditions set to zero.

    Returns:
        Side: A new Side object with the specified active Pokemon, an empty reserve,
              default wish and future sight settings, and the given or default side conditions.
    """
    if side_conditions is None:
        side_conditions = defaultdict(int, {
            'stealthrock': 0,
            'spikes': 0,
            'toxicspikes': 0,
            'tailwind': 0,
            'reflect': 0,
            'lightscreen': 0,
            'auroraveil': 0,
            'protect': 0,
        })
    side = Side(
        active=pokemon,
        reserve={},
        wish=(0, 0),
        side_conditions=side_conditions,
        future_sight=(0, 0),
    )
    return side

def simulate_battle_with_poke_engine(
    main_pokemon: Pokemon,
    enemy_pokemon: Pokemon,
    main_move: str,
    enemy_move: str,
    mutator_full_reset: int,
    state: Union[State, None]=None,
    ):
    """
    Simulates a battle between two Pokémon using the poke-engine if available.
    The function selects the Pokémon moves (either provided or random), handles state changes,
    and applies battle instructions based on the current battle state. The function then
    computes and returns the battle results, including damage dealt, missed moves,
    and the updated battle state.

    Args:
        main_pokemon (Pokemon): The user's active Pokémon.
        enemy_pokemon (Pokemon): The opponent's active Pokémon.
        main_move (str or None): The move chosen by the user's Pokémon. If None, a random move will be selected.
        enemy_move (str or None): The move chosen by the opponent's Pokémon. If None, a random move will be selected.
        new_state (State): The current battle state, including the Pokémon's stats, field conditions, etc.
        mutator_full_reset (int): A flag controlling whether the battle state should be reset.

    Returns:
        tuple: A tuple containing:
            - battle_info (dict): A dictionary with the battle header and instructions for each Pokémon move.
            - new_state (State): The updated battle state after the battle simulation.
            - dmg_from_enemy_move (int): The damage dealt to the user's Pokémon by the enemy.
            - dmg_from_user_move (int): The damage dealt to the enemy's Pokémon by the user.
            - mutator_full_reset (int): The flag indicating if the battle state was reset.

    Raises:
        Exception: If any unexpected error occurs during the simulation, the traceback will be printed.

    Notes:
        - If no moves are provided for the Pokémon, a random move is selected.
        - The outcome of the battle is determined based on probability, with weights reflecting typical battle mechanics.
        - The function prints a summary of the battle result, including damage dealt and whether any moves missed.
        - The state mutator is applied to update the battle state after the moves are resolved.
    """

    # If no move is provided, use a random move
    if main_move is None and main_pokemon.attacks:
        main_move = random.choice(main_pokemon.attacks)
    if enemy_move is None and enemy_pokemon.attacks:
        enemy_move = random.choice(enemy_pokemon.attacks)
    if not main_move:
        main_move = "Splash"
    if not enemy_move:
        enemy_move = "Splash"


    if (state is not None) and (state.user.active.id != main_pokemon.name.lower()):
        mutator_full_reset = 1 # reset AFTER Pokemon is changed !
    if mutator_full_reset not in (0, 1):
        mutator_full_reset = 1

    try:
        main_move_normalized = normalize_name(main_move)
        enemy_move_normalized = normalize_name(enemy_move)


        # Store only the chosen outcome
        battle_header = {
            'user': {
                'name': main_pokemon.name,
                'level': main_pokemon.level,
                'move': main_move
            },
            'opponent': {
                'name': enemy_pokemon.name,
                'level': enemy_pokemon.level,
                'move': enemy_move
            }
        }

        # Create Pokemon objects
        main_pokemon_poke_engine = main_pokemon.to_poke_engine_Pokemon()
        enemy_pokemon_poke_engine = enemy_pokemon.to_poke_engine_Pokemon()

        # Default side_conditions with all needed keys
        side_conditions = defaultdict(int, {
            'stealthrock': 0,
            'spikes': 0,
            'toxicspikes': 0,
            'tailwind': 0,
            'reflect': 0,
            'lightscreen': 0,
            'auroraveil': 0,
            'protect': 0,
        })

        if state is None:
            state = State(
                user=reset_side(main_pokemon_poke_engine),
                opponent=reset_side(enemy_pokemon_poke_engine),
                weather=None,
                field=None,
                trick_room=False,
                )
        else:
            if mutator_full_reset == 0:  # Combat is ongoing
                pass
            elif mutator_full_reset == 1:  # Reset both sides of the fight
                state.user.active = reset_stat_boosts(state.user.active)
                state.user = reset_side(main_pokemon_poke_engine)
                state.opponent = reset_side(enemy_pokemon_poke_engine)

                # Reset battle_status and volatile_status for both engine state Pokémon
                if hasattr(state.user.active, 'battle_status'):
                    state.user.active.battle_status = 'fighting'
                if hasattr(state.user.active, 'volatile_status'):
                    state.user.active.volatile_status = set()
                if hasattr(state.opponent.active, 'battle_status'):
                    state.opponent.active.battle_status = 'fighting'
                if hasattr(state.opponent.active, 'volatile_status'):
                    state.opponent.active.volatile_status = set()
                # Clear Future Sight state on reset - NEW
                if hasattr(state.user, 'future_sight'):
                    state.user.future_sight = (0, 0)
                if hasattr(state.opponent, 'future_sight'):
                    state.opponent.future_sight = (0, 0)

                # Also reset the main_pokemon and enemy_pokemon Python objects
                main_pokemon.battle_status = 'fighting'
                main_pokemon.volatile_status = set()
                enemy_pokemon.battle_status = 'fighting'
                enemy_pokemon.volatile_status = set()

                state.weather = None # Reset weather to None
                state.field = None # Reset field to None
                state.trick_room = False # Reset trick room to None

            else:
                raise ValueError(f"Wrong mutator_full_reset encountered : {mutator_full_reset}")

        mutator = StateMutator(state)

        if state.opponent.active.hp == 0:
            main_move = "Splash"
            enemy_move = "Splash"

        # Get all possible outcomes
        transpose_instructions = get_all_state_instructions(
            mutator, main_move_normalized, enemy_move_normalized
        )

        # Randomly select ONE outcome from possible outcomes, using probability weights for the outcomes in actual Pokemon battles
        # e.g. if P(outcome 1):P(outcome 2) = 20% : 80%, then 20% chance to pick outcome 1 (picks randomly)
        weights = [outcome.percentage for outcome in transpose_instructions]
        chosen_outcome = random.choices(transpose_instructions, weights=weights, k=1)[0]


        if settings_obj.get("battle.review_based_damage"):
            instrs = []
            for instr in chosen_outcome.instructions:
                if instr[0] == constants.DAMAGE and instr[1] == constants.OPPONENT:
                    modified_instr = (instr[0], instr[1], math.floor(instr[2] * ankimon_tracker_obj.multiplier)) + instr[3:]
                    instrs.append(modified_instr)
                else:
                    instrs.append(instr)
        else:
            instrs = chosen_outcome.instructions

        user_hp_before = int(state.user.active.hp)
        opponent_hp_before = int(state.opponent.active.hp)

        # --- Debugging: State changes BEFORE applying instructions
        state_before = copy.deepcopy(mutator.state)
        mutator.apply(instrs)
        state_after = mutator.state
        battle_info_changes = diff_states(state_before, state_after)
        print_state_changes(battle_info_changes)
        # --- End Debugging

        # Save changes from State to Pokemon objects (enhanced for volatile status)
        main_pokemon.hp = state.user.active.hp
        main_pokemon.current_hp = state.user.active.hp
        enemy_pokemon.hp = state.opponent.active.hp
        enemy_pokemon.current_hp = state.opponent.active.hp

        main_pokemon.stat_stages = {
            'atk': state.user.active.attack_boost,
            'def': state.user.active.defense_boost,
            'spa': state.user.active.special_attack_boost,
            'spd': state.user.active.special_defense_boost,
            'spe': state.user.active.speed_boost,
            'accuracy': state.user.active.accuracy_boost,
            'evasion': state.user.active.evasion_boost
        }

        # Save volatile status from poke-engine state to Pokemon object - NEW
        if hasattr(state.user.active, 'volatile_status'):
            main_pokemon.volatile_status = state.user.active.volatile_status.copy()
        elif not hasattr(main_pokemon, 'volatile_status'):
            main_pokemon.volatile_status = set()


        # Same for enemy Pokemon
        enemy_pokemon.stat_stages = {
            'atk': state.opponent.active.attack_boost,
            'def': state.opponent.active.defense_boost,
            'spa': state.opponent.active.special_attack_boost,
            'spd': state.opponent.active.special_defense_boost,
            'spe': state.opponent.active.speed_boost,
            'accuracy': state.opponent.active.accuracy_boost,
            'evasion': state.opponent.active.evasion_boost
        }

        # Save volatile status for enemy - NEW
        if hasattr(state.opponent.active, 'volatile_status'):
            enemy_pokemon.volatile_status = state.opponent.active.volatile_status.copy()
        elif not hasattr(enemy_pokemon, 'volatile_status'):
            enemy_pokemon.volatile_status = set()

        new_state = copy.deepcopy(state)

        mutator_full_reset = 0 # preserve battle state - until something else changes this value

        user_hp_after = int(new_state.user.active.hp)
        opponent_hp_after = int(new_state.opponent.active.hp)

        dmg_from_user_move = int(opponent_hp_before - opponent_hp_after)
        dmg_from_enemy_move = int(user_hp_before - user_hp_after)

        # Reference to the founder and creator of Ankimon, Unlucky-life.
        # Unlucky, we are very proud of you for your work. You are a legend.
        # It's been a pleasure being part of this journey. -- h0tp (and friends)

        if int(chosen_outcome.percentage) == 0:
            unlucky_life = 1
        else:
            unlucky_life = int(chosen_outcome.percentage)

        # On a serious note, the function above is the CHANCE that the chosen_outcome was picked out of ALL
        # the choices in transpose_instructions, based on factors like accuracy rate, the chance to
        # inflict a certain status (like sleep or paralyze), etc.

        battle_effects = []
        for instr in instrs:
            battle_effects.append(list(instr))  # Convert tuples to lists

        battle_info = {
            'battle_header': battle_header,
            'instructions': battle_effects,
            'state': new_state
            }

        print(f"{unlucky_life * 100}% chance: {battle_effects}")
        return battle_info, new_state, dmg_from_enemy_move, dmg_from_user_move, mutator_full_reset, battle_info_changes

    except Exception as e:
        show_warning_with_traceback(exception=e, message="Error simulating battle:")

def diff_states(state_before, state_after, path="", changes=None):
    """
    Recursively compare two state objects and return a list of changed attributes.
    Returns changes in format: {'key': path, 'before': value_before, 'after': value_after}
    """
    if changes is None:
        changes = []

    # Handle None cases
    if state_before is None and state_after is None:
        return changes
    if state_before is None or state_after is None:
        changes.append({
            'key': path or 'root',
            'before': state_before,
            'after': state_after
        })
        return changes

    # Handle primitive types (int, float, str, bool)
    if isinstance(state_before, (int, float, str, bool)) or isinstance(state_after, (int, float, str, bool)):
        if state_before != state_after:
            changes.append({
                'key': path or 'root',
                'before': state_before,
                'after': state_after
            })
        return changes

    # Handle sets
    if isinstance(state_before, set) or isinstance(state_after, set):
        if state_before != state_after:
            changes.append({
                'key': path or 'root',
                'before': state_before,
                'after': state_after
            })
        return changes

    # Handle tuples
    if isinstance(state_before, tuple) or isinstance(state_after, tuple):
        if state_before != state_after:
            changes.append({
                'key': path or 'root',
                'before': state_before,
                'after': state_after
            })
        return changes

    # Handle lists
    if isinstance(state_before, list) and isinstance(state_after, list):
        # Compare list lengths and elements
        if len(state_before) != len(state_after):
            changes.append({
                'key': f"{path}.length" if path else 'length',
                'before': len(state_before),
                'after': len(state_after)
            })

        # Compare elements up to the shorter length
        min_len = min(len(state_before), len(state_after))
        for i in range(min_len):
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            diff_states(state_before[i], state_after[i], new_path, changes)

        # Handle extra elements in longer list
        if len(state_before) > min_len:
            for i in range(min_len, len(state_before)):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                changes.append({
                    'key': new_path,
                    'before': state_before[i],
                    'after': None
                })
        elif len(state_after) > min_len:
            for i in range(min_len, len(state_after)):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                changes.append({
                    'key': new_path,
                    'before': None,
                    'after': state_after[i]
                })
        return changes

    # Handle dictionaries
    if isinstance(state_before, dict) and isinstance(state_after, dict):
        all_keys = set(state_before.keys()) | set(state_after.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else str(key)
            before_val = state_before.get(key, None)
            after_val = state_after.get(key, None)
            diff_states(before_val, after_val, new_path, changes)
        return changes

    # Handle custom objects - check if they're the same type
    if type(state_before) != type(state_after):
        changes.append({
            'key': path or 'root',
            'before': state_before,
            'after': state_after
        })
        return changes

    # Custom class: recurse into attributes (__dict__ and __slots__ on the class)
    attrs = set()
    for obj in (state_before, state_after):
        # __dict__ attributes
        if hasattr(obj, "__dict__"):
            attrs.update(vars(obj).keys())
        # __slots__ attributes (check on the class)
        if hasattr(obj.__class__, "__slots__"):
            for slot in obj.__class__.__slots__:
                attrs.add(slot)

    if attrs:
        for attr in attrs:
            before_val = getattr(state_before, attr, None)
            after_val = getattr(state_after, attr, None)
            new_path = f"{path}.{attr}" if path else attr
            diff_states(before_val, after_val, new_path, changes)

    return changes


def print_state_changes(changes):
    """
    Print state changes in a clean format: key: before -> after
    """
    if not changes:
        return

    for change in changes:
        key = change['key']
        before = change['before']
        after = change['after']
        print(f"{key}: {before} -> {after}")



---

[9]. src/Ankimon/poke_engine/battle.py
Why this file is critical: Core logic file within the isolated battle engine handling combat turns and state evaluation.

import itertools
from collections import defaultdict
from collections import namedtuple
from copy import copy
from copy import deepcopy
from abc import ABC
from abc import abstractmethod

from . import constants
import logging

from . import data
from .data import all_move_json
from .data import pokedex
from .data.parse_smogon_stats import MOVES_STRING
from .data.parse_smogon_stats import SPREADS_STRING
from .data.parse_smogon_stats import ABILITY_STRING
from .data.parse_smogon_stats import ITEM_STRING
from .data.helpers import get_pokemon_sets
from .data.helpers import get_mega_pkmn_name
from .data.helpers import PASS_ITEMS
from .data.helpers import PASS_ABILITIES
from .data.helpers import get_all_likely_moves
from .data.helpers import get_most_likely_item
from .data.helpers import get_most_likely_ability
from .data.helpers import get_most_likely_spread
from .data.helpers import get_all_possible_moves_for_random_battle

from .objects import State
from .objects import Side
from .objects import Pokemon as TransposePokemon

from .helpers import remove_duplicate_spreads
from .helpers import get_pokemon_info_from_condition
from .helpers import set_makes_sense
from .helpers import normalize_name
from .helpers import calculate_stats


logger = logging.getLogger(__name__)


LastUsedMove = namedtuple('LastUsedMove', ['pokemon_name', 'move', 'turn'])
DamageDealt = namedtuple('DamageDealt', ['attacker', 'defender', 'move', 'percent_damage', 'crit'])
StatRange = namedtuple("Range", ["min", "max"])


# Based on the format, this dict controls which pokemon will be replaced during team preview
# Some pokemon's forms are not revealed in team preview
smart_team_preview = {
    "gen8ou": {
        "urshifu": "urshifurapidstrike"  # urshifu banned in gen8ou
    }
}


class Battle(ABC):

    def __init__(self, battle_tag):
        self.battle_tag = battle_tag
        self.user = Battler()
        self.opponent = Battler()
        self.weather = None
        self.field = None
        self.trick_room = False

        self.turn = False

        self.started = False
        self.rqid = None

        self.force_switch = False
        self.wait = False

        self.battle_type = None
        self.generation = None
        self.time_remaining = None

        self.request_json = None

    def initialize_team_preview(self, user_json, opponent_pokemon, battle_type):
        self.user.from_json(user_json, first_turn=True)
        self.user.reserve.insert(0, self.user.active)
        self.user.active = None

        for pkmn_string in opponent_pokemon:
            pokemon = Pokemon.from_switch_string(pkmn_string)

            if pokemon.name in smart_team_preview.get(battle_type, {}):
                new_pokemon_name = smart_team_preview[battle_type][pokemon.name]
                logger.info(
                    "Smart team preview: Replaced {} with {}".format(
                        pokemon.name,
                        new_pokemon_name
                    )
                )
                pokemon = Pokemon(new_pokemon_name, pokemon.level)

            self.opponent.reserve.append(pokemon)

        self.started = True
        self.rqid = user_json[constants.RQID]

    def during_team_preview(self):
        ...

    def start_non_team_preview_battle(self, user_json, opponent_switch_string):
        self.user.from_json(user_json, first_turn=True)

        pkmn_information = opponent_switch_string.split('|')[3]
        pkmn = Pokemon.from_switch_string(pkmn_information)
        self.opponent.active = pkmn

        self.started = True
        self.rqid = user_json[constants.RQID]

    def mega_evolve_possible(self):
        return (
                any(g in self.generation for g in constants.MEGA_EVOLVE_GENERATIONS)
        )

    def prepare_battles(self, guess_mega_evo_opponent=True, join_moves_together=False):
        """Returns a list of battles based on this one
        The battles have the opponent's reserve pokemon's unknowns filled in
        The opponent's active pokemon in each of the battles has a different set"""
        battle_copy = deepcopy(self)
        battle_copy.opponent.lock_moves()
        battle_copy.user.lock_active_pkmn_first_turn_moves()

        if battle_copy.user.active.can_mega_evo:
            # mega-evolving here gives the pkmn the random-battle spread (Serious + 85s)
            # unfortunately the correct spread is not stored anywhere as of this being written
            # this only happens on the turn the pkmn mega-evolves - the next turn will be fine
            battle_copy.user.active.forme_change(get_mega_pkmn_name(battle_copy.user.active.name))

        if guess_mega_evo_opponent and not battle_copy.opponent.mega_revealed() and self.mega_evolve_possible():
            check_in_sets = battle_copy.battle_type == constants.STANDARD_BATTLE
            battle_copy.opponent.active.try_convert_to_mega(check_in_sets=check_in_sets)

        # for reserve pokemon only guess their most likely item/ability/spread and guess all moves
        for pkmn in filter(lambda x: x.is_alive(), battle_copy.opponent.reserve):
            pkmn.guess_most_likely_attributes()

        try:
            pokemon_sets = get_pokemon_sets(battle_copy.opponent.active.name)
        except KeyError:
            logger.warning("No sets for {}, trying to find most likely attributes".format(battle_copy.opponent.active.name))
            battle_copy.opponent.active.guess_most_likely_attributes()
            return [battle_copy]

        possible_spreads = sorted(pokemon_sets[SPREADS_STRING], key=lambda x: x[2], reverse=True)
        possible_abilities = sorted(pokemon_sets[ABILITY_STRING], key=lambda x: x[1], reverse=True)
        possible_items = sorted(pokemon_sets[ITEM_STRING], key=lambda x: x[1], reverse=True)
        possible_moves = sorted(pokemon_sets[MOVES_STRING], key=lambda x: x[1], reverse=True)

        spreads = battle_copy.opponent.active.get_possible_spreads(possible_spreads)
        items = battle_copy.opponent.active.get_possible_items(possible_items)
        abilities = battle_copy.opponent.active.get_possible_abilities(possible_abilities)
        expected_moves, chance_moves = battle_copy.opponent.active.get_possible_moves(possible_moves, battle_copy.battle_type)

        if join_moves_together:
            chance_move_combinations = [chance_moves]
        else:
            number_of_unknown_moves = max(4 - len(battle_copy.opponent.active.moves) - len(expected_moves), 0)
            chance_move_combinations = list(itertools.combinations(chance_moves, number_of_unknown_moves))

        combinations = list(itertools.product(spreads, items, abilities, chance_move_combinations))

        # create battle clones for each of the combinations
        battles = list()
        for c in combinations:
            new_battle = deepcopy(battle_copy)

            all_moves = [m.name for m in new_battle.opponent.active.moves]
            all_moves += expected_moves
            all_moves += c[3]
            all_moves = [Move(m) for m in all_moves]

            if join_moves_together or set_makes_sense(c[0][0], c[0][1], c[1], c[2], all_moves):
                new_battle.opponent.active.set_spread(c[0][0], c[0][1])
                if new_battle.opponent.active.name == 'ditto':
                    new_battle.opponent.active.stats = battle_copy.opponent.active.stats
                new_battle.opponent.active.item = c[1]
                new_battle.opponent.active.ability = c[2]
                for m in expected_moves:
                    new_battle.opponent.active.add_move(m)
                for m in c[3]:
                    new_battle.opponent.active.add_move(m)

                logger.debug("Possible set for opponent's {}:\t{} {} {} {} {}".format(battle_copy.opponent.active.name, c[0][0], c[0][1], c[1], c[2], all_moves))
                battles.append(new_battle)

            new_battle.opponent.lock_moves()

        return battles if battles else [battle_copy]

    def create_state(self):
        user_active = TransposePokemon.from_state_pokemon_dict(self.user.active.to_dict())
        user_reserve = dict()
        for mon in self.user.reserve:
            user_reserve[mon.name] = TransposePokemon.from_state_pokemon_dict(mon.to_dict())

        opponent_active = TransposePokemon.from_state_pokemon_dict(self.opponent.active.to_dict())
        opponent_reserve = dict()
        for mon in self.opponent.reserve:
            opponent_reserve[mon.name] = TransposePokemon.from_state_pokemon_dict(mon.to_dict())

        user = Side(user_active, user_reserve, copy(self.user.wish), copy(self.user.side_conditions), copy(self.user.future_sight))
        opponent = Side(opponent_active, opponent_reserve, copy(self.opponent.wish), copy(self.opponent.side_conditions), copy(self.opponent.future_sight))

        state = State(user, opponent, self.weather, self.field, self.trick_room)
        return state

    def get_all_options(self):
        force_switch = self.force_switch or self.user.active.hp <= 0
        wait = self.wait or self.opponent.active.hp <= 0

        # double faint or team preview
        if force_switch and wait:
            user_options = self.user.get_switches() or [constants.DO_NOTHING_MOVE]

            # edge-case for uturn or voltswitch killing
            if (
                    self.user.last_used_move.move in constants.SWITCH_OUT_MOVES and
                    self.opponent.active.hp <= 0 and
                    self.user.last_used_move.turn == self.turn

            ):
                opponent_options = [constants.DO_NOTHING_MOVE]
            else:
                opponent_options = self.opponent.get_switches() or [constants.DO_NOTHING_MOVE]

            return user_options, opponent_options

        if force_switch:
            user_options = self.user.get_switches(reviving=self.user.active.reviving)

            # uturn or voltswitch
            if (
                    self.user.last_used_move.move in constants.SWITCH_OUT_MOVES and
                    self.opponent.last_used_move.turn != self.turn and
                    self.user.last_used_move.turn == self.turn
            ):
                opponent_options = [m.name for m in self.opponent.active.moves if not m.disabled] or [constants.DO_NOTHING_MOVE]
            else:
                opponent_options = [constants.DO_NOTHING_MOVE]
        elif wait:
            opponent_options = self.opponent.get_switches()
            user_options = [constants.DO_NOTHING_MOVE]
        else:
            user_forced_move = self.user.active.forced_move()
            if user_forced_move:
                user_options = [user_forced_move]
            else:
                user_options = [m.name for m in self.user.active.moves if not m.disabled]
                user_options += self.user.get_switches()

            opponent_forced_move = self.opponent.active.forced_move()
            if opponent_forced_move:
                opponent_options = [opponent_forced_move]
            else:
                opponent_options = [m.name for m in self.opponent.active.moves if not m.disabled] or [constants.DO_NOTHING_MOVE]
                opponent_options += self.opponent.get_switches()

        return user_options, opponent_options

    @abstractmethod
    def find_best_move(self):
        ...


class Battler:

    def __init__(self):
        self.active = None
        self.reserve = []
        self.side_conditions = defaultdict(lambda: 0)

        self.name = None
        self.trapped = False
        self.wish = (0, 0)
        self.future_sight = (0, 0)

        self.account_name = None

        self.last_used_move = LastUsedMove('', '', 0)

    def mega_revealed(self):
        return self.active.is_mega or any(p.is_mega for p in self.reserve)

    def lock_active_pkmn_first_turn_moves(self):
        # disable firstimpression and fakeout if the last_used_move was not a switch
        if self.last_used_move.pokemon_name == self.active.name:
            for m in self.active.moves:
                if m.name in constants.FIRST_TURN_MOVES:
                    m.disabled = True

    def lock_active_pkmn_status_moves_if_active_has_assaultvest(self):
        if self.active.item == 'assaultvest':
            for m in self.active.moves:
                if all_move_json[m.name][constants.CATEGORY] == constants.STATUS:
                    m.disabled = True

    def choice_lock_moves(self):
        # if the active pokemon has a choice item and their last used move was by this pokemon -> lock their other moves
        if self.active.item in constants.CHOICE_ITEMS and self.last_used_move.pokemon_name == self.active.name:
            for m in self.active.moves:
                if m.name != self.last_used_move.move:
                    m.disabled = True

    def taunt_lock_moves(self):
        if constants.TAUNT in self.active.volatile_statuses:
            for m in self.active.moves:
                if all_move_json[m.name][constants.CATEGORY] == constants.STATUS:
                    m.disabled = True

    def lock_moves(self):
        self.choice_lock_moves()
        self.lock_active_pkmn_status_moves_if_active_has_assaultvest()
        self.lock_active_pkmn_first_turn_moves()
        self.taunt_lock_moves()

    def from_json(self, user_json, first_turn=False):

        # user_json does not track boosts or volatile statuses
        # they must be taken from the current battle
        if first_turn:
            existing_conditions = (None, None, None)
        else:
            existing_conditions = (
                self.active.name,
                self.active.boosts,
                self.active.volatile_statuses,
                self.active.terastallized,
                self.active.types
            )

        try:
            trapped = user_json[constants.ACTIVE][0].get(constants.TRAPPED, False)
            maybe_trapped = user_json[constants.ACTIVE][0].get(constants.MAYBE_TRAPPED, False)
            self.trapped = trapped or maybe_trapped
        except KeyError:
            self.trapped = False

        self.name = user_json[constants.SIDE][constants.ID]
        self.reserve.clear()
        for index, pkmn_dict in enumerate(user_json[constants.SIDE][constants.POKEMON]):

            nickname = pkmn_dict[constants.IDENT]
            pkmn = Pokemon.from_switch_string(pkmn_dict[constants.DETAILS], nickname=nickname)
            pkmn.ability = pkmn_dict[constants.REQUEST_DICT_ABILITY]
            pkmn.index = index + 1
            pkmn.reviving = pkmn_dict.get(constants.REVIVING, False)
            pkmn.hp, pkmn.max_hp, pkmn.status = get_pokemon_info_from_condition(pkmn_dict[constants.CONDITION])
            for stat, number in pkmn_dict[constants.STATS].items():
                pkmn.stats[constants.STAT_ABBREVIATION_LOOKUPS[stat]] = number

            pkmn.item = pkmn_dict[constants.ITEM] if pkmn_dict[constants.ITEM] else None

            if pkmn_dict[constants.ACTIVE]:
                self.active = pkmn
                if existing_conditions[0] == pkmn.name:
                    pkmn.boosts = existing_conditions[1]
                    pkmn.volatile_statuses = existing_conditions[2]
                    if existing_conditions[3]:
                        pkmn.terastallized = True
                        pkmn.types = existing_conditions[4]
            else:
                self.reserve.append(pkmn)

            for move_name in pkmn_dict[constants.MOVES]:
                pkmn.add_move(move_name)

        # if there is no active pokemon, we do not want to look through it's moves
        if constants.ACTIVE not in user_json:
            return

        try:
            self.active.can_mega_evo = user_json[constants.ACTIVE][0][constants.CAN_MEGA_EVO]
        except KeyError:
            self.active.can_mega_evo = False

        try:
            self.active.can_ultra_burst = user_json[constants.ACTIVE][0][constants.CAN_ULTRA_BURST]
        except KeyError:
            self.active.can_ultra_burst = False

        try:
            self.active.can_dynamax = user_json[constants.ACTIVE][0][constants.CAN_DYNAMAX]
        except KeyError:
            self.active.can_dynamax = False

        try:
            self.active.can_terastallize = user_json[constants.ACTIVE][0][constants.CAN_TERASTALLIZE]
        except KeyError:
            self.active.can_terastallize = False

        # clear the active moves so they can be reset by the options available
        self.active.moves.clear()

        # update the active pokemon's moves to show disabled status/pp remaining
        # this assumes that there is only one active pokemon (single-battle)
        for index, move in enumerate(user_json[constants.ACTIVE][0][constants.MOVES]):
            # hidden power's ID is always 'hiddenpower' regardless of the type
            # the type needs to be parsed separately from the 'move' attribute
            if move[constants.ID] == constants.HIDDEN_POWER:
                self.active.add_move('{}{}'.format(
                        constants.HIDDEN_POWER,
                        move['move'].split()[constants.HIDDEN_POWER_TYPE_STRING_INDEX].lower()
                    )
                )
            else:
                self.active.add_move(move[constants.ID])
            self.active.moves[-1].disabled = move.get(constants.DISABLED, False)
            self.active.moves[-1].current_pp = move.get(constants.PP, 1)

            try:
                self.active.moves[index].can_z = user_json[constants.ACTIVE][0][constants.CAN_Z_MOVE][index]
            except KeyError:
                pass

    def get_switches(self, reviving=False):
        if self.trapped:
            return []

        switches = []
        if reviving:
            it = filter(lambda p: p.hp <= 0, self.reserve)
        else:
            it = filter(lambda p: p.hp > 0, self.reserve)

        for pkmn in it:
            switches.append("{} {}".format(constants.SWITCH_STRING, pkmn.name))
        return switches

    def to_dict(self):
        return {
            constants.TRAPPED: self.trapped,
            constants.ACTIVE: self.active.to_dict(),
            constants.RESERVE: [p.to_dict() for p in self.reserve],
            constants.WISH: copy(self.wish),
            constants.FUTURE_SIGHT: copy(self.future_sight),
            constants.SIDE_CONDITIONS: copy(self.side_conditions)
        }


class Pokemon:

    def __init__(self, name: str, level: int, nature="serious", evs=(85,) * 6):
        self.name = normalize_name(name)
        self.nickname = None
        self.base_name = self.name
        self.level = level
        self.nature = nature
        self.evs = evs
        self.speed_range = StatRange(min=0, max=float("inf"))

        try:
            self.base_stats = pokedex[self.name][constants.BASESTATS]
        except KeyError:
            logger.info("Could not pokedex entry for {}".format(self.name))
            self.name = [k for k in pokedex if self.name.startswith(k)][0]
            logger.info("Using {} instead".format(self.name))
            self.base_stats = pokedex[self.name][constants.BASESTATS]

        self.stats = calculate_stats(self.base_stats, self.level, nature=nature, evs=evs)

        self.max_hp = self.stats.pop(constants.HITPOINTS)
        self.hp = self.max_hp
        if self.name == 'shedinja':
            self.max_hp = 1
            self.hp = 1

        self.ability = None
        self.types = pokedex[self.name][constants.TYPES]
        self.item = constants.UNKNOWN_ITEM

        self.terastallized = False
        self.fainted = False
        self.reviving = False
        self.moves = []
        self.status = None
        self.volatile_statuses = []
        self.boosts = defaultdict(lambda: 0)
        self.can_mega_evo = False
        self.can_ultra_burst = False
        self.can_dynamax = False
        self.is_mega = False
        self.can_have_assaultvest = True
        self.can_have_choice_item = True
        self.can_not_have_band = False
        self.can_not_have_specs = False
        self.can_have_life_orb = True
        self.can_have_heavydutyboots = True

    def forme_change(self, new_pkmn_name):
        hp_percent = float(self.hp) / self.max_hp
        moves = self.moves
        boosts = self.boosts
        status = self.status

        self.__init__(new_pkmn_name, self.level)
        self.hp = round(hp_percent * self.max_hp)
        self.moves = moves
        self.boosts = boosts
        self.status = status

    def try_convert_to_mega(self, check_in_sets=False):
        if self.item != constants.UNKNOWN_ITEM:
            return
        mega_pkmn_name = get_mega_pkmn_name(self.name)
        in_sets_data = mega_pkmn_name in data.pokemon_sets

        if (mega_pkmn_name and check_in_sets and in_sets_data) or (mega_pkmn_name and not check_in_sets):
            logger.debug("Guessing mega-evolution: {}".format(mega_pkmn_name))
            self.forme_change(mega_pkmn_name)

    def is_alive(self):
        return self.hp > 0

    @classmethod
    def extract_nickname_from_pokemonshowdown_string(cls, ps_string):
        return "".join(ps_string.split(":")[1:]).strip()

    @classmethod
    def from_switch_string(cls, switch_string, nickname=None):
        if nickname is not None:
            nickname = cls.extract_nickname_from_pokemonshowdown_string(nickname)

        details = switch_string.split(',')
        name = details[0]
        try:
            level = int(details[1].replace('L', '').strip())
        except (IndexError, ValueError):
            level = 100
        pkmn = Pokemon(name, level)
        pkmn.nickname = nickname
        return pkmn

    def set_spread(self, nature, evs):
        if isinstance(evs, str):
            evs = [int(e) for e in evs.split(',')]
        hp_percent = self.hp / self.max_hp
        self.stats = calculate_stats(self.base_stats, self.level, evs=evs, nature=nature)
        self.nature = nature
        self.evs = evs
        self.max_hp = self.stats.pop(constants.HITPOINTS)
        self.hp = round(self.max_hp * hp_percent)

    def add_move(self, move_name: str):
        try:
            new_move = Move(move_name)
            self.moves.append(new_move)
            return new_move
        except KeyError:
            logger.warning("{} is not a known move".format(move_name))
            return None

    def get_move(self, move_name: str):
        for m in self.moves:
            if m.name == normalize_name(move_name):
                return m
        return None

    def set_likely_moves_unless_revealed(self):
        if len(self.moves) == 4:
            return
        additional_moves = get_all_likely_moves(self.name, [m.name for m in self.moves])
        for m in additional_moves:
            self.moves.append(Move(m))

    def set_most_likely_ability_unless_revealed(self):
        if self.ability is not None:
            return
        ability = get_most_likely_ability(self.name)
        self.ability = ability

    def set_most_likely_item_unless_revealed(self):
        if self.item != constants.UNKNOWN_ITEM:
            return
        item = get_most_likely_item(self.name)
        self.item = item

    def set_most_likely_spread(self):
        nature, evs, _ = get_most_likely_spread(self.name)
        self.set_spread(nature, evs)

    def guess_most_likely_attributes(self):
        self.set_most_likely_ability_unless_revealed()
        self.set_most_likely_item_unless_revealed()
        self.set_likely_moves_unless_revealed()
        self.set_most_likely_spread()

    def get_possible_spreads(self, spreads):
        # update this once you can use previous attacks to rule out spreads
        cumulative_percentage = 0
        possible_spreads = []
        for s in spreads:
            cumulative_percentage += s[2]
            possible_spreads.append(s[:2])
            if s[2] < 20 or cumulative_percentage >= 80:
                break

        return remove_duplicate_spreads(possible_spreads)

    def get_possible_items(self, items):
        # a bunch of flags could be set by the logic in the `battle_modifier` module
        # these flags being set render some items not possible
        # for example, if a pkmn uses 2 different moves without switching, then 'can_have_choice_item' will be False
        # this will omit choice items when guessing an item

        if self.item == constants.UNKNOWN_ITEM:
            cumulative_percentage = 0
            possible_items = []
            for i in items:
                if i[1] < 10 or cumulative_percentage >= 80:
                    return possible_items if possible_items else [constants.UNKNOWN_ITEM]
                elif i[0] in constants.CHOICE_ITEMS and not self.can_have_choice_item:
                    pass
                elif i[0] == 'lifeorb' and not self.can_have_life_orb:
                    pass
                elif i[0] == 'assaultvest' and not self.can_have_assaultvest:
                    pass
                elif i[0] == 'heavydutyboots' and not self.can_have_heavydutyboots:
                    pass
                elif i[0] == 'choiceband' and self.can_not_have_band:
                    pass
                elif i[0] == 'choicespecs' and self.can_not_have_specs:
                    pass
                elif i[0] not in PASS_ITEMS:
                    possible_items.append(i[0])

                cumulative_percentage += i[1]

            return possible_items if possible_items else [constants.UNKNOWN_ITEM]

        else:
            return [self.item]

    def get_possible_abilities(self, abilities):
        if self.ability is None:
            cumulative_percentage = 0
            possible_abilities = []
            for i in abilities:
                if i[1] < 10 or cumulative_percentage >= 80:
                    return possible_abilities if possible_abilities else [None]
                elif i[0] not in PASS_ABILITIES:
                    possible_abilities.append(i[0])

                cumulative_percentage += i[1]

            return possible_abilities if possible_abilities else [None]
        else:
            return [self.ability]

    def get_possible_moves(self, moves, battle_type=constants.STANDARD_BATTLE):
        if battle_type == constants.RANDOM_BATTLE:
            if len(self.moves) == 4:
                return [], []
            known_move_names = [m.name for m in self.moves]
            return [], get_all_possible_moves_for_random_battle(self.name, known_move_names)

        moves_remaining = 4 - len(self.moves)
        expected_moves = list()
        chance_moves = list()

        for m in moves:
            if moves_remaining <= 0:
                break
            elif m[1] > 60 and self.get_move(m[0]) is None:
                expected_moves.append(m[0])
                moves_remaining -= 1
            elif m[1] > 20 and self.get_move(m[0]) is None:
                chance_moves.append(m[0])

        return expected_moves, chance_moves

    def forced_move(self):
        if "phantomforce" in self.volatile_statuses:
            return "phantomforce"
        elif "shadowforce" in self.volatile_statuses:
            return "shadowforce"
        elif "dive" in self.volatile_statuses:
            return "dive"
        elif "dig" in self.volatile_statuses:
            return "dig"
        elif "bounce" in self.volatile_statuses:
            return "bounce"
        elif "fly" in self.volatile_statuses:
            return "fly"
        else:
            return None

    def to_dict(self):
        return {
            constants.FAINTED: self.fainted,
            constants.ID: self.name,
            constants.LEVEL: self.level,
            constants.TYPES: self.types,
            constants.HITPOINTS: self.hp,
            constants.MAXHP: self.max_hp,
            constants.ABILITY: self.ability,
            constants.ITEM: self.item,
            constants.BASESTATS: self.base_stats,
            constants.STATS: self.stats,
            constants.NATURE: self.nature,
            constants.EVS: self.evs,
            constants.BOOSTS: self.boosts,
            constants.STATUS: self.status,
            constants.TERASTALLIZED: self.terastallized,
            constants.VOLATILE_STATUS: set(self.volatile_statuses),
            constants.MOVES: [m.to_dict() for m in self.moves]
        }

    @classmethod
    def get_dummy(cls):
        p = Pokemon('pikachu', 100)
        p.hp = 0
        p.name = ''
        p.ability = None
        p.fainted = True
        return p

    def __eq__(self, other):
        return self.name == other.name and self.level == other.level

    def __repr__(self):
        return "{}, level {}".format(self.name, self.level)


class Move:
    def __init__(self, name):
        name = normalize_name(name)
        if constants.HIDDEN_POWER in name and not name.endswith(constants.HIDDEN_POWER_ACTIVE_MOVE_BASE_DAMAGE_STRING):
            name = "{}{}".format(name, constants.HIDDEN_POWER_ACTIVE_MOVE_BASE_DAMAGE_STRING)
        move_json = all_move_json[name]
        self.name = name
        self.max_pp = int(move_json.get(constants.PP) * 1.6)

        self.disabled = False
        self.can_z = False
        self.current_pp = self.max_pp

    def to_dict(self):
        return {
            "id": self.name,
            "disabled": self.disabled,
            "current_pp": self.current_pp
        }

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return "{}".format(self.name)


---

[10]. src/Ankimon/reviewer_ui.py
Why this file is critical: Sets up the reviewer UI shortcuts and modifies Anki's bottom HTML to inject Ankimon features.

from anki.hooks import wrap
from aqt.reviewer import Reviewer
from aqt.utils import downArrow, tooltip, tr

from .singletons import (
    enemy_pokemon,
    main_pokemon,
    ankimon_tracker_obj,
    test_window,
    evo_window,
    logger,
    achievements,
    trainer_card,
    reviewer_obj,
)
from .functions.encounter_functions import (
    catch_pokemon,
    kill_pokemon,
    new_pokemon,
)
from .texts import _bottomHTML_template, button_style

_collected_pokemon_ids = set()


def set_collected_ids(ids):
    global _collected_pokemon_ids
    _collected_pokemon_ids = ids


def catch_shortcut_function():
    if enemy_pokemon.hp < 1:
        catch_pokemon(
            enemy_pokemon,
            ankimon_tracker_obj,
            logger,
            "",
            _collected_pokemon_ids,
            achievements,
        )
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)
    else:
        tooltip("You only catch a pokemon once it's fainted!")


def defeat_shortcut_function():
    if enemy_pokemon.hp < 1:
        kill_pokemon(
            main_pokemon, enemy_pokemon, evo_window, logger, achievements, trainer_card
        )
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)
    else:
        tooltip("Wild pokemon has to be fainted to defeat it!")


def setup_reviewer_ui(catch_shortcut: str, defeat_shortcut: str, reviewer_buttons: bool):
    catch_key = str(catch_shortcut).lower()
    defeat_key = str(defeat_shortcut).lower()

    def _shortcutKeys_wrap(self, _old):
        original = _old(self)
        original.append((catch_key, lambda: catch_shortcut_function()))
        original.append((defeat_key, lambda: defeat_shortcut_function()))
        return original

    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, _shortcutKeys_wrap, "around")

    if reviewer_buttons is True:
        Review_linkHandler_Original = Reviewer._linkHandler

        def linkHandler_wrap(reviewer, url):
            if url == "catch":
                catch_shortcut_function()
            elif url == "defeat":
                defeat_shortcut_function()
            else:
                Review_linkHandler_Original(reviewer, url)

        def _bottomHTML(self) -> str:
            return _bottomHTML_template % dict(
                edit=tr.studying_edit(),
                editkey=tr.actions_shortcut_key(val="E"),
                more=tr.studying_more(),
                morekey=tr.actions_shortcut_key(val="M"),
                downArrow=downArrow(),
                time=self.card.time_taken() // 1000,
                CatchKey=tr.actions_shortcut_key(val=f"{catch_key}"),
                DefeatKey=tr.actions_shortcut_key(val=f"{defeat_key}"),
            )

        Reviewer._bottomHTML = _bottomHTML
        Reviewer._linkHandler = linkHandler_wrap


---

[11]. src/Ankimon/functions/reviewer_iframe.py
Why this file is critical: Generates the HTML/CSS payload needed to display the battle HUD within Anki's reviewer.

import os
import fnmatch

def list_audio_files(folder_path):
    # Define common audio file extensions
    audio_extensions = ['*.mp3', '*.wav', '*.flac', '*.aac', '*.ogg', '*.wma', '*.m4a', '*.aiff']

    # List to store audio files
    audio_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(folder_path):
        for extension in audio_extensions:
            for filename in fnmatch.filter(files, extension):
                audio_files.append(filename)

    return audio_files

from aqt import mw
from .pokemon_functions import find_experience_for_level

def create_html_code(genderTop, genderBottom, nameTop, nameBottom, levelTop, levelBottom, current_health_bottom, max_hp_bottom, max_hp_top, current_health_top, text, general_url, font_url, bottom_pokemon_sprite, top_pokemon_sprite, display, main_attack, enemy_attack, xp_bar_width = 0):
    html_code = """<div id="spacer">&nbsp;</div>"""
    html_code += """<div id="AnkimonWindow"></div>"""
    html_code += f"""<iframe id="myIframe" class="Ankimon" src='{general_url}index.html?bottomPokemonSprite={bottom_pokemon_sprite}&topPokemonSprite={top_pokemon_sprite}&text={text}&levelTop={levelTop}&levelBottom={levelBottom}&nameTop={nameTop}&nameBottom={nameBottom}&genderTop={genderTop}&genderBottom={genderBottom}&current_health_bottom={current_health_bottom}&max_hp_bottom={max_hp_bottom}&max_hp_top={max_hp_top}&fontUrl={font_url}&current_health_top={current_health_top}&main_attack={main_attack}&enemy_attack={enemy_attack}' width=100% style="display:{display};"></iframe>"""
    return html_code

def create_iframe_html(main_pokemon, enemy_pokemon, settings_obj, textmsg):
    text = str(textmsg)
    text = text.replace("'", "")
    nameBottom = main_pokemon.nickname if main_pokemon.nickname else main_pokemon.name
    nameTop = enemy_pokemon.name
    current_health_top = enemy_pokemon.hp
    current_health_bottom = main_pokemon.hp
    levelTop = enemy_pokemon.level
    levelBottom = main_pokemon.level
    genderTop = enemy_pokemon.gender
    genderBottom = main_pokemon.gender
    max_hp_bottom = main_pokemon.max_hp
    max_hp_top = enemy_pokemon.max_hp
    display = "block" #fallback
    mainpokemon_attack = False
    enemypokemon_attack = False
    experience_for_next_lvl = int(find_experience_for_level(f"{main_pokemon.growth_rate}", int(main_pokemon.level), settings_obj))
    xp_bar_width = int((int(main_pokemon.xp or 0) / experience_for_next_lvl) * 100)
    ankimon_package = mw.addonManager.addonFromModule(__name__)
    general_url = f"""/_addons/{ankimon_package}/user_files/web/"""
    sprites_url = f"""/_addons/{ankimon_package}/user_files/sprites/"""
    if settings_obj.get("gui.reviewer_image_gif") == False:
        top_pokemon_sprite = f"""{sprites_url}front_default/{enemy_pokemon.id}.png"""
        bottom_pokemon_sprite = f"""{sprites_url}back_default/{main_pokemon.id}.png"""
    else:
        top_pokemon_sprite = f"""{sprites_url}front_default_gif/{enemy_pokemon.id}.gif"""
        bottom_pokemon_sprite = f"""{sprites_url}back_default_gif/{main_pokemon.id}.gif"""
    font_url = f"""/_addons/{ankimon_package}/web/assetts/PokemonGB.ttf"""
    html_code = create_html_code(genderTop, genderBottom, nameTop, nameBottom, levelTop, levelBottom, current_health_bottom, max_hp_bottom, max_hp_top, current_health_top, text, general_url, font_url, bottom_pokemon_sprite, top_pokemon_sprite, display, mainpokemon_attack, enemypokemon_attack, xp_bar_width)
    return html_code

def prepare(html, content, context):
    html_code = create_iframe_html(main_pokemon, enemy_pokemon, settings_obj, textmsg="")
    return html + html_code

def create_head_code(generalurl):
    css_code = f"""
	:root {{
        --background_music: "{generalurl}/"
	}}

	@keyframes attack {{
    0% {{ transform: translate(0px, 0px); }}
    50% {{ transform: translate(300px, -10px); width: 60%; height: 70%}}
    100% {{ transform: translate(0px, 0px); }}
	}}

    @font-face {{
        font-family: 'Pokemon';
        src: url("{generalurl}Early_GameBoy.ttf");
    }}

    #bottomPokemon {{
        width: 50%  ;
        height: 70%  ;
        background-image: url("{generalurl}/images/1.gif");
        background-size: contain  ;
        background-repeat: no-repeat  ;
        margin: auto  ;
        display: block  ;
        float: left  ;
        z-index: 3  ;
        position: absolute;
        top: 40%  ;
        left: 25%  ;
    }}

    #topPoke {{
        width: 50%  ;
        height: 70%  ;
        background-image: url("{generalurl}images/4.gif")  ;
        background-size: contain  ;
        margin: auto  ;
        display: block  ;
        background-repeat: no-repeat  ;
        float: right  ;
        position: relative  ;
        left: -5%  ;
        top: 10%  ;
    }}

    .innerRectangleBit {{
	width: 75%  ;
	height: 20%  ;
	position: relative  ;
	background-color: rgb(171,154,84)  ;
	top: 75%  ;
	display:inline-block  ;
	background-image: url("/_addons/1908235722/web/images/1.gif")  ;
    background-repeat: repeat-x  ;
    background-size: contain  ;
    }}

    .ovalOutterTop {{
	z-index: 1 ;
	position: absolute ;
    right: 2%;
	top: 35% ;
    width: 40% !important;
	max-width: 300px ;
	height: 20px ;
	background: rgb(200,200,176) ;
	border-radius: 50% / 50% ;
    }}

    .ovalOutterBottom {{
	z-index: 1 ;
	position: absolute ;
	bottom: 3% ;
    left: 2% ;
    width: 40% !important;
	max-width: 300px ;
	height: 20px ;
	background: rgb(200,200,176) ;
	border-radius: 50% / 50% ;
    }}

    #AnkimonContainer {{
    position: absolute;
	height: 100% ;
    width: 100%;
	background-color: rgb(223,225,218) ;
	overflow: hidden ;
	font-family: pokemon ;
	max-width: 800px ;
	max-height: 900px ;
    min-height: 300px;
	margin: auto ;
    }}

#top {{
	background-color: rgb(223,225,218) ;
	height: 70% ;
	width:100% ;
}}

#bottom {{
	background-color: rgb(64,64,80) ;
	height: 30% ;
	width:100% ;
	z-index: 3 ;
}}

#bottomBox {{
	height: 90% ;
	background-color: rgb(207,81,50) ;
	border-radius: 20px ;
	width:99% ;
	position:relative ;
	top: 5% ;
	left:0.5% ;
	z-index: 4 ;
}}

#bottomBoxInner {{
	height: 90% ;
	background-color: rgb(88,144,152) ;
	border-radius: 20px ;
	width:95% ;
	position:relative ;
	top: 5% ;
	left:2.5% ;
	z-index: 5 ;
}}

.topHalf {{
	height: 50% ;
	width: 100% ;

}}

.ovalInner {{
	z-index:2 ;
	width: 90% ;
	height: 80% ;
	background: rgb(176,176,144) ;
	border-radius: 50% / 50% ;
	position: relative ;
	transform: translateY(-180%) ;
	left: 5% ;
}}

.rectangleOutter {{
	z-index: 3 ;
	width: 85% ;
	height: 85% ;
	background: rgb(31,31,39) ;
	margin-left: 10% ;
	border-bottom-right-radius: 20px ;
	border-top-left-radius: 20px ;
	border-top-right-radius: 10px ;
	border-bottom-left-radius: 10px ;
}}

.rectangleInner {{
	z-index: 4 ;
	width: 95% ;
	height: 90% ;
	background: rgb(240,240,208) ;
	position: relative ;
	top: -55% ;
	left: 2.5% ;
	border-bottom-right-radius: 20px ;
	border-top-left-radius: 20px ;
	border-top-right-radius: 10px ;
	border-bottom-left-radius: 10px ;
}}

#healthContainer {{
	width: 30% ;
	height: 150px ;
	z-index:2 ;
	position: relative ;
	top: 45% ;
}}

.hpContent {{
	width:90% ;
	height: 90% ;
	position: relative ;
	top: 10% ;
	left: 5% ;
	list-style: none ;
}}

#UpperHealthContainer {{
    width: 60%;
    height: 60px;
	z-index:2 !important;
    position: absolute !important;
	top: -5% !important;
	left: 5% !important;
}}

.UpperHpContent {{
	width:90% ;
	height: 90% ;
	position: relative ;
	top: 5% ;
	left: 5% ;
	list-style: none ;
}}

.hpList {{
	width:100% ;
	height:33% ;
}}


.UpperHpList {{
	width:100% ;
	height:50% ;
}}

.left {{
	float:left ;
	width:50% ;
	height: 100% ;
	overflow: hidden ;
}}

.right {{
	margin-left: 50% ;
	width:50% ;
	height: 100% ;
}}

#theTop {{
	float:right ;
	z-index: 0 ;
}}



.triangleBit {{
	z-index: -1 ;
	width:10% ;
	height: 40% ;
	left: 0px ;
	position: relative ;
	top: -25% ;
	float: left ;
	background: linear-gradient(to right bottom, transparent 50%, rgb(64,64,80) 50%) ;
}}

.exp {{
	width: 15% ;
	float: left ;
	position: relative ;
	top: 77% ;
	text-align: center ;
	display:inline-block ;
	color: rgb(240,208,0) ;
	font-size: xx-small ;
}}

.rectangleBit {{
	z-index: -1 ;
	width: 90% ;
	height: 50% ;
	float:right ;
	top:-35% ;
	position: relative ;
	background-color: rgb(64,64,80) ;
	border-bottom-right-radius: 20px ;
}}

#nameTop {{
	float: left ;
	font-size: 2.5vh ;
	font-weight: bold ;
    top: -140%;
    left: 0%;
    position: absolute;
    color: black !important;
}}

#nameBottom {{
	float: left ;
	font-size: 2.5vh ;
	font-weight: bold ;
	transform: translateY(10%) ;
}}

#hp {{
	color: rgb(230, 121, 89) ;
	float:left ;
	width: 20% ;
	position: relative ;
	left: 2% ;
	top: 15% ;
	font-size: 2vh ;
}}

#rhombus {{
	position: relative ;
    width: 80% ;
    height: 40% ;
    -o-transform: skew(45deg) ;
    background-color: rgb(64,64,80) ;
    margin-left: 5% ;
    top: -25% ;
    z-index: -1 ;
}}

#level {{
	float: right ;
	text-align: right ;
	font-weight: bold ;
	transform: translateY(30%) ;
	font-size: 2.5vh ;
}}

#health  {{
	float: right ;
	text-align: right ;
	font-size: 2.5vh ;
}}

#genderm  {{
	color: rgb(0,162,232) ;
	font-size: 1em ;
}}

#genderf  {{
	color: rgb(255,174,201) ;
	font-size: 1em ;
}}

#hpBar {{
	float: right ;
	width:80% ;
	height:70% ;
	background-color: rgb(64,64,80) ;
	border-radius: 500px ;
}}

#hpBarInner {{
	width:85% ;
	height:70% ;
	background-color: rgb(255,255,255) ;
	border-radius: 500px ;
	position: relative ;
	top: 16% ;
	left: 13% ;
}}

#hpSlider {{
	width:100% ;
	height:100% ;
	background-color: rgb(110,218,163) ;
	border-radius: 500px ;
	position: relative ;
	top: 0% ;
	left: 0% ;
}}

#healthTop {{
	margin-left: 0% ;
}}

#battleText {{
	height: 100% ;
	width: 100% ;
	text-align: center ;
	display: table ;
	float: left ;
	font-size: 1.5rem ;
	text-shadow: 2px 2px 0px #43547A ;
	font-family: Pokemon ;
	color: #ECEEED ;
}}

#battleText p{{
	display: table-cell ;
    vertical-align: middle ;
}}

#menuText {{

	display: inline-block ;
	height: 100% ;
	width: 38% ;
	background-color: white ;

}}

.menuRow {{
	height:45% ;
	width: 100% ;
}}

.menuHalf {{
	width: 45% ;
	font-size: 3.5vw ;
	padding: 2% ;
	border: 2px solid transparent ;
}}


.theFocus {{
    border-radius: 5px ;
    border: 2px solid rgb(207,81,50) ;
    padding: 2% ;
}}


.clearBoth {{
	clear:both ;
}}
    """
    return css_code

---

[12]. src/Ankimon/pyobj/ankimon_tracker.py
Why this file is critical: Tracks session statistics, multipliers, streaks, and flashcard review counts.

from PyQt6.QtCore import QTimer
from .pokemon_obj import PokemonObject
from datetime import datetime
from .error_handler import show_warning_with_traceback
from ..functions.pokedex_functions import extract_ids_from_file
from ..utils import random_battle_scene
from aqt import mw
import re


class AnkimonTracker:
    def __init__(self, trainer_card):
        # Object bindings
        self.trainer_card = trainer_card

        # Card reviews
        self.card_ratings_count = {"again": 0, "hard": 0, "good": 0, "easy": 0}
        self.total_reviews = 0

        self.current_mode = "idle"

        # Session and card timers
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_session_timer)
        self.card_timer = QTimer()
        self.card_timer.timeout.connect(self.update_card_timer)
        self.cards_battle_round = 0

        # Time tracking
        self.session_time_elapsed = 0
        self.card_time_elapsed = 0
        self.session_time = 0

        # Tracking for multiplier
        self.multiplier = 1
        self.multiplier_card_ratings_count = {
            "again": 0,
            "hard": 0,
            "good": 0,
            "easy": 0,
        }
        self.cards_until_calc_multiplier = 2

        self.card_streak = 0  # Streak for follow up right cards

        self.streak_days = []  # List to track [date, streak]
        self.check_streak()

        self.main_pokemon = None
        self.enemy_pokemon = None

        self.pokemon_stats = {}

        # Track Pokemon Battle Cards
        self.cry_counter = 0
        self.attack_counter = 0
        self.slp_counter = 0

        # battlescene
        self.randomize_battle_scene()

        # Check if Pokemon is already caught
        self.owned_pokemon_ids = extract_ids_from_file()
        self.pokemon_in_collection = False

        self.pokemon_encounter = 0  # mode for pokemon encounter
        self.general_card_count_for_battle = (
            0  # count for general card count for battle
        )
        self.caught = 0  # check if pokemon is caught

        # Start the session timer when the object is initialized
        self.start_session_timer()

    def get_total_reviews(self):
        if mw.col is None:
            return 0
        match = re.search(r'Studied\s+[^\d]*(\d+)(?=[^\n]*card)', mw.col.studied_today())
        if match is None:
            # Empty-study session or localized Anki whose "Studied N cards"
            # text doesn't match the English regex.
            return 0
        return int(match.group(1))

    def set_main_pokemon(self, pokemon):
        """Set the main Pokémon being used."""
        if isinstance(pokemon, PokemonObject):
            self.main_pokemon = pokemon

    def set_enemy_pokemon(self, pokemon):
        """Set the enemy Pokémon being fought against."""
        if isinstance(pokemon, PokemonObject):
            self.enemy_pokemon = pokemon

    def check_streak(self):
        """Check and update streak_days based on today's date."""
        today = datetime.today().date()

        if not self.streak_days:
            # Initialize streak if it doesn't exist
            self.streak_days = [[today, 1]]
            return

        # Retrieve the last recorded date and streak count
        last_date, current_streak = self.streak_days[0]

        if last_date == today:
            # No need to update if today is already recorded
            return

        # Calculate the difference in days between today and the last recorded date
        days_difference = (today - last_date).days

        if days_difference == 1:
            # If it's exactly 1 day ago, increase the streak
            self.streak_days[0] = [today, current_streak + 1]
        elif days_difference > 1:
            # If it's more than 1 day, reset the streak
            self.streak_days[0] = [today, 1]

    def get_main_pokemon_stats(self):
        """Retrieve the stats of the main Pokémon."""
        if self.main_pokemon:
            return self.main_pokemon.get_stats()
        return None

    def get_enemy_pokemon_stats(self):
        """Retrieve the stats of the enemy Pokémon."""
        if self.enemy_pokemon:
            return self.enemy_pokemon.get_stats()
        return None

    def add_pokemon(self, pokemon):
        """Add a PokemonObject to the tracker."""
        if isinstance(pokemon, PokemonObject):
            self.pokemon_stats[pokemon.id] = pokemon.get_stats()

    def update_pokemon_stats(self, pokemon):
        """Update stats of a given PokemonObject in the tracker."""
        if pokemon.id in self.pokemon_stats:
            self.pokemon_stats[pokemon.id] = pokemon.get_stats()

    def get_pokemon_stats(self, pokemon_id):
        """Retrieve stats of a specific Pokémon by its ID."""
        return self.pokemon_stats.get(pokemon_id)

    def review(self, grade):
        """Track review statistics based on the grade."""

        if grade == "again":
            # Reset streak
            self.card_streak = 0
        elif grade in ["good", "hard", "easy"]:
            # Increment streak
            self.card_streak += 1
        else:
            raise ValueError("Invalid grade type")
        self.card_ratings_count[grade] += 1
        self.multiplier_card_ratings_count[grade] += 1

        # Stop the card timer after answering
        self.reset_card_timer()

        self.cards_until_calc_multiplier -= 1
        # After 2 cards - calculate multiplier
        if self.cards_until_calc_multiplier <= 0:
            self.cards_until_calc_multiplier = 2
            self.calc_multiply_card_rating()

    # def update_streak(self, new_day):
    #    """Update the streak for daily reviews (each position represents a day)."""
    #    if not self.streak_days or self.streak_days[-1] != new_day:
    #        self.streak_days.append(new_day)  # Add a new day to the streak_days array

    def get_stats(self):
        """Get all the tracked statistics."""
        return {
            "total_reviews": self.get_total_reviews(),
            "card_streak": self.card_streak,
            "card_ratings_count": self.card_ratings_count,
            "multiplier": self.multiplier,
            "multiplier_card_ratings_count": self.multiplier_card_ratings_count,
            "card_time_elapsed": self.card_time_elapsed,
            "session_time": self.session_time_elapsed,  # Include session time here
            "current_mode": self.current_mode,
            "streak_days": self.streak_days,
            "main_pokemon": self.get_main_pokemon_stats(),
            "enemy_pokemon": self.get_enemy_pokemon_stats(),
        }

    def start_card_timer(self):
        """Start the card answer timer."""
        self.card_time_elapsed = 0  # Reset for each new card
        self.card_timer.start(1000)  # Update every second

    def stop_card_timer(self):
        """Stop the card answer timer."""
        self.card_timer.stop()

    def update_card_timer(self):
        """Update the card timer for each second spent on a card."""
        self.card_time_elapsed += 1

    def start_session_timer(self):
        """Start the session timer."""
        self.session_time_elapsed = 0  # Reset session timer on new session
        self.session_timer.start(1000)  # Session timer updates every second

    def stop_session_timer(self):
        """Stop the session timer."""
        self.session_timer.stop()

    def update_session_timer(self):
        """Increment the total session time each second."""
        self.session_time_elapsed += 1

    def calc_multiply_card_rating(self):
        """Calculate the multiplier based on recent card rating counts."""

        max_points = 20
        multiply_sum = (
            self.multiplier_card_ratings_count["easy"] * 20
            + self.multiplier_card_ratings_count["hard"] * 5
            + self.multiplier_card_ratings_count["good"] * 10
        )

        self.multiplier = multiply_sum / max_points
        # Reset card ratings count for next round
        self.multiplier_card_ratings_count = {
            "again": 0,
            "hard": 0,
            "good": 0,
            "easy": 0,
        }

    def reset_timers(self):
        """Reset both the session and card timers."""
        self.session_time_elapsed = 0

    def reset_card_timer(self):
        self.card_time_elapsed = 0

    # def check_pokecoll_in_list(self):
    #    owned_pokemon_ids = self.owned_pokemon_ids
    #    id = self.enemy_pokemon.id
    #    self.pokemon_in_collection = False
    #    for num in owned_pokemon_ids:
    #        if num == id:
    #            self.pokemon_in_collection = True

    def get_ids_in_collection(self):
        try:
            owned_pokemon_ids = []
            owned_pokemon_ids = extract_ids_from_file()
            self.owned_pokemon_ids = owned_pokemon_ids
        except Exception as e:
            show_warning_with_traceback(
                parent=mw,
                exception=e,
                message="Error: from AnkimonTracker with function extract_ids_from_file",
            )

    # def get_badges(self):
    #    pass

    def randomize_battle_scene(self):
        self.battlescene_file = random_battle_scene()


---

[13]. src/Ankimon/resources.py
Why this file is critical: Centralized registry for file paths, constants, and Pokémon tier definitions.

from pathlib import Path
import os
import json

addon_dir = Path(__file__).parents[0]

#safe route for updates
user_path = addon_dir / "user_files"
user_path_data = addon_dir / "user_files" / "data_files"
user_path_sprites = addon_dir / "user_files" / "sprites"
user_path_credentials = addon_dir / "user_files" / "data.json"
manifest_path = addon_dir / "manifest.json"

font_path = addon_dir / "addon_files"

# Assign Pokemon Image folder directory name
pkmnimgfolder = addon_dir / "user_files" / "sprites"
backdefault = addon_dir / "user_files" / "sprites" / "back_default"
frontdefault = addon_dir / "user_files" / "sprites" / "front_default"
#Assign saved Pokemon Directory
mypokemon_path = addon_dir / "user_files" / "mypokemon.json"
mainpokemon_path = addon_dir / "user_files" / "mainpokemon.json"
pokemon_history_path = addon_dir / "user_files" / "pokemon_history.json"
battlescene_path = addon_dir / "addon_sprites" / "battle_scenes"
trainer_sprites_path = addon_dir / "addon_sprites" / "trainers"
battlescene_path_without_dialog = addon_dir / "addon_sprites" / "battle_scenes_without_dialog"
battle_ui_path = addon_dir / "pkmnbattlescene - UI_transp"
type_style_file = addon_dir / "addon_files" / "types.json"
next_lvl_file_path = addon_dir / "addon_files" / "ExpPokemonAddon.csv"
berries_path = addon_dir / "user_files" / "sprites" / "berries"
background_dialog_image_path  = addon_dir / "background_dialog_image.png"
pokeball_path = addon_dir / "addon_files" / "pokeball.png"
pokedex_image_path = addon_dir / "addon_sprites" / "pokedex_template.jpg"
evolve_image_path = addon_dir / "addon_sprites" / "evo_temp.jpg"
learnset_path = addon_dir / "user_files" / "data_files" / "learnsets.json"
pokedex_path = addon_dir / "user_files" / "data_files" / "pokedex.json"
stats_csv = addon_dir / "user_files" / "data_files" / "pokemon_stats.csv"
moves_file_path = addon_dir / "user_files" / "data_files" / "moves.json"
move_names_file_path = addon_dir / "user_files" / "data_files" / "move_names.json"
items_path = addon_dir / "user_files" / "sprites" / "items"
badges_path = addon_dir / "user_files" / "sprites" / "badges"
itembag_path = addon_dir / "user_files" / "items.json"
badgebag_path = addon_dir / "user_files" / "badges.json"
pokenames_lang_path = addon_dir / "user_files" / "data_files" / "pokemon_species_names.csv"
pokedesc_lang_path = addon_dir / "user_files" / "data_files" / "pokemon_species_flavor_text.csv"
poke_evo_path = addon_dir / "user_files" / "data_files" / "pokemon_evolution.csv"
poke_species_path = addon_dir / "user_files" / "data_files" / "pokemon_species.csv"
eff_chart_html_path = addon_dir / "addon_files" / "eff_chart_html.html"
effectiveness_chart_file_path = addon_dir / "addon_files" / "eff_chart.json"
table_gen_id_html_path = addon_dir / "addon_files" / "table_gen_id.html"
icon_path = addon_dir / "addon_files" / "pokeball.png"
sound_list_path = addon_dir / "addon_files" / "sound_list.json"
badges_list_path = addon_dir / "addon_files" / "badges.json"
items_list_path = addon_dir / "addon_files" / "items.json"
rate_path = addon_dir / "user_files" / "rate_this.json"
csv_file_items = addon_dir / "user_files" / "data_files" / "item_names.csv"
csv_file_descriptions = addon_dir / "user_files" / "data_files" / "item_flavor_text.csv"
csv_file_items_cost = addon_dir / "user_files" / "data_files" / "items.csv"
pokemon_csv = addon_dir / "user_files" / "data_files" / "pokemon.csv"
pokemon_tm_learnset_path = addon_dir / "user_files" / "data_files" / "pokemon_tm_learnset.json"
pokeapi_db_path = addon_dir / "user_files" / "ankimon.db"

#effect sounds paths
hurt_normal_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtNormal.mp3"
hurt_noteff_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtNotEffective.mp3"
hurt_supereff_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtSuper.mp3"
ownhplow_sound_path = addon_dir / "addon_sprites" / "sounds" / "OwnHpLow.mp3"
hpheal_sound_path = addon_dir / "addon_sprites" / "sounds" / "HpHeal.mp3"
fainted_sound_path = addon_dir / "addon_sprites" / "sounds" / "Fainted.mp3"

#utils
json_file_structure = addon_dir / "addon_files" / "folder_structure.json"

#move ui paths
type_icon_path_resources = addon_dir / "addon_sprites" / "Types"

team_pokemon_path = addon_dir / "user_files" / "team.json"

#lang routes
lang_path = addon_dir / "lang"
lang_path_de = addon_dir / "lang" / "de_text.json"
lang_path_ch = addon_dir / "lang" / "ch_text.json"
lang_path_en = addon_dir / "lang" / "en_text.json"
lang_path_fr = addon_dir / "lang" / "fr_text.json"
lang_path_jp = addon_dir / "lang" / "jp_text.json"
lang_path_sp = addon_dir / "lang" / "sp_text.json"
lang_path_it = addon_dir / "lang" / "it_text.json"
lang_path_cz = addon_dir / "lang" / "cz_text.json"
lang_path_po = addon_dir / "lang" / "po_text.json"
lang_path_kr = addon_dir / "lang" / "kr_text.json"
lang_path_es_latam = addon_dir / "lang" / "es_latam_text.json"

#backup_routes
backup_root = addon_dir / "user_files" / "backups"
backup_folder_1 = backup_root / "backup_1"
backup_folder_2 = backup_root / "backup_2"
backup_folders = [os.path.join(backup_root, f"backup_{i}") for i in range(1, 4)]

#detect add-on version
try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    addon_ver = manifest.get("version", "unknown")
except Exception:
    addon_ver = "unknown"

#note if it is an experimental build
IS_EXPERIMENTAL_BUILD = addon_ver.endswith("-E")


POKEMON_TIERS = {
  "Normal": [
    # Generation 1
    10, 11, 12,	# caterpie, metapod, butterfree
    13, 14, 15,	# weedle, kakuna, beedrill
    16, 17, 18,	# pidgey, pidgeotto, pidgeot
    19, 20, 21,	# rattata, raticate, spearow
    22, 23, 24,	# fearow, ekans, arbok
    25, 26, 27,	# pikachu, raichu, sandshrew
    28, 29, 30,	# sandslash, nidoran-f, nidorina
    31, 32, 33,	# nidoqueen, nidoran-m, nidorino
    34, 35, 36,	# nidoking, clefairy, clefable
    37, 38, 39,	# vulpix, ninetales, jigglypuff
    40, 41, 42,	# wigglytuff, zubat, golbat
    43, 44, 45,	# oddish, gloom, vileplume
    46, 47, 48,	# paras, parasect, venonat
    49, 50, 51,	# venomoth, diglett, dugtrio
    52, 53, 54,	# meowth, persian, psyduck
    55, 56, 57,	# golduck, mankey, primeape
    58, 59, 60,	# growlithe, arcanine, poliwag
    61, 62, 63,	# poliwhirl, poliwrath, abra
    64, 65, 66,	# kadabra, alakazam, machop
    67, 68, 69,	# machoke, machamp, bellsprout
    70, 71, 72,	# weepinbell, victreebel, tentacool
    73, 74, 75,	# tentacruel, geodude, graveler
    76, 77, 78,	# golem, ponyta, rapidash
    79, 80, 81,	# slowpoke, slowbro, magnemite
    82, 83, 84,	# magneton, farfetchd, doduo
    85, 86, 87,	# dodrio, seel, dewgong
    88, 89, 90,	# grimer, muk, shellder
    91, 92, 93,	# cloyster, gastly, haunter
    94, 95, 96,	# gengar, onix, drowzee
    97, 98, 99,	# hypno, krabby, kingler
    100, 101, 102,	# voltorb, electrode, exeggcute
    103, 104, 105,	# exeggutor, cubone, marowak
    106, 107, 108,	# hitmonlee, hitmonchan, lickitung
    109, 110, 111,	# koffing, weezing, rhyhorn
    112, 113, 114,	# rhydon, chansey, tangela
    115, 116, 117,	# kangaskhan, horsea, seadra
    118, 119, 120,	# goldeen, seaking, staryu
    121, 122, 123,	# starmie, mr-mime, scyther
    124, 125, 126,	# jynx, electabuzz, magmar
    127, 128, 129,	# pinsir, tauros, magikarp
    130, 131, 132,	# gyarados, lapras, ditto
    133, 134, 135,	# eevee, vaporeon, jolteon
    136, 137, 143,	# flareon, porygon, snorlax
    147, 148, 149,	# dratini, dragonair, dragonite
    # Generation 2
    161, 162, 163,	# sentret, furret, hoothoot
    164, 165, 166,	# noctowl, ledyba, ledian
    167, 168, 169,	# spinarak, ariados, crobat
    170, 171, 176,	# chinchou, lanturn, togetic
    177, 178, 179,	# natu, xatu, mareep
    180, 181, 182,	# flaaffy, ampharos, bellossom
    183, 184, 185,	# marill, azumarill, sudowoodo
    186, 187, 188,	# politoed, hoppip, skiploom
    189, 190, 191,	# jumpluff, aipom, sunkern
    192, 193, 194,	# sunflora, yanma, wooper
    195, 196, 197,	# quagsire, espeon, umbreon
    198, 199, 200,	# murkrow, slowking, misdreavus
    201, 202, 203,	# unown, wobbuffet, girafarig
    204, 205, 206,	# pineco, forretress, dunsparce
    207, 208, 209,	# gligar, steelix, snubbull
    210, 211, 212,	# granbull, qwilfish, scizor
    213, 214, 215,	# shuckle, heracross, sneasel
    216, 217, 218,	# teddiursa, ursaring, slugma
    219, 220, 221,	# magcargo, swinub, piloswine
    222, 223, 224,	# corsola, remoraid, octillery
    225, 226, 227,	# delibird, mantine, skarmory
    228, 229, 230,	# houndour, houndoom, kingdra
    231, 232, 233,	# phanpy, donphan, porygon2
    234, 235, 237,	# stantler, smeargle, hitmontop
    241, 242, 246,	# miltank, blissey, larvitar
    247, 248,	# pupitar, tyranitar
    # Generation 3
    261, 262, 263,	# poochyena, mightyena, zigzagoon
    264, 265, 266,	# linoone, wurmple, silcoon
    267, 268, 269,	# beautifly, cascoon, dustox
    270, 271, 272,	# lotad, lombre, ludicolo
    273, 274, 275,	# seedot, nuzleaf, shiftry
    276, 277, 278,	# taillow, swellow, wingull
    279, 280, 281,	# pelipper, ralts, kirlia
    282, 283, 284,	# gardevoir, surskit, masquerain
    285, 286, 287,	# shroomish, breloom, slakoth
    288, 289, 290,	# vigoroth, slaking, nincada
    291, 292, 293,	# ninjask, shedinja, whismur
    294, 295, 296,	# loudred, exploud, makuhita
    297, 299, 300,	# hariyama, nosepass, skitty
    301, 302, 303,	# delcatty, sableye, mawile
    304, 305, 306,	# aron, lairon, aggron
    307, 308, 309,	# meditite, medicham, electrike
    310, 311, 312,	# manectric, plusle, minun
    313, 314, 315,	# volbeat, illumise, roselia
    316, 317, 318,	# gulpin, swalot, carvanha
    319, 320, 321,	# sharpedo, wailmer, wailord
    322, 323, 324,	# numel, camerupt, torkoal
    325, 326, 327,	# spoink, grumpig, spinda
    328, 329, 330,	# trapinch, vibrava, flygon
    331, 332, 333,	# cacnea, cacturne, swablu
    334, 335, 336,	# altaria, zangoose, seviper
    337, 338, 339,	# lunatone, solrock, barboach
    340, 341, 342,	# whiscash, corphish, crawdaunt
    343, 344, 349,	# baltoy, claydol, feebas
    350, 351, 352,	# milotic, castform, kecleon
    353, 354, 355,	# shuppet, banette, duskull
    356, 357, 358,	# dusclops, tropius, chimecho
    359, 361, 362,	# absol, snorunt, glalie
    363, 364, 365,	# spheal, sealeo, walrein
    366, 367, 368,	# clamperl, huntail, gorebyss
    369, 370, 371,	# relicanth, luvdisc, bagon
    372, 373, 374,	# shelgon, salamence, beldum
    375, 376,	# metang, metagross
    # Generation 4
    396, 397, 398,	# starly, staravia, staraptor
    399, 400, 401,	# bidoof, bibarel, kricketot
    402, 403, 404,	# kricketune, shinx, luxio
    405, 407, 412,	# luxray, roserade, burmy
    413, 414, 415,	# wormadam-plant, mothim, combee
    416, 417, 418,	# vespiquen, pachirisu, buizel
    419, 420, 421,	# floatzel, cherubi, cherrim
    422, 423, 424,	# shellos, gastrodon, ambipom
    425, 426, 427,	# drifloon, drifblim, buneary
    428, 429, 430,	# lopunny, mismagius, honchkrow
    431, 432, 434,	# glameow, purugly, stunky
    435, 436, 437,	# skuntank, bronzor, bronzong
    441, 442, 443,	# chatot, spiritomb, gible
    444, 445, 448,	# gabite, garchomp, lucario
    449, 450, 451,	# hippopotas, hippowdon, skorupi
    452, 453, 454,	# drapion, croagunk, toxicroak
    455, 456, 457,	# carnivine, finneon, lumineon
    459, 460, 461,	# snover, abomasnow, weavile
    462, 463, 464,	# magnezone, lickilicky, rhyperior
    465, 466, 467,	# tangrowth, electivire, magmortar
    468, 469, 470,	# togekiss, yanmega, leafeon
    471, 472, 473,	# glaceon, gliscor, mamoswine
    474, 475, 476,	# porygon-z, gallade, probopass
    477, 478, 479,	# dusknoir, froslass, rotom
    # Generation 5
    504, 505, 506,	# patrat, watchog, lillipup
    507, 508, 509,	# herdier, stoutland, purrloin
    510, 511, 512,	# liepard, pansage, simisage
    513, 514, 515,	# pansear, simisear, panpour
    516, 517, 518,	# simipour, munna, musharna
    519, 520, 521,	# pidove, tranquill, unfezant
    522, 523, 524,	# blitzle, zebstrika, roggenrola
    525, 526, 527,	# boldore, gigalith, woobat
    528, 529, 530,	# swoobat, drilbur, excadrill
    531, 532, 533,	# audino, timburr, gurdurr
    534, 535, 536,	# conkeldurr, tympole, palpitoad
    537, 538, 539,	# seismitoad, throh, sawk
    540, 541, 542,	# sewaddle, swadloon, leavanny
    543, 544, 545,	# venipede, whirlipede, scolipede
    546, 547, 548,	# cottonee, whimsicott, petilil
    549, 550, 551,	# lilligant, basculin-red-striped, sandile
    552, 553, 554,	# krokorok, krookodile, darumaka
    555, 556, 557,	# darmanitan-standard, maractus, dwebble
    558, 559, 560,	# crustle, scraggy, scrafty
    561, 562, 563,	# sigilyph, yamask, cofagrigus
    568, 569, 570,	# trubbish, garbodor, zorua
    571, 572, 573,	# zoroark, minccino, cinccino
    574, 575, 576,	# gothita, gothorita, gothitelle
    577, 578, 579,	# solosis, duosion, reuniclus
    580, 581, 582,	# ducklett, swanna, vanillite
    583, 584, 585,	# vanillish, vanilluxe, deerling
    586, 587, 588,	# sawsbuck, emolga, karrablast
    589, 590, 591,	# escavalier, foongus, amoonguss
    592, 593, 594,	# frillish, jellicent, alomomola
    595, 596, 597,	# joltik, galvantula, ferroseed
    598, 599, 600,	# ferrothorn, klink, klang
    601, 602, 603,	# klinklang, tynamo, eelektrik
    604, 605, 606,	# eelektross, elgyem, beheeyem
    607, 608, 609,	# litwick, lampent, chandelure
    610, 611, 612,	# axew, fraxure, haxorus
    613, 614, 615,	# cubchoo, beartic, cryogonal
    616, 617, 618,	# shelmet, accelgor, stunfisk
    619, 620, 621,	# mienfoo, mienshao, druddigon
    622, 623, 624,	# golett, golurk, pawniard
    625, 626, 627,	# bisharp, bouffalant, rufflet
    628, 629, 630,	# braviary, vullaby, mandibuzz
    631, 632, 633,	# heatmor, durant, deino
    634, 635, 636,	# zweilous, hydreigon, larvesta
    637,	# volcarona
    # Generation 6
    659, 660, 661,	# bunnelby, diggersby, fletchling
    662, 663, 664,	# fletchinder, talonflame, scatterbug
    665, 666, 667,	# spewpa, vivillon, litleo
    668, 669, 670,	# pyroar, flabebe, floette
    671, 672, 673,	# florges, skiddo, gogoat
    674, 675, 676,	# pancham, pangoro, furfrou
    677, 678, 679,	# espurr, meowstic-male, honedge
    680, 681, 682,	# doublade, aegislash-shield, spritzee
    683, 684, 685,	# aromatisse, swirlix, slurpuff
    686, 687, 688,	# inkay, malamar, binacle
    689, 690, 691,	# barbaracle, skrelp, dragalge
    692, 693, 694,	# clauncher, clawitzer, helioptile
    695, 700, 701,	# heliolisk, sylveon, hawlucha
    702, 703, 704,	# dedenne, carbink, goomy
    705, 706, 707,	# sliggoo, goodra, klefki
    708, 709, 710,	# phantump, trevenant, pumpkaboo-average
    711, 712, 713,	# gourgeist-average, bergmite, avalugg
    714, 715,	# noibat, noivern
    # Generation 7
    731, 732, 733,	# pikipek, trumbeak, toucannon
    734, 735, 736,	# yungoos, gumshoos, grubbin
    737, 738, 739,	# charjabug, vikavolt, crabrawler
    740, 741, 742,	# crabominable, oricorio-baile, cutiefly
    743, 744, 745,	# ribombee, rockruff, lycanroc-midday
    746, 747, 748,	# wishiwashi-solo, mareanie, toxapex
    749, 750, 751,	# mudbray, mudsdale, dewpider
    752, 753, 754,	# araquanid, fomantis, lurantis
    755, 756, 757,	# morelull, shiinotic, salandit
    758, 759, 760,	# salazzle, stufful, bewear
    761, 762, 763,	# bounsweet, steenee, tsareena
    764, 765, 766,	# comfey, oranguru, passimian
    767, 768, 769,	# wimpod, golisopod, sandygast
    770, 771, 774,	# palossand, pyukumuku, minior-red-meteor
    775, 776, 777,	# komala, turtonator, togedemaru
    778, 779, 780,	# mimikyu-disguised, bruxish, drampa
    781, 782, 783,	# dhelmise, jangmo-o, hakamo-o
    784,	# kommo-o
    # Generation 8
    819, 820, 821,	# skwovet, greedent, rookidee
    822, 823, 824,	# corvisquire, corviknight, blipbug
    825, 826, 827,	# dottler, orbeetle, nickit
    828, 829, 830,	# thievul, gossifleur, eldegoss
    831, 832, 833,	# wooloo, dubwool, chewtle
    834, 835, 836,	# drednaw, yamper, boltund
    837, 838, 839,	# rolycoly, carkol, coalossal
    840, 841, 842,	# applin, flapple, appletun
    843, 844, 845,	# silicobra, sandaconda, cramorant
    846, 847, 849,	# arrokuda, barraskewda, toxtricity-amped
    850, 851, 852,	# sizzlipede, centiskorch, clobbopus
    853, 854, 855,	# grapploct, sinistea, polteageist
    856, 857, 858,	# hatenna, hattrem, hatterene
    859, 860, 861,	# impidimp, morgrem, grimmsnarl
    862, 863, 864,	# obstagoon, perrserker, cursola
    865, 866, 867,	# sirfetchd, mr-rime, runerigus
    868, 869, 870,	# milcery, alcremie, falinks
    871, 872, 873,	# pincurchin, snom, frosmoth
    874, 875, 876,	# stonjourner, eiscue-ice, indeedee-male
    877, 878, 879,	# morpeko-full-belly, cufant, copperajah
    884, 885, 886,	# duraludon, dreepy, drakloak
    887, 899, 900,	# dragapult, wyrdeer, kleavor
    901, 902, 903,	# ursaluna, basculegion-male, sneasler
    904, 905,	# overqwil, enamorus-incarnate
    # Generation 9
    915, 916, 917,	# lechonk, oinkologne, tarountula
    918, 919, 920,	# spidops, nymble, lokix
    921, 922, 923,	# pawmi, pawmo, pawmot
    924, 925, 926,	# tandemaus, maushold, fidough
    927, 928, 929,	# dachsbun, smoliv, dolliv
    930, 931, 932,	# arboliva, squawkabilly, nacli
    933, 934, 935,	# naclstack, garganacl, charcadet
    936, 937, 938,	# armarouge, ceruledge, tadbulb
    939, 940, 941,	# bellibolt, wattrel, kilowattrel
    942, 943, 944,	# maschiff, mabosstiff, shroodle
    945, 946, 947,	# grafaiai, bramblin, brambleghast
    948, 949, 950,	# toedscool, toedscruel, klawf
    951, 952, 953,	# capsakid, scovillain, rellor
    954, 955, 956,	# rabsca, flittle, espathra
    957, 958, 959,	# tinkatink, tinkatuff, tinkaton
    960, 961, 962,	# wiglett, wugtrio, bombirdier
    963, 964, 965,	# finizen, palafin, varoom
    966, 967, 968,	# revavroom, cyclizar, orthworm
    969, 970, 971,	# glimmet, glimmora, greavard
    972, 973, 974,	# houndstone, flamigo, cetoddle
    975, 976, 977,	# cetitan, veluza, dondozo
    978, 979, 980,	# tatsugiri, annihilape, clodsire
    981, 982, 983,	# farigiraf, dudunsparce, kingambit
    984, 985, 986,	# great-tusk, scream-tail, brute-bonnet
    987, 988, 989,	# flutter-mane, slither-wing, sandy-shocks
    990, 991, 992,	# iron-treads, iron-bundle, iron-hands
    993, 994, 995,	# iron-jugulis, iron-moth, iron-thorns
    996, 997, 998,	# frigibax, arctibax, baxcalibur
    999, 1000, 1005,	# gimmighoul, gholdengo, roaring-moon
    1006, 1011, 1012,	# iron-valiant, dipplin, poltchageist
    1013, 1018, 1019,	# sinistcha, archaludon, hydrapple
],
  "Legendary": [
  # Gen 1
  144, 145, 146, 150,
  # Gen 2
  243, 244, 245, 249, 250,
  # Gen 3
  377, 378, 379, 380, 381, 382, 383, 384,
  # Gen 4
  480, 481, 482, 483, 484, 485, 486, 487, 488,
  # Gen 5
  638, 639, 640, 641, 642, 643, 644, 645, 646,
  # Gen 6
  716, 717, 718,
  # Gen 7
  772, 773, 785, 786, 787, 788, 789, 790, 791, 792, 800,
  # Gen 8
  888, 889, 890, 891, 892, 894, 895, 896, 897, 898,
  # Gen 9
  1001,  # wo-chien
  1002,  # chien-pao
  1003,  # ting-lu
  1004,  # chi-yu
  1007,  # koraidon
  1008,  # miraidon
  1009,  # walking-wake
  1010,  # iron-leaves
  1014,  # okidogi
  1015,  # munkidori
  1016,  # fezandipiti
  1017,  # ogerpon
  1020,  # gouging-fire
  1021,  # raging-bolt
  1022,  # iron-boulder
  1023,  # iron-crown
  1024,  # terapagos
  1025,  # pecharunt
]
,
  "Mythical": [
  # Gen 1
  151,        # Mew
  # Gen 2
  251,        # Celebi
  # Gen 3
  385, 386,   # Jirachi, Deoxys
  # Gen 4
  489, 490, 491, 492, 493,   # Phione, Manaphy, Darkrai, Shaymin, Arceus
  # Gen 5
  494, 647, 648, 649,        # Victini, Keldeo, Meloetta, Genesect
  # Gen 6
  719, 720, 721,             # Diancie, Hoopa, Volcanion
  # Gen 7
  801, 802, 807, 808, 809,   # Magearna, Marshadow, Zeraora, Meltan, Melmetal
  # Gen 8
  893                        # Zarude
]
,
  "Ultra": [
  793,  # Nihilego
  794,  # Buzzwole
  795,  # Pheromosa
  796,  # Xurkitree
  797,  # Celesteela
  798,  # Kartana
  799,  # Guzzlord
  803,  # Poipole
  804,  # Naganadel
  805,  # Stakataka
  806   # Blacephalon
]
,
  "Fossil": [
  # Gen 1
  138, 139, 140, 141, 142,        # Omanyte, Omastar, Kabuto, Kabutops, Aerodactyl
  # Gen 3
  345, 346, 347, 348,             # Lileep, Cradily, Anorith, Armaldo
  # Gen 4
  408, 409, 410, 411,             # Cranidos, Rampardos, Shieldon, Bastiodon
  # Gen 5
  564, 565, 566, 567,             # Tirtouga, Carracosta, Archen, Archeops
  # Gen 6
  696, 697, 698, 699,             # Tyrunt, Tyrantrum, Amaura, Aurorus
  # Gen 8
  880, 881, 882, 883              # Dracozolt, Arctozolt, Dracovish, Arctovish
]
,
  "Starter": [
  # Gen 1 (Kanto)
  1, 2, 3,      # Bulbasaur, Ivysaur, Venusaur
  4, 5, 6,      # Charmander, Charmeleon, Charizard
  7, 8, 9,      # Squirtle, Wartortle, Blastoise

  # Gen 2 (Johto)
  152, 153, 154,  # Chikorita, Bayleef, Meganium
  155, 156, 157,  # Cyndaquil, Quilava, Typhlosion
  158, 159, 160,  # Totodile, Croconaw, Feraligatr

  # Gen 3 (Hoenn)
  252, 253, 254,  # Treecko, Grovyle, Sceptile
  255, 256, 257,  # Torchic, Combusken, Blaziken
  258, 259, 260,  # Mudkip, Marshtomp, Swampert

  # Gen 4 (Sinnoh)
  387, 388, 389,  # Turtwig, Grotle, Torterra
  390, 391, 392,  # Chimchar, Monferno, Infernape
  393, 394, 395,  # Piplup, Prinplup, Empoleon

  # Gen 5 (Unova)
  495, 496, 497,  # Snivy, Servine, Serperior
  498, 499, 500,  # Tepig, Pignite, Emboar
  501, 502, 503,  # Oshawott, Dewott, Samurott

  # Gen 6 (Kalos)
  650, 651, 652,  # Chespin, Quilladin, Chesnaught
  653, 654, 655,  # Fennekin, Braixen, Delphox
  656, 657, 658,  # Froakie, Frogadier, Greninja

  # Gen 7 (Alola)
  722, 723, 724,  # Rowlet, Dartrix, Decidueye
  725, 726, 727,  # Litten, Torracat, Incineroar
  728, 729, 730,  # Popplio, Brionne, Primarina

  # Gen 8 (Galar)
  810, 811, 812,  # Grookey, Thwackey, Rillaboom
  813, 814, 815,  # Scorbunny, Raboot, Cinderace
  816, 817, 818,   # Sobble, Drizzile, Inteleon

  # Gen 9
  906, 907, 908, # Sprigatito, Floragato, Meowscarada
  909, 910, 911, # Fuecoco, Crocalor, Skeledirge
  912, 913, 914 # Quaxly, Quaxwell, Quaquaval
]
,
  "Baby": [
    # Gen 2 (Johto)
    172,  # Pichu
    173,  # Cleffa
    174,  # Igglybuff
    175,  # Togepi
    236,  # Tyrogue
    238,  # Smoochum
    239,  # Elekid
    240,  # Magby

    # Gen 3 (Hoenn)
    298,  # Azurill
    360,  # Wynaut

    # Gen 4 (Sinnoh)
    406,  # Budew
    433,  # Chingling
    438,  # Bonsly
    439,  # Mime Jr.
    440,  # Happiny
    446,  # Munchlax
    447,  # Riolu
    458,  # Mantyke

    # Gen 8 (Galar)
    848,  # Toxel
]
,
  "Hisuian": [
    # Gen 8 (Legends: Arceus - Hisui region)
    899,  # Wyrdeer
    900,  # Kleavor
    901,  # Ursaluna
    902,  # Basculegion
    903,  # Sneasler
    904,  # Overqwil
    905,  # Enamorus
]

}

def ensure_ankimon_infrastructure(base_path, base_user_path):
    """
    Ensures the necessary directories and static files exist at startup.
    NOTE: No longer generates legacy JSON data files as these are managed by SQLite.
    """
    # Create user files directory
    os.makedirs(base_user_path, exist_ok=True)
    os.makedirs(os.path.join(base_user_path, "data_files"), exist_ok=True)
    os.makedirs(os.path.join(base_user_path, "sprites"), exist_ok=True)

    # Automatically initialize git submodule for local developers if missing
    objects_py = os.path.join(base_path, "poke_engine", "objects.py")
    if not os.path.exists(objects_py):
        parent = os.path.abspath(base_path)
        is_git_repo = False
        for _ in range(4):
            if os.path.exists(os.path.join(parent, ".git")):
                is_git_repo = True
                break
            parent = os.path.dirname(parent)

        if is_git_repo:
            print("Ankimon: Developer environment detected and poke_engine submodule is missing.")
            print("Attempting to automatically initialize the Git submodule...")
            try:
                import subprocess
                subprocess.run(
                    ["git", "submodule", "update", "--init", "--recursive"],
                    cwd=parent,
                    check=True,
                    capture_output=True
                )
                print("Ankimon: Submodule successfully initialized!")
            except Exception as e:
                # If git command failed, raise a clear developer-friendly error message with diagnostics
                error_details = ""
                if isinstance(e, subprocess.CalledProcessError):
                    stderr_msg = e.stderr.decode("utf-8", errors="replace").strip() if e.stderr else ""
                    stdout_msg = e.stdout.decode("utf-8", errors="replace").strip() if e.stdout else ""
                    if stderr_msg:
                        error_details = f"\nGit Diagnostics (stderr):\n{stderr_msg}\n"
                    elif stdout_msg:
                        error_details = f"\nGit Diagnostics (stdout):\n{stdout_msg}\n"
                else:
                    error_details = f"\nSystem Diagnostics:\n{str(e)}\n"

                raise ImportError(
                    "\n\n[Developer Setup Error]\n"
                    "The 'poke_engine' submodule is missing or uninitialized!\n"
                    "Please initialize the submodule manually in your repository root:\n\n"
                    "    git submodule update --init --recursive\n"
                    f"{error_details}"
                ) from e

    # Create blank HelpInfos.html and updateinfos.md at base_path if they don't exist
    helpinfos_path = os.path.join(base_path, 'HelpInfos.html')
    updateinfos_path = os.path.join(base_path, 'updateinfos.md')

    if not os.path.exists(helpinfos_path):
        with open(helpinfos_path, 'w', encoding='utf-8') as f:
            f.write('')

    if not os.path.exists(updateinfos_path):
        with open(updateinfos_path, 'w', encoding='utf-8') as f:
            f.write('')

    return True



---

[14]. src/Ankimon/utils.py
Why this file is critical: Provides essential global utilities for audio, RNG, calculations, and API interactions.

import os
from pathlib import Path
import requests
import json
import random
import csv
import base64
from typing import Any, Optional

from aqt import mw
from aqt.utils import showWarning, showInfo

from aqt.qt import QFontDatabase, QFont, QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from .pyobj.settings import Settings
from .pyobj.InfoLogger import ShowInfoLogger

from .functions.battle_functions import calculate_hp
from .functions.pokedex_functions import find_details_move, search_pokedex

from .pyobj.error_handler import show_warning_with_traceback
from .resources import (
    battlescene_path,
    berries_path,
    items_path,
    csv_file_items_cost,
    csv_file_descriptions,
    font_path,
    hurt_normal_sound_path,
    hurt_noteff_sound_path,
    hurt_supereff_sound_path,
    hpheal_sound_path,
    ownhplow_sound_path,
    fainted_sound_path,
    addon_dir,
    POKEMON_TIERS,
    pokedex_path,
)
from .move_names import format_move_name


audio_output = QAudioOutput()
media_player = QMediaPlayer()
media_player.setAudioOutput(audio_output)

with open(pokedex_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    POKEMON_NAME_LOOKUP = {x: data[x]["name"] for x in data}


def format_pokemon_name(name: str) -> str:
    """
    Look up the official Pokémon name using the normalized key.
    Falls back to capitalizing if not found.
    """
    key = name.replace(" ", "").replace("-", "").replace("_", "").lower()
    return POKEMON_NAME_LOOKUP.get(key, name.capitalize())


def check_folders_exist(parent_directory, folder):
    folder_path = os.path.join(parent_directory, folder)
    return os.path.isdir(folder_path)


def check_file_exists(folder, filename):
    file_path = os.path.join(folder, filename)
    return os.path.isfile(file_path)


def test_online_connectivity(
    url="https://raw.githubusercontent.com/Unlucky-Life/ankimon/main/update_txt.md",
    timeout=5,
):
    try:
        # Attempt to get the URL
        response = requests.get(url, timeout=timeout)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            return True
    except:
        # Connection error means no internet connectivity
        return False


# Define the hook function
def addon_config_editor_will_display_json(text: str) -> str:
    """
    This function modifies the JSON configuration text before displaying it to the user.
    It replaces the values for the keys "pokemon_collection" and "mainpokemon".

    Args:
        text (str): The JSON configuration text.

    Returns:
        str: The modified JSON configuration text.
    """
    try:
        # Parse the JSON text
        config = json.loads(text)
        if "mainpokemon" in config:
            # showInfo(f"{config}")
            showInfo(
                "This Configuration is old and wont be used anymore. \n Please use the Settings Window in the Ankimon Menu => Settings"
            )
            # mw.settings_ankimon.show_window()
            # dont show all mainpokemon and mypokemon information in config
            if "pokemon_collection" in config:
                del config["pokemon_collection"]
            if "mainpokemon" in config:
                del config["mainpokemon"]
            if "trainer.cash" in config:
                del config["trainer.cash"]

            # Convert back to JSON string
            modified_text = json.dumps(config, indent=4)
            return modified_text
        return text
    except (requests.RequestException, json.JSONDecodeError):
        # Handle JSON parsing or network errors
        return text


# Function to read the content of the local file
def read_local_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return None


# Function to check if the file exists on GitHub and read its content
def read_github_file(url):
    response = requests.get(url)

    if response.status_code == 200:
        # File exists, parse the Markdown content
        content = response.text
        return content
    else:
        return None


# Function to check if the content of the two files is the same
def compare_files(local_content, github_content):
    return local_content == github_content


# Function to write content to a local file
def write_local_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def read_html_file(file_path):
    """Reads an HTML file and returns its content as a string."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def random_battle_scene():
    # TODO: choice?
    # TODO: merge with random_berries and
    battle_scenes = {}
    for index, filename in enumerate(os.listdir(battlescene_path)):
        if filename.endswith(".png"):
            battle_scenes[index + 1] = filename
    # Get the corresponding file name
    battlescene_file = battle_scenes.get(random.randint(1, len(battle_scenes)))
    return battlescene_file


def random_berries():
    berries = {}
    for index, filename in enumerate(os.listdir(berries_path)):
        if filename.endswith(".png"):
            berries[index + 1] = filename
    # Get the corresponding file name
    berries_file = berries.get(random.randint(1, len(berries)))
    return berries_file


def filter_item_sprites(string):
    # Initialize an empty list to store the file names
    item_names = []
    # Iterate over each file in the directory
    for file in os.listdir(items_path):
        # Check if the file is a .png file
        if file.endswith(".png"):
            # Append the file name without the .png extension to the list
            item_names.append(file[:-4])
    # filter by -ball, -repel..etc
    item_names = [name for name in item_names if name.endswith(f"{string}")]
    showInfo(f"{item_names}")
    return item_names


USELESS_ITEMS = {
    # not real items
    # NOTE: maybe these should be in a separate folder?
    "Bag_TM_normal_SV_Sprite",
    "Bag_TM_bug_SV_Sprite",
    "Bag_TM_dark_SV_Sprite",
    "Bag_TM_dragon_SV_Sprite",
    "Bag_TM_electric_SV_Sprite",
    "Bag_TM_fairy_SV_Sprite",
    "Bag_TM_fighting_SV_Sprite",
    "Bag_TM_fire_SV_Sprite",
    "Bag_TM_flying_SV_Sprite",
    "Bag_TM_ghost_SV_Sprite",
    "Bag_TM_grass_SV_Sprite",
    "Bag_TM_ground_SV_Sprite",
    "Bag_TM_ice_SV_Sprite",
    "Bag_TM_poison_SV_Sprite",
    "Bag_TM_psychic_SV_Sprite",
    "Bag_TM_rock_SV_Sprite",
    "Bag_TM_steel_SV_Sprite",
    "Bag_TM_water_SV_Sprite",
    # items that are sold for cash
    "balm-mushroom",
    "big-mushroom",
    "big-pearl",
    "comet-shard",
    "nugget",
    "pearl",
    "pearl-string",
    "pretty-wing",
    "rare-bone",
    "relic-gold",
    "tiny-mushroom",
    # catching / escape / encounter rate items
    "dive-ball",
    "dusk-ball",
    "great-ball",
    "heal-ball",
    "luxury-ball",
    "master-ball",
    "nest-ball",
    "net-ball",
    "poke-ball",
    "premier-ball",
    "quick-ball",
    "repeat-ball",
    "safari-ball",
    "timer-ball",
    "ultra-ball",
    "smoke-ball",  # escape from wild battles
    "fluffy-tail",  # escape from wild battles
    "repel",
    "max-repel",
    "super-repel",
    # Flutes and scarves, that work outside battle
    "black-flute",
    "blue-flute",
    "red-flute",
    "white-flute",
    "yellow-flute",
    "blue-scarf",
    "green-scarf",
    "pink-scarf",
    "red-scarf",
    "yellow-scarf",
    # Collectible shards
    "blue-shard",
    "green-shard",
    "red-shard",
    "yellow-shard",
    # Contest / Grooming / Friendship items outside battle
    "soothe-bell",
    "luxury-ball",
    "pretty-wing",
    # Miscellaneous items for info
    "heart-scale",
    "honey",
    "heart-scale",
    "shoal-salt",
    "shoal-shell",
    # Non-heal status items that only work out of battle
    "antidote",
    "awakening",
    "burn-heal",
    "full-heal",
    "ice-heal",
    "lava-cookie",
    "old-gateau",
    "heal-powder",
    "paralyze-heal",
    # Non-battle stat=ups or contests
    "calcium",
    "carbos",
    "clever-wing",
    "genius-wing",
    "health-wing",
    "hp-up",
    "iron",
    "muscle-wing",
    "protein",
    "resist-wing",
    "swift-wing",
    "zinc",
    # Rare candy and PP / elixirs
    "rare-candy",
    "pp-max",
    "pp-up",
    "max-elixir",
    "max-ether",
    "elixir",
    "ether",
}


def random_item():
    item_names: list[str] = []

    # Iterate over each file in the directory
    for file in os.listdir(items_path):
        # Check if the file is a .png file
        if not file.endswith(".png"):
            continue

        # File name without the .png extension to the list
        name = file[:-4]

        if name in USELESS_ITEMS:
            continue
        if name.endswith("-ball"):
            continue
        if name.endswith("-repel"):
            continue
        if name.endswith("-incense"):
            continue
        if name.endswith("-fang"):
            continue
        if name.endswith("dust"):
            continue
        if name.endswith("-piece"):
            continue
        if name.endswith("-nugget"):
            continue

        item_names.append(name)

    item_name = random.choice(item_names)
    # add item to item list
    give_item(item_name)
    return item_name


# Function to get the list of daily items
def daily_item_list():
    """
    Generates a list of items available for the daily shop, filtering out certain categories.
    """
    # Check if the sprites directory exists. If not, trigger the download dialog.
    if not Path(items_path).exists():
        from .pyobj.download_sprites import show_agreement_and_download_dialog

        show_agreement_and_download_dialog(force_download=True)
        # Return an empty list to prevent the crash and allow the addon to load.
        return []

    # Items with these suffixes will be excluded from the daily shop
    excluded_suffixes = ["dust", "-piece", "-nugget", "-berry"]
    # Add full item names here to exclude them from the daily shop, e.g., ["master-ball"]

    item_names = []
    for file in os.listdir(items_path):
        if not file.endswith(".png"):
            continue

        item_name = file[:-4]

        # Filter out excluded items
        if (
            get_item_price(item_name) == 0
            or item_name in USELESS_ITEMS
            or any(item_name.endswith(suffix) for suffix in excluded_suffixes)
        ):
            continue

        item_names.append(
            {
                "name": item_name,
                "description": f"Item: {item_name}",
                "price": get_item_price(item_name),
            }
        )

    return item_names


# Function to give an item to the player
def give_item(item_name: str, item_type: Optional[str] = None):
    """Gives an item to the user."""
    db = mw.ankimon_db

    # Get current item or create new
    existing = db.get_item(item_name)
    if existing:
        db.update_item_quantity(item_name, 1)
        return

    extra_data = {"type": item_type} if item_type else None
    db.add_item(item_name, 1, extra_data)


# Function to return a cost of an item
def get_item_price(item_name, file_path=csv_file_items_cost):
    """
    Returns the cost of an item from a CSV file based on its identifier (name).

    Parameters:
        file_path (str): Path to the CSV file.
        item_name (str): The identifier (name) of the item.

    Returns:
        int: The cost of the item, or None if the item is not found or has no id.
    """
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["identifier"] == item_name:
                    cost = row["cost"]
                    return int(cost)
    except FileNotFoundError:
        showWarning(f"Error: File {file_path} not found.")
        return 1000
    except KeyError:
        showWarning("Error: CSV file does not contain the expected headers.")
        return 1000
    except Exception as e:
        showWarning(f"Unexpected error: {e}")
        return 1000

    return None


# Function to return a cost of an item
def get_item_id(item_name, file_path=csv_file_items_cost):
    """
    Returns the cost of an item from a CSV file based on its identifier (name).

    Parameters:
        file_path (str): Path to the CSV file.
        item_name (str): The identifier (name) of the item.

    Returns:
        int: The id of the item, or None if the item is not found or has no id.
    """
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["identifier"] == item_name:
                    id = row["id"]
                    return int(id)
    except (OSError, KeyError) as e:
        show_warning_with_traceback(
            parent=mw, exception=e, message="Error reading item data:"
        )
        return 4
    except Exception as e:
        show_warning_with_traceback(
            parent=mw, exception=e, message=f"Unexpected error: {e}"
        )
        return 4


# Function to return a random fossil
def random_fossil():
    fossil_names = []
    # Iterate over each file in the directory
    for file in os.listdir(items_path):
        # Check if the file is a .png file
        if file.endswith("-fossil.png"):
            # Append the file name without the .png extension to the list
            fossil_names.append(file[:-4])
    fossil_name = random.choice(fossil_names)
    give_item(fossil_name)
    return fossil_name


def count_items_and_rewrite():
    """
    Consolidates item quantities in the database.
    Legacy: Previously read from items.json, now uses database.
    """
    try:
        db = mw.ankimon_db

        # Get all items from database - they're already unique by item_name
        # so no need to aggregate, the database handles this automatically
        items = db.get_all_items()

        if items:
            print(f"Database contains {len(items)} unique items.")
        else:
            print("No items in database.")

    except Exception as e:
        show_warning_with_traceback(
            exception=e, message=f"An unexpected error occurred: {e}"
        )


# Assuming the data is stored in a CSV file named 'item_flavor_texts.csv'
def get_item_description(item_name, language_id):
    """
    Fetch the flavor text for an item based on its item_id, version_group_id, and language_id.
    => get item_id from item_name via items.csv
    :param item_id: The ID of the item.
    :param language_id: The language ID for the flavor text.
    :param file_path: The path to the CSV file containing the flavor texts.
    :return: The flavor text if found, otherwise None.
    """
    try:
        item_id = get_item_id(item_name)
        file_path = csv_file_descriptions
        # Normalize language: fall back to Spanish data for es_latam (14), English on errors.
        try:
            normalized_lang = int(language_id)
        except Exception:
            normalized_lang = 9
        if normalized_lang == 14:
            normalized_lang = 7

        # Open the CSV file and read the contents
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Iterate through each row in the CSV
            for row in reader:
                # Check if the current row matches the item_id, version_group_id, and language_id
                if (
                    int(row["item_id"]) == item_id
                    and int(row["language_id"]) == normalized_lang
                ):
                    return row["flavor_text"]  # Return the matching flavor text

        # If no match is found, return None
        return None

    except Exception as e:
        show_warning_with_traceback(exception=e, message="An error occurred:")
        return None


def load_custom_font(font_size, language):
    if language == 1:
        font_file = "pkmn_w.ttf"
        font_file_path = font_path / font_file
        font_size = int((font_size * 1) / 2)
        if font_file_path.exists():
            font_name = "PKMN Western"
        else:
            font_name = "Early GameBoy"
            font_file = "Early GameBoy.ttf"
            font_size = int((font_size * 5) / 7)
    else:
        font_name = "Early GameBoy"
        font_file = "Early GameBoy.ttf"
        font_size = int((font_size * 2) / 5)

    # Register the custom font with its file path
    QFontDatabase.addApplicationFont(str(font_path / font_file))
    custom_font = QFont(
        font_name
    )  # Use the font family name you specified in the font file
    custom_font.setPointSize(int(font_size))  # Adjust the font size as needed

    return custom_font


def get_all_sprites(directory):
    """
    Returns a list of trainer sprite names without the '.png' extension
    from the specified directory.

    :param directory: Path to the directory containing trainer sprite images.
    :return: List of sprite names without '.png'.
    """
    try:
        sprite_names = [
            os.path.splitext(file)[0]  # Remove the file extension
            for file in os.listdir(directory)
            if file.endswith(".png")  # Filter for .png files
        ]
        return sprite_names
    except FileNotFoundError:
        print(f"Error: The directory '{directory}' does not exist.")
        return []


def play_effect_sound(settings_obj, sound_type):
    sound_effects = settings_obj.get("audio.sound_effects")
    if sound_effects is True:
        audio_path = None
        if sound_type == "HurtNotEffective":
            audio_path = hurt_noteff_sound_path
        elif sound_type == "HurtNormal":
            audio_path = hurt_normal_sound_path
        elif sound_type == "HurtSuper":
            audio_path = hurt_supereff_sound_path
        elif sound_type == "OwnHpLow":
            audio_path = ownhplow_sound_path
        elif sound_type == "HpHeal":
            audio_path = hpheal_sound_path
        elif sound_type == "Fainted":
            audio_path = fainted_sound_path

        if not audio_path.is_file():
            return
        else:
            audio_output.setVolume(settings_obj.get("audio.volume"))
            media_player.setSource(QUrl.fromLocalFile(str(audio_path)))
            media_player.play()
    else:
        pass


def save_error_code(error_code, logger=None):
    error_fix_msg = ""
    try:
        # Find the position of the phrase "can't be transferred from Gen"
        index = error_code.find("can't be transferred from Gen")

        # Extract the substring starting from this position
        relevant_text = error_code[index:]

        # Find the first number in the extracted text (assuming it's the generation number)
        generation_number = int("".join(filter(str.isdigit, relevant_text)))

        # Show the generation number
        error_fix_msg += f"\n Please use Gen {str(generation_number)[0]} or lower"

        index = error_code.find("can't be transferred from Gen")

        # Extract the substring starting from this position
        relevant_text = error_code[index:]

        # Find the first number in the extracted text (assuming it's the generation number)
        generation_number = int("".join(filter(str.isdigit, relevant_text)))

        error_fix_msg += f"\n Please use Gen {str(generation_number)[0]} or lower"

    except Exception as e:
        if logger is not None:
            show_warning_with_traceback(exception=e, message="An error occurred:")

    if logger is not None:
        logger.log_and_showinfo("info", f"{error_fix_msg}")


def get_main_pokemon_data():
    main_pokemon_data = mw.ankimon_db.get_main_pokemon()

    if not main_pokemon_data:
        return None

    _name = main_pokemon_data["name"]
    if not main_pokemon_data.get('nickname') or main_pokemon_data.get('nickname') is None:
        _nickname = None
    else:
        _nickname = main_pokemon_data['nickname']
    _id = main_pokemon_data["id"]
    _ability = main_pokemon_data["ability"]
    _type = main_pokemon_data["type"]
    _stats = main_pokemon_data.get("stats") or main_pokemon_data.get("base_stats", {})
    _attacks = main_pokemon_data["attacks"]
    _level = main_pokemon_data["level"]
    _hp_base_stat = _stats.get("hp", 1)
    _growth_rate = main_pokemon_data["growth_rate"]
    _base_experience = main_pokemon_data["base_experience"]
    _ev = main_pokemon_data["ev"]
    _iv = main_pokemon_data["iv"]
    _gender = main_pokemon_data["gender"]
    _shiny = main_pokemon_data.get("shiny", False)
    _individual_id = main_pokemon_data.get("individual_id")
    _pokemon_defeated = main_pokemon_data.get("pokemon_defeated", 0)
    _current_hp = main_pokemon_data.get("current_hp")
    _xp = main_pokemon_data.get("xp", 0)
    _max_moves = main_pokemon_data.get("max_moves", [])
    _mega = main_pokemon_data.get("mega", False)
    _everstone = main_pokemon_data.get("everstone", False)
    _friendship = main_pokemon_data.get("friendship", 0)
    _held_item = main_pokemon_data.get("held_item")
    _status = main_pokemon_data.get("status")

    return {
        "name": _name, "nickname": _nickname, "id": _id, "ability": _ability,
        "type": _type, "stats": _stats, "attacks": _attacks,
        "level": _level, "hp": _hp_base_stat, "growth_rate": _growth_rate,
        "base_experience": _base_experience, "ev": _ev, "iv": _iv,
        "gender": _gender, "shiny": _shiny, "individual_id": _individual_id,
        "pokemon_defeated": _pokemon_defeated, "current_hp": _current_hp, "xp": _xp,
        "max_moves": _max_moves, "mega": _mega, "everstone": _everstone,
        "friendship": _friendship, "held_item": _held_item, "status": _status
    }


def play_sound(enemy_pokemon_id: int, settings_obj: Settings):
    if settings_obj.get("audio.sounds"):
        file_name = f"{enemy_pokemon_id}.ogg"
        audio_path = addon_dir / "user_files" / "sprites" / "sounds" / file_name
        if audio_path.is_file():
            audio_output.setVolume(settings_obj.get("audio.volume"))
            media_player.setSource(QUrl.fromLocalFile(str(audio_path)))
            media_player.play()


def load_collected_pokemon_ids() -> set:
    """Loads all captured pokemon IDs from the database."""
    return mw.ankimon_db.get_all_pokemon_ids()


def limit_ev_yield(
    current_pokemon_ev: dict[str, int], ev_yield: dict[str, int]
) -> dict[str, int]:
    """
    Limits the EV (Effort Value) yield for a Pokémon based on current EVs and Pokémon game rules.

    Ensures that the total EVs after applying the yield do not exceed 510, and that no single
    stat exceeds 252 EVs. Adjusts the EV yield to comply with these constraints by capping individual
    stats and reducing EVs randomly if the total would exceed the maximum allowed.

    Args:
        current_pokemon_ev (dict[str, int]): Current EVs of the Pokémon, with keys as stat abbreviations
            ("hp", "atk", "def", "spa", "spd", "spe") and values as their EV amounts.
        ev_yield (dict[str, int]): Proposed EV yields from a defeated Pokémon, with keys as full stat names
            ("hp", "attack", "defense", "special-attack", "special-defense", "speed") and values as EV amounts.

    Raises:
        ValueError: If any key in `current_pokemon_ev` or `ev_yield` is not a recognized stat.

    Returns:
        dict[str, int]: Adjusted EV yields that do not cause the Pokémon's total EVs to exceed 510 or any
        single stat to exceed 252. The keys correspond to full stat names.
    """
    # The sum of EVs of a Pokemon can only add up to 510. With a limit of 252 EVs in a single stat.
    for stat in current_pokemon_ev.keys():
        if stat not in ("hp", "atk", "def", "spa", "spd", "spe"):
            raise ValueError(f"Unknown EV : {stat}")

    for stat in ev_yield.keys():
        if stat not in (
            "hp",
            "attack",
            "defense",
            "special-attack",
            "special-defense",
            "speed",
        ):
            raise ValueError(f"Unknown EV : {stat}")

    zipped_keys = zip(
        ["hp", "atk", "def", "spa", "spd", "spe"],
        ["hp", "attack", "defense", "special-attack", "special-defense", "speed"],
    )

    new_ev_yield = {
        "hp": 0,
        "attack": 0,
        "defense": 0,
        "special-attack": 0,
        "special-defense": 0,
        "speed": 0,
    }

    for key_1, key_2 in zipped_keys:
        # For each stat, we yield an amount of EVs that will not exceed the value of 252
        new_ev_yield[key_2] = min(ev_yield[key_2], 252 - current_pokemon_ev[key_1])

    # To ensure that we won't go above 510 EVs after yielding the EVs, we randomly reduce the EV yield until we drop below the 510 limit
    while (sum(current_pokemon_ev.values()) + sum(new_ev_yield.values())) > 510:
        rand_key = [
            key for key, val in new_ev_yield.items() if val > 0
        ]  # We only reduce the positive EV yield values. In other words : We don't give out negative EV yields
        if len(rand_key) == 0:
            break
        rand_key = random.choice(rand_key)
        new_ev_yield[rand_key] -= 1

    # This final block here is specifically made to give out negative EV yields
    # This might be necessary if, for any reason, the user's pokemon has a total EV sum already above 510
    # In that case, we randomly give out negative EV yields to bring down the EVs of the user's pokemon below 510
    while (sum(current_pokemon_ev.values()) + sum(new_ev_yield.values())) > 510:
        rand_key = random.choice(
            list(new_ev_yield.keys())
        )  # This time, we choose any EV yields, including those that could already have a negative EV yield
        new_ev_yield[rand_key] -= 1

    return new_ev_yield


def iv_rand_gauss(mu: float = 15, sigma: float = 5) -> int:
    """
    Generates a random individual value (IV) using a Gaussian distribution,
    clamped to the range [0, 31].

    Args:
        mu (float, optional): The mean of the Gaussian distribution. Defaults to 15.
        sigma (float, optional): The standard deviation of the Gaussian distribution. Defaults to 5.

    Returns:
        int: An integer IV value between 0 and 31 inclusive.
    """
    rand = random.gauss(mu, sigma)
    rand = max(0, rand)  # ensures that rand >= 0
    rand = min(31, rand)  # ensures that rand <= 31
    return int(rand)


def get_ev_spread(mode: str = "random") -> dict[str, int]:
    """
    Generate an EV (Effort Value) spread for Pokémon stats based on the specified mode.

    Args:
        mode (str): The mode of EV distribution. Supported modes are:
            - "random": Randomly distributes up to 510 EVs across stats using a uniform distribution,
                        with each stat capped at 252 EVs.
            - "pair": Assigns 252 EVs to two random stats and 4 EVs to a third random stat.
            - "defense": Returns a predefined defensive spread with 252 EVs in Defense and Special Defense,
                         and 4 EVs in HP.
            - "uniform": Distributes EVs evenly (84 EVs) across all stats.

    Returns:
        dict[str, int]: A dictionary mapping each stat ("hp", "atk", "def", "spa", "spd", "spe")
                        to its corresponding EV value according to the selected mode.
    """
    stat_names = ["hp", "atk", "def", "spa", "spd", "spe"]
    if mode == "random":  # Draws each EV following a uniform probability distribution
        cuts = sorted(random.sample(range(510 + 1), 6 - 1))
        parts = [a - b for a, b in zip(cuts + [510], [0] + cuts)]
        parts = [min(252, part) for part in parts]
        evs = {stat: val for stat, val in zip(stat_names, parts)}
        return evs
    elif mode == "pair":  # Draws 2 stats at 252 EVs, and a 3rd at 4 EVs
        ev = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        stats = random.sample(stat_names, 3)
        ev[stats[0]] = 252
        ev[stats[1]] = 252
        ev[stats[2]] = 4
        return ev
    elif mode == "defense":
        return {"hp": 4, "atk": 0, "def": 252, "spa": 0, "spd": 252, "spe": 0}
    elif mode == "uniform":
        return {"hp": 84, "atk": 84, "def": 84, "spa": 84, "spd": 84, "spe": 84}

    raise ValueError(f"Received unknown value for 'mode': {mode}")


def get_tier_by_id(pokemon_id: int) -> Optional[str]:
    """
    Determines the tier category of a Pokémon based on its ID.

    Searches through lists in resources.py representing different Pokémon tiers
    (Normal, Legendary, Mythical, Baby, Ultra, Fossil, Hisuian, Starter) to find the tier corresponding
    to the given Pokémon ID.

    Args:
        pokemon_id (int): The unique identifier of the Pokémon.

    Returns:
        str | None: The tier name as a string if the Pokémon ID is found
        in one of the tier lists; otherwise, None.
    """

    for tier, ids in POKEMON_TIERS.items():
        if pokemon_id in ids:
            return tier
    return None


def safe_get_random_move(
    pokemon_moves: list[str], logger: Optional[ShowInfoLogger] = None
) -> dict:
    """
    Attempts to retrieve details of a randomly selected move from a list of Pokémon moves.

    This function shuffles the provided list of move names and tries to find the first
    move for which details can be successfully retrieved using `find_details_move`. If no
    valid move is found, it logs a warning (if a logger is provided) and defaults to
    returning the details for the move "Splash".

    Args:
        pokemon_moves (list[str]): A list of move names to select from.
        logger (ShowInfoLogger | None, optional): An optional logger instance for
            logging warnings if no valid move is found. Defaults to None.

    Returns:
        dict: A dictionary containing the details of a valid move if found;
            otherwise, the details for the move "Splash".
    """
    rand_moves = pokemon_moves.copy()
    random.shuffle(rand_moves)
    # We go through the shuffled list to find the first move that gets successfully parsed
    for move in rand_moves:
        move_details = find_details_move(move) or find_details_move(
            format_move_name(move)
        )
        if move_details is not None:
            return move_details
        else:
            if logger is not None:
                logger.log(
                    "warning",
                    f"Could not parse the following move : {str(move)}",
                )

    # If we fail to successfully parse a single move, we just return Splash
    if logger is not None:
        logger.log(
            "warning",
            f"Could not parse a single move in the following moveset : {str(pokemon_moves)}",
        )
    return find_details_move(format_move_name("splash"))

def png_to_base64(path: str) -> str:
    """Convert a PNG file to a base64 data URI for embedding into HTML.

    Args:
        path (str): absolute or relative filesystem path to a PNG file.

    Returns:
        str: a data URI string like ``data:image/png;base64,...`` or empty
             string if the file does not exist.
    """
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")


def close_anki():
    mw.close()


---

[15]. src/Ankimon/user_files/web/ankimon_hud_portal.js
Why this file is critical: Client-side JavaScript responsible for injecting and rendering the visual HUD overlay securely via Shadow DOM.

// user_files/web/ankimon_hud_portal.js
(function initAnkimonHUD() {
  try {
    if (window.__ankimonHud) return;

    // Create a fixed container near the bottom center
    const hostId = "ankimon-hud-host";
    const existing = document.getElementById(hostId);
    if (existing) existing.remove();

    const host = document.createElement("div");
    host.id = hostId;

    const force = (el, props) => {
      if (!el) return;
      for (const [k, v] of Object.entries(props)) {
        try { el.style.setProperty(k, v, "important"); } catch (e) {}
      }
    };

    // Pin to viewport bottom-center like the legacy HUD (you can tweak sizes later)
    force(host, {
      all: "initial",
      position: "fixed",
      left: "50%",
      bottom: "16px",
      transform: "translateX(-50%)",
      width: "min(900px, 96vw)",
      height: "auto",
      "z-index": "2147483646",
      background: "transparent",
      "pointer-events": "none", // HUD outer lets clicks pass; inner can enable if needed
      display: "block",
      isolation: "isolate",
      filter: "invert(1) hue-rotate(180deg) saturate(0.555) contrast(0.833)" // Counter-filter
    });

    // Append outside card flow to avoid scroll/overflow containers
    (document.documentElement || document.body).appendChild(host);

    // Closed shadow root = max isolation
    const root = host.attachShadow({ mode: "closed" });

    // Base reset inside the shadow; the dynamic CSS you provide will be appended on update()
    const baseStyle = document.createElement("style");
    baseStyle.textContent = `
      :host { all: initial !important; }
      #hud-root {
        all: initial !important;
        display: block !important;
        position: relative !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none !important;
      }
      *, *::before, *::after {
        box-sizing: border-box !important;
        animation: none !important;
        transition: none !important;
        filter: none !important;
        /* Explicitly unset filter and transform for all elements inside shadow DOM */
        filter: none !important;
      }
      img { /* Target images specifically within the shadow DOM */
        filter: none !important;
      }
    `;

    const hudRoot = document.createElement("div");
    hudRoot.id = "hud-root";

    root.appendChild(baseStyle);
    root.appendChild(hudRoot);

    // Public API used by Python to render/update HUD content
    window.__ankimonHud = {
      update: (html, css) => {
        try {
          hudRoot.textContent = "";

          const wrapper = document.createElement("div");
          wrapper.style.pointerEvents = "auto"; // Allow interaction inside HUD if needed

          if (css && css.length) {
            const dynStyle = document.createElement("style");
            dynStyle.textContent = css;
            hudRoot.appendChild(dynStyle);
          }

          wrapper.innerHTML = html || "";
          hudRoot.appendChild(wrapper);
        } catch (e) {
          try { console.error("Ankimon HUD update failed:", e); } catch (_) {}
        }
      },
      clear: () => {
        try { hudRoot.textContent = ""; } catch (_) {}
      }
    };
  } catch (e) {
    try { console.error("Ankimon HUD init failed:", e); } catch (_) {}
  }
})();

---
