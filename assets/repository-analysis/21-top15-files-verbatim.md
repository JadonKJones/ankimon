[1]. src/Ankimon/__init__.py
Why this file is critical: Primary entrypoint configuring Anki hooks.

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
Why this file is critical: Central repository for all global application state.

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
Why this file is critical: Handles initial bootstrap processes like migrations, asset checks.

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
Why this file is critical: Directly interfaces with Anki's card review hooks.

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

[7]. src/Ankimon/functions/ankimon_hooks_to_poke_engine.py
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

[8]. src/Ankimon/poke_engine/evaluate.py
Why this file is critical: Entrypoint for evaluating a combat turn within the poke_engine.

from . import constants
from .data import effectiveness


class Scoring:
    POKEMON_ALIVE_STATIC = 75
    POKEMON_HP = 100  # 100 points for 100% hp, 0 points for 0% hp. This is in addition to being alive
    POKEMON_HIDDEN = 10
    POKEMON_BOOSTS = {
        constants.ATTACK: 15,
        constants.DEFENSE: 15,
        constants.SPECIAL_ATTACK: 15,
        constants.SPECIAL_DEFENSE: 15,
        constants.SPEED: 25,
        constants.ACCURACY: 3,
        constants.EVASION: 3
    }

    POKEMON_BOOST_DIMINISHING_RETURNS = {
        -6: -3.3,
        -5: -3.15,
        -4: -3,
        -3: -2.5,
        -2: -2,
        -1: -1,
        0: 0,
        1: 1,
        2: 2,
        3: 2.5,
        4: 3,
        5: 3.15,
        6: 3.30,
    }

    POKEMON_STATIC_STATUSES = {
        constants.FROZEN: -40,
        constants.SLEEP: -25,
        constants.PARALYZED: -25,
        constants.TOXIC: -30,
        constants.POISON: -10,
        None: 0
    }

    MATCHUP_BONUS = 20

    @staticmethod
    def BURN(burn_multiplier):
        return -25*burn_multiplier

    POKEMON_VOLATILE_STATUSES = {
        constants.LEECH_SEED: -30,
        constants.SUBSTITUTE: 40,
        constants.CONFUSION: -20
    }

    STATIC_SCORED_SIDE_CONDITIONS = {
        constants.REFLECT: 20,
        constants.STICKY_WEB: -25,
        constants.LIGHT_SCREEN: 20,
        constants.AURORA_VEIL: 40,
        constants.SAFEGUARD: 5,
        constants.TAILWIND: 7,
    }

    POKEMON_COUNT_SCORED_SIDE_CONDITIONS = {
        constants.STEALTH_ROCK: -10,
        constants.SPIKES: -7,
        constants.TOXIC_SPIKES: -7,
    }


def evaluate_pokemon(pkmn):
    score = 0
    if pkmn.hp <= 0:
        return score

    score += Scoring.POKEMON_ALIVE_STATIC
    score += Scoring.POKEMON_HP * (float(pkmn.hp) / pkmn.maxhp)

    # boosts have diminishing returns
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.attack_boost] * Scoring.POKEMON_BOOSTS[constants.ATTACK]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.defense_boost] * Scoring.POKEMON_BOOSTS[constants.DEFENSE]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.special_attack_boost] * Scoring.POKEMON_BOOSTS[constants.SPECIAL_ATTACK]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.special_defense_boost] * Scoring.POKEMON_BOOSTS[constants.SPECIAL_DEFENSE]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.speed_boost] * Scoring.POKEMON_BOOSTS[constants.SPEED]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.accuracy_boost] * Scoring.POKEMON_BOOSTS[constants.ACCURACY]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.evasion_boost] * Scoring.POKEMON_BOOSTS[constants.EVASION]

    try:
        score += Scoring.POKEMON_STATIC_STATUSES[pkmn.status]
    except KeyError:
        # KeyError only happens when the status is BURN
        score += Scoring.BURN(pkmn.burn_multiplier)

    for vol_stat in pkmn.volatile_status:
        try:
            score += Scoring.POKEMON_VOLATILE_STATUSES[vol_stat]
        except KeyError:
            pass

    return round(score)


def evaluate(state):
    score = 0

    number_of_opponent_reserve_revealed = len(state.opponent.reserve) + 1
    bot_alive_reserve_count = len([p.hp for p in state.user.reserve.values() if p.hp > 0])
    opponent_alive_reserves_count = len([p for p in state.opponent.reserve.values() if p.hp > 0]) + (6-number_of_opponent_reserve_revealed)

    # evaluate the bot's pokemon
    score += evaluate_pokemon(state.user.active)
    for pkmn in state.user.reserve.values():
        this_pkmn_score = evaluate_pokemon(pkmn)
        score += this_pkmn_score

    # evaluate the opponent's visible pokemon
    score -= evaluate_pokemon(state.opponent.active)
    for pkmn in state.opponent.reserve.values():
        this_pkmn_score = evaluate_pokemon(pkmn)
        score -= this_pkmn_score

    # evaluate the side-conditions for the bot
    for condition, count in state.user.side_conditions.items():
        if condition in Scoring.STATIC_SCORED_SIDE_CONDITIONS:
            score += count * Scoring.STATIC_SCORED_SIDE_CONDITIONS[condition]
        elif condition in Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS:
            score += count * Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS[condition] * bot_alive_reserve_count

    # evaluate the side-conditions for the opponent
    for condition, count in state.opponent.side_conditions.items():
        if condition in Scoring.STATIC_SCORED_SIDE_CONDITIONS:
            score -= count * Scoring.STATIC_SCORED_SIDE_CONDITIONS[condition]
        elif condition in Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS:
            score -= count * Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS[condition] * opponent_alive_reserves_count

    try:
        matchup_score = Scoring.MATCHUP_BONUS * effectiveness[state.user.active.id][state.opponent.active.id]
        matchup_score -= Scoring.MATCHUP_BONUS * effectiveness[state.opponent.active.id][state.user.active.id]
        score += matchup_score
    except KeyError:
        pass

    return int(score)


---

[9]. src/Ankimon/poke_engine/instruction_generator.py
Why this file is critical: Translates raw attacks into discrete status and damage instructions inside the engine.

from copy import copy

from . import constants
import logging

from .damage_calculator import type_effectiveness_modifier
from .special_effects.abilities.on_switch_in import ability_on_switch_in
from .special_effects.items.on_switch_in import item_on_switch_in
from .special_effects.items.end_of_turn import item_end_of_turn
from .special_effects.abilities.end_of_turn import ability_end_of_turn
from .special_effects.moves.after_move import after_move
from .special_effects.moves import move_special_effect

logger = logging.getLogger(__name__)


opposite_side = {
    constants.USER: constants.OPPONENT,
    constants.OPPONENT: constants.USER
}


same_side_strings = [
    constants.SELF,
    constants.ALLY_SIDE
]


opposing_side_strings = [
    constants.NORMAL,
    constants.OPPONENT,
    constants.FOESIDE,
    constants.ALL_ADJACENT_FOES,
    constants.ALL_ADJACENT,
    constants.ALL,
]


accuracy_multiplier_lookup = {
    -6: 3/9,
    -5: 3/8,
    -4: 3/7,
    -3: 3/6,
    -2: 3/5,
    -1: 3/4,
    0: 3/3,
    1: 4/3,
    2: 5/3,
    3: 6/3,
    4: 7/3,
    5: 8/3,
    6: 9/3
}





def get_instructions_from_move_special_effect(mutator, attacking_side, attacking_pokemon, defending_pokemon, move_name, instructions):
    if instructions.frozen:
        return [instructions]

    try:
        special_logic_move_function = getattr(move_special_effect, move_name)
    except AttributeError:
        new_instructions = list()
    else:
        mutator.apply(instructions.instructions)
        new_instructions = special_logic_move_function(mutator, attacking_side, get_side_from_state(mutator.state, attacking_side), attacking_pokemon, defending_pokemon)
        new_instructions = new_instructions or list()
        mutator.reverse(instructions.instructions)

    for i in new_instructions:
        instructions.add_instruction(i)

    return [instructions]


