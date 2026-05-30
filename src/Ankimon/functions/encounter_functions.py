from __future__ import annotations

import json
import random
import math
from typing import TYPE_CHECKING, Union
from datetime import datetime
import uuid

from ..services import services
from ..events import events
from ..functions.pokemon_functions import (
    find_experience_for_level,
    get_levelup_move_for_pokemon,
    pick_random_gender,
    shiny_chance,
)
from ..functions.pokedex_functions import (
    check_evolution_for_pokemon,
    get_all_pokemon_moves,
    get_base_experience,
    get_effort_values,
    get_growth_rate,
    return_name_for_id,
    search_pokedex,
    search_pokedex_by_id,
)
from ..functions.friendship_evolution import (
    check_friendship_evolution_for_pokemon,
)
from ..pyobj.error_handler import show_warning_with_traceback
from ..functions.trainer_functions import xp_share_gain_exp
from ..functions.badges_functions import check_for_badge, receive_badge
from ..functions.drawing_utils import tooltipWithColour
from ..utils import limit_ev_yield, play_effect_sound, get_ev_spread
from ..business import calc_experience, calculate_cp_from_dict
from ..const import gen_ids

if TYPE_CHECKING:
    # Type-hint-only imports (several pull in Qt). `from __future__ import
    # annotations` keeps the signatures below as strings so these never run.
    from ..pyobj.ankimon_tracker import AnkimonTracker
    from ..pyobj.pokemon_obj import PokemonObject
    from ..pyobj.reviewer_obj import Reviewer_Manager
    from ..pyobj.test_window import TestWindow
    from ..pyobj.trainer_card import TrainerCard
    from ..pyobj.InfoLogger import ShowInfoLogger
    from ..pyobj.evolution_window import EvoWindow
    from ..pyobj.translator import Translator

# Shared singletons used as bare module globals below. They are bound to the live
# registry objects by core.bind_runtime_globals() after composition, exactly as
# the old `from ..singletons import ...` did (a snapshot of stable objects).
# Function parameters of the same name shadow these where the faint/defeat
# helpers operate on the Pokemon passed in.
main_pokemon = None
ankimon_tracker_obj = None
trainer_card = None
settings_obj = None
translator = None
ankimon_db = None
pokemon_pc = None


_percentages_cache = {
    'percentages': None,
    'total_reviews': None,
    'trainer_level': None,
    'main_pokemon_level': None,
}

# ==============================================================================
# ENCOUNTER OVERHAUL CONFIGURATION (DEVELOPER TOGGLES & BALANCING COEFFICIENTS)
# ==============================================================================
USE_OVERHAUL_ENCOUNTER_SYSTEM = False

# EP Mastery Index Components Weights
EP_WEIGHT_TRAINER_LEVEL = 0.25     # T_norm weight
EP_WEIGHT_DEX_COMPLETION = 0.25    # D_norm weight
EP_WEIGHT_SESSION_PROGRESS = 0.25  # S_norm weight
EP_WEIGHT_CORE_TEAM_POWER = 0.25   # C_norm weight

# Scale limits for EP components
TRAINER_LEVEL_CAP = 50.0
CORE_TEAM_POWER_CAP = 16000.0

# Master Rarity Parameters: (Beginner Base Rate, Master Max Rate)
OVERHAUL_TIER_PARAMS = {
    "Normal": (96.98, 84.70),
    "Baby": (2.30, 3.0),
    "Ultra": (0.35, 4.50),
    "Gmax": (0.15, 2.50),
    "Starter": (0.10, 1.80),
    "Mega": (0.05, 1.50),
    "Legendary": (0.05, 1.50),
    "Mythical": (0.02, 0.50)
}

# Main Pokémon level thresholds for unlocking tiers
OVERHAUL_LEVEL_THRESHOLDS = {
    "Ultra": 30,
    "Legendary": 50,
    "Mega": 60,
    "Gmax": 65,
    "Mythical": 75,
    "Starter": 80,
}

# Dry spell thresholds for independent pity (Pi reviews)
OVERHAUL_PITY_THRESHOLDS = {
    "Ultra": 100,
    "Gmax": 150,
    "Starter": 175,
    "Mega": 200,
    "Legendary": 200,
    "Mythical": 400
}

# Pity divisor/scaling factor (the quadratic denominator)
OVERHAUL_PITY_DIVISOR = 50.0
# ==============================================================================


def calculate_mastery_index_ep(total_reviews, daily_average, trainer_level):
    """
    Calculate the Encounter Potential (EP) Mastery Index (0.0 to 100.0).
    EP = 0.30 * T_norm + 0.30 * D_norm + 0.25 * S_norm + 0.15 * C_norm
    """
    # 1. T_norm (Trainer Level)
    level_val = trainer_level if trainer_level is not None else 1
    t_norm = min((level_val / TRAINER_LEVEL_CAP) * 100.0, 100.0)

    # 2. D_norm (Pokedex Completion)
    d_norm = 0.0
    try:
        from ..functions.pokedex_functions import _load_pokedex_cache
        pokedex_data = _load_pokedex_cache()
        if pokedex_data and hasattr(mw, 'ankimon_db') and mw.ankimon_db:
            caught_ids = mw.ankimon_db.get_all_pokemon_ids()
            caught_species = set()
            for pid in caught_ids:
                if pid >= 10000:
                    name = search_pokedex_by_id(pid)
                    if name and name != "Pokémon not found":
                        base_id = safe_int(search_pokedex(name, "species_id"))
                        if base_id:
                            caught_species.add(base_id)
                else:
                    caught_species.add(pid)
                    
            unique_species_in_game = {safe_int(v.get("species_id")) for v in pokedex_data.values() if v.get("species_id")}
            unique_species_in_game.discard(0)
            total_species_count = len(unique_species_in_game) if unique_species_in_game else 1
            d_norm = (len(caught_species & unique_species_in_game) / total_species_count) * 100.0
    except Exception as e:
        print(f"[Ankimon] Warning: Error calculating Dex Completion for EP: {e}")

    # 3. S_norm (Session Progress)
    daily_goal = daily_average if daily_average and daily_average > 0 else 100.0
    s_norm = min((total_reviews / daily_goal) * 100.0, 100.0)

    # 4. C_norm (Core Team Power)
    c_norm = 0.0
    try:
        if hasattr(mw, 'ankimon_db') and mw.ankimon_db:
            all_pkmn = mw.ankimon_db.get_all_pokemon()
            if all_pkmn:
                cps = []
                for p in all_pkmn:
                    try:
                        cp = calculate_cp_from_dict(p)
                        cps.append(cp)
                    except Exception:
                        pass
                cps.sort(reverse=True)
                top_6 = cps[:6]
                avg_top_6_cp = sum(top_6) / len(top_6) if top_6 else 0.0
                c_norm = min((avg_top_6_cp / CORE_TEAM_POWER_CAP) * 100.0, 100.0)
    except Exception as e:
        print(f"[Ankimon] Warning: Error calculating Core Team Power for EP: {e}")

    ep = (EP_WEIGHT_TRAINER_LEVEL * t_norm) + \
         (EP_WEIGHT_DEX_COMPLETION * d_norm) + \
         (EP_WEIGHT_SESSION_PROGRESS * s_norm) + \
         (EP_WEIGHT_CORE_TEAM_POWER * c_norm)
    return max(0.0, min(ep, 100.0))

