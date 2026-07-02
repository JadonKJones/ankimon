"""
singletons.py

This module groups up some of the global variables that originally were in the __init__.py.
This module serves as the production GUI-dependent adapter layer for Ankimon's game state.

Author: Axil, Ankimon contributors
"""

import json
import uuid

from aqt import mw

from .pyobj.ankimon_shop import PokemonShopManager
from .pyobj.reviewer_obj import Reviewer_Manager
from .resources import addon_dir
from .utils import is_alive

from .core import build_core, bind_runtime_globals
from .services import services

# --- RELOAD-SAFE SINGLETONS ---
# We anchor these to 'mw' so they persist across add-on reloads.
# Establish core services and game state via the composition root
core_state = build_core(
    logger=getattr(mw, "logger", None),
    db=getattr(mw, "ankimon_db", None),
    settings=getattr(mw, "settings_obj", None),
    translator=getattr(mw, "translator", None),
    main_pokemon=getattr(mw, "main_pokemon", None),
    enemy_pokemon=getattr(mw, "enemy_pokemon", None),
    trainer_card=getattr(mw, "trainer_card", None),
    tracker=getattr(mw, "ankimon_tracker_obj", None),
    achievements=getattr(mw, "achievements_dict", None),
)

# Anchor everything to mw so they persist
mw.logger = core_state.logger
mw.ankimon_db = core_state.ankimon_db
mw.settings_obj = core_state.settings_obj
mw.translator = core_state.translator
mw.main_pokemon = core_state.main_pokemon
mw.enemy_pokemon = core_state.enemy_pokemon
mw.trainer_card = core_state.trainer_card
mw.ankimon_tracker_obj = core_state.ankimon_tracker_obj
mw.achievements_dict = core_state.achievements

# Backwards compatibility shims
logger = core_state.logger
ankimon_db = core_state.ankimon_db
settings_obj = core_state.settings_obj
translator = core_state.translator
main_pokemon = core_state.main_pokemon
enemy_pokemon = core_state.enemy_pokemon
trainer_card = core_state.trainer_card
ankimon_tracker_obj = core_state.ankimon_tracker_obj
achievements = core_state.achievements

# Bind initial production collection
services.populate(col=getattr(mw, "col", None))

# --- LAZY WINDOWS & DIALOGS ---
settings_window = None


def get_settings_window():
    global settings_window
    if not is_alive(settings_window):
        settings_window = getattr(mw, "settings_ankimon", None)
        if not is_alive(settings_window):
            from .pyobj.settings_window import SettingsWindow

            settings_window = SettingsWindow(
                config=settings_obj.config,
                set_config_callback=settings_obj.set,
                save_config_callback=settings_obj.save_config,
                load_config_callback=settings_obj.load_config,
            )
            mw.settings_ankimon = settings_window
        services.populate(settings_window=settings_window)
        bind_runtime_globals()
    return settings_window


starter_window = None


def get_starter_window():
    global starter_window
    if not is_alive(starter_window):
        starter_window = getattr(mw, "starter_window", None)
        if not is_alive(starter_window):
            from .pyobj.starter_window import StarterWindow

            starter_window = StarterWindow(logger, settings_obj)
            mw.starter_window = starter_window
        services.populate(starter_window=starter_window)
        bind_runtime_globals()
    return starter_window


# Test Window
test_window = None


def get_test_window():
    global test_window
    if not is_alive(test_window):
        test_window = getattr(mw, "test_window", None)
        if not is_alive(test_window):
            from .pyobj.test_window import TestWindow

            test_window = TestWindow(
                main_pokemon=main_pokemon,
                enemy_pokemon=enemy_pokemon,
                settings_obj=settings_obj,
                ankimon_tracker_obj=ankimon_tracker_obj,
                translator=translator,
                parent=mw,
                logger=logger,
            )
            mw.test_window = test_window
        services.populate(test_window=test_window)
        bind_runtime_globals()
    return test_window


# Shop Manager
shop_manager = getattr(mw, "shop_manager", None) or PokemonShopManager(
    logger=logger,
    settings_obj=settings_obj,
    set_callback=settings_obj.set,
    get_callback=settings_obj.get,
)
mw.shop_manager = shop_manager
services.populate(shop_manager=shop_manager)

# Reviewer Manager
reviewer_obj = getattr(mw, "reviewer_obj", None) or Reviewer_Manager(
    settings_obj=settings_obj,
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    ankimon_tracker=ankimon_tracker_obj,
)
mw.reviewer_obj = reviewer_obj
services.populate(reviewer=reviewer_obj)


# Windows & Bags
achievement_bag = None


def get_achievement_bag():
    global achievement_bag
    if not is_alive(achievement_bag):
        achievement_bag = getattr(mw, "achievement_bag", None)
        if not is_alive(achievement_bag):
            from .pyobj.achievement_window import AchievementWindow

            achievement_bag = AchievementWindow()
            mw.achievement_bag = achievement_bag
        services.populate(achievement_bag=achievement_bag)
        bind_runtime_globals()
    return achievement_bag


ankimon_tracker_window = None