def get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, affected_side, first_move, instruction):
    if instruction.frozen or not volatile_status:
        return [instruction]

    if affected_side in same_side_strings:
        affected_side = attacker
    elif affected_side in opposing_side_strings:
        affected_side = opposite_side[attacker]
    else:
        logger.critical("Invalid affected_side: {}".format(affected_side))
        return [instruction]

    side = get_side_from_state(mutator.state, affected_side)
    mutator.apply(instruction.instructions)
    if volatile_status in side.active.volatile_status:
        mutator.reverse(instruction.instructions)
        return [instruction]

    if can_be_volatile_statused(side, volatile_status, first_move) and volatile_status not in side.active.volatile_status:
        apply_status_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            affected_side,
            volatile_status
        )
        mutator.reverse(instruction.instructions)
        instruction.add_instruction(apply_status_instruction)
        if volatile_status == constants.SUBSTITUTE:
            instruction.add_instruction(
                (
                    constants.MUTATOR_DAMAGE,
                    affected_side,
                    side.active.maxhp * 0.25
                )
            )
    else:
        mutator.reverse(instruction.instructions)

    return [instruction]


def get_instructions_from_switch(mutator, attacker, switch_pokemon_name, instructions):
    if attacker not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    attacking_side = get_side_from_state(mutator.state, attacker)
    defending_side = get_side_from_state(mutator.state, opposite_side[attacker])
    mutator.apply(instructions.instructions)
    instruction_additions = remove_volatile_status_and_boosts_instructions(attacking_side, attacker)
    mutator.apply(instruction_additions)

    for move in filter(lambda x: x[constants.DISABLED] is True and x[constants.CURRENT_PP], attacking_side.active.moves):
        remove_disabled_instruction = (
            constants.MUTATOR_ENABLE_MOVE,
            attacker,
            move[constants.ID]
        )
        mutator.apply_one(remove_disabled_instruction)
        instruction_additions.append(remove_disabled_instruction)

    if attacking_side.active.ability == 'regenerator' and attacking_side.active.hp:
        hp_missing = attacking_side.active.maxhp - attacking_side.active.hp
        regenerator_instruction = (
            constants.MUTATOR_HEAL,
            attacker,
            int(min(1 / 3 * attacking_side.active.maxhp, hp_missing))
        )
        mutator.apply_one(regenerator_instruction)
        instruction_additions.append(regenerator_instruction)
    elif attacking_side.active.ability == 'naturalcure' and attacking_side.active.status is not None:
        naturalcure_instruction = (
            constants.MUTATOR_REMOVE_STATUS,
            attacker,
            attacking_side.active.status
        )
        mutator.apply_one(naturalcure_instruction)
        instruction_additions.append(naturalcure_instruction)

    switch_instruction = (
        constants.MUTATOR_SWITCH,
        attacker,
        attacking_side.active.id,
        switch_pokemon_name
    )
    mutator.apply_one(switch_instruction)
    instruction_additions.append(switch_instruction)

    switch_pkmn = attacking_side.active
    if switch_pkmn.item != 'heavydutyboots':

        # account for stealth rock damage
        if attacking_side.side_conditions[constants.STEALTH_ROCK] == 1:
            multiplier = type_effectiveness_modifier('rock', switch_pkmn.types)
            stealth_rock_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(1 / 8 * multiplier * switch_pkmn.maxhp, switch_pkmn.hp)
            )
            mutator.apply_one(stealth_rock_instruction)
            instruction_additions.append(stealth_rock_instruction)

        # account for spikes damage
        if attacking_side.side_conditions[constants.SPIKES] > 0 and switch_pkmn.is_grounded():
            spike_count = attacking_side.side_conditions[constants.SPIKES]
            spikes_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(1 / 8 * spike_count * switch_pkmn.maxhp, switch_pkmn.hp)
            )
            mutator.apply_one(spikes_instruction)
            instruction_additions.append(spikes_instruction)

        # account for stickyweb speed drop
        if attacking_side.side_conditions[constants.STICKY_WEB] == 1 and switch_pkmn.is_grounded() and switch_pkmn.ability not in constants.IMMUNE_TO_STAT_LOWERING_ABILITIES:
            sticky_web_instruction = (
                constants.MUTATOR_UNBOOST,
                attacker,
                constants.SPEED,
                1
            )
            mutator.apply_one(sticky_web_instruction)
            instruction_additions.append(sticky_web_instruction)

        # account for toxic spikes effect
        if attacking_side.side_conditions[constants.TOXIC_SPIKES] >= 1 and switch_pkmn.is_grounded():
            toxic_spike_instruction = None
            if not immune_to_status(mutator.state, switch_pkmn, switch_pkmn, constants.POISON):
                if attacking_side.side_conditions[constants.TOXIC_SPIKES] == 1:
                    toxic_spike_instruction = (
                        constants.MUTATOR_APPLY_STATUS,
                        attacker,
                        constants.POISON
                    )
                elif attacking_side.side_conditions[constants.TOXIC_SPIKES] == 2:
                    toxic_spike_instruction = (
                        constants.MUTATOR_APPLY_STATUS,
                        attacker,
                        constants.TOXIC
                    )
            elif 'poison' in switch_pkmn.types:
                toxic_spike_instruction = (
                    constants.MUTATOR_SIDE_END,
                    attacker,
                    constants.TOXIC_SPIKES,
                    attacking_side.side_conditions[constants.TOXIC_SPIKES]
                )
            if toxic_spike_instruction is not None:
                mutator.apply_one(toxic_spike_instruction)
                instruction_additions.append(toxic_spike_instruction)

    # account for switch-in abilities
    ability_switch_in_instructions = ability_on_switch_in(
        switch_pkmn.ability,
        mutator.state,
        attacker,
        attacking_side.active,
        opposite_side[attacker],
        defending_side.active
    )
    if ability_switch_in_instructions is not None:
        for i in ability_switch_in_instructions:
            mutator.apply_one(i)
            instruction_additions.append(i)

    # account for switch-in items
    item_switch_in_instructions = item_on_switch_in(
        switch_pkmn.item,
        mutator.state,
        attacker,
        attacking_side.active,
        opposite_side[attacker],
        defending_side.active
    )
    if item_switch_in_instructions is not None:
        for i in item_switch_in_instructions:
            mutator.apply_one(i)
            instruction_additions.append(i)

    mutator.reverse(instruction_additions)
    mutator.reverse(instructions.instructions)
    for i in instruction_additions:
        instructions.add_instruction(i)

    return instructions


def get_instructions_from_flinched(mutator, attacker, instruction):
    """If the attacker has been flinched, freeze the state so that nothing happens"""
    if attacker not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    side = get_side_from_state(mutator.state, attacker)
    if constants.FLINCH in side.active.volatile_status:
        remove_flinch_instruction = (
            constants.MUTATOR_REMOVE_VOLATILE_STATUS,
            attacker,
            constants.FLINCH
        )
        mutator.apply_one(remove_flinch_instruction)
        instruction.add_instruction(remove_flinch_instruction)
        instruction.frozen = True
        return instruction
    else:
        return instruction


def get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, move, opponent_move, instruction):
    instructions = [instruction]
    attacker_side = get_side_from_state(mutator.state, attacker)
    defender_side = get_side_from_state(mutator.state, defender)

    mutator.apply(instruction.instructions)

    if constants.PARALYZED == attacker_side.active.status:
        fully_paralyzed_instruction = copy(instruction)
        fully_paralyzed_instruction.update_percentage(constants.FULLY_PARALYZED_PERCENT)
        fully_paralyzed_instruction.frozen = True
        instruction.update_percentage(1 - constants.FULLY_PARALYZED_PERCENT)
        instructions.append(fully_paralyzed_instruction)

    elif constants.SLEEP == attacker_side.active.status:
        still_asleep_instruction = copy(instruction)
        still_asleep_instruction.update_percentage(1 - constants.WAKE_UP_PERCENT)
        still_asleep_instruction.frozen = True
        instruction.update_percentage(constants.WAKE_UP_PERCENT)
        instruction.add_instruction(
            (
                constants.MUTATOR_REMOVE_STATUS,
                attacker,
                constants.SLEEP
            )
        )
        instructions.append(still_asleep_instruction)

    elif constants.FROZEN == attacker_side.active.status:
        still_frozen_instruction = copy(instruction)
        instruction.add_instruction(
            (
                constants.MUTATOR_REMOVE_STATUS,
                attacker,
                constants.FROZEN
            )
        )
        if move[constants.ID] not in constants.THAW_IF_USES and opponent_move.get(constants.ID) not in constants.THAW_IF_HIT_BY and opponent_move.get(constants.TYPE) != 'fire':
            still_frozen_instruction.update_percentage(1 - constants.THAW_PERCENT)
            still_frozen_instruction.frozen = True
            instruction.update_percentage(constants.THAW_PERCENT)
            instructions.append(still_frozen_instruction)

    if constants.POWDER in move[constants.FLAGS] and ('grass' in defender_side.active.types or defender_side.active.ability == 'overcoat'):
        instruction.frozen = True

    if move[constants.TYPE] == 'electric' and 'ground' in defender_side.active.types:
        instruction.frozen = True

    mutator.reverse(instruction.instructions)

    return instructions