def load_pity_trackers() -> dict:
    default_pity = {
        "Ultra": 0,
        "Gmax": 0,
        "Starter": 0,
        "Mega": 0,
        "Legendary": 0,
        "Mythical": 0
    }
    try:
        if hasattr(mw, 'ankimon_db') and mw.ankimon_db:
            stored = mw.ankimon_db.get_user_data("ankimon_pity_trackers")
            if isinstance(stored, dict):
                for k in default_pity:
                    if k in stored:
                        default_pity[k] = int(stored[k])
    except Exception as e:
        print(f"[Ankimon] Warning: Error loading pity trackers: {e}")
    return default_pity

def save_pity_trackers(trackers: dict):
    try:
        if hasattr(mw, 'ankimon_db') and mw.ankimon_db:
            mw.ankimon_db.set_user_data("ankimon_pity_trackers", trackers)
    except Exception as e:
        print(f"[Ankimon] Warning: Error saving pity trackers: {e}")

def _modify_percentages_overhaul(total_reviews, daily_average, trainer_level):
    """
    Overhaul calculation for encounter percentages based on the Mastery Index (EP),
    Exponential Rarity Scaling, and Independent Pity systems.
    """
    ep = calculate_mastery_index_ep(total_reviews, daily_average, trainer_level)

    # Generate base weights
    weights = {}
    for tier, (base, max_val) in OVERHAUL_TIER_PARAMS.items():
        weights[tier] = base * ((max_val / base) ** (ep / 100.0))

    # Apply level thresholds
    level_val = main_pokemon.level if main_pokemon and hasattr(main_pokemon, 'level') and main_pokemon.level is not None else 1
    for tier, limit in OVERHAUL_LEVEL_THRESHOLDS.items():
        if level_val < limit:
            weights[tier] = 0.0

    # Apply pity multipliers
    pity_trackers = load_pity_trackers()
    for tier in OVERHAUL_PITY_THRESHOLDS:
        p_i = pity_trackers.get(tier, 0)
        t_i = OVERHAUL_PITY_THRESHOLDS[tier]
        multiplier = 1.0 + (max(0, (p_i - t_i) / OVERHAUL_PITY_DIVISOR)) ** 2
        weights[tier] = weights[tier] * multiplier

    # Force Starter to 0 (Comment to activate starters)
    #weights["Starter"] = 0.0

    total_sum = sum(weights.values())
    percentages = {}
    for tier in weights:
        percentages[tier] = (weights[tier] / total_sum) * 100.0 if total_sum > 0.0 else 0.0

    return percentages

def modify_percentages(total_reviews, daily_average, trainer_level):
    """
    Modify Pokémon encounter percentages based on total reviews, trainer level, and main Pokémon level.
    """
    if USE_OVERHAUL_ENCOUNTER_SYSTEM:
        return _modify_percentages_overhaul(total_reviews, daily_average, trainer_level)

    # Legacy System
    # Performance Guard: Skip recalculation if inputs haven't changed
    # Check if cache is valid
    if (_percentages_cache['percentages'] is not None and
        _percentages_cache['total_reviews'] == total_reviews and
        _percentages_cache['trainer_level'] == trainer_level and
        _percentages_cache['main_pokemon_level'] == main_pokemon.level):
        return _percentages_cache['percentages']

    # Start with the base percentages
    percentages = {"Baby": 2, "Legendary": 0.5, "Mythical": 0.2, "Normal": 92.3, "Ultra": 5}

    # Adjust percentages based on total reviews relative to the daily average
    review_ratio = total_reviews / daily_average if daily_average > 0 else 0

    # Adjust for review progress
    if review_ratio < 0.4:
        percentages["Normal"] += percentages.pop("Baby", 0) + percentages.pop("Legendary", 0) + \
                                 percentages.pop("Mythical", 0) + percentages.pop("Ultra", 0)
    elif review_ratio < 0.6:
        percentages["Baby"] += 2
        percentages["Normal"] -= 2
    elif review_ratio < 0.8:
        percentages["Ultra"] += 3
        percentages["Normal"] -= 3
    else:
        percentages["Legendary"] += 2
        percentages["Ultra"] += 3
        percentages["Normal"] -= 5

    # Restrict access to certain tiers based on main Pokémon level
    if main_pokemon.level:
        # Define level thresholds for each tier
        level_thresholds = {
            "Ultra": 30,  # Example threshold for Ultra Pokémon
            "Legendary": 50,  # Example threshold for Legendary Pokémon
            "Mythical": 75  # Example threshold for Mythical Pokémon
        }

        for tier in ["Ultra", "Legendary", "Mythical"]:
            if main_pokemon.level < level_thresholds.get(tier, float("inf")):
                percentages[tier] = 0  # Set percentage to 0 if the level requirement isn't met

    # Example modification based on trainer level
    if trainer_level:
        adjustment = 5  # Adjustment value for the example
        if trainer_level > 10:
            for tier in percentages:
                if tier == "Normal":
                    percentages[tier] = max(percentages[tier] - adjustment, 0)
                else:
                    percentages[tier] = percentages.get(tier, 0) + adjustment

    # Normalize percentages to ensure they sum to 100
    total = sum(percentages.values())
    for tier in percentages:
        percentages[tier] = (percentages[tier] / total) * 100 if total > 0 else 0

    # Cache and return
    _percentages_cache['percentages'] = percentages
    _percentages_cache['total_reviews'] = total_reviews
    _percentages_cache['trainer_level'] = trainer_level
    _percentages_cache['main_pokemon_level'] = main_pokemon.level
    
    # this function gets called maybe 10 times per battle round, which is concerning.
    # it could be rewritten to run ONLY when the change in review ratio is detected.
    return percentages