def get_ankimon_tracker_window():
    global ankimon_tracker_window
    if not is_alive(ankimon_tracker_window):
        ankimon_tracker_window = getattr(mw, "ankimon_tracker_window", None)
        if not is_alive(ankimon_tracker_window):
            from .pyobj.ankimon_tracker_window import AnkimonTrackerWindow

            ankimon_tracker_window = AnkimonTrackerWindow(tracker=ankimon_tracker_obj)
            mw.ankimon_tracker_window = ankimon_tracker_window
        services.populate(ankimon_tracker_window=ankimon_tracker_window)
        bind_runtime_globals()
    return ankimon_tracker_window


# Ankidex
ankidex_window = getattr(mw, "ankidex_window", None)


def get_ankidex_window():
    global ankidex_window
    if not is_alive(ankidex_window):
        from .ankidex.ankidex_obj import Ankidex

        ankidex_window = Ankidex(addon_dir, ankimon_tracker=ankimon_tracker_obj)
        mw.ankidex_window = ankidex_window
    services.populate(ankidex_window=ankidex_window)
    bind_runtime_globals()
    return ankidex_window


# Unified Ankimon shell window — Items, Ankidex, Profile, Team and Settings
# all live in this one web shell (one window, one dropdown navigator).
items_web_window = getattr(mw, "items_web_window", None)


def get_items_window():
    global items_web_window
    if not is_alive(items_web_window):
        from .ankimon_items_web.shop_obj import AnkimonItemsWeb

        items_web_window = AnkimonItemsWeb(
            addon_dir,
            shop_manager=shop_manager,
            item_window=get_item_window(),
            ankimon_tracker=ankimon_tracker_obj,
            trainer_card=trainer_card,
            settings_obj=settings_obj,
            logger=logger,
        )
        mw.items_web_window = items_web_window
    services.populate(items_web_window=items_web_window)
    bind_runtime_globals()
    return items_web_window


def notify_stats_changed():
    """Tell the open Ankimon shell that gameplay stats changed (a catch, XP
    gain, cash reward, level-up, ...) so it can live-refresh whichever screen is
    showing — no manual reload. Screen-agnostic: the shell decides what (if
    anything) to refresh based on its current screen (see
    ``AnkimonItemsWeb.refresh_live_screen`` and ``LIVE_UPDATES.md``).

    Pure best-effort and cheap: never creates the window, no-ops when no live
    screen is visible, and swallows any error so a UI hiccup can't interfere
    with gameplay. Call it from gameplay write chokepoints via a deferred
    ``from .singletons import notify_stats_changed`` wrapped in try/except."""
    from .utils import is_main_thread
    if not is_main_thread():
        return
    win = getattr(mw, "items_web_window", None)
    if not is_alive(win):
        return
    try:
        win.refresh_live_screen()
    except Exception as e:
        print(f"[Ankimon] notify_stats_changed failed: {e}")


evo_window = None


def get_evo_window():
    global evo_window
    if not is_alive(evo_window):
        evo_window = getattr(mw, "evo_window", None)
        if not is_alive(evo_window):
            import os
            if "PYTEST_CURRENT_TEST" in os.environ or (mw and "mock" in mw.__class__.__name__.lower()):
                class FakeEvoWindow:
                    def __getattr__(self, name):
                        return lambda *args, **kwargs: FakeEvoWindow()
                evo_window = FakeEvoWindow()
                mw.evo_window = evo_window
            else:
                from .pyobj.evolution_window import EvoWindow

                evo_window = EvoWindow(
                    logger,
                    settings_obj,
                    main_pokemon,
                    translator,
                    reviewer_obj,
                    get_test_window(),
                    achievements,
                )
                mw.evo_window = evo_window
        services.populate(evo_window=evo_window)
        bind_runtime_globals()
    return evo_window


item_window = None


def get_item_window():
    global item_window
    if not is_alive(item_window):
        item_window = getattr(mw, "item_window", None)
        if not is_alive(item_window):
            from .pyobj.item_window import ItemWindow

            item_window = ItemWindow(
                logger=logger,
                settings_obj=settings_obj,
                main_pokemon=main_pokemon,
                enemy_pokemon=enemy_pokemon,
                achievements=achievements,
                starter_window=get_starter_window(),
                evo_window=get_evo_window(),
            )
            mw.item_window = item_window
        services.populate(item_window=item_window)
        bind_runtime_globals()
    return item_window


# Pokemon PC
pokemon_pc = getattr(mw, "pokemon_pc", None)


def get_pokemon_pc():
    global pokemon_pc
    if not is_alive(pokemon_pc):
        pokemon_pc = getattr(mw, "pokemon_pc", None)
        if not is_alive(pokemon_pc):
            from .pyobj.pc_box import PokemonPC

            pokemon_pc = PokemonPC(
                logger=logger,
                translator=translator,
                reviewer_obj=reviewer_obj,
                test_window=get_test_window(),
                settings=settings_obj,
                main_pokemon=main_pokemon,
                achievements=achievements,
            )
            mw.pokemon_pc = pokemon_pc
        services.populate(pokemon_pc=pokemon_pc)
        bind_runtime_globals()
    return pokemon_pc