def get_instructions_from_damage(mutator, defender, damage, accuracy, attacking_move, instruction):
    attacker = opposite_side[defender]
    attacker_side = get_side_from_state(mutator.state, attacker)
    damage_side = get_side_from_state(mutator.state, defender)

    # `damage is None` means that the move does not deal damage
    # for example, will-o-wisp
    if instruction.frozen or damage is None:
        return [instruction]

    crash = attacking_move.get(constants.CRASH)
    recoil = attacking_move.get(constants.RECOIL)
    drain = attacking_move.get(constants.DRAIN)
    move_flags = attacking_move.get(constants.FLAGS, {})

    mutator.apply(instruction.instructions)

    if accuracy is True or "glaiverush" in damage_side.active.volatile_status:
        accuracy = 100
    else:
        accuracy = min(100, accuracy * accuracy_multiplier_lookup[attacker_side.active.accuracy_boost] / accuracy_multiplier_lookup[damage_side.active.evasion_boost])
    percent_hit = accuracy / 100

    # `damage == 0` means that the move deals damage, but not in this situation
    # for example: using Return against a Ghost-type
    # the state must be frozen because any secondary effects must not take place
    if damage == 0:
        if crash:
            crash_percent = crash[0] / crash[1]
            crash_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(int(crash_percent * attacker_side.active.maxhp), attacker_side.active.hp)
            )
            mutator.reverse(instruction.instructions)
            instruction.add_instruction(crash_instruction)
        else:
            mutator.reverse(instruction.instructions)
        instruction.frozen = True
        return [instruction]

    if defender not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    instructions = []
    instruction_additions = []
    move_missed_instruction = copy(instruction)
    hit_sub = False
    if percent_hit > 0:
        if constants.SUBSTITUTE in damage_side.active.volatile_status and constants.SOUND not in move_flags and attacker_side.active.ability != 'infiltrator':
            hit_sub = True
            if damage >= damage_side.active.maxhp * 0.25:
                actual_damage = damage_side.active.maxhp * 0.25
                instruction_additions.append(
                    (
                        constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                        defender,
                        constants.SUBSTITUTE
                    )
                )
            else:
                actual_damage = damage
        else:
            # dont drop hp below 0 (min() statement), and dont overheal (max() statement)
            actual_damage = max(min(damage, damage_side.active.hp), -1*(damage_side.active.maxhp - damage_side.active.hp))

            if damage_side.active.ability == 'sturdy' and damage_side.active.hp == damage_side.active.maxhp:
                actual_damage -= 1

            instruction_additions.append(
                (
                    constants.MUTATOR_DAMAGE,
                    defender,
                    actual_damage
                )
            )

            if attacker_side.active.ability == "beastboost" and actual_damage == damage_side.active.hp:
                highest_stat = attacker_side.active.get_highest_stat()
                if attacker_side.active.get_boost_from_boost_string(highest_stat) < 6:
                    instruction_additions.append(
                        (
                            constants.MUTATOR_BOOST,
                            attacker,
                            highest_stat,
                            1
                        )
                    )

        instruction.update_percentage(percent_hit)

        if damage_side.active.hp <= 0:
            instruction.frozen = True

        if drain:
            drain_percent = drain[0] / drain[1]
            drain_instruction = (
                constants.MUTATOR_HEAL,
                attacker,
                min(int(drain_percent * actual_damage), int(attacker_side.active.maxhp - attacker_side.active.hp))
            )
            instruction_additions.append(drain_instruction)
        if recoil:
            recoil_percent = recoil[0] / recoil[1]
            recoil_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(int(recoil_percent * actual_damage), int(attacker_side.active.hp))
            )
            instruction_additions.append(recoil_instruction)

        after_move_instructions = after_move(
            attacking_move[constants.ID],
            mutator.state,
            attacker,
            defender,
            attacker_side,
            damage_side,
            True,
            hit_sub
        )
        instruction_additions += after_move_instructions

        instructions.append(instruction)

    if percent_hit < 1:
        move_missed_instruction.frozen = True
        move_missed_instruction.update_percentage(1 - percent_hit)
        if crash:
            crash_percent = crash[0] / crash[1]
            crash_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(int(crash_percent * attacker_side.active.maxhp), attacker_side.active.hp)
            )
            move_missed_instruction.add_instruction(crash_instruction)

        if attacker_side.active.item == 'blunderpolicy':
            blunder_policy_increase_speed_instruction = (
                constants.MUTATOR_BOOST,
                attacker,
                constants.SPEED,
                2
            )
            move_missed_instruction.add_instruction(blunder_policy_increase_speed_instruction)

        after_move_instructions = after_move(
            attacking_move[constants.ID],
            mutator.state,
            attacker,
            defender,
            attacker_side,
            damage_side,
            False,
            False
        )
        for i in after_move_instructions:
            move_missed_instruction.add_instruction(i)

        instructions.append(move_missed_instruction)

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return instructions


def get_instructions_from_defenders_ability_after_move(mutator, move, ability_name, attacking_pokemon, attacker_string, instruction):
    all_instructions = [instruction]
    if instruction.frozen:
        return all_instructions

    if attacker_string not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    if (
        ability_name == "static"
        and constants.CONTACT in move[constants.FLAGS]
        and attacking_pokemon.item != "protectivepads"
    ):
        return get_instructions_from_status_effects(
            mutator,
            attacker_string,
            constants.PARALYZED,
            30,
            instruction
        )
    elif (
        ability_name == "flamebody"
        and constants.CONTACT in move[constants.FLAGS]
        and attacking_pokemon.item != "protectivepads"
    ):
        return get_instructions_from_status_effects(
            mutator,
            attacker_string,
            constants.BURN,
            30,
            instruction
        )

    return all_instructions


def get_instructions_from_side_conditions(mutator, attacker_string, side_string, condition, instruction):
    if instruction.frozen:
        return [instruction]

    if attacker_string not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    if side_string in same_side_strings:
        side_string = attacker_string
    elif side_string in opposing_side_strings:
        side_string = opposite_side[attacker_string]
    else:
        raise ValueError("Invalid Side String: {}".format(side_string))

    instruction_additions = []
    side = get_side_from_state(mutator.state, side_string)
    mutator.apply(instruction.instructions)

    if condition == constants.WISH:
        if side.wish[0] == 0:
            instruction_additions.append(
                (
                    constants.MUTATOR_WISH_START,
                    side_string,
                    side.active.maxhp / 2,
                    side.wish[1]
                )
            )

    else:
        if condition == constants.SPIKES:
            max_layers = 3
        elif condition == constants.TOXIC_SPIKES:
            max_layers = 2
        elif condition == constants.AURORA_VEIL:
            max_layers = 1 if mutator.state.weather in constants.HAIL_OR_SNOW else 0
        else:
            max_layers = 1

        if side.side_conditions[condition] < max_layers:
            instruction_additions.append(
                (
                    constants.MUTATOR_SIDE_START,
                    side_string,
                    condition,
                    1
                )
            )

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return [instruction]