def get_random_pokemon_in_tier(tier):
    from . import encounter_data

    if tier == "Normal":
        id_data = encounter_data.NORMAL
    elif tier == "Baby":
        id_data = encounter_data.BABY
    elif tier == "Ultra":
        id_data = encounter_data.ULTRA
    elif tier == "Legendary":
        id_data = encounter_data.LEGENDARY
    elif tier == "Mythical":
        id_data = encounter_data.MYTHICAL
    else:
        raise ValueError()

    # Select a random Pokemon ID from those in the tier
    random_pokemon_id = random.choice(id_data)
    return random_pokemon_id


def get_tier(total_reviews, trainer_level=1, event_modifier=None):
    """_summary_
    Randomly picks the tier for a new enemy Pokemon to be generated from, based on weighted probabilities based on number of reviews and trainer level.

    Args:
        total_reviews (int): Number of reviews done in that Anki session.
        trainer_level (int, optional): Trainer XP level. Defaults to 1.
        event_modifier (?, optional): Unused argument. Defaults to None.

    Returns:
        choice[0]: The first choice of TIER picked randomly (by a random.choices function)
    """
    daily_average = int(settings_obj.get("battle.daily_average"))
    percentages = modify_percentages(total_reviews, daily_average, trainer_level)

    tiers = list(percentages.keys())
    probabilities = list(percentages.values())

    choice = random.choices(tiers, probabilities, k=1)
    return choice[0]


def choose_random_pkmn_from_tier():
    """
    Runs a tier-selection and a subsequent ID-selection function to pick a random Pokemon from a given randomly picked Tier.
    The tier is a weighted probability selection, based on total_reviews and trainer_level.
    Pokemon ID is picked randomly from within that tier.

    Returns:
        id (int): Pokedex ID for generated Pokemon
        tier (str): Rarity tier for generated Pokemon (normal/ultra/legendary etc.)
    """
    total_reviews = ankimon_tracker_obj.get_total_reviews()
    trainer_level = trainer_card.level
    try:
        tier = get_tier(total_reviews, trainer_level)
        id = get_random_pokemon_in_tier(tier)
        services.logger.game_log(f"Selected tier: {tier}, Resulting Pokemon ID: {id}")
        return id, tier
    except Exception as e:
        services.logger.log("error", f"Error in choose_random_pkmn_from_tier: {str(e)}")
        show_warning_with_traceback(exception=e, message="Error occurred")


def check_min_generate_level(name):
    evoType = search_pokedex(name.lower(), "evoType")
    evoLevel = search_pokedex(name.lower(), "evoLevel")
    if evoLevel:
        return int(evoLevel)
    elif evoType != []:
        min_level = 100
        return min_level
    else:
        min_level = 1
        return min_level


def check_id_ok(id_num: Union[int, list[int]]):
    if isinstance(id_num, list):
        if len(id_num) > 0:
            id_num = id_num[0]
        else:
            return False

    if not isinstance(id_num, int):
        return False

    generation = 0
    for gen, max_id in gen_ids.items():
        if id_num <= max_id:
            generation = int(gen.split("_")[1])

            gen_config = [settings_obj.get(f"misc.gen{i}") for i in range(1, 10)]
            return gen_config[generation - 1]

    return False