# UI Utilities
eff_chart = None


def get_eff_chart():
    global eff_chart
    if not is_alive(eff_chart):
        from .gui_entities import TableWidget

        eff_chart = TableWidget()
    return eff_chart


gen_id_chart = None


def get_gen_id_chart():
    global gen_id_chart
    if not is_alive(gen_id_chart):
        from .gui_entities import IDTableWidget

        gen_id_chart = IDTableWidget()
    return gen_id_chart


nature_chart = None


def get_nature_chart():
    global nature_chart
    if not is_alive(nature_chart):
        from .gui_entities import NatureTableWidget

        nature_chart = NatureTableWidget()
    return nature_chart


license = None


def get_license():
    global license
    if not is_alive(license):
        from .gui_entities import License

        license = License()
    return license


credits = None


def get_credits():
    global credits
    if not is_alive(credits):
        from .gui_entities import Credits

        credits = Credits()
    return credits


version_dialog = None


def get_version_dialog():
    global version_dialog
    if not is_alive(version_dialog):
        from .gui_entities import Version_Dialog

        version_dialog = Version_Dialog()
    return version_dialog


def __getattr__(name):
    if name == "settings_window":
        return get_settings_window()
    elif name == "starter_window":
        return get_starter_window()
    elif name == "test_window":
        return get_test_window()
    elif name == "achievement_bag":
        return get_achievement_bag()
    elif name == "ankimon_tracker_window":
        return get_ankimon_tracker_window()
    elif name == "evo_window":
        return get_evo_window()
    elif name == "item_window":
        return get_item_window()
    elif name == "eff_chart":
        return get_eff_chart()
    elif name == "gen_id_chart":
        return get_gen_id_chart()
    elif name == "nature_chart":
        return get_nature_chart()
    elif name == "license":
        return get_license()
    elif name == "credits":
        return get_credits()
    elif name == "version_dialog":
        return get_version_dialog()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def swap_ankimon_account():
    """Toggles between ankimon.db and ankimonDEV.db and refreshes the game state."""
    from aqt.utils import tooltip
    from .functions.update_main_pokemon import update_main_pokemon
    from .functions.encounter_functions import new_pokemon, clear_encounter_cache

    current_name = mw.ankimon_db.db_path.name
    new_name = "ankimonDEV.db" if current_name == "ankimon.db" else "ankimon.db"

    try:
        # Switch DB connection
        mw.ankimon_db.switch_database(new_name)

        # Reload configuration (in-place)
        mw.settings_obj.load_config()

        # Update main pokemon in-place
        new_main_pokemon, mainpokemon_empty = update_main_pokemon(mw.main_pokemon)
        mw.main_pokemon = new_main_pokemon
        services.populate(main_pokemon=new_main_pokemon)
        bind_runtime_globals()

        # Refresh trainer card data
        mw.trainer_card.refresh()

        # Reset battle and capture state so no stale data can bleed through
        mw.ankimon_tracker_obj.caught = 0
        mw.ankimon_tracker_obj.general_card_count_for_battle = 0

        # Sync collected IDs to current account
        from .reviewer_ui import set_collected_ids
        from .battle_loop import init_battle_state

        new_ids = mw.ankimon_db.get_all_pokemon_ids()
        set_collected_ids(new_ids)
        init_battle_state(new_ids)

        # Update mobile reviews badge with the new database's pending count
        try:
            from .menu_buttons import update_mobile_badge
            pending_count = mw.ankimon_db.get_pending_mobile_count()
            update_mobile_badge(pending_count)
        except Exception:
            pass

        # Clear encounter percentages cache (uses new trainer level/stats)
        clear_encounter_cache()

        # Generate a fresh encounter for the new account
        new_pokemon(
            mw.enemy_pokemon,
            getattr(mw, "test_window", None),
            mw.ankimon_tracker_obj,
            mw.reviewer_obj,
        )

        # Refresh windows if they are open
        if hasattr(mw, "pokemon_pc") and is_alive(mw.pokemon_pc):
            # Reset selection because IDs change between databases
            mw.pokemon_pc._selected_individual_id = None
            mw.pokemon_pc.pokemon_details_layout = None
            mw.pokemon_pc.refresh_gui()

        if hasattr(mw, "item_window") and is_alive(mw.item_window):
            mw.item_window.renewWidgets()

        if hasattr(mw, "ankidex_window") and is_alive(mw.ankidex_window):
            mw.ankidex_window.update_ui_data()

        if hasattr(mw, "items_web_window") and is_alive(mw.items_web_window) and mw.items_web_window.isVisible():
            mw.items_web_window.update_ui_data()

        # If in reviewer, force HUD update
        if hasattr(mw, "reviewer") and mw.reviewer and hasattr(mw, "reviewer_obj"):
            mw.reviewer_obj.update_life_bar(mw.reviewer, None, 0)

        tooltip(f"Switched to {new_name}")
    except Exception as e:
        tooltip(f"Failed to switch account: {e}")
        import traceback

        traceback.print_exc()