def get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, instruction):
    if instruction.frozen:
        return [instruction]

    if attacker_string not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    defender_string = opposite_side[attacker_string]

    instruction_additions = []
    mutator.apply(instruction.instructions)

    attacker_side = get_side_from_state(mutator.state, attacker_string)
    defender_side = get_side_from_state(mutator.state, defender_string)

    if move[constants.ID] == 'defog':
        if mutator.state.field is not None:
            instruction_additions.append(
                (
                    constants.MUTATOR_FIELD_END,
                    mutator.state.field
                )
            )
        for side_condition, amount in attacker_side.side_conditions.items():
            if amount > 0 and side_condition in constants.DEFOG_CLEARS:
                instruction_additions.append(
                    (
                        constants.MUTATOR_SIDE_END,
                        attacker_string,
                        side_condition,
                        amount
                    )
                )
        for side_condition, amount in defender_side.side_conditions.items():
            if amount > 0 and side_condition in constants.DEFOG_CLEARS:
                instruction_additions.append(
                    (
                        constants.MUTATOR_SIDE_END,
                        defender_string,
                        side_condition,
                        amount
                    )
                )

    # ghost-type misses are dealt with by freezing the state. i.e. this elif will not be reached if the move missed
    elif move[constants.ID] == "rapidspin" or move[constants.ID] == "mortalspin" or move[constants.ID] == "tidyup":
        side = get_side_from_state(mutator.state, attacker_string)
        for side_condition, amount in side.side_conditions.items():
            if amount > 0 and side_condition in constants.SPIN_TIDYUP_CLEARS:
                instruction_additions.append(
                    (
                        constants.MUTATOR_SIDE_END,
                        attacker_string,
                        side_condition,
                        amount
                    )
                )
    elif move[constants.ID] == constants.COURT_CHANGE:
        sides = [
            (constants.USER, mutator.state.user),
            (constants.OPPONENT, mutator.state.opponent)
        ]
        for side_name, side_object in sides:
            for side_condition in side_object.side_conditions:
                if side_object.side_conditions[side_condition] and side_condition in constants.COURT_CHANGE_SWAPS:
                    instruction_additions.append(
                        (
                            constants.MUTATOR_SIDE_END,
                            side_name,
                            side_condition,
                            side_object.side_conditions[side_condition]
                        )
                    )
                    instruction_additions.append(
                        (
                            constants.MUTATOR_SIDE_START,
                            opposite_side[side_name],
                            side_condition,
                            side_object.side_conditions[side_condition]
                        )
                    )

    else:
        raise ValueError("{} is not a hazard clearing move".format(move[constants.ID]))

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return [instruction]


def get_instructions_from_status_effects(mutator, defender, status, accuracy, instruction):
    """Returns the possible states from status effects"""
    if instruction.frozen or status is None:
        return [instruction]

    if defender not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    instructions = []
    if accuracy is True:
        accuracy = 100
    percent_hit = accuracy / 100

    mutator.apply(instruction.instructions)
    instruction_additions = []
    defending_side = get_side_from_state(mutator.state, defender)
    attacking_side = get_side_from_state(mutator.state, opposite_side[defender])

    if sleep_clause_activated(defending_side, status):
        mutator.reverse(instruction.instructions)
        return [instruction]

    if immune_to_status(mutator.state, defending_side.active, attacking_side.active, status):
        mutator.reverse(instruction.instructions)
        return [instruction]

    move_missed_instruction = copy(instruction)
    if percent_hit > 0:
        move_hit_instruction = (
            constants.MUTATOR_APPLY_STATUS,
            defender,
            status
        )

        instruction_additions.append(move_hit_instruction)
        instruction.update_percentage(percent_hit)
        instructions.append(instruction)

    if percent_hit < 1:
        move_missed_instruction.frozen = True
        move_missed_instruction.update_percentage(1 - percent_hit)
        if attacking_side.active.item == 'blunderpolicy':
            blunder_policy_increase_speed_instruction = (
                constants.MUTATOR_BOOST,
                opposite_side[defender],
                constants.SPEED,
                2
            )
            move_missed_instruction.add_instruction(blunder_policy_increase_speed_instruction)
        instructions.append(move_missed_instruction)

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return instructions


def get_instructions_from_boosts(mutator, side_string, boosts, accuracy, instruction):
    if instruction.frozen or not boosts:
        return [instruction]

    if side_string not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}. Value: {}".format(
            ', '.join(opposite_side),
            side_string
        )
        )

    instructions = []
    if accuracy is True:
        accuracy = 100
    percent_hit = accuracy / 100

    mutator.apply(instruction.instructions)
    side = get_side_from_state(mutator.state, side_string)

    instruction_additions = []
    move_missed_instruction = copy(instruction)
    if percent_hit > 0:
        for k, v in boosts.items():
            pkmn_boost = side.active.get_boost_from_boost_string(k)
            if v > 0:
                new_boost = pkmn_boost + v
                if new_boost > constants.MAX_BOOSTS:
                    new_boost = constants.MAX_BOOSTS
                boost_instruction = (
                    constants.MUTATOR_BOOST,
                    side_string,
                    k,
                    new_boost - pkmn_boost
                )
                instruction_additions.append(boost_instruction)
            elif (
                side.active.ability not in constants.IMMUNE_TO_STAT_LOWERING_ABILITIES and
                side.active.item not in constants.IMMUNE_TO_STAT_LOWERING_ITEMS
            ):
                new_boost = pkmn_boost + v
                if new_boost < -1 * constants.MAX_BOOSTS:
                    new_boost = -1 * constants.MAX_BOOSTS
                boost_instruction = (
                    constants.MUTATOR_BOOST,
                    side_string,
                    k,
                    new_boost - pkmn_boost
                )
                instruction_additions.append(boost_instruction)

        instruction.update_percentage(percent_hit)
        instructions.append(instruction)

    if percent_hit < 1:
        move_missed_instruction.update_percentage(1 - percent_hit)
        instructions.append(move_missed_instruction)

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return instructions


def get_instructions_from_flinching_moves(defender, accuracy, first_move, instruction):
    if instruction.frozen or not first_move:
        return [instruction]

    if defender not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    instructions = []
    if accuracy is True:
        accuracy = 100
    percent_hit = accuracy / 100

    if percent_hit > 0:
        flinched_instruction = copy(instruction)
        flinch_mutator_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )
        flinched_instruction.add_instruction(flinch_mutator_instruction)
        flinched_instruction.update_percentage(percent_hit)
        instructions.append(flinched_instruction)

    if percent_hit < 1:
        instruction.update_percentage(1 - percent_hit)
        instructions.append(instruction)

    return instructions


def get_instructions_from_attacker_recovery(mutator, attacker_string, move, instruction):
    if instruction.frozen:
        return [instruction]

    mutator.apply(instruction.instructions)

    target = move[constants.HEAL_TARGET]
    if target in opposing_side_strings:
        side_string = opposite_side[attacker_string]
    else:
        side_string = attacker_string

    pkmn = get_side_from_state(mutator.state, side_string).active
    try:
        health_recovered = float(move[constants.HEAL][0] / move[constants.HEAL][1]) * pkmn.maxhp
    except KeyError:
        health_recovered = 0

    if health_recovered == 0:
        mutator.reverse(instruction.instructions)
        return [instruction]

    final_health = pkmn.hp + health_recovered
    if final_health > pkmn.maxhp:
        health_recovered -= (final_health - pkmn.maxhp)
    elif final_health < 0:
        health_recovered -= final_health

    heal_instruction = (
        constants.MUTATOR_HEAL,
        side_string,
        health_recovered
    )

    mutator.reverse(instruction.instructions)

    if health_recovered:
        instruction.add_instruction(heal_instruction)

    return [instruction]


