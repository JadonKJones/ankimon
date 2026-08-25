import json

from .badges_functions import get_achieved_badges
from .pokedex_functions import extract_ids_from_file
from .pokemon_functions import find_experience_for_level
from .pokedex_functions import check_evolution_for_pokemon, return_name_for_id
from .friendship_evolution import check_friendship_evolution_for_pokemon
from ..services import services

def find_trainer_rank(highest_level, trainer_level):
    """
    Determines the Pokémon rank based on the player's achievements like Pokémon caught (from Pokedex),
    highest level Pokémon, trainer XP, trainer level, shiny Pokémon count, and badges.

    Args:
    highest_level (int): The highest level Pokémon the player owns.
    trainer_level (int): The level of the trainer.

    Returns:
    str: The Pokémon rank (Grand Champion, Champion, Elite, Veteran, Rookie, etc.).
    """
    try:
        # Count the amount of Pokémon caught based on the Pokedex
        caught_pokemon = services.db.execute("SELECT COUNT(DISTINCT pokedex_id) FROM captured_pokemon").fetchone()[0]

        # Count the number of shiny Pokémon
        shiny_pokemon_count = services.db.get_shiny_count()

        # Count badges
        badge_count = len(get_achieved_badges())

        # Determine rank based on achievements
        if caught_pokemon >= 900 and highest_level >= 99 and trainer_level >= 100 and shiny_pokemon_count >= 50:
            rank = "Legendary Trainer"
        elif caught_pokemon >= 800 and highest_level >= 95 and trainer_level >= 80 and shiny_pokemon_count >= 25:
            rank = "Grand Champion"
        elif caught_pokemon >= 700 and highest_level >= 90 and trainer_level >= 70 and shiny_pokemon_count >= 20:
            rank = "Champion"
        elif caught_pokemon >= 600 and highest_level >= 80 and trainer_level >= 60 and shiny_pokemon_count >= 10 and badge_count >= 8:
            rank = "Master Trainer"
        elif caught_pokemon >= 500 and highest_level >= 75 and trainer_level >= 50 and shiny_pokemon_count >= 5 and badge_count > 6:
            rank = "Elite"
        elif caught_pokemon >= 400 and highest_level >= 70 and trainer_level >= 45 and shiny_pokemon_count >= 3 and badge_count > 5:
            rank = "Elite Trainer"
        elif caught_pokemon >= 350 and highest_level >= 60 and trainer_level >= 40 and shiny_pokemon_count >= 2 and badge_count > 4:
            rank = "Advanced Trainer"
        elif caught_pokemon >= 300 and highest_level >= 50 and trainer_level >= 30 and shiny_pokemon_count > 0 and badge_count > 3:
            rank = "Veteran"
        elif caught_pokemon >= 250 and highest_level >= 40 and trainer_level >= 20 and shiny_pokemon_count > 0:
            rank = "Skilled Trainer"
        elif caught_pokemon >= 150 and highest_level >= 30 and trainer_level >= 10:
            rank = "Rookie"
        else:
            rank = "Novice Trainer"  # Default rank for beginners

        return rank

    except FileNotFoundError:
        print("Error: One of the files (Pokedex or MyPokemon) could not be found.")
        return "Unknown Rank"

def resolve_xp_share_targets(settings_obj):
    """The individual_ids XP Share should actually apply to right now.

    When ``trainer.xp_share_full_team`` is on (the mainline Gen-6+ "whole
    party" style — X/Y, ORAS, Sun/Moon and everything since, where Exp.
    Share became a key item shared by the whole team instead of a single
    held item), every current team member is a target, ignoring whatever
    individual picks are stored. Otherwise falls back to the manually
    picked list in ``trainer.xp_share`` (list, or a bare string for
    older saves). ``xp_share_gain_exp``/``_xp_share_split`` already
    de-dupe and drop the main Pokémon, so no filtering needed here.
    """
    try:
        if settings_obj.get("trainer.xp_share_full_team"):
            db = services.db
            if db is not None:
                return [m["individual_id"] for m in db.get_team() if m.get("individual_id")]
    except Exception:
        pass
    return settings_obj.get("trainer.xp_share")


def remove_xp_share_target(settings_obj, individual_id):
    """Drop one Pokémon from the XP Share list (e.g. it was released/traded).

    Handles both the current list-of-ids storage and a legacy bare-string
    value, so a Pokémon being removed cleanly disappears from the target set
    either way instead of leaving a dangling id behind.
    """
    if settings_obj is None:
        return
    current = settings_obj.get("trainer.xp_share")
    individual_id = str(individual_id)
    if isinstance(current, list):
        remaining = [ind_id for ind_id in current if str(ind_id) != individual_id]
        if remaining != current:
            settings_obj.set("trainer.xp_share", remaining)
    elif current and str(current) == individual_id:
        settings_obj.set("trainer.xp_share", None)


