import json
from collections import defaultdict
import uuid

from aqt.utils import showInfo, showWarning
from ..pyobj.error_handler import show_warning_with_traceback
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from aqt import mw
import re

from ..pyobj.InfoLogger import ShowInfoLogger
from ..pyobj.pokemon_obj import PokemonObject
from ..pyobj.InfoLogger import ShowInfoLogger
from ..pyobj.translator import Translator
from ..pyobj.test_window import TestWindow
from ..pyobj.reviewer_obj import Reviewer_Manager
from ..functions.pokedex_functions import search_pokedex, search_pokedex_by_id

def MainPokemon(
    pokemon_data: dict,
    main_pokemon: PokemonObject,
    logger: ShowInfoLogger,
    translator: Translator,
    reviewer_obj: Reviewer_Manager,
    test_window: TestWindow,
):
    from ..functions.migration import migrate_starter_individual_id

    db = mw.ankimon_db
    
    # --- Save the existing mainpokemon to mypokemon before replacing ---
    # Persist the OUTGOING main's IN-MEMORY state (xp, friendship, current_hp
    # gained during reviews) rather than the stale on-disk copy returned by
    # db.get_main_pokemon(). At this point ``main_pokemon`` still references the
    # current main; it is only overwritten with the new selection further below.
    try:
        # Only save if there's already an active main pokemon to replace.
        if main_pokemon is not None and getattr(main_pokemon, "individual_id", None) and db.get_main_pokemon():
            # Use main_pokemon.to_dict() to capture in-memory stats like xp.
            db.save_pokemon(main_pokemon.to_dict())
    except Exception:
        pass  # If no main pokemon exists, just continue

    # --- Now proceed to set the new mainpokemon as before ---
    pokemon_id = pokemon_data.get("id")
    pokemon_name = search_pokedex_by_id(pokemon_id)
    base_stats = search_pokedex(pokemon_name, "baseStats")
    # HP: hand the constructor the PERSISTED values and let PokemonObject
    # normalize them. Passing a freshly computed max-HP stat here (the old
    # behaviour) silently full-healed the incoming main and, via
    # db.save_main_pokemon(to_dict()) below, persisted that full HP.
    #
    # ``hp`` is the live field -- to_dict() labels it "Current HP", and
    # battle_loop/item_window write it -- with ``current_hp`` as its mirror.
    # Partially migrated records can carry one without the other (see
    # update_main_pokemon._normalize_loaded_hp), so fall back to the mirror
    # when ``hp`` is missing or null; otherwise _normalize_hp resolves a None
    # ``hp`` to full max HP and we re-persist the very heal this fixes.
    # Deliberately NOT _normalize_loaded_hp's current_hp-first order:
    # item_window.Check_Heal_Item bumps ``hp`` alone, so preferring the mirror
    # would silently undo a potion used just before the switch.
    persisted_hp = pokemon_data.get("hp")
    if persisted_hp is None:
        persisted_hp = pokemon_data.get("current_hp")

    # Create NEW PokemonObject instance using class constructor
    new_main_pokemon = PokemonObject(
        name=pokemon_name,
        level=pokemon_data.get("level", 5),
        ability=pokemon_data.get("ability", ["none"]),
        type=pokemon_data.get("type", ["Normal"]),
        base_stats=base_stats,
        ev=pokemon_data.get("ev", defaultdict(int)),
        iv=pokemon_data.get("iv", defaultdict(int)),
        attacks=pokemon_data.get("attacks", ["Struggle"]),
        base_experience=pokemon_data.get("base_experience", 0),
        growth_rate=pokemon_data.get("growth_rate", "medium"),
        # ``or`` not a get() default: a record holding an explicit null nature
        # would otherwise reach get_nature_stat_mult() and blow up on None.lower().
        nature=pokemon_data.get("nature") or "serious",
        hp=persisted_hp,
        current_hp=pokemon_data.get("current_hp"),
        gender=pokemon_data.get("gender", "N"),
        shiny=pokemon_data.get("shiny", False),
        individual_id=pokemon_data.get("individual_id", str(uuid.uuid4())),
        id=pokemon_data.get("id", 133),
        volatile_status=set(pokemon_data.get("volatile_status", [])),
        xp=pokemon_data.get("xp", 0),
        nickname=pokemon_data.get("nickname", ""),
        # Add common extra fields if constructor supports them
        friendship=pokemon_data.get("friendship", 0),
        pokemon_defeated=pokemon_data.get("pokemon_defeated", 0),
        everstone=pokemon_data.get("everstone", False),
        evolution_rejected=pokemon_data.get("evolution_rejected", False),
        mega=pokemon_data.get("mega", False),
        special_form=pokemon_data.get("special_form", None),
        tier=pokemon_data.get("tier", None),
        captured_date=pokemon_data.get("captured_date", None),
        is_favorite=pokemon_data.get("is_favorite", False),
        held_item=pokemon_data.get("held_item"),
    )
    # Set any additional fields not in constructor
    extra_fields = [
        "captured_date",
        "tier",
        "friendship",
        "pokemon_defeated",
        "everstone",
        "mega",
        "special_form",
        "base_experience",
    ]
    for attr in extra_fields:
        if attr in pokemon_data:
            setattr(new_main_pokemon, attr, pokemon_data[attr])

    # Update existing reference
    main_pokemon.__dict__.update(new_main_pokemon.__dict__)

    # Save to database
    db.save_main_pokemon(main_pokemon.to_dict())

    logger.log_and_showinfo(
        "info",
        translator.translate(
            "picked_main_pokemon", main_pokemon_name=main_pokemon.name.capitalize()
        ),
    )

    # Update UI components. refresh_hud() is Reviewer_Manager's single entry
    # point for a repaint: it builds the reviewer shim itself and is guarded, so
    # no reviewer/webview is a silent no-op instead of an AttributeError that
    # would abort the rest of this function. No extra bookkeeping is needed
    # here: reviewer_obj.main_pokemon IS the object line above mutated in place,
    # and db.save_main_pokemon() already invalidated the HUD cache via
    # _clear_reviewer_ownership_cache().
    reviewer_obj.refresh_hud()

    if test_window.isVisible():
        test_window.display_first_encounter()

    from ..singletons import pokemon_pc

    pokemon_pc.refresh_pokemon_grid()