def get_end_of_turn_instructions(mutator, instruction, bot_move, opponent_move, bot_moves_first):
    # determine which goes first
    if bot_moves_first:
        sides = [constants.USER, constants.OPPONENT]
    else:
        sides = [constants.OPPONENT, constants.USER]

    mutator.apply(instruction.instructions)

    # weather damage - sand and hail
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        pkmn = side.active

        if pkmn.ability == 'magicguard' or not pkmn.hp:
            continue

        if mutator.state.weather == constants.SAND and not any(t in pkmn.types for t in ['steel', 'rock', 'ground']):
            sand_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                max(0, int(min(pkmn.maxhp * 0.0625, pkmn.hp)))
            )
            mutator.apply_one(sand_damage_instruction)
            instruction.add_instruction(sand_damage_instruction)

        elif mutator.state.weather == constants.HAIL and 'ice' not in pkmn.types and pkmn.ability != 'icebody':
            ice_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                max(0, int(min(pkmn.maxhp * 0.0625, pkmn.hp)))
            )
            mutator.apply_one(ice_damage_instruction)
            instruction.add_instruction(ice_damage_instruction)

    # futuresight
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        if side.future_sight[0] == 1:
            from .damage_calculator import calculate_futuresight_damage
            damage_dealt = calculate_futuresight_damage(
                mutator.state,
                attacker,
                side.future_sight[1]
            )[0]
            if damage_dealt:
                futuresight_damage_instruction = (
                    constants.MUTATOR_DAMAGE,
                    opposite_side[attacker],
                    damage_dealt
                )
                mutator.apply_one(futuresight_damage_instruction)
                instruction.add_instruction(futuresight_damage_instruction)
        if side.future_sight[0] > 0:
            futuresight_decrement_instruction = (
                constants.MUTATOR_FUTURESIGHT_DECREMENT,
                attacker,
            )
            mutator.apply_one(futuresight_decrement_instruction)
            instruction.add_instruction(futuresight_decrement_instruction)

    # wish
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        if side.wish[0] == 1 and 0 < side.active.hp < side.active.maxhp:
            wish_heal_instruction = (
                constants.MUTATOR_HEAL,
                attacker,
                min(side.wish[1], side.active.maxhp - side.active.hp)
            )
            mutator.apply_one(wish_heal_instruction)
            instruction.add_instruction(wish_heal_instruction)
        if side.wish[0] > 0:
            wish_decrement_instruction = (
                constants.MUTATOR_WISH_DECREMENT,
                attacker
            )
            mutator.apply_one(wish_decrement_instruction)
            instruction.add_instruction(wish_decrement_instruction)

    # item and ability - they can add one instruction each
    for attacker in sides:
        defender = opposite_side[attacker]
        side = get_side_from_state(mutator.state, attacker)
        defending_side = get_side_from_state(mutator.state, defender)
        pkmn = side.active
        defending_pkmn = defending_side.active

        item_instruction = item_end_of_turn(side.active.item, mutator.state, attacker, pkmn, defender, defending_pkmn)
        if item_instruction is not None:
            mutator.apply_one(item_instruction)
            instruction.add_instruction(item_instruction)

        ability_instruction = ability_end_of_turn(side.active.ability, mutator.state, attacker, pkmn, defender, defending_pkmn)
        if ability_instruction is not None:
            mutator.apply_one(ability_instruction)
            instruction.add_instruction(ability_instruction)

    # poison, toxic, and burn damage
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        pkmn = side.active

        if pkmn.ability == 'magicguard' or not pkmn.hp:
            continue

        if constants.TOXIC == pkmn.status and pkmn.ability != 'poisonheal':
            toxic_count = side.side_conditions[constants.TOXIC_COUNT]
            toxic_multiplier = (1 / 16) * toxic_count + (1 / 16)
            toxic_damage = max(0, int(min(pkmn.maxhp * toxic_multiplier, pkmn.hp)))

            toxic_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                toxic_damage
            )
            toxic_count_instruction = (
                constants.MUTATOR_SIDE_START,
                attacker,
                constants.TOXIC_COUNT,
                1
            )
            mutator.apply_one(toxic_damage_instruction)
            mutator.apply_one(toxic_count_instruction)

            instruction.add_instruction(toxic_damage_instruction)
            instruction.add_instruction(toxic_count_instruction)

        elif constants.BURN == pkmn.status:
            burn_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                max(0, int(min(pkmn.maxhp * 0.0625, pkmn.hp)))
            )
            mutator.apply_one(burn_damage_instruction)
            instruction.add_instruction(burn_damage_instruction)

        elif constants.POISON == pkmn.status and pkmn.ability != 'poisonheal':
            poison_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                max(0, int(min(pkmn.maxhp * 0.125, pkmn.hp)))
            )
            mutator.apply_one(poison_damage_instruction)
            instruction.add_instruction(poison_damage_instruction)

    # leechseed sap damage
    for attacker in sides:
        defender = opposite_side[attacker]
        side = get_side_from_state(mutator.state, attacker)
        defending_side = get_side_from_state(mutator.state, defender)
        pkmn = side.active
        defending_pkmn = defending_side.active

        if pkmn.ability == 'magicguard' or not pkmn.hp or not defending_pkmn.hp:
            continue

        if constants.LEECH_SEED in pkmn.volatile_status:
            # damage taken
            damage_sapped = max(0, int(min(pkmn.maxhp * 0.125, pkmn.hp)))
            sap_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                damage_sapped
            )

            # heal amount
            damage_from_full = defending_pkmn.maxhp - defending_pkmn.hp
            heal_instruction = (
                constants.MUTATOR_HEAL,
                defender,
                min(damage_sapped, damage_from_full)
            )

            mutator.apply_one(sap_instruction)
            mutator.apply_one(heal_instruction)
            instruction.add_instruction(sap_instruction)
            instruction.add_instruction(heal_instruction)

    # volatile-statuses
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        pkmn = side.active

        if any(vs in constants.PROTECT_VOLATILE_STATUSES for vs in pkmn.volatile_status):
            if constants.PROTECT in pkmn.volatile_status:
                volatile_status_to_remove = constants.PROTECT
            elif constants.BANEFUL_BUNKER in pkmn.volatile_status:
                volatile_status_to_remove = constants.BANEFUL_BUNKER
            elif constants.SPIKY_SHIELD in pkmn.volatile_status:
                volatile_status_to_remove = constants.SPIKY_SHIELD
            elif constants.SILK_TRAP in pkmn.volatile_status:
                volatile_status_to_remove = constants.SILK_TRAP
            else:
                # should never happen
                raise Exception("Pokemon has volatile status that is not caught here: {}".format(pkmn.volatile_status))

            remove_protect_volatile_status_instruction = (
                constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                attacker,
                volatile_status_to_remove
            )
            start_protect_side_condition_instruction = (
                    constants.MUTATOR_SIDE_START,
                    attacker,
                    constants.PROTECT,
                    1
            )
            mutator.apply_one(remove_protect_volatile_status_instruction)
            mutator.apply_one(start_protect_side_condition_instruction)
            instruction.add_instruction(remove_protect_volatile_status_instruction)
            instruction.add_instruction(start_protect_side_condition_instruction)

        elif side.side_conditions[constants.PROTECT]:
            end_protect_side_condition_instruction = (
                constants.MUTATOR_SIDE_END,
                attacker,
                constants.PROTECT,
                side.side_conditions[constants.PROTECT]
            )
            mutator.apply_one(end_protect_side_condition_instruction)
            instruction.add_instruction(end_protect_side_condition_instruction)

        if constants.ROOST in pkmn.volatile_status:
            remove_roost_instruction = (
                constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                attacker,
                constants.ROOST,
            )
            mutator.apply_one(remove_roost_instruction)
            instruction.add_instruction(remove_roost_instruction)

        if constants.PARTIALLY_TRAPPED in pkmn.volatile_status:
            damage_taken = max(0, int(min(pkmn.maxhp * 0.125, pkmn.hp)))
            partially_trapped_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                damage_taken
            )
            mutator.apply_one(partially_trapped_damage_instruction)
            instruction.add_instruction(partially_trapped_damage_instruction)

        if "saltcure" in pkmn.volatile_status:
            divisor = 4 if any(t in pkmn.types for t in ["water", "steel"]) else 8
            damage_taken = max(0, int(min(pkmn.maxhp * (1/divisor), pkmn.hp)))
            partially_trapped_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                damage_taken
            )
            mutator.apply_one(partially_trapped_damage_instruction)
            instruction.add_instruction(partially_trapped_damage_instruction)

    # disable not used moves if choice-item is held
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        pkmn = side.active

        if attacker == constants.USER:
            move = bot_move
            other_move = opponent_move
        else:
            move = opponent_move
            other_move = bot_move

        try:
            locking_move = move[constants.SELF][constants.VOLATILE_STATUS] == constants.LOCKED_MOVE
        except KeyError:
            locking_move = False

        if (
            constants.SWITCH_STRING not in move and
            constants.DRAG not in other_move.get(constants.FLAGS, {}) and
            move[constants.ID] not in constants.SWITCH_OUT_MOVES and
            (pkmn.item in constants.CHOICE_ITEMS or locking_move or pkmn.ability == 'gorillatactics')
        ):
            move_used = move[constants.ID]
            for m in filter(
                lambda x: x[constants.ID] != move_used and not x.get(constants.DISABLED, False),
                pkmn.moves
            ):
                disable_instruction = (
                    constants.MUTATOR_DISABLE_MOVE,
                    attacker,
                    m[constants.ID]
                )
                mutator.apply_one(disable_instruction)
                instruction.add_instruction(disable_instruction)

    mutator.reverse(instruction.instructions)

    return [instruction]