def xp_share_gain_exp(logger, settings_obj, evo_window, main_pokemon_id, exp, xp_share_ids):
    """Split defeat XP between the main Pokémon and one or more XP Share targets.

    ``xp_share_ids`` accepts either a single individual_id (legacy/back-compat
    — older saves stored ``trainer.xp_share`` as a bare string) or a list of
    them. The main Pokémon always keeps half; the other half is divided evenly
    across however many (deduplicated, main-excluded) targets are given, and
    each target is leveled up/evolved exactly as the old single-target flow did.
    """
    if not xp_share_ids:
        return exp

    if isinstance(xp_share_ids, str):
        xp_share_ids = [xp_share_ids]

    # De-dupe and drop the main Pokémon (it already gets its own half below).
    seen = set()
    targets = []
    for ind_id in xp_share_ids:
        if not ind_id or ind_id == main_pokemon_id or ind_id in seen:
            continue
        seen.add(ind_id)
        targets.append(ind_id)

    if not targets:
        return exp

    original_exp = int(exp * 0.5)
    shared_exp = int(exp * 0.5)
    # Split the shared half evenly across every target.
    per_target_exp = max(1, shared_exp // len(targets)) if shared_exp > 0 else 0

    for target_id in targets:
        _xp_share_gain_exp_one(
            logger, settings_obj, evo_window, target_id, per_target_exp
        )

    return original_exp  # The main Pokémon's own half.


def _xp_share_gain_exp_one(logger, settings_obj, evo_window, xp_share_individual_id, exp):
    """Apply one XP Share target's share of XP (leveling/evolution included)."""
    remove_level_cap = settings_obj.get("misc.remove_level_cap")
    exp = int(exp)  # Convert the experience to an integer

    # Load pokemon from database
    db = services.db

    msg = ""
    evolution_triggered = False

    pokemon = db.get_pokemon(xp_share_individual_id)
    # The XP-Share target may have been released or traded away since it was
    # selected, leaving a dangling individual_id in settings. get_pokemon then
    # returns None and any pokemon[...] access below would raise
    # "'NoneType' object is not subscriptable" on the next review/defeat.
    # Drop just this stale id from the list (the other targets, if any, still
    # get their share) so the review continues normally.
    if pokemon is None:
        remaining = [
            ind_id
            for ind_id in (settings_obj.get("trainer.xp_share") or [])
            if ind_id != xp_share_individual_id
        ] if isinstance(settings_obj.get("trainer.xp_share"), list) else None
        settings_obj.set("trainer.xp_share", remaining)
        logger.log("info", "An XP Share target no longer exists; removed it from the list.")
        return

    current_level = int(pokemon['level'])  # MODIFIED: Use local variable for level
    if pokemon.get('held_item') == "lucky-egg":
        exp = int(exp * 1.5) # Multiply by 1.5 if pokemon holds lucky egg
        msg += f"{pokemon['name']}'s Lucky Egg boosts its XP gained!\n"
    # Increase the xp of the matched Pokémon
    current_xp = pokemon.get("xp") or pokemon.get("stats", {}).get("xp", 0)
    growth_rate = pokemon['growth_rate']  # MODIFIED: Use local variable for growth rate
    experience_needed = int(find_experience_for_level(growth_rate, current_level, remove_level_cap))  # MODIFIED: Pre-calculate needed XP
    evo_id = None # Initialize variable

    levels_gained = 0
    logger.log("info", "Running XP share function")
    if experience_needed > exp + current_xp:
        pokemon["xp"] = current_xp + exp
    else:
        while exp + current_xp > experience_needed:
            if (remove_level_cap or current_level < 100):
                if levels_gained >= 10:
                    logger.log("error", f"XP Share level-up loop exceeded safety cap of 10 for {pokemon['name']}")
                    exp = max(0, experience_needed - 1)
                    current_xp = 0
                    break
                levels_gained += 1
                current_level += 1
                exp = exp + current_xp - experience_needed
                current_xp = 0
                experience_needed = int(find_experience_for_level(growth_rate, current_level, remove_level_cap))  # MODIFIED: Recalculate needed XP
                msg += f"XP increased for {pokemon['name']} with level {current_level} and XP {exp}\n"
            else:
                break
        pokemon['level'] = current_level
        pokemon['xp'] = 0 if exp < 0 else exp

    # Check for evolution
    evo_id = check_evolution_for_pokemon(
        pokemon['individual_id'],
        pokemon['id'],
        pokemon['level'],
        evo_window,
        pokemon.get('everstone', False),
        pokemon.get('evolution_rejected', False)
    )

    if evo_id is not None:
        # return_name_for_id can return None if the evolved id is missing from
        # the name CSV; guard the .capitalize() so a data gap can't crash the
        # XP-share flow (mirrors the friendship path below).
        evo_disp_name = return_name_for_id(evo_id)
        evo_disp_name = evo_disp_name.capitalize() if evo_disp_name else str(evo_id)
        msg += f"{pokemon['name']} is about to evolve to {evo_disp_name} at level {pokemon['level']}"
        evolution_triggered = True

        # Write the XP/level changes to database BEFORE calling evolution
        db.save_pokemon(pokemon)

        # Now call evolution (which will read the updated file and handle the evolution)

    # Secondary friendship/time-of-day evolution check. Only fires if the level
    # check above did not already prompt an evolution (avoids double-prompting).
    # No friendship is granted here; it only triggers if stored friendship
    # already meets the species threshold.
    if not evolution_triggered:
        friendship_evo_id = check_friendship_evolution_for_pokemon(
            pokemon["individual_id"],
            pokemon["id"],
            evo_window,
            pokemon.get("everstone", False),
            pokemon.get("friendship", 0),
            pokemon.get("evolution_rejected", False),
        )
        if friendship_evo_id is not None:
            # return_name_for_id can return None if the evolved id is missing
            # from the name CSV; guard the .capitalize() so a data gap can't
            # crash the XP-share flow.
            friendship_evo_name = return_name_for_id(friendship_evo_id)
            friendship_evo_name = friendship_evo_name.capitalize() if friendship_evo_name else str(friendship_evo_id)
            msg += evo_window.translator.translate(
                "pokemon_about_to_evolve_friendship",
                main_pokemon_name=pokemon["name"],
                evo_pokemon_name=friendship_evo_name,
            )
            evolution_triggered = True

            # Write the XP/level changes to database BEFORE calling evolution
            db.save_pokemon(pokemon)

    # Only save to database if no evolution was triggered (since evolution already saved)
    if not evolution_triggered:
        db.save_pokemon(pokemon)

    logger.log("info", f"{msg}")