def generate_random_pokemon(
    main_pokemon_level: int, ankimon_tracker_obj: AnkimonTracker
):
    """
    Generates a random wild Pokémon with attributes scaled to the level of the player's main Pokémon.

    This function resets the encounter and battle round state in the provided `AnkimonTracker` object.
    It then selects a valid Pokémon that can appear at the current level range, computes its stats,
    determines its moves, ability, and other combat-relevant characteristics, and returns all necessary
    data required for a battle.

    Args:
        main_pokemon_level (int): The level of the player's main Pokémon. Determines the level range of
            the generated wild Pokémon.
        ankimon_tracker_obj (AnkimonTracker): An object used to track battle state, such as the number
            of Pokémon encountered and cards used in the battle.

    Returns:
        tuple: A tuple containing the following elements:
            - name (str): Name of the wild Pokémon.
            - pokemon_id (int): Unique ID of the Pokémon.
            - wild_pokemon_lvl (int): The level of the generated Pokémon.
            - ability (str): The selected ability of the Pokémon.
            - pokemon_type (list[str]): List of type(s) the Pokémon belongs to.
            - base_stats (dict): Dictionary of the Pokémon's base stats.
            - moves (list[str]): List of up to 4 moves the Pokémon can use in battle.
            - base_experience (int): Experience points awarded for defeating the Pokémon.
            - growth_rate (str): Growth rate category of the Pokémon (e.g., "slow", "fast").
            - ev (dict): Effort values (EVs) for each stat, initialized to 0.
            - iv (dict): Randomly generated individual values (IVs) for each stat.
            - gender (str): Randomly assigned gender.
            - battle_status (str): Current status of the Pokémon in battle, defaulted to "fighting".
            - final_stats (dict): Final computed stats of the Pokémon.
            - tier (str): Tier from which the Pokémon was selected (e.g., common, rare).
            - ev_yield (dict): Effort values (EVs) awarded upon defeating the Pokémon.
            - is_shiny (bool): Indicates whether the Pokémon is shiny.

    Raises:
        ValueError: If no valid Pokémon can be generated (highly unlikely under normal conditions).
    """
    lvl_variation = 3
    lvl_range = (
        max(1, main_pokemon_level - lvl_variation),
        max(1, main_pokemon_level + lvl_variation),
    )
    wild_pokemon_lvl = random.randint(*lvl_range)
    wild_pokemon_lvl = max(
        1, wild_pokemon_lvl
    )  # Ensures that the wild pokemon's level is at least 1
    if main_pokemon_level == 100:
        wild_pokemon_lvl = 100

    from ..utils import load_collected_pokemon_ids
    collected_ids = load_collected_pokemon_ids()

    # FALLBACK HIERARCHY
    # If a rolled tier fails, try the next one in the list.
    TIER_ORDER = ["Mythical", "Mega", "Legendary", "Gmax", "Ultra", "Starter", "Baby", "Normal"]
    
    selected_pokemon_id = None
    selected_tier = None
    
    # 1. Select the initial tier based on probabilities
    initial_tier = get_tier(ankimon_tracker_obj.get_total_reviews(), trainer_card.level)
    
    # Find starting point in fallback order
    try:
        start_idx = TIER_ORDER.index(initial_tier)
    except ValueError:
        start_idx = TIER_ORDER.index("Normal")
        
    # Iterate through tiers starting from the rolled one
    for i in range(start_idx, len(TIER_ORDER)):
        current_tier = TIER_ORDER[i]
        
        tier_ids = get_all_pokemon_in_tier(current_tier)
        full_pool = []
        for pokemon_id in tier_ids:
            name = search_pokedex_by_id(pokemon_id)
            if not name or name == "Pokémon not found":
                continue
                
            # Guard 1: Generation check
            if not check_id_ok(pokemon_id):
                continue

            # Guard 2: Level check
            min_allowed_pokemon_lvl = check_min_generate_level(str(name.lower()))
            if wild_pokemon_lvl < min_allowed_pokemon_lvl:
                continue

            # Guard 3: Mega/Gmax base ownership
            if current_tier in ("Mega", "Gmax") and not _player_owns_base_form(pokemon_id, collected_ids):
                continue

            # Guard 4: Prerequisite check
            if not _meets_prerequisites(pokemon_id, collected_ids):
                continue
                
            full_pool.append(pokemon_id)
            
        if not full_pool:
            continue

        active_region = settings_obj.get("misc.active_region")
        boosted_pool = []

        if active_region:
            boosted_gens = get_boosted_gens_for_region(active_region)
            
            for pid in full_pool:
                if get_base_species_gen(pid) in boosted_gens:
                    if pid not in boosted_pool:
                        boosted_pool.append(pid)
                
                # Add eligible regional variants for the active region
                options = encounter_data.REGIONAL_FORM_LOOKUP.get(pid, {}).get(active_region, [])
                for opt in options:
                    if check_id_ok(opt) and opt not in boosted_pool:
                        boosted_pool.append(opt)

        if active_region and boosted_pool:
            chance = get_boosted_pool_chance(active_region)
            if random.random() < chance:
                selected_pokemon_id = random.choice(boosted_pool)
            else:
                selected_pokemon_id = random.choice(full_pool)
        else:
            selected_pokemon_id = random.choice(full_pool)

        selected_tier = current_tier
        break
            
    # Final fallback if somehow everything failed (e.g. settings restrict all IDs)
    if not selected_pokemon_id:
        selected_pokemon_id = 19 # Rattata
        selected_tier = "Normal"

    # --- Regional form resolution ---
    # Apply 7%-per-variant resolution for base species.
    if selected_pokemon_id < 10000:
        region_forms = encounter_data.REGIONAL_FORM_LOOKUP.get(selected_pokemon_id, {})
        num_eligible = 0
        for variants in region_forms.values():
            for v in variants:
                if check_id_ok(v):
                    num_eligible += 1
        
        if num_eligible > 0:
            if random.random() < 0.07 * num_eligible:
                sub = get_regional_substitute(selected_pokemon_id)
                if sub:
                    selected_pokemon_id = sub
    # --- End form resolution ---

    pokemon_id = selected_pokemon_id
    tier = selected_tier

    # Update pity trackers if overhaul system is active
    if USE_OVERHAUL_ENCOUNTER_SYSTEM:
        try:
            pity_trackers = load_pity_trackers()
            rare_tiers = ["Ultra", "Gmax", "Starter", "Mega", "Legendary", "Mythical"]
            if tier in rare_tiers:
                pity_trackers[tier] = 0
                for rt in rare_tiers:
                    if rt != tier:
                        pity_trackers[rt] += 1
            else:
                for rt in rare_tiers:
                    pity_trackers[rt] += 1
            save_pity_trackers(pity_trackers)
        except Exception as e:
            print(f"[Ankimon] Warning: Error updating pity trackers in generate_random_pokemon: {e}")
    name = search_pokedex_by_id(pokemon_id)
    min_allowed_pokemon_lvl = check_min_generate_level(
        str(name.lower())
    )  # Gets the minimum allowed level for that pokemon given its stage of evolution

    attempts = 0
    while (not check_id_ok(pokemon_id)) or (
        wild_pokemon_lvl < min_allowed_pokemon_lvl
    ):  # We keep drawing a random pokemon until we find a valid one
        attempts += 1
        if attempts >= 500:
            services.ui.warn("Failed to generate a valid Pokémon after 500 attempts. Please ensure at least one generation is enabled in the settings. Defaulting to Rattata.")
            pokemon_id = 19
            name = search_pokedex_by_id(19)
            tier = "Normal"
            min_allowed_pokemon_lvl = check_min_generate_level(str(name.lower()))
            wild_pokemon_lvl = max(wild_pokemon_lvl, min_allowed_pokemon_lvl)
            break

        pokemon_id, tier = choose_random_pkmn_from_tier()
        name = search_pokedex_by_id(pokemon_id)
        min_allowed_pokemon_lvl = check_min_generate_level(
            str(name.lower())
        )  # Gets the minimum allowed level for that pokemon given its stage of evolution

    # Now we get all necessary information about the chosen pokemon.
    pokemon_type = search_pokedex(name, "types")
    base_experience = get_base_experience(
        search_pokedex(name, "actual_id")
    )  # Experience that the wild pokemon will give once beaten
    growth_rate = get_growth_rate(pokemon_id)
    ev_yield = get_effort_values(search_pokedex(name, "actual_id"))
    gender = pick_random_gender(name)
    is_shiny = shiny_chance()
    battle_status = "fighting"
    base_stats = search_pokedex(name, "baseStats")

    all_possible_moves = get_all_pokemon_moves(name, wild_pokemon_lvl)
    if len(all_possible_moves) <= 4:
        moves = all_possible_moves
    else:
        moves = random.sample(all_possible_moves, 4)

    ability = "no_ability"  # Default value for ability
    possible_abilities = search_pokedex(name, "abilities")
    if possible_abilities:
        numeric_abilities = {k: v for k, v in possible_abilities.items() if k.isdigit()}
        if numeric_abilities:
            ability = random.choice(list(numeric_abilities.values()))

    stat_names = ["hp", "atk", "def", "spa", "spd", "spe"]
    # ev = {stat: 0 for stat in stat_names}
    ev = get_ev_spread(random.choice(["random", "pair", "defense", "uniform"]))
    # tau = 200
    # mu = 31 * (1 - math.exp(-ankimon_tracker_obj.total_reviews / tau))  # At total reviews > 3 * tau, we get mu ~= 31
    # iv = {stat: iv_rand_gauss(mu=mu, sigma=5) for stat in stat_names}  # The higher the number of reviews, the higher the IVs
    iv = {stat: random.randint(0, 31) for stat in stat_names}
    final_stats = base_stats

    ankimon_tracker_obj.pokemon_encounter = 0  # 0: Start of Battle: 1: Current Battle
    ankimon_tracker_obj.cards_battle_round = 0  # Amount of cards in this current battle

    return (
        name,
        pokemon_id,
        wild_pokemon_lvl,
        ability,
        pokemon_type,
        base_stats,
        moves,
        base_experience,
        growth_rate,
        ev,
        iv,
        gender,
        battle_status,
        final_stats,
        tier,
        ev_yield,
        is_shiny,
    )