def get_instructions_from_drag(mutator, attacking_side_string, move_target, instruction):
    if instruction.frozen:
        return [instruction]

    new_instructions = []

    if move_target in same_side_strings:
        affected_side = get_side_from_state(mutator.state, attacking_side_string)
        affected_side_string = attacking_side_string
    elif move_target in opposing_side_strings:
        affected_side = get_side_from_state(mutator.state, opposite_side[attacking_side_string])
        affected_side_string = opposite_side[attacking_side_string]
    else:
        raise ValueError("Invalid value for move_target: {}".format(move_target))

    mutator.apply(instruction.instructions)
    alive_reserves = [s.id for s in affected_side.reserve.values() if s.hp > 0]
    num_reserve_alive = len(alive_reserves)
    mutator.reverse(instruction.instructions)
    if num_reserve_alive == 0:
        return [instruction]

    for pkmn_name in alive_reserves:
        new_instruction = get_instructions_from_switch(mutator, affected_side_string, pkmn_name, copy(instruction))
        new_instruction.update_percentage(1 / num_reserve_alive)
        new_instructions.append(new_instruction)

    return new_instructions


def get_instructions_from_boost_reset_moves(mutator, attacking_move, attacking_side_string, instruction):
    if instruction.frozen:
        return [instruction]

    attacking_side = get_side_from_state(mutator.state, attacking_side_string)
    defending_side_string = opposite_side[attacking_side_string]
    defending_side = get_side_from_state(mutator.state, defending_side_string)

    mutator.apply(instruction.instructions)
    new_instructions = []
    if attacking_move[constants.TARGET] in constants.MOVE_TARGET_SELF:
        new_instructions += remove_volatile_status_and_boosts_instructions(attacking_side, attacking_side_string)
    if attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        new_instructions += remove_volatile_status_and_boosts_instructions(defending_side, defending_side_string)
    mutator.reverse(instruction.instructions)

    for new_instruction in new_instructions:
        instruction.add_instruction(new_instruction)

    return [instruction]


def remove_volatile_status_and_boosts_instructions(side, side_string):
    instruction_additions = []
    for v_status in side.active.volatile_status:
        instruction_additions.append(
            (
                constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                side_string,
                v_status
            )
        )
    if side.side_conditions[constants.TOXIC_COUNT]:
        instruction_additions.append(
            (
                constants.MUTATOR_SIDE_END,
                side_string,
                constants.TOXIC_COUNT,
                side.side_conditions[constants.TOXIC_COUNT]
            ))
    if side.active.attack_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.ATTACK,
                side.active.attack_boost
            ))
    if side.active.defense_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.DEFENSE,
                side.active.defense_boost
            ))
    if side.active.special_attack_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.SPECIAL_ATTACK,
                side.active.special_attack_boost
            ))
    if side.active.special_defense_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.SPECIAL_DEFENSE,
                side.active.special_defense_boost
            ))
    if side.active.speed_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.SPEED,
                side.active.speed_boost
            ))

    return instruction_additions


def get_side_from_state(state, side_string):
    if side_string == constants.USER:
        return state.user
    elif side_string == constants.OPPONENT:
        return state.opponent
    else:
        raise ValueError("Invalid value for `side`")


def can_be_volatile_statused(side, volatile_status, first_move):
    if volatile_status in constants.PROTECT_VOLATILE_STATUSES:
        if side.side_conditions[constants.PROTECT]:
            return False
        elif first_move:
            return True
        else:
            return False
    if constants.SUBSTITUTE in side.active.volatile_status:
        return False
    if volatile_status == constants.SUBSTITUTE and side.active.hp < side.active.maxhp * 0.25:
        return False

    return True


def sleep_clause_activated(side, status):
    if status == constants.SLEEP:
        for p in side.reserve.values():
            if p.status == constants.SLEEP and p.hp > 0:
                return True
    return False


def immune_to_status(state, defending_pkmn, attacking_pkmn, status):
    # General status immunity
    if defending_pkmn.status is not None or defending_pkmn.hp <= 0:
        return True
    if constants.SUBSTITUTE in defending_pkmn.volatile_status and attacking_pkmn.ability != 'infiltrator':
        return True
    if defending_pkmn.ability == 'shieldsdown' and ((defending_pkmn.hp / defending_pkmn.maxhp) > 0.5):
        return True
    if defending_pkmn.ability == 'comatose':
        return True
    if state.field == constants.MISTY_TERRAIN and defending_pkmn.is_grounded():
        return True
    if defending_pkmn.ability == "purifyingsalt":
        return True
    if defending_pkmn.ability == "thermalexchange" and status == constants.BURN:
        return True

    # Specific status immunity
    return (
        status == constants.FROZEN and is_immune_to_freeze(state, defending_pkmn) or
        status == constants.BURN and is_immune_to_burn(defending_pkmn) or
        status == constants.SLEEP and is_immune_to_sleep(state, defending_pkmn) or
        status == constants.PARALYZED and is_immune_to_paralysis(defending_pkmn) or
        status in [constants.POISON, constants.TOXIC] and is_immune_to_poison(attacking_pkmn, defending_pkmn)
    )


def is_immune_to_freeze(state, pkmn):
    return (
        'ice' in pkmn.types or
        pkmn.ability in constants.IMMUNE_TO_FROZEN_ABILITIES or
        state.weather == constants.DESOLATE_LAND
    )


def is_immune_to_burn(pkmn):
    return (
        'fire' in pkmn.types or
        pkmn.ability in constants.IMMUNE_TO_BURN_ABILITIES
    )


def is_immune_to_sleep(state, pkmn):
    return (
        pkmn.ability in constants.IMMUNE_TO_SLEEP_ABILITIES or
        state.field == constants.ELECTRIC_TERRAIN and pkmn.is_grounded()
    )


def is_immune_to_poison(attacking, defending):
    return (
        any(t in ['poison', 'steel'] for t in defending.types) and not attacking.ability == 'corrosion'  or
        defending.ability in constants.IMMUNE_TO_POISON_ABILITIES
    )


def is_immune_to_paralysis(pkmn):
    return (
        'electric' in pkmn.types or
        pkmn.ability in constants.IMMUNE_TO_PARALYSIS_ABILITIES
    )

---

[10]. src/Ankimon/poke_engine/damage_calculator.py
Why this file is critical: Applies base power, STAB, type multipliers, and RNG for damage.

from copy import copy
from copy import deepcopy

from . import constants
from .data import all_move_json
from .data import pokedex


pokemon_type_indicies = {
    'normal': 0,
    'fire': 1,
    'water': 2,
    'electric': 3,
    'grass': 4,
    'ice': 5,
    'fighting': 6,
    'poison': 7,
    'ground': 8,
    'flying': 9,
    'psychic': 10,
    'bug': 11,
    'rock': 12,
    'ghost': 13,
    'dragon': 14,
    'dark': 15,
    'steel': 16,
    'fairy': 17,

    # ??? and typeless are the same thing
    'typeless': 18,
    '???': 18,
}

# Note : I changed the 0s to 1/8. Also, the following matrix seems to be taken from https://pokemondb.net/type
damage_multipication_array = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1/2, 1/8, 1, 1, 1/2, 1, 1],
                              [1, 1/2, 1/2, 1, 2, 2, 1, 1, 1, 1, 1, 2, 1/2, 1, 1/2, 1, 2, 1, 1],
                              [1, 2, 1/2, 1, 1/2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1/2, 1, 1, 1, 1],
                              [1, 1, 2, 1/2, 1/2, 1, 1, 1, 1/8, 2, 1, 1, 1, 1, 1/2, 1, 1, 1, 1],
                              [1, 1/2, 2, 1, 1/2, 1, 1, 1/2, 2, 1/2, 1, 1/2, 2, 1, 1/2, 1, 1/2, 1, 1],
                              [1, 1/2, 1/2, 1, 2, 1/2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1/2, 1, 1],
                              [2, 1, 1, 1, 1, 2, 1, 1/2, 1, 1/2, 1/2, 1/2, 2, 1/8, 1, 2, 2, 1/2, 1],
                              [1, 1, 1, 1, 2, 1, 1, 1/2, 1/2, 1, 1, 1, 1/2, 1/2, 1, 1, 1/8, 2, 1],
                              [1, 2, 1, 2, 1/2, 1, 1, 2, 1, 1/8, 1, 1/2, 2, 1, 1, 1, 2, 1, 1],
                              [1, 1, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1/2, 1, 1],
                              [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1/2, 1, 1, 1, 1, 1/8, 1/2, 1, 1],
                              [1, 1/2, 1, 1, 2, 1, 1/2, 1/2, 1, 1/2, 2, 1, 1, 1/2, 1, 2, 1/2, 1/2, 1],
                              [1, 2, 1, 1, 1, 2, 1/2, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 1/2, 1, 1],
                              [1/8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1/2, 1/8, 1],
                              [1, 1, 1, 1, 1, 1, 1/2, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1/2, 1],
                              [1, 1/2, 1/2, 1/2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1/2, 2, 1],
                              [1, 1/2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1, 1, 1, 2, 2, 1/2, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]