def new_pokemon(
    pokemon: PokemonObject,
    test_window: TestWindow,
    ankimon_tracker: AnkimonTracker,
    reviewer_obj: Reviewer_Manager,
) -> PokemonObject:
    """
    Initializes a new wild Pokémon encounter by generating a random Pokémon,
    updating its stats, setting its HP, and preparing the battle scene.

    This function uses the player's main Pokémon level to generate an appropriately
    leveled wild Pokémon with randomized attributes. It updates the provided `pokemon`
    object with generated data, resets HP, triggers any battle scene randomization,
    and updates the reviewer interface if applicable.

    Args:
        pokemon (PokemonObject): The Pokémon object to be updated with the new wild Pokémon's data.
        test_window (TestWindow): Optional UI window to display the first encounter scene.
        ankimon_tracker (AnkimonTracker): Object tracking battle-related state and handling battle scene randomization.
        reviewer_obj (Reviewer_Manager): Manager object responsible for updating battle review elements like life bars.

    Returns:
        PokemonObject: The updated `pokemon` object representing the newly generated wild Pokémon ready for battle.
    """
    (
        name,
        pkmn_id,
        level,
        ability,
        pkmn_type,
        base_stats,
        enemy_attacks,
        base_experience,
        growth_rate,
        ev,
        iv,
        gender,
        battle_status,
        battle_stats,
        tier,
        ev_yield,
        is_shiny,
    ) = generate_random_pokemon(main_pokemon.level, ankimon_tracker_obj)
    pokemon_data = {
        "name": name,
        "id": pkmn_id,
        "level": level,
        "ability": ability,
        "type": pkmn_type,
        "base_stats": base_stats,
        "attacks": enemy_attacks,
        "base_experience": base_experience,
        "growth_rate": growth_rate,
        "ev": ev,
        "iv": iv,
        "gender": gender,
        "battle_status": battle_status,
        "battle_stats": battle_stats,
        "stat_stages": {
            "atk": 0,
            "def": 0,
            "spa": 0,
            "spd": 0,
            "spe": 0,
            "accuracy": 0,
            "evasion": 0,
        },
        "tier": tier,
        "ev_yield": ev_yield,
        "shiny": is_shiny,
    }
    pokemon.update_stats(**pokemon_data)
    max_hp = pokemon.calculate_max_hp()
    pokemon.current_hp = max_hp
    pokemon.hp = max_hp
    pokemon.max_hp = max_hp

    ankimon_tracker.randomize_battle_scene()
    if test_window is not None:
        test_window.display_first_encounter()

    # Observable: a fresh wild Pokemon appeared.
    events.emit(
        "encounter",
        pokemon=pokemon.name,
        id=pokemon.id,
        level=pokemon.level,
        tier=pokemon.tier,
        shiny=pokemon.shiny,
        hp=pokemon.hp,
        max_hp=pokemon.max_hp,
    )

    # Re-render the reviewer HUD. refresh_hud() grabs the live webview under
    # Anki and is a recorded no-op headless.
    if reviewer_obj is not None:
        reviewer_obj.refresh_hud()

    return pokemon