SPECIAL_LOGIC_MOVES = {
    "seismictoss": lambda attacker, defender: [int(attacker.level)] if "ghost" not in defender.types else None,
    "nightshade": lambda attacker, defender: [int(attacker.level)] if "normal" not in defender.types else None,
    "superfang": lambda attacker, defender: [int(defender.hp / 2)] if "ghost" not in defender.types else None,
    "naturesmadness": lambda attacker, defender: [int(defender.hp / 2)],
    "guardianofalola": lambda attacker, defender: [int(3*defender.hp / 4)],
    "ruination": lambda attacker, defender: [int(defender.hp / 2)],
    "finalgambit": lambda attacker, defender: [int(attacker.hp)] if "ghost" not in defender.types else None,
    "endeavor": lambda attacker, defender: [int(defender.hp - attacker.hp)] if defender.hp > attacker.hp and "ghost" not in defender.types else None,
    "painsplit": lambda attacker, defender: [defender.hp - (attacker.hp + defender.hp)/2],
}


TERRAIN_DAMAGE_BOOST = 1.3


def _calculate_damage(attacker, defender, move, conditions=None, calc_type='average'):
    # This function assumes the `move` dictionary has already been updated to account for move/item/ability special-effects
    # You may want to use `calculate_damage`

    acceptable_calc_types = ['average', 'min', 'max', 'min_max', 'min_max_average', 'all']
    if calc_type not in acceptable_calc_types:
        raise ValueError("{} is not one of {}".format(calc_type, acceptable_calc_types))

    attacking_move = get_move(move)
    if attacking_move is None:
        raise TypeError("Invalid move: {}".format(move))

    attacking_type = attacking_move.get(constants.CATEGORY)
    if attacking_type == constants.PHYSICAL:
        attack = constants.ATTACK
        defense = constants.DEFENSE
    elif attacking_type == constants.SPECIAL:
        attack = constants.SPECIAL_ATTACK
        defense = constants.SPECIAL_DEFENSE
    else:
        return None

    try:
        return SPECIAL_LOGIC_MOVES[attacking_move[constants.ID]](attacker, defender)
    except KeyError:
        pass

    if attacking_move[constants.BASE_POWER] == 0:
        return [0]

    if conditions is None:
        conditions = {}

    attacking_stats = attacker.calculate_boosted_stats()
    defending_stats = defender.calculate_boosted_stats()

    if attacker.ability == 'unaware':
        if defense == constants.DEFENSE:
            defending_stats[defense] = defender.defense
        elif defense == constants.SPECIAL_DEFENSE:
            defending_stats[defense] = defender.special_defense
    if defender.ability == 'unaware':
        if attack == constants.ATTACK:
            attacking_stats[attack] = attacker.attack
        elif defense == constants.SPECIAL_ATTACK:
            attacking_stats[attack] = attacker.special_attack

    defending_types = defender.types
    if attacking_move[constants.ID] == 'thousandarrows' and 'flying' in defending_types:
        defending_types = copy(defender.types)
        defending_types.remove('flying')
    if attacking_move[constants.TYPE] == 'ground' and constants.ROOST in defender.volatile_status:
        defending_types = copy(defender.types)
        try:
            defending_types.remove('flying')
        except ValueError:
            pass

    # rock types get 1.5x SPDEF in sand
    # ice types get 1.5x DEF in snow
    try:
        if conditions[constants.WEATHER] == constants.SAND and 'rock' in defender.types:
            defending_stats[constants.SPECIAL_DEFENSE] = int(defending_stats[constants.SPECIAL_DEFENSE] * 1.5)
        elif conditions[constants.WEATHER] == constants.SNOW and 'ice' in defender.types:
            defending_stats[constants.DEFENSE] = int(defending_stats[constants.DEFENSE] * 1.5)
    except KeyError:
        pass

    if defender.ability == "tabletsofruin":
        attacking_stats[constants.ATTACK] *= 0.75
    elif defender.ability == "vesselofruin":
        attacking_stats[constants.SPECIAL_ATTACK] *= 0.75
    if attacker.ability == "swordofruin":
        defending_stats[constants.DEFENSE] *= 0.75
    elif attacker.ability == "beadsofruin":
        defending_stats[constants.SPECIAL_DEFENSE] *= 0.75

    damage = int(int((2 * attacker.level) / 5) + 2) * attacking_move[constants.BASE_POWER]
    damage = int(damage * attacking_stats[attack] / defending_stats[defense])
    damage = int(damage / 50) + 2
    damage *= calculate_modifier(attacker, defender, defending_types, attacking_move, conditions)

    damage_rolls = get_damage_rolls(damage, calc_type)

    return list(set(damage_rolls))


def is_super_effective(move_type, defending_pokemon_types):
    multiplier = type_effectiveness_modifier(move_type, defending_pokemon_types)
    return multiplier > 1


def is_not_very_effective(move_type, defending_pokemon_types):
    multiplier = type_effectiveness_modifier(move_type, defending_pokemon_types)
    return multiplier < 1


def calculate_modifier(attacker, defender, defending_types, attacking_move, conditions):

    modifier = 1
    modifier *= type_effectiveness_modifier(attacking_move[constants.TYPE], defending_types)
    modifier *= weather_modifier(attacking_move, conditions.get(constants.WEATHER))
    modifier *= stab_modifier(attacker, attacking_move)
    modifier *= burn_modifier(attacker, attacking_move)
    modifier *= terrain_modifier(attacker, defender, attacking_move, conditions.get(constants.TERRAIN))
    modifier *= volatile_status_modifier(attacking_move, attacker, defender)

    if attacker.ability != 'infiltrator':
        modifier *= light_screen_modifier(attacking_move, conditions.get(constants.LIGHT_SCREEN))
        modifier *= reflect_modifier(attacking_move, conditions.get(constants.REFLECT))
        modifier *= aurora_veil_modifier(conditions.get(constants.AURORA_VEIL))

    return modifier


def get_move(move):
    if isinstance(move, dict):
        return move
    if isinstance(move, str):
        return deepcopy(all_move_json.get(move, None))
    else:
        return None


def get_damage_rolls(damage, calc_type):
    if calc_type == 'average':
        damage *= 0.925
        return [int(damage)]
    elif calc_type == 'min':
        return [int(damage * 0.85)]
    elif calc_type == 'max':
        return [int(damage)]
    elif calc_type == 'min_max':
        return [
            int(damage * 0.85),
            int(damage)
        ]
    elif calc_type == 'min_max_average':
        return [
            int(damage * 0.85),
            int(damage * 0.925),
            int(damage)
        ]
    elif calc_type == 'all':
        return [
            int(damage * 0.85),
            int(damage * 0.86),
            int(damage * 0.87),
            int(damage * 0.88),
            int(damage * 0.89),
            int(damage * 0.90),
            int(damage * 0.91),
            int(damage * 0.92),
            int(damage * 0.93),
            int(damage * 0.94),
            int(damage * 0.95),
            int(damage * 0.96),
            int(damage * 0.97),
            int(damage * 0.98),
            int(damage * 0.99),
            int(damage)
        ]


def type_effectiveness_modifier(attacking_move_type, defending_types):
    modifier = 1
    attacking_type_index = pokemon_type_indicies[attacking_move_type]
    for pkmn_type in defending_types:
        defending_type_index = pokemon_type_indicies[pkmn_type]
        modifier *= damage_multipication_array[attacking_type_index][defending_type_index]

    return modifier


def weather_modifier(attacking_move, weather):
    if not isinstance(weather, str):
        return 1

    if weather == constants.SUN and attacking_move[constants.TYPE] == 'fire':
        return 1.5
    elif weather == constants.SUN and attacking_move[constants.TYPE] == 'water':
        return 0.5
    elif weather == constants.RAIN and attacking_move[constants.TYPE] == 'water':
        return 1.5
    elif weather == constants.RAIN and attacking_move[constants.TYPE] == 'fire':
        return 0.5
    elif weather == constants.HEAVY_RAIN and attacking_move[constants.TYPE] == 'fire':
        return 0
    elif weather == constants.HEAVY_RAIN and attacking_move[constants.TYPE] == 'water':
        return 1.5
    elif weather == constants.DESOLATE_LAND and attacking_move[constants.TYPE] == 'water':
        return 0
    elif weather == constants.DESOLATE_LAND and attacking_move[constants.TYPE] == 'fire':
        return 1.5
    return 1