def save_main_pokemon_progress(
    main_pokemon: PokemonObject,
    enemy_pokemon: PokemonObject,
    exp: int,
    achievements: dict,
    logger: ShowInfoLogger,
    evo_window: EvoWindow,
):
    experience = int(
        find_experience_for_level(
            main_pokemon.growth_rate,
            main_pokemon.level,
            settings_obj.get("misc.remove_level_cap"),
        )
    )
    if settings_obj.get("misc.remove_level_cap") is True:
        main_pokemon.xp += exp
        level_cap = None
    elif main_pokemon.level != 100:
        main_pokemon.xp += exp
        level_cap = 100
    else:
        # Cap is on AND the main is already level 100: no XP is granted, but
        # level_cap must still be defined or the while-loop condition below
        # raises NameError and crashes every post-cap defeat (upstream #402).
        level_cap = 100
    try:
        db = services.db
        main_pokemon_data = db.get_main_pokemon()
        if not main_pokemon_data:
            services.ui.warn(translator.translate("missing_mainpokemon_data"))
    except Exception as e:
        services.logger.log("error", f"Error loading main pokemon data: {str(e)}")
        show_warning_with_traceback(
            exception=e, message="Error loading main pokemon data."
        )
        return
    evolution_prompted = False
    while int(
        find_experience_for_level(
            main_pokemon.growth_rate,
            main_pokemon.level,
            settings_obj.get("misc.remove_level_cap"),
        )
    ) < int(main_pokemon.xp) and (level_cap is None or main_pokemon.level < level_cap):
        main_pokemon.level += 1
        events.emit("levelup", pokemon=main_pokemon.name, level=main_pokemon.level)
        msg = ""
        msg += f"Your {main_pokemon.name} is now level {main_pokemon.level} !"
        color = "#6A4DAC"  # pokemon leveling info color for tooltip
        check = check_for_badge(achievements, 5)
        if check is False:
            achievements = receive_badge(5, achievements)
        try:
            services.logger.game_log(f"Level Up: {msg}")
            tooltipWithColour(msg, color)
        except:
            pass
        if settings_obj.get("gui.pop_up_dialog_message_on_defeat") is True:
            logger.log_and_showinfo("info", f"{msg}")
        main_pokemon.xp = int(max(0, int(main_pokemon.xp) - int(experience)))

        # Request to open the pokemon evo window
        evo_id = check_evolution_for_pokemon(
            main_pokemon.individual_id,
            main_pokemon.id,
            main_pokemon.level,
            evo_window,
            main_pokemon.everstone,
            getattr(main_pokemon, "evolution_rejected", False),
        )
        if evo_id is not None:
            evolution_prompted = True
            events.emit("evolution_offered", pokemon=main_pokemon.name, trigger="level", evo_id=evo_id)
            # None-safe: return_name_for_id can return None for an unknown id, so
            # fall back to the numeric id instead of crashing on .capitalize()
            # (mirrors the friendship-evolution path below).
            evo_display_name = return_name_for_id(evo_id)
            evo_display_name = (
                evo_display_name.capitalize() if evo_display_name else str(evo_id)
            )
            logger.log_and_showinfo(
                "info",
                translator.translate(
                    "pokemon_about_to_evolve",
                    main_pokemon_name=main_pokemon.name,
                    evo_pokemon_name=evo_display_name,
                    main_pokemon_level=main_pokemon.level,
                ),
            )

        if main_pokemon_data:
            mainpkmndata = main_pokemon_data
            if mainpkmndata["name"] == main_pokemon.name.capitalize():
                attacks = mainpkmndata["attacks"]
                new_attacks = get_levelup_move_for_pokemon(
                    main_pokemon.name.lower(), int(main_pokemon.level)
                )
                if new_attacks:
                    msg = ""
                    msg += translator.translate(
                        "mainpokemon_can_learn_new_attack",
                        main_pokemon_name=main_pokemon.name.capitalize(),
                    )
                for new_attack in new_attacks:
                    if len(attacks) < 4 and new_attack not in attacks:
                        attacks.append(new_attack)
                        msg += translator.translate(
                            "mainpokemon_learned_new_attack",
                            new_attack_name=new_attack,
                            main_pokemon_name=main_pokemon.name.capitalize(),
                        )
                        color = "#6A4DAC"
                        tooltipWithColour(msg, color)
                        if (
                            settings_obj.get("gui.pop_up_dialog_message_on_defeat")
                            is True
                        ):
                            logger.log_and_showinfo("info", f"{msg}")
                    else:
                        # Ask via the UI port (real dialog under Anki; scripted
                        # choice headless). None => discard the new move.
                        selected_attack = services.ui.choose_attack_to_replace(
                            attacks, new_attack
                        )
                        if selected_attack is not None:
                            index_to_replace = None
                            for index, attack in enumerate(attacks):
                                if attack == selected_attack:
                                    index_to_replace = index
                            # If the attack is found, replace it with 'new_attack'
                            if index_to_replace is not None:
                                attacks[index_to_replace] = new_attack
                                logger.log_and_showinfo(
                                    "info",
                                    f"Replaced '{selected_attack}' with '{new_attack}'",
                                )
                            else:
                                logger.log_and_showinfo(
                                    "info", f"'{selected_attack}' not found in the list"
                                )
                        else:
                            # User declined to replace a move; discard the new one.
                            logger.log_and_showinfo(
                                "info", f"{new_attack} will be discarded."
                            )
                mainpkmndata["attacks"] = attacks
    msg = ""
    msg += translator.translate(
        "mainpokemon_gained_xp",
        main_pokemon_name=main_pokemon.name,
        exp=exp,
        experience_till_next_level=experience,
        main_pokemon_xp=main_pokemon.xp,
    )
    color = "#a17cf7"  # pokemon leveling info color for tooltip
    tooltipWithColour(msg, color)
    if settings_obj.get("gui.pop_up_dialog_message_on_defeat") is True:
        logger.log_and_showinfo("info", f"{msg}")

    # Load existing Pokémon data if it exists
    if main_pokemon_data:
        mainpkmndata = main_pokemon_data
        mainpkmndata["stats"] = main_pokemon.stats
        mainpkmndata["xp"] = int(main_pokemon.xp)
        mainpkmndata["level"] = int(main_pokemon.level)
        # Clone raw EV yield to avoid mutating the in-memory enemy template
        raw_ev_yield = enemy_pokemon.ev_yield.copy()
        
        # Normalize keys to the standard long form expected by limit_ev_yield
        normalized_yield = {
            "hp": raw_ev_yield.get("hp", 0),
            "attack": raw_ev_yield.get("attack", 0) + raw_ev_yield.get("atk", 0),
            "defense": raw_ev_yield.get("defense", 0) + raw_ev_yield.get("def", 0),
            "special-attack": raw_ev_yield.get("special-attack", 0) + raw_ev_yield.get("spa", 0),
            "special-defense": raw_ev_yield.get("special-defense", 0) + raw_ev_yield.get("spd", 0),
            "speed": raw_ev_yield.get("speed", 0) + raw_ev_yield.get("spe", 0),
        }

        held_item = mainpkmndata.get("held_item", main_pokemon.held_item)

        # Apply EV-boosting held items
        if held_item == "macho-brace":
            for stat in normalized_yield:
                normalized_yield[stat] *= 2
        else:
            power_item_mapping = {
                "power-weight": "hp",
                "power-bracer": "attack",
                "power-belt": "defense",
                "power-lens": "special-attack",
                "power-band": "special-defense",
                "power-anklet": "speed",
            }
            if held_item in power_item_mapping:
                stat_to_boost = power_item_mapping[held_item]
                normalized_yield[stat_to_boost] += 8

        ev_yield = limit_ev_yield(mainpkmndata["ev"], normalized_yield)
        mainpkmndata["ev"]["hp"] += ev_yield["hp"]
        mainpkmndata["ev"]["atk"] += ev_yield["attack"]
        mainpkmndata["ev"]["def"] += ev_yield["defense"]
        mainpkmndata["ev"]["spa"] += ev_yield["special-attack"]
        mainpkmndata["ev"]["spd"] += ev_yield["special-defense"]
        mainpkmndata["ev"]["spe"] += ev_yield["speed"]
        # Mirror EV gain onto the in-memory object so CP/stats reads
        # stay consistent with the persisted dict until next restart.
        # Dict-item mutation doesn't fire __setattr__, so invalidate
        # the CP cache explicitly.
        main_pokemon.ev["hp"] += ev_yield["hp"]
        main_pokemon.ev["atk"] += ev_yield["attack"]
        main_pokemon.ev["def"] += ev_yield["defense"]
        main_pokemon.ev["spa"] += ev_yield["special-attack"]
        main_pokemon.ev["spd"] += ev_yield["special-defense"]
        main_pokemon.ev["spe"] += ev_yield["speed"]
        main_pokemon.invalidate_cp_cache()
        mainpkmndata["current_hp"] = int(main_pokemon.hp)
        # Friendship is uncapped — it keeps climbing past MAX_FRIENDSHIP (400) so
        # players can flex a super-bonded Pokémon. The progress bar still fills at
        # MAX_FRIENDSHIP; the raw number above it is what keeps growing.
        main_pokemon.friendship += random.randint(5, 9)
        mainpkmndata["friendship"] = main_pokemon.friendship
        if not evolution_prompted:
            friendship_evo_id = check_friendship_evolution_for_pokemon(
                main_pokemon.individual_id,
                main_pokemon.id,
                evo_window,
                main_pokemon.everstone,
                main_pokemon.friendship,
                getattr(main_pokemon, "evolution_rejected", False),
            )
            if friendship_evo_id is not None:
                evolution_prompted = True
                events.emit("evolution_offered", pokemon=main_pokemon.name, trigger="friendship", evo_id=friendship_evo_id)
                # return_name_for_id can return None (and pop a spurious warning)
                # if the evolved id is missing from the name CSV; guard the
                # .capitalize() so a data gap can't crash the defeat flow.
                friendship_evo_name = return_name_for_id(friendship_evo_id)
                friendship_evo_name = friendship_evo_name.capitalize() if friendship_evo_name else str(friendship_evo_id)
                logger.log_and_showinfo(
                    "info",
                    translator.translate(
                        "pokemon_about_to_evolve_friendship",
                        main_pokemon_name=main_pokemon.name,
                        evo_pokemon_name=friendship_evo_name,
                    ),
                )
        main_pokemon.pokemon_defeated += 1
        mainpkmndata["pokemon_defeated"] = main_pokemon.pokemon_defeated
        if hasattr(main_pokemon, "tier"):
            mainpkmndata["tier"] = main_pokemon.tier
        if hasattr(main_pokemon, "is_favorite"):
            mainpkmndata["is_favorite"] = main_pokemon.is_favorite

        # Save to database (replaces JSON file I/O for performance)
        ankimon_db.save_main_pokemon(mainpkmndata)
        ankimon_db.save_pokemon(mainpkmndata)  # Also update the captured pokemon collection

    return main_pokemon.level