def stab_modifier(attacking_pokemon, attacking_move):
    if attacking_move[constants.TYPE] in [t for t in attacking_pokemon.types]:
        if (
            attacking_pokemon.terastallized and
            attacking_pokemon.types[0] in pokedex[attacking_pokemon.id][constants.TYPES]
        ):
            return 2
        else:
            return 1.5

    elif (
        attacking_pokemon.terastallized and
        attacking_move[constants.TYPE] in pokedex[attacking_pokemon.id][constants.TYPES]
    ):
        return 1.5

    return 1


def burn_modifier(attacking_pokemon, attacking_move):
    if constants.BURN == attacking_pokemon.status and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        return 0.5
    return 1


def light_screen_modifier(attacking_move, light_screen):
    if light_screen and attacking_move[constants.CATEGORY] == constants.SPECIAL:
        return 0.5
    return 1


def reflect_modifier(attacking_move, reflect):
    if reflect and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        return 0.5
    return 1


def aurora_veil_modifier(aurora_veil):
    if aurora_veil:
        return 0.5
    return 1


def terrain_modifier(attacker, defender, attacking_move, terrain):
    if terrain == constants.ELECTRIC_TERRAIN and attacking_move[constants.TYPE] == 'electric' and attacker.is_grounded():
        return TERRAIN_DAMAGE_BOOST
    elif terrain == constants.GRASSY_TERRAIN and attacking_move[constants.TYPE] == 'grass' and attacker.is_grounded():
        return TERRAIN_DAMAGE_BOOST
    elif terrain == constants.GRASSY_TERRAIN and attacking_move[constants.ID] == 'earthquake':
        return 0.5
    elif terrain == constants.MISTY_TERRAIN and attacking_move[constants.TYPE] == 'dragon' and defender.is_grounded():
        return 0.5
    elif terrain == constants.PSYCHIC_TERRAIN and attacking_move[constants.TYPE] == 'psychic' and attacker.is_grounded():
        return TERRAIN_DAMAGE_BOOST
    elif terrain == constants.PSYCHIC_TERRAIN and attacking_move[constants.PRIORITY] > 0 and defender.is_grounded():
        return 0
    return 1


def volatile_status_modifier(attacking_move, attacker, defender):
    modifier = 1
    if 'magnetrise' in defender.volatile_status and attacking_move[constants.TYPE] == 'ground' and attacking_move[constants.ID] != 'thousandarrows':
        modifier *= 0
    if 'flashfire' in attacker.volatile_status and attacking_move[constants.TYPE] == 'fire':
        modifier *= 1.5
    if 'tarshot' in defender.volatile_status and attacking_move[constants.TYPE] == 'fire':
        modifier *= 2
    if 'phantomforce' in defender.volatile_status:
        modifier *= 0
    if 'shadowforce' in defender.volatile_status:
        modifier *= 0
    if (
        'dive' in defender.volatile_status and
        attacker.ability != "noguard" and
        defender.ability != "noguard" and
        attacking_move[constants.ID] not in [
            "surf", "whirlpool"
        ]
    ):
        modifier *= 0
    if (
        'dig' in defender.volatile_status and
        attacker.ability != "noguard" and
        defender.ability != "noguard" and
        attacking_move[constants.ID] not in [
            "earthquake", "magnitude", "fissure"
        ]
    ):
        modifier *= 0
    if (
        (
            "fly" in defender.volatile_status or
            "bounce" in defender.volatile_status
        ) and
        attacker.ability != "noguard" and
        defender.ability != "noguard" and
        attacking_move[constants.ID] not in [
            "gust", "thunder", "twister", "skyuppercut", "hurricane", "thousandarrows", "smackdown"
        ]
    ):
        modifier *= 0
    if 'glaiverush' in defender.volatile_status:
        modifier *= 2
    if any(vs in attacker.volatile_status for vs in ['quarkdriveatk', "protosynthesisatk"]) and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        modifier *= 1.3
    if any(vs in attacker.volatile_status for vs in ['quarkdrivespa', "protosynthesisspa"]) and attacking_move[constants.CATEGORY] == constants.SPECIAL:
        modifier *= 1.3
    if any(vs in defender.volatile_status for vs in ['quarkdrivedef', "protosynthesisdef"]) and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        modifier *= (1/1.3)
    if any(vs in defender.volatile_status for vs in ['quarkdrivespd', "protosynthesisspd"]) and attacking_move[constants.CATEGORY] == constants.SPECIAL:
        modifier *= (1/1.3)
    return modifier


def calculate_damage(state, attacking_side_string, attacking_move, defending_move, calc_type='average'):
    # a wrapper for `_calculate_damage` that takes into account move/item/ability special-effects
    from .find_state_instructions import update_attacking_move
    from .find_state_instructions import user_moves_first

    attacking_move_dict = get_move(attacking_move)
    if defending_move.startswith(constants.SWITCH_STRING + " "):
        defending_move_dict = {constants.SWITCH_STRING: defending_move.split(constants.SWITCH_STRING)[-1]}
    else:
        defending_move_dict = get_move(defending_move)

    if attacking_side_string == constants.USER:
        attacking_side = state.user
        defending_side = state.opponent
    elif attacking_side_string == constants.OPPONENT:
        attacking_side = state.opponent
        defending_side = state.user
    else:
        raise ValueError("attacking_side_string must be one of: ['self', 'opponent']")

    conditions = {
        constants.REFLECT: defending_side.side_conditions[constants.REFLECT],
        constants.LIGHT_SCREEN: defending_side.side_conditions[constants.LIGHT_SCREEN],
        constants.AURORA_VEIL: defending_side.side_conditions[constants.AURORA_VEIL],
        constants.WEATHER: state.weather,
        constants.TERRAIN: state.field
    }

    attacker_moves_first = user_moves_first(state, attacking_move_dict, defending_move_dict)

    if constants.CHARGE in attacking_move_dict[constants.FLAGS]:
        attacking_move_dict = attacking_move_dict.copy()
        # a charge move doesn't need to charge when only calculating damage
        attacking_move_dict[constants.FLAGS].pop(constants.CHARGE, None)

    attacking_move_dict = update_attacking_move(
        attacking_side,
        attacking_side.active,
        defending_side.active,
        attacking_move_dict,
        defending_move_dict,
        attacker_moves_first,
        state.weather,
        state.field
    )

    return _calculate_damage(attacking_side.active, defending_side.active, attacking_move_dict, conditions=conditions, calc_type=calc_type)


def calculate_futuresight_damage(state, attacking_side_string, future_sight_user, calc_type='average'):
    if attacking_side_string == constants.USER:
        attacking_side = state.user
        defending_side = state.opponent
    else:
        attacking_side = state.opponent
        defending_side = state.user

    if attacking_side.active.id == future_sight_user:
        attacker = attacking_side.active
    else:
        attacker = attacking_side.reserve[future_sight_user]

    defender = defending_side.active

    attacking_move_dict = {
        "accuracy": 100,
        "basePower": 120,
        "category": "special",
        "flags": {},
        "id": "futuresight",
        "name": "Future Sight",
        "priority": 0,
        "secondary": False,
        "target": "normal",
        "type": "psychic",
        "pp": 10
    }

    conditions = {
        constants.REFLECT: defending_side.side_conditions[constants.REFLECT],
        constants.LIGHT_SCREEN: defending_side.side_conditions[constants.LIGHT_SCREEN],
        constants.AURORA_VEIL: defending_side.side_conditions[constants.AURORA_VEIL],
        constants.WEATHER: state.weather,
        constants.TERRAIN: state.field
    }

    return _calculate_damage(
        attacker,
        defender,
        attacking_move_dict,
        conditions=conditions,
        calc_type=calc_type
    )

---

[11]. src/Ankimon/pyobj/pokemon_obj.py
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

[12]. src/Ankimon/reviewer_ui.py
Why this file is critical: Sets up the reviewer UI shortcuts.

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

[13]. src/Ankimon/user_files/web/ankimon_hud_portal.js
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

[14]. src/Ankimon/pyobj/ankimon_tracker.py
Why this file is critical: Tracks session statistics, multipliers, streaks.

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

[15]. src/Ankimon/resources.py
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