# --- Utility: Sync mainpokemon to mypokemon ---
def sync_mainpokemon_to_mypokemon(main_pokemon):
    """
    Update the relevant entry in mypokemon database with the latest values from mainpokemon.
    Uses database instead of JSON files.
    """
    db = services.db

    # Get main pokemon from database
    main_entry = db.get_main_pokemon()
    if not main_entry:
        return
    
    main_id = main_entry.get("individual_id", None)
    if not main_id:
        main_id = getattr(main_pokemon, "individual_id", None)
    if not main_id:
        return
    
    # Save/update in captured_pokemon table
    db.save_pokemon(main_entry)
    return

def kill_pokemon(
    main_pokemon: PokemonObject,
    enemy_pokemon: PokemonObject,
    evo_window: EvoWindow,
    logger: ShowInfoLogger,
    achievements: dict,
    trainer_card: Union[TrainerCard, None] = None,
):
    events.emit(
        "defeat",
        pokemon=enemy_pokemon.name,
        id=enemy_pokemon.id,
        level=enemy_pokemon.level,
        tier=enemy_pokemon.tier,
    )
    if trainer_card is not None:
        trainer_card.gain_xp(
            enemy_pokemon.tier, settings_obj.get("controls.allow_to_choose_moves")
        )

    # Calculate experience based on whether moves are chosen manually
    exp = calc_experience(enemy_pokemon.base_experience, enemy_pokemon.level)
    if settings_obj.get("controls.allow_to_choose_moves"):
        exp *= 0.5

    # Ensure exp is at least 1 and round up if it's a decimal
    exp = max(1, math.ceil(exp))

    # Handle XP share logic
    xp_share_individual_id = settings_obj.get("trainer.xp_share")
    if xp_share_individual_id:
        exp = xp_share_gain_exp(logger, settings_obj, evo_window, main_pokemon.id, exp, xp_share_individual_id)
    
    msg = ""

    if main_pokemon.held_item == "lucky-egg":
        exp = int(exp * 1.5)
        msg += f"{main_pokemon.name}'s Lucky Egg boosts its XP gained!\n"

    logger.log("info", msg)

    # Save main Pokémon's progress
    main_pokemon.level = save_main_pokemon_progress(
        main_pokemon,
        enemy_pokemon,
        exp,
        achievements,
        logger,
        evo_window,
    )

    ankimon_tracker_obj.general_card_count_for_battle = 0


def save_caught_pokemon(
    enemy_pokemon: PokemonObject,
    nickname: Union[str, None] = None,
    achievements: Union[dict, None] = None,
):
    # Create a dictionary to store the Pokémon's data
    # add all new values like hp as max_hp, evolution_data, description and growth rate
    if enemy_pokemon.tier is not None and achievements is not None:
        if enemy_pokemon.tier == "Normal":
            check = check_for_badge(achievements, 17)
            if check is False:
                achievements = receive_badge(17, achievements)
        elif enemy_pokemon.tier == "Baby":
            check = check_for_badge(achievements, 18)
            if check is False:
                achievements = receive_badge(18, achievements)
        elif enemy_pokemon.tier == "Ultra":
            check = check_for_badge(achievements, 8)
            if check is False:
                achievements = receive_badge(8, achievements)
        elif enemy_pokemon.tier == "Legendary":
            check = check_for_badge(achievements, 9)
            if check is False:
                achievements = receive_badge(9, achievements)
        elif enemy_pokemon.tier == "Mythical":
            check = check_for_badge(achievements, 10)
            if check is False:
                achievements = receive_badge(10, achievements)

    # enemy_pokemon.stats["xp"] = 0
    enemy_pokemon.xp = 0
    # Use to_dict() so the caught record shares the canonical shape with
    # saved main Pokemon (includes base_stats, level-scaled stats, cp,
    # nature). Then override caught-only fields.
    _max_hp = enemy_pokemon.calculate_max_hp()
    caught_pokemon = enemy_pokemon.to_dict()
    caught_pokemon.update({
        "name": enemy_pokemon.name.capitalize(),
        "nickname": nickname or "",
        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        "friendship": 0,
        "pokemon_defeated": 0,
        "xp": 0,
        "everstone": False,
        "captured_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "individual_id": str(uuid.uuid4()),
        "mega": False,
        "special_form": None,
        "is_favorite": False,
        "held_item": None,
        "hp": _max_hp,
        "current_hp": _max_hp,
    })
    # Recompute CP against the overridden (zeroed) EVs.
    caught_pokemon["cp"] = calculate_cp_from_dict(caught_pokemon)

    # Save to database (replaces JSON file I/O for performance)
    ankimon_db.save_pokemon(caught_pokemon)


def catch_pokemon(
    enemy_pokemon: PokemonObject,
    ankimon_tracker_obj: AnkimonTracker,
    logger: Union[ShowInfoLogger, None] = None,
    nickname: Union[str, None] = None,
    collected_pokemon_ids: Union[set, None] = None,
    achievements: Union[dict, None] = None,
):
    ankimon_tracker_obj.caught += 1
    if ankimon_tracker_obj.caught > 1:
        if settings_obj.get("gui.pop_up_dialog_message_on_defeat") is True:
            logger.log_and_showinfo(
                "info", translator.translate("already_caught_pokemon")
            )  # Display a message when the Pokémon is caught
            return

    # If we arrive here, this means that ankimon_tracker_obj.caught == 1
    if not nickname:
        nickname = enemy_pokemon.name.capitalize()
    if collected_pokemon_ids is not None:
        collected_pokemon_ids.add(enemy_pokemon.id)  # Update cache
    save_caught_pokemon(enemy_pokemon, nickname, achievements)
    events.emit(
        "catch",
        pokemon=enemy_pokemon.name,
        id=enemy_pokemon.id,
        shiny=enemy_pokemon.shiny,
        tier=enemy_pokemon.tier,
        nickname=nickname,
    )

    ankimon_tracker_obj.general_card_count_for_battle = 0

    msg = translator.translate(
        "caught_wild_pokemon", enemy_pokemon_name=enemy_pokemon.name.capitalize()
    )

    if settings_obj.get("gui.pop_up_dialog_message_on_defeat") is True:
        if logger is not None:
            logger.log_and_showinfo(
                "info", f"{msg}"
            )  # Display a message when the Pokémon is caught

    color = "#a17cf7"  # 6A4DAC" #pokemon leveling info color for tooltip
    try:
        tooltipWithColour(msg, color)
    except Exception as e:
        if logger is not None:
            show_warning_with_traceback(
                exception=e, message="Error while catching Pokemon:"
            )  # Display a message when the Pokémon is caught

    pokemon_pc.refresh_pokemon_grid()


def handle_enemy_faint(
    main_pokemon: PokemonObject,
    enemy_pokemon: PokemonObject,
    collected_pokemon_ids: set,
    test_window: TestWindow,
    evo_window: EvoWindow,
    reviewer_obj: Reviewer_Manager,
    logger: ShowInfoLogger,
    achievements: dict,
):
    """
    Handles what automatically happens when the enemy Pokémon faints, based on auto-battle settings.
    """
    events.emit("faint", who="enemy", pokemon=enemy_pokemon.name, id=enemy_pokemon.id)
    try:
        auto_battle_setting = int(settings_obj.get("battle.automatic_battle"))
        if not (0 <= auto_battle_setting <= 3):
            auto_battle_setting = 0  # fallback
    except ValueError:
        auto_battle_setting = 0  # fallback

    if auto_battle_setting == 3:  # Catch if uncollected
        enemy_id = enemy_pokemon.id
        # Check cache instead of file
        if enemy_id not in collected_pokemon_ids or enemy_pokemon.shiny:
            catch_pokemon(
                enemy_pokemon,
                ankimon_tracker_obj,
                logger,
                "",
                collected_pokemon_ids,
                achievements,
            )
        else:
            kill_pokemon(
                main_pokemon,
                enemy_pokemon,
                evo_window,
                logger,
                achievements,
                trainer_card,
            )
        new_pokemon(
            enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj
        )  # Show a new random Pokémon
    elif auto_battle_setting == 1:  # Existing auto-catch
        catch_pokemon(
            enemy_pokemon,
            ankimon_tracker_obj,
            logger,
            "",
            collected_pokemon_ids,
            achievements,
        )
        new_pokemon(
            enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj
        )  # Show a new random Pokémon
    elif auto_battle_setting == 2:  # Existing auto-defeat
        kill_pokemon(
            main_pokemon, enemy_pokemon, evo_window, logger, achievements, trainer_card
        )
        new_pokemon(
            enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj
        )  # Show a new random Pokémon

    # For Manual mode (auto_battle_setting == 0): no need to show window or do actions automatically
    test_window.display_pokemon_death()
    main_pokemon.reset_bonuses()
    ankimon_tracker_obj.general_card_count_for_battle = 0


def handle_main_pokemon_faint(
    main_pokemon: PokemonObject,
    enemy_pokemon: PokemonObject,
    test_window: TestWindow,
    reviewer_obj: Reviewer_Manager,
    translator: Translator,
):
    """
    Handles what happens when the main Pokémon faints.
    """
    msg = translator.translate(
        "pokemon_fainted", enemy_pokemon_name=main_pokemon.name.capitalize()
    )
    tooltipWithColour(msg, "#E12939")
    events.emit("faint", who="main", pokemon=main_pokemon.name)
    play_effect_sound(settings_obj, "Fainted")

    main_pokemon.hp = main_pokemon.max_hp
    main_pokemon.current_hp = main_pokemon.max_hp
    main_pokemon.reset_bonuses()

    new_pokemon(
        enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj
    )  # Show a new random Pokémon
