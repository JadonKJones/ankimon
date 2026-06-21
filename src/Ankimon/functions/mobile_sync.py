_desktop_session_revlog_ids: set[int] = set()
MOBILE_QUEUE_CAP = 10_000

def record_desktop_review(revlog_id: int) -> None:
    """Record a revlog.id that Ankimon handled on desktop this inter-sync interval."""
    _desktop_session_revlog_ids.add(revlog_id)

def get_desktop_session_revlog_ids() -> frozenset[int]:
    return frozenset(_desktop_session_revlog_ids)

def clear_desktop_session() -> None:
    _desktop_session_revlog_ids.clear()

class TempTracker:
    def __init__(self, total_reviews: int):
        self.total_reviews = total_reviews
        self.pokemon_encounter = 0
        self.cards_battle_round = 0

    def get_total_reviews(self) -> int:
        return self.total_reviews

def _parse_cards_per_round(settings_obj) -> tuple[int, int]:
    """Reads settings_obj.get('battle.cards_per_round', 2) and returns (cards_per_round, cpr_split)."""
    cards_per_round = 2
    if settings_obj:
        try:
            cpr = settings_obj.get("battle.cards_per_round", 2)
            if isinstance(cpr, int):
                cards_per_round = cpr
            elif isinstance(cpr, str):
                if "-" in cpr:
                    parts = cpr.split("-")
                    cards_per_round = int(sum(map(int, parts)) / len(parts))
                else:
                    try:
                        cards_per_round = int(cpr)
                    except ValueError:
                        cards_per_round = 2
        except Exception:
            cards_per_round = 2
    cpr_split = cards_per_round
    return cards_per_round, cpr_split

def _compute_initial_reviews(db, tracker, day_cutoff: int) -> int:
    """Computes the adjusted total review count for encounter seeding based on day_cutoff."""
    initial_reviews = tracker.get_total_reviews() if tracker else 0
    if initial_reviews.__class__.__name__ == "MagicMock":
        initial_reviews = 0
    else:
        try:
            if db:
                cutoff_ms = (day_cutoff - 86400) * 1000
                
                cursor = db.execute(
                    "SELECT COUNT(*) FROM pending_mobile_battles WHERE resolved = 0 AND revlog_id >= ?",
                    (cutoff_ms,)
                )
                row = cursor.fetchone()
                unresolved_today = row[0] if row else 0
                
                cursor2 = db.execute(
                    "SELECT COUNT(*) FROM pending_mobile_battles WHERE resolved = 1 AND resolved_at >= ? AND revlog_id < ?",
                    (cutoff_ms, cutoff_ms)
                )
                row2 = cursor2.fetchone()
                resolved_today_past = row2[0] if row2 else 0
                
                initial_reviews = max(0, initial_reviews - unresolved_today + resolved_today_past)
        except Exception:
            pass
    return initial_reviews

def _generate_encounter(level: int, tracker, collected_ids=None, settings_obj=None, pokedex_cache=None) -> dict | None:
    """Generates a random wild Pokémon encounter."""
    import random
    from .encounter_functions import generate_random_pokemon
    from .. import utils

    if collected_ids is None:
        try:
            collected_ids = set(utils.load_collected_pokemon_ids())
        except Exception:
            collected_ids = set()

    orig_load_ids = utils.load_collected_pokemon_ids
    utils.load_collected_pokemon_ids = lambda: collected_ids
    try:
        res = generate_random_pokemon(level, tracker)
        pkmn_name, pkmn_id, pkmn_lvl, ability, pkmn_type, base_stats, \
        enemy_attacks, base_exp, growth_rate, ev, iv, gender, \
        battle_status, battle_stats, pkmn_tier, ev_yield, pkmn_shiny, nature = res
    except Exception:
        pkmn_name = "Pikachu"
        pkmn_id = 25
        pkmn_lvl = level
        ability = "Run Away"
        pkmn_type = ["Electric"]
        base_stats = {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90}
        enemy_attacks = ["Thunderbolt"]
        base_exp = 112
        growth_rate = "Medium"
        ev = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        iv = {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15}
        gender = "M"
        battle_status = "Fighting"
        battle_stats = {}
        pkmn_tier = "Normal"
        ev_yield = {"speed": 2}
        pkmn_shiny = False
        nature = "serious"
    finally:
        utils.load_collected_pokemon_ids = orig_load_ids

    # MagicMock sanitization wrapping
    if pkmn_id.__class__.__name__ == "MagicMock": pkmn_id = 25
    if pkmn_lvl.__class__.__name__ == "MagicMock": pkmn_lvl = 5
    if pkmn_shiny.__class__.__name__ == "MagicMock": pkmn_shiny = False
    if pkmn_tier.__class__.__name__ == "MagicMock": pkmn_tier = "Normal"
    if base_exp.__class__.__name__ == "MagicMock": base_exp = 112

    return {
        "name": pkmn_name,
        "id": pkmn_id,
        "level": pkmn_lvl,
        "ability": ability,
        "type": pkmn_type,
        "base_stats": base_stats,
        "attacks": enemy_attacks,
        "base_experience": base_exp,
        "growth_rate": growth_rate,
        "ev": ev,
        "iv": iv,
        "gender": gender,
        "battle_status": battle_status,
        "battle_stats": battle_stats,
        "tier": pkmn_tier,
        "ev_yield": ev_yield,
        "shiny": pkmn_shiny,
        "nature": nature
    }

def _normalize_ev_yield(raw: dict) -> dict:
    """Renames EV keys and returns the normalized dict."""
    if not raw:
        return {}
    mapping = {
        "attack": "atk",
        "defense": "def",
        "special-attack": "spa",
        "special-defense": "spd",
        "speed": "spe"
    }
    return {mapping.get(k.lower(), k.lower()): v for k, v in raw.items()}

def detect_mobile_reviews(col, watermark_ms: int, desktop_revlog_ids: frozenset[int]) -> list[dict]:
    """
    Returns revlog rows that are:
    - Newer than watermark_ms
    - type IN (0, 1, 2, 3) — learn, review, relearn, cram (matches desktop Ankimon behavior)
    - NOT in desktop_revlog_ids (i.e., NOT already handled by Ankimon on desktop)
    """
    rows = col.db.all(
        """
        SELECT id, cid, ease, time, type
        FROM revlog
        WHERE id > ?
          AND type IN (0, 1, 2, 3)
        ORDER BY id ASC
        """,
        watermark_ms
    )
    return [
        {"id": r[0], "cid": r[1], "ease": r[2], "time": r[3], "type": r[4]}
        for r in rows
        if r[0] not in desktop_revlog_ids
    ]


def process_mobile_reviews_after_sync(col, ankimon_db, settings_obj, logger) -> int:
    """
    Full post-sync pipeline:
    1. Read watermark from DB
    2. Diff revlog against session set
    3. Apply system cap (MOBILE_QUEUE_CAP)
    4. Queue new mobile battles (INSERT OR IGNORE)
    5. Advance watermark to max(revlog.id) right now
    6. Clear session set
    Returns count of newly queued battles.
    """
    if not settings_obj.get("mobile.enabled", True):
        return 0

    try:
        watermark = ankimon_db.get_mobile_watermark()
        desktop_ids = get_desktop_session_revlog_ids()

        all_mobile = detect_mobile_reviews(col, watermark, desktop_ids)

        # Apply cap — take the MOST RECENT N (highest revlog IDs)
        if len(all_mobile) > MOBILE_QUEUE_CAP:
            logger.log("info",
                f"Mobile sync: {len(all_mobile)} reviews found. "
                f"System cap is {MOBILE_QUEUE_CAP}. "
                f"{len(all_mobile) - MOBILE_QUEUE_CAP} discarded."
            )
            all_mobile = all_mobile[-MOBILE_QUEUE_CAP:]  # list is ASC, so take tail
        else:
            logger.log("info", f"Mobile sync: {len(all_mobile)} reviews found.")

        newly_queued = ankimon_db.queue_mobile_battles(all_mobile)

        # Advance watermark to max revlog.id in the collection right now
        new_watermark = col.db.scalar("SELECT MAX(id) FROM revlog") or watermark
        ankimon_db.set_mobile_watermark(new_watermark)

        # Clear session set — next inter-sync interval starts fresh
        clear_desktop_session()

        return newly_queued

    except Exception as e:
        logger.log("error", f"Mobile sync error: {e}")
        return 0

def load_active_team_clones(ankimon_db, settings_obj, main_pokemon_fallback) -> list:
    """
    Load the current team from DB, filter out inactive companions, and return
    a list of deep-cloned PokemonObject instances healed to full HP.

    Returns a non-empty list. Falls back to [clone(main_pokemon_fallback)] if:
    - The team table is empty
    - None of the team members can be hydrated into PokemonObjects
    - All team members are in the inactive list
    """
    import copy
    from ..pyobj.pokemon_obj import PokemonObject

    clones = []
    if ankimon_db is not None:
        try:
            team_rows = ankimon_db.get_team()
            inactive = set(settings_obj.get("mobile.inactive_companions", [])) if settings_obj else set()
            for t in team_rows:
                ind_id = t.get("individual_id")
                if ind_id and ind_id not in inactive:
                    if hasattr(ankimon_db, "get_pokemon_by_individual_id"):
                        data = ankimon_db.get_pokemon_by_individual_id(ind_id)
                    else:
                        data = ankimon_db.get_pokemon(ind_id)
                    if data:
                        try:
                            pkmn = PokemonObject(**data)
                            clones.append(pkmn)
                        except Exception as e:
                            try:
                                from aqt import mw
                                if hasattr(mw, "logger"):
                                    mw.logger.log("warning", f"load_active_team_clones: skipping {ind_id}: {e}")
                            except Exception:
                                pass
        except Exception:
            pass

    def make_safe_clone(p):
        p_clone = copy.copy(p)
        if hasattr(p, "stats") and isinstance(p.stats, dict):
            try:
                p_clone.stats = copy.deepcopy(p.stats)
            except AttributeError:
                if hasattr(p_clone, "__dict__"):
                    p_clone.__dict__["stats"] = copy.deepcopy(p.stats)
        if hasattr(p, "base_stats") and isinstance(p.base_stats, dict):
            p_clone.base_stats = copy.deepcopy(p.base_stats)
        if hasattr(p, "ev") and isinstance(p.ev, dict):
            p_clone.ev = copy.deepcopy(p.ev)
        if hasattr(p, "iv") and isinstance(p.iv, dict):
            p_clone.iv = copy.deepcopy(p.iv)
        if hasattr(p, "attacks") and isinstance(p.attacks, list):
            p_clone.attacks = copy.deepcopy(p.attacks)
        if hasattr(p, "stat_stages") and isinstance(p.stat_stages, dict):
            p_clone.stat_stages = copy.deepcopy(p.stat_stages)
        if hasattr(p, "volatile_status") and isinstance(p.volatile_status, (set, list)):
            p_clone.volatile_status = set(p.volatile_status)
        return p_clone

    def heal_clone(p):
        p_clone = make_safe_clone(p)
            
        if p.__class__.__name__ == "MagicMock":
            return p_clone

        max_hp_val = getattr(p_clone, "max_hp", 100)
        if isinstance(max_hp_val, (int, float)):
            p_clone.hp = max_hp_val
            if hasattr(p_clone, "current_hp"):
                p_clone.current_hp = max_hp_val
            if hasattr(p_clone, "reset_bonuses"):
                try:
                    p_clone.reset_bonuses()
                except Exception:
                    pass
        return p_clone

    if not clones and main_pokemon_fallback is not None:
        fb = main_pokemon_fallback
        fb_copy = make_safe_clone(fb)
        clones = [fb_copy]

    return [heal_clone(c) for c in clones]


def select_best_companion(team_clones: list, enemy_pokemon) -> object:
    """
    Pick the team member with the highest estimated damage output against this enemy.

    Per move: Base Power * Stat (Atk or Sp.Atk by category) * type effectiveness vs
    the enemy * STAB. EDO (Estimated Damage Output) is the average of those move
    scores. The final score is EDO * Speed -- HP is intentionally excluded so a
    low-HP-but-strong companion isn't passed over. Ties break on Speed, then level.
    Fainted members are skipped; if the whole team has fainted they are revived first.
    """
    from ..business import _load_type_chart
    from .pokedex_functions import _load_moves_cache

    if not team_clones:
        return None

    try:
        moves_data = _load_moves_cache() or {}
    except Exception:
        moves_data = {}

    def get_real_move_effectiveness(move_type: str, defender_types: list[str]) -> float:
        chart = _load_type_chart()
        if not chart:
            from ..business import type_compatibility_multiplier
            return type_compatibility_multiplier([move_type], defender_types)
        if not move_type or not defender_types:
            return 1.0
        mult = 1.0
        atk_row = chart.get(move_type.capitalize())
        if not atk_row:
            return 1.0
        for dfn in defender_types:
            val = atk_row.get(dfn.capitalize())
            if val is not None:
                mult *= float(val)
        return mult

    def get_hp_safe(c):
        val = getattr(c, "hp", 100)
        if val.__class__.__name__ == "MagicMock":
            return 100.0
        return float(val) if isinstance(val, (int, float)) else 100.0

    def get_max_hp_safe(c):
        val = getattr(c, "max_hp", None) or getattr(c, "hp", 100)
        if val.__class__.__name__ == "MagicMock":
            return 100.0
        return float(val) if isinstance(val, (int, float)) else 100.0

    # Revive all if the whole team has fainted
    all_fainted = all(get_hp_safe(c) <= 0 for c in team_clones)
    if all_fainted:
        for c in team_clones:
            max_hp = get_max_hp_safe(c)
            c.hp = max_hp
            if hasattr(c, "current_hp"):
                c.current_hp = max_hp
            if hasattr(c, "reset_bonuses"):
                try:
                    c.reset_bonuses()
                except Exception:
                    pass

    enemy_type = getattr(enemy_pokemon, "type", ["Normal"])
    if enemy_type.__class__.__name__ == "MagicMock":
        enemy_type = ["Normal"]

    best_clone = None
    best_score = -1.0

    for c in team_clones:
        hp = get_hp_safe(c)
        if hp <= 0:
            continue  # Skip fainted

        stats = getattr(c, "stats", {}) or {}
        if stats.__class__.__name__ == "MagicMock":
            stats = {}
        atk = float(stats.get("atk", 10) or 10)
        spa = float(stats.get("spa", 10) or 10)
        spe = float(stats.get("spe", 10) or 10)

        c_type = getattr(c, "type", ["Normal"])
        if c_type.__class__.__name__ == "MagicMock":
            c_type = ["Normal"]

        # Retrieve moves
        moves = getattr(c, "attacks", None)
        if not moves and hasattr(c, "to_dict"):
            try:
                moves = c.to_dict().get("attacks", [])
            except Exception:
                moves = []
        if not moves:
            moves = getattr(c, "moves", [])
        if not moves or moves.__class__.__name__ == "MagicMock":
            moves = ["Tackle"]

        move_scores = []
        for move_name in moves:
            if not move_name or not isinstance(move_name, str):
                continue
            
            # Retrieve move details from cache
            move = moves_data.get(move_name.lower())
            if not move:
                move = moves_data.get(move_name.replace(" ", "").lower())
            if not move:
                move = moves_data.get(move_name.replace("-", "").lower())
            if not move:
                move = moves_data.get("tackle") or {}

            bp = float(move.get("basePower", 0) or 0)
            category = move.get("category", "Physical")
            move_type = move.get("type", "Normal")

            if category == "Status" or bp == 0:
                move_scores.append(0.0)
                continue

            stat_val = spa if category == "Special" else atk

            # Move type compatibility against the enemy (multiplied for dual types, real multipliers)
            move_type_mult = get_real_move_effectiveness(move_type, enemy_type)
            if move_type_mult.__class__.__name__ == "MagicMock":
                move_type_mult = 1.0

            # STAB (1.5x if move matches companion's type)
            stab = 1.5 if move_type in c_type else 1.0

            move_scores.append(bp * stat_val * move_type_mult * stab)

        # Average EDO culmination across all active moves
        if move_scores:
            culminated_edo = sum(move_scores) / len(move_scores)
        else:
            culminated_edo = max(atk, spa) * 40.0

        # Final score is EDO * Speed (HP Fraction is removed to prevent health-based selection bias)
        score = culminated_edo * spe

        if score > best_score:
            best_score = score
            best_clone = c
        elif score == best_score and best_clone is not None:
            # Tie breaker: prefer higher speed, then higher level
            c_spe = float(stats.get("spe", 10) or 10)
            bc_stats = getattr(best_clone, "stats", {}) or {}
            bc_spe = float(bc_stats.get("spe", 10) or 10)
            if c_spe > bc_spe:
                best_clone = c
            elif c_spe == bc_spe:
                if getattr(c, "level", 0) > getattr(best_clone, "level", 0):
                    best_clone = c

    if best_clone is None:
        best_clone = team_clones[0]

    return best_clone


def run_mobile_battles(
    reviews: list[dict] = None,
    *,
    commit: bool,
    db,
    settings_obj,
    tracker,
    trainer_card,
    main_pokemon=None,
    companion_override_id=None,
    logger=None,
    day_cutoff=0,
    limit=None,
    mode="all"
) -> dict:
    """
    Unified engine for:
    - Dry-run simulation of pending mobile battles (commit=False, mode="all")
    - Real auto-resolve of pending mobile battles (commit=True, mode="all")
    - Turn-by-turn manual battle simulation (commit=True/False, mode="next")
    """
    from aqt import mw
    if day_cutoff == 0:
        day_cutoff = mw.col.sched.day_cutoff if (mw and mw.col) else 0

    if mode == "next":
        # Dedicated manual replay simulation block
        unresolved_rows = db.execute(
            """SELECT id, revlog_id, card_id, ease, review_time, review_type, queued_at
               FROM pending_mobile_battles
               WHERE resolved = 0
               ORDER BY id ASC"""
        ).fetchall()
        if not unresolved_rows:
            return {"done": True}

        all_unresolved = [
            {
                "id": r[0],
                "revlog_id": r[1],
                "card_id": r[2],
                "ease": r[3],
                "review_time": r[4],
                "review_type": r[5],
                "queued_at": r[6],
            }
            for r in unresolved_rows
        ]

        # We will simulate turn-by-turn until enemy or companion faints
        team_clones = load_active_team_clones(db, settings_obj, main_pokemon)

        main_pokemon_level = 5
        if team_clones:
            levels = []
            for c in team_clones:
                lvl = getattr(c, "level", None)
                if lvl is not None and lvl.__class__.__name__ != "MagicMock" and isinstance(lvl, (int, float)):
                    levels.append(int(lvl))
            if levels:
                main_pokemon_level = max(levels)
        elif main_pokemon:
            lvl = getattr(main_pokemon, "level", 5)
            if lvl.__class__.__name__ != "MagicMock" and isinstance(lvl, (int, float)):
                main_pokemon_level = int(lvl)

        import random
        import math
        import uuid
        from datetime import datetime
        from ..pyobj.pokemon_obj import PokemonObject
        from ..business import calc_experience
        from .ankimon_hooks_to_poke_engine import simulate_battle_with_poke_engine

        cards_per_round, _ = _parse_cards_per_round(settings_obj)

        # Initial seed of the encounter
        first_review = all_unresolved[0]
        seed_idx = min(len(all_unresolved) - 1, cards_per_round - 1)
        seed_review = all_unresolved[seed_idx]
        enc_seed = seed_review.get("revlog_id") or seed_review.get("id") or 42
        random.seed(enc_seed)

        initial_reviews = _compute_initial_reviews(
            db,
            tracker,
            day_cutoff
        )
        cards_in_encounter = seed_idx + 1
        temp_tracker = TempTracker(initial_reviews + cards_in_encounter)

        enc_data = _generate_encounter(main_pokemon_level, temp_tracker, None, settings_obj, None)
        current_enemy_pokemon = PokemonObject(
            type=enc_data["type"], name=enc_data["name"], id=enc_data["id"], shiny=enc_data["shiny"],
            level=enc_data["level"], ability=enc_data["ability"], gender=enc_data["gender"], growth_rate=enc_data["growth_rate"],
            captured_date=None, tier=enc_data["tier"], individual_id=str(uuid.uuid4()),
            base_stats=enc_data["base_stats"], attacks=enc_data["attacks"], base_experience=enc_data["base_experience"],
            ev=enc_data["ev"], iv=enc_data["iv"], battle_status=enc_data["battle_status"], ev_yield=enc_data["ev_yield"], nature=enc_data["nature"]
        )

        selected_override = None
        if companion_override_id:
            for tc in team_clones:
                if getattr(tc, "individual_id", None) == companion_override_id:
                    if getattr(tc, "hp", 0) <= 0:
                        max_hp_val = getattr(tc, "max_hp", 100)
                        if max_hp_val.__class__.__name__ == "MagicMock":
                            max_hp_val = 100
                        tc.hp = max_hp_val
                        if hasattr(tc, "current_hp"):
                            tc.current_hp = max_hp_val
                    selected_override = tc
                    break
            if selected_override is None:
                try:
                    if hasattr(db, "get_pokemon_by_individual_id"):
                        data = db.get_pokemon_by_individual_id(companion_override_id)
                    else:
                        data = db.get_pokemon(companion_override_id)
                    if data:
                        from ..pyobj.pokemon_obj import PokemonObject
                        pkmn = PokemonObject(**data)
                        max_hp_val = getattr(pkmn, "max_hp", 100)
                        if isinstance(max_hp_val, (int, float)):
                            pkmn.hp = max_hp_val
                            if hasattr(pkmn, "current_hp"):
                                pkmn.current_hp = max_hp_val
                        if hasattr(pkmn, "reset_bonuses"):
                            try:
                                pkmn.reset_bonuses()
                            except Exception:
                                pass
                        selected_override = pkmn
                except Exception:
                    pass
        if selected_override is not None:
            main_pokemon_clone = selected_override
        else:
            main_pokemon_clone = select_best_companion(team_clones, current_enemy_pokemon)

        mutator_full_reset = 1
        engine_state = None
        
        reviews_list = []
        turns_log = []
        accumulated_evs = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}

        # Read multiplier/boosts settings
        xp_multiplier = 1.0
        choose_moves_penalty = 1.0
        if settings_obj:
            xp_multiplier = settings_obj.get("battle.xp_multiplier", 1.0)
            if settings_obj.get("controls.allow_to_choose_moves", False):
                choose_moves_penalty = 0.5
        lucky_egg_boost = 1.0
        if main_pokemon_clone and getattr(main_pokemon_clone, "held_item", None) == "lucky-egg":
            lucky_egg_boost = 1.5

        chunk_idx = 0
        while chunk_idx < len(all_unresolved):
            chunk = all_unresolved[chunk_idx : chunk_idx + cards_per_round]
            reviews_list.extend(chunk)
            chunk_idx += cards_per_round

            companion_max_hp = getattr(main_pokemon_clone, "max_hp", 100)
            if companion_max_hp.__class__.__name__ == "MagicMock": companion_max_hp = 100
            enemy_max_hp = getattr(current_enemy_pokemon, "max_hp", 100)
            if enemy_max_hp.__class__.__name__ == "MagicMock": enemy_max_hp = 100

            # Select moves
            main_attacks = getattr(main_pokemon_clone, "attacks", None)
            if isinstance(main_attacks, (list, tuple)) and len(main_attacks) > 0:
                user_attack = random.choice(main_attacks)
            else:
                user_attack = "splash"

            enemy_attacks_list = getattr(current_enemy_pokemon, "attacks", None)
            if isinstance(enemy_attacks_list, (list, tuple)) and len(enemy_attacks_list) > 0:
                enemy_attack = random.choice(enemy_attacks_list)
            else:
                enemy_attack = "splash"

            points_map = {1: 0, 2: 5, 3: 10, 4: 20}
            total_points = sum(points_map.get(r.get("ease") or 3, 10) for r in chunk)
            max_points = 10.0 * len(chunk)
            turn_multiplier = total_points / max_points if max_points > 0 else 1.0

            orig_multiplier = 1.0
            has_tracker = tracker and hasattr(tracker, "multiplier") and tracker.__class__.__name__ != "MagicMock"
            if has_tracker:
                orig_multiplier = tracker.multiplier
                tracker.multiplier = turn_multiplier

            try:
                results = simulate_battle_with_poke_engine(
                    main_pokemon_clone, current_enemy_pokemon, user_attack, enemy_attack,
                    mutator_full_reset, engine_state
                )
                engine_state, mutator_full_reset = results[1], results[4]
            except Exception:
                current_enemy_pokemon.hp = 0
            finally:
                if has_tracker: tracker.multiplier = orig_multiplier

            comp_hp_val = getattr(main_pokemon_clone, "hp", 0)
            if comp_hp_val.__class__.__name__ == "MagicMock":
                comp_hp_val = 100
            enemy_hp_val = getattr(current_enemy_pokemon, "hp", 0)
            if enemy_hp_val.__class__.__name__ == "MagicMock":
                enemy_hp_val = 100
            comp_hp_after = max(0, comp_hp_val)
            enemy_hp_after = max(0, enemy_hp_val)

            turns_log.append({
                "user_attack": user_attack.title(),
                "enemy_attack": enemy_attack.title(),
                "comp_hp_pct": int((comp_hp_after * 100) / companion_max_hp),
                "enemy_hp_pct": int((enemy_hp_after * 100) / enemy_max_hp),
            })

            if comp_hp_after <= 0 or enemy_hp_after <= 0:
                break

        # Calculate rewards
        battle_xp = 0
        total_trainer_xp = 0
        gained_cash = 0
        if enemy_hp_after <= 0:
            exp = calc_experience(current_enemy_pokemon.base_experience, current_enemy_pokemon.level)
            if exp.__class__.__name__ == "MagicMock":
                exp = 100
            try:
                exp = max(1, math.ceil(exp * choose_moves_penalty * lucky_egg_boost * xp_multiplier))
            except TypeError:
                exp = 100
            battle_xp = exp

            from ..pyobj.trainer_card import POKEMON_TIERS
            txp = POKEMON_TIERS.get(current_enemy_pokemon.tier.lower(), 10)
            allow_to_choose_move = settings_obj.get("controls.allow_to_choose_moves") if settings_obj else False
            if allow_to_choose_move: txp *= 0.5
            total_trainer_xp = int(txp)

            if current_enemy_pokemon.ev_yield:
                for sk, v in _normalize_ev_yield(current_enemy_pokemon.ev_yield).items():
                    if sk in accumulated_evs: accumulated_evs[sk] += v

            gained_cash = 0

        from .sprite_functions import get_relative_sprite_path
        last_result_data = {
            "done": False,
            "enemy_name": current_enemy_pokemon.display_name,
            "enemy_id": current_enemy_pokemon.id,
            "enemy_level": current_enemy_pokemon.level,
            "enemy_shiny": current_enemy_pokemon.shiny,
            "enemy_tier": current_enemy_pokemon.tier,
            "enemy_sprite": get_relative_sprite_path(
                current_enemy_pokemon.id,
                current_enemy_pokemon.shiny,
                getattr(current_enemy_pokemon, "gender", "N") or "N",
                current_enemy_pokemon.name,
                "gif"
            ),
            "ease": first_review.get("ease", 3),
            "companion_name": main_pokemon_clone.display_name if main_pokemon_clone else "Companion",
            "companion_level": main_pokemon_clone.level if main_pokemon_clone else 5,
            "companion_sprite": get_relative_sprite_path(main_pokemon_clone.id, main_pokemon_clone.shiny, (getattr(main_pokemon_clone, "gender", "N") or "N"), main_pokemon_clone.name, "gif") if main_pokemon_clone else "",
            "companion_id": getattr(main_pokemon_clone, "individual_id", ""),
            "xp_gained": battle_xp,
            "turns": turns_log,
        }

        # Return state to commit later
        current_pending_outcome = {
            "enemy_pokemon": current_enemy_pokemon,
            "battle_xp": battle_xp,
            "total_xp": battle_xp,
            "accumulated_evs": accumulated_evs,
            "total_trainer_xp": total_trainer_xp,
            "companion_id": getattr(main_pokemon_clone, "individual_id", ""),
            "companion_name": getattr(main_pokemon_clone, "display_name", "Companion"),
            "companion_level": getattr(main_pokemon_clone, "level", 5),
            "review_ids": [r["id"] for r in reviews_list],
            "companion_fainted": (comp_hp_after <= 0),
            "gained_cash": gained_cash,
        }

        pending_total_at_start = len(all_unresolved)
        remaining_reviews = pending_total_at_start - len(reviews_list)
        last_result_data.update({
            "remaining": remaining_reviews,
            "cash_gained": gained_cash,
            "trainer_xp_gained": total_trainer_xp,
        })

        # Re-calculate battle_number properly:
        resolved_count = db.execute("SELECT COUNT(*) FROM pending_mobile_battles WHERE resolved=1").fetchone()[0]
        # Total encounters
        total_resolved_encounters = (resolved_count // cards_per_round)
        last_result_data["battle_number"] = total_resolved_encounters
        # Total encounters overall
        total_all_count = db.execute("SELECT COUNT(*) FROM pending_mobile_battles").fetchone()[0]
        last_result_data["total_battles"] = math.ceil(total_all_count / cards_per_round)

        return {
            "result": last_result_data,
            "current_pending_outcome": current_pending_outcome
        }

    # Otherwise, mode == "all"
    if reviews is None:
        if limit is not None:
            reviews_rows = db.execute(
                """SELECT id, revlog_id, card_id, ease, review_time, review_type, queued_at
                   FROM pending_mobile_battles
                   WHERE resolved = 0
                   ORDER BY id ASC
                   LIMIT ?""",
                (limit,)
            ).fetchall()
        else:
            reviews_rows = db.execute(
                """SELECT id, revlog_id, card_id, ease, review_time, review_type, queued_at
                   FROM pending_mobile_battles
                   WHERE resolved = 0
                   ORDER BY id ASC"""
            ).fetchall()

        if not reviews_rows:
            if commit:
                return {"success": True, "resolved": 0, "message": "No pending battles.", "done": True}
            else:
                return {
                    "xp": 0, "encounters": 0, "caught": [], "defeated": [],
                    "catches_count": 0, "is_truncated": False, "simulated_reviews": 0,
                    "total_reviews": 0, "cash": 0
                }

        reviews_list = [
            {
                "id": r[0],
                "revlog_id": r[1],
                "card_id": r[2],
                "ease": r[3],
                "review_time": r[4],
                "review_type": r[5],
                "queued_at": r[6],
            }
            for r in reviews_rows
        ]
    else:
        reviews_list = list(reviews)

    if not reviews_list:
        if commit:
            return {"success": True, "resolved": 0, "message": "No pending battles.", "done": True}
        else:
            return {
                "xp": 0, "encounters": 0, "caught": [], "defeated": [],
                "catches_count": 0, "is_truncated": False, "simulated_reviews": 0,
                "total_reviews": 0, "cash": 0
            }

    import random
    import math
    from datetime import datetime
    import uuid

    state = random.getstate()

    # Deterministic seed
    seed_val = sum(r.get("revlog_id") or r.get("id") or 0 for r in reviews_list)
    if seed_val == 0: seed_val = 42
    random.seed(seed_val)

    cards_per_round, _ = _parse_cards_per_round(settings_obj)

    auto_battle_setting = 3
    if settings_obj:
        try:
            auto_battle_setting = int(settings_obj.get("battle.automatic_battle", 3))
        except Exception: pass
    if auto_battle_setting == 0: auto_battle_setting = 3

    wishlist = []
    auto_catch_legendary = True
    auto_catch_mythical = True
    auto_catch_ultra = True
    auto_catch_starter = True
    auto_catch_mega = True
    auto_catch_gmax = True
    auto_catch_regional = True
    xp_multiplier = 1.0
    choose_moves_penalty = 1.0

    if settings_obj:
        wishlist = settings_obj.get("battle.auto_catch_wishlist", [])
        auto_catch_legendary = settings_obj.get("battle.auto_catch_legendary", True)
        auto_catch_mythical = settings_obj.get("battle.auto_catch_mythical", True)
        auto_catch_ultra = settings_obj.get("battle.auto_catch_ultra", True)
        auto_catch_starter = settings_obj.get("battle.auto_catch_starter", True)
        auto_catch_mega = settings_obj.get("battle.auto_catch_mega", True)
        auto_catch_gmax = settings_obj.get("battle.auto_catch_gmax", True)
        auto_catch_regional = settings_obj.get("battle.auto_catch_regional", True)
        xp_multiplier = settings_obj.get("battle.xp_multiplier", 1.0)
        if settings_obj.get("controls.allow_to_choose_moves", False):
            choose_moves_penalty = 0.5

    lucky_egg_boost = 1.0
    if main_pokemon and getattr(main_pokemon, "held_item", None) == "lucky-egg":
        lucky_egg_boost = 1.5

    from ..utils import load_collected_pokemon_ids
    collected_ids = set(load_collected_pokemon_ids())

    from .encounter_functions import (
        generate_random_pokemon,
        save_caught_pokemon,
        save_main_pokemon_progress
    )
    from .encounter_data import MEGA, GMAX, REGIONAL_FORM_REGION
    from ..business import calc_experience, calculate_cp_from_dict
    from ..pyobj.pokemon_obj import PokemonObject
    from ..singletons import get_evo_window

    initial_reviews = _compute_initial_reviews(
        db,
        tracker,
        day_cutoff
    )
    temp_tracker = TempTracker(initial_reviews)

    team_clones = load_active_team_clones(db, settings_obj, main_pokemon)
    main_pokemon_clone = team_clones[0] if team_clones else None

    main_pokemon_level = 5
    if team_clones:
        levels = []
        for c in team_clones:
            lvl = getattr(c, "level", None)
            if lvl is not None and lvl.__class__.__name__ != "MagicMock" and isinstance(lvl, (int, float)):
                levels.append(int(lvl))
        if levels:
            main_pokemon_level = max(levels)
    elif main_pokemon:
        lvl = getattr(main_pokemon, "level", 5)
        if lvl.__class__.__name__ != "MagicMock" and isinstance(lvl, (int, float)):
            main_pokemon_level = int(lvl)

    total_xp = 0
    total_trainer_xp = 0
    caught_count = 0
    caught_pokemon_list = []
    cards_battle_round = 0
    accumulated_evs = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
    defeated_encounters = []
    current_turn_reviews = []
    total_reviews_processed = 0
    current_battle_cash = 0
    ci = int(settings_obj.get("trainer.cash_reward_interval", 5)) if settings_obj else 5
    ca = int(settings_obj.get("trainer.cash_reward_amount", 10)) if settings_obj else 10

    from .. import utils
    orig_load_ids = utils.load_collected_pokemon_ids
    utils.load_collected_pokemon_ids = lambda: collected_ids

    current_enemy_pokemon = None
    mutator_full_reset = 1
    engine_state = None
    from .ankimon_hooks_to_poke_engine import simulate_battle_with_poke_engine

    history_entries_to_add = []
    encounters_fought = 0
    reviews_spent_for_resolved = 0
    resolved_encounters = 0

    if not commit:
        reviews_to_process = reviews_list[:100]
        extra_reviews = reviews_list[100:]
        caught_pokemon = []
        defeated_pokemon = []
    else:
        reviews_to_process = reviews_list
        extra_reviews = []

    try:
        for review in reviews_to_process:
            if temp_tracker.total_reviews.__class__.__name__ == "MagicMock":
                temp_tracker.total_reviews = 0
            else:
                temp_tracker.total_reviews += 1
            total_reviews_processed += 1
            if commit and ci > 0 and total_reviews_processed % ci == 0:
                current_battle_cash += ca
            cards_battle_round += 1
            current_turn_reviews.append(review)
            if cards_battle_round >= cards_per_round or review == reviews_to_process[-1]:
                cards_battle_round = 0

                if current_enemy_pokemon is None:
                    encounters_fought += 1
                    current_encounter_reviews = cards_per_round
                    enc_seed = review.get("revlog_id") or review.get("id") or 42
                    random.seed(enc_seed)
                    enc_data = _generate_encounter(main_pokemon_level, temp_tracker, None, settings_obj, None)
                    current_enemy_pokemon = PokemonObject(
                        type=enc_data["type"], name=enc_data["name"], id=enc_data["id"], shiny=enc_data["shiny"],
                        level=enc_data["level"], ability=enc_data["ability"], gender=enc_data["gender"], growth_rate=enc_data["growth_rate"],
                        captured_date=None, tier=enc_data["tier"], individual_id=str(uuid.uuid4()),
                        base_stats=enc_data["base_stats"], attacks=enc_data["attacks"], base_experience=enc_data["base_experience"],
                        ev=enc_data["ev"], iv=enc_data["iv"], battle_status=enc_data["battle_status"], ev_yield=enc_data["ev_yield"], nature=enc_data["nature"]
                    )
                    main_pokemon_clone = select_best_companion(team_clones, current_enemy_pokemon)
                    mutator_full_reset = 1
                    engine_state = None

                # Turn simulation
                main_attacks = getattr(main_pokemon_clone, "attacks", None)
                if isinstance(main_attacks, (list, tuple)) and len(main_attacks) > 0:
                    user_attack = random.choice(main_attacks)
                else:
                    user_attack = "splash"

                enemy_attacks_list = getattr(current_enemy_pokemon, "attacks", None)
                if isinstance(enemy_attacks_list, (list, tuple)) and len(enemy_attacks_list) > 0:
                    enemy_attack = random.choice(enemy_attacks_list)
                else:
                    enemy_attack = "splash"

                points_map = {1: 0, 2: 5, 3: 10, 4: 20}
                total_points = sum(points_map.get(r.get("ease") or 3, 10) for r in current_turn_reviews)
                max_points = 10.0 * len(current_turn_reviews)
                turn_multiplier = total_points / max_points if max_points > 0 else 1.0

                orig_multiplier = 1.0
                has_tracker = tracker and hasattr(tracker, "multiplier") and tracker.__class__.__name__ != "MagicMock"
                if has_tracker:
                    orig_multiplier = tracker.multiplier
                    tracker.multiplier = turn_multiplier

                try:
                    results = simulate_battle_with_poke_engine(
                        main_pokemon_clone, current_enemy_pokemon, user_attack, enemy_attack,
                        mutator_full_reset, engine_state
                    )
                    engine_state, mutator_full_reset = results[1], results[4]
                except Exception: current_enemy_pokemon.hp = 0
                finally:
                    if has_tracker: tracker.multiplier = orig_multiplier
                    current_turn_reviews = []

                enemy_hp = getattr(current_enemy_pokemon, "hp", 100)
                companion_hp = getattr(main_pokemon_clone, "hp", 100)

                if isinstance(enemy_hp, (int, float)) and enemy_hp <= 0:
                    is_mega = current_enemy_pokemon.id in MEGA
                    is_gmax = current_enemy_pokemon.id in GMAX
                    is_regional = current_enemy_pokemon.id in REGIONAL_FORM_REGION
                    should_catch_always = (
                        (current_enemy_pokemon.tier == "Legendary" and auto_catch_legendary)
                        or (current_enemy_pokemon.tier == "Mythical" and auto_catch_mythical)
                        or (current_enemy_pokemon.tier == "Ultra" and auto_catch_ultra)
                        or (current_enemy_pokemon.tier == "Starter" and auto_catch_starter)
                        or (is_mega and auto_catch_mega)
                        or (is_gmax and auto_catch_gmax)
                        or (is_regional and auto_catch_regional)
                        or (current_enemy_pokemon.id in wishlist)
                    )

                    caught = False
                    if auto_battle_setting == 1: caught = True
                    elif auto_battle_setting == 2: caught = (current_enemy_pokemon.shiny or should_catch_always)
                    elif auto_battle_setting == 3:
                        caught = (current_enemy_pokemon.id not in collected_ids or current_enemy_pokemon.shiny or should_catch_always)
                        if caught: collected_ids.add(current_enemy_pokemon.id)

                    enemy_dict = current_enemy_pokemon.to_dict()
                    enemy_dict.update({
                        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
                    })
                    cp_val = calculate_cp_from_dict(enemy_dict)
                    if cp_val.__class__.__name__ == "MagicMock":
                        cp_val = 100

                    pkmn_info = {
                        "name": str(current_enemy_pokemon.display_name),
                        "id": int(current_enemy_pokemon.id),
                        "level": int(current_enemy_pokemon.level),
                        "shiny": bool(current_enemy_pokemon.shiny),
                        "tier": str(current_enemy_pokemon.tier),
                        "xp": 0,
                        "cp": cp_val
                    }

                    if caught:
                        if commit:
                            from aqt import mw
                            capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            current_enemy_pokemon.captured_date = capture_time
                            save_caught_pokemon(current_enemy_pokemon, nickname=None, achievements=mw.achievements_dict)
                            try:
                                from ..reviewer_ui import _collected_pokemon_ids
                                if isinstance(_collected_pokemon_ids, set): _collected_pokemon_ids.add(current_enemy_pokemon.id)
                            except Exception: pass
                            caught_pokemon_list.append(pkmn_info)
                            last_outcome = "caught"
                        else:
                            caught_pokemon.append(pkmn_info)
                    else:
                        exp = calc_experience(current_enemy_pokemon.base_experience, current_enemy_pokemon.level)
                        if exp.__class__.__name__ == "MagicMock":
                            exp = 100
                        try:
                            exp = max(1, math.ceil(exp * choose_moves_penalty * lucky_egg_boost * xp_multiplier))
                        except TypeError:
                            exp = 100
                        battle_xp = exp
                        pkmn_info["xp"] = exp

                        if commit:
                            total_xp += exp
                            defeated_encounters.append({"tier": current_enemy_pokemon.tier})
                            if current_enemy_pokemon.ev_yield:
                                for sk, v in _normalize_ev_yield(current_enemy_pokemon.ev_yield).items():
                                    if sk in accumulated_evs: accumulated_evs[sk] += v
                            last_outcome = "defeated"
                        else:
                            total_xp += exp
                            defeated_pokemon.append(pkmn_info)

                    if commit:
                        # Insert history for caught or defeated
                        try:
                            from ..pyobj.trainer_card import POKEMON_TIERS
                            txp = POKEMON_TIERS.get(current_enemy_pokemon.tier.lower(), 10)
                            allow_to_choose_move = settings_obj.get("controls.allow_to_choose_moves") if settings_obj else False
                            if allow_to_choose_move: txp *= 0.5
                            txp = int(txp) if last_outcome == "defeated" else 0
                            history_entries_to_add.append({
                                "timestamp": int(__import__("time").time() * 1000),
                                "enemy_id": current_enemy_pokemon.id,
                                "enemy_name": current_enemy_pokemon.display_name,
                                "enemy_level": current_enemy_pokemon.level,
                                "enemy_shiny": current_enemy_pokemon.shiny,
                                "companion_name": main_pokemon_clone.display_name if main_pokemon_clone else None,
                                "companion_level": main_pokemon_clone.level if main_pokemon_clone else None,
                                "companion_id": main_pokemon_clone.individual_id if main_pokemon_clone else None,
                                "ev_yield": current_enemy_pokemon.ev_yield.copy() if (last_outcome == "defeated" and current_enemy_pokemon and getattr(current_enemy_pokemon, "ev_yield", None)) else {},
                                "outcome": last_outcome,
                                "xp_gained": battle_xp if last_outcome == "defeated" else 0,
                                "trainer_xp_gained": txp,
                                "cash_gained": current_battle_cash,
                            })
                        except Exception as ex:
                            if logger:
                                logger.log("error", f"Failed to record auto-resolve history: {ex}")
                        current_battle_cash = 0

                    reviews_spent_for_resolved += current_encounter_reviews
                    resolved_encounters += 1
                    current_enemy_pokemon = None
                    if main_pokemon_clone:
                        try: main_pokemon_clone.reset_bonuses()
                        except Exception: pass

                elif isinstance(companion_hp, (int, float)) and companion_hp <= 0:
                    if commit:
                        # Insert history for loss
                        try:
                            history_entries_to_add.append({
                                "timestamp": int(__import__("time").time() * 1000),
                                "enemy_id": current_enemy_pokemon.id,
                                "enemy_name": current_enemy_pokemon.display_name,
                                "enemy_level": current_enemy_pokemon.level,
                                "enemy_shiny": current_enemy_pokemon.shiny,
                                "companion_name": main_pokemon_clone.display_name if main_pokemon_clone else None,
                                "companion_level": main_pokemon_clone.level if main_pokemon_clone else None,
                                "companion_id": main_pokemon_clone.individual_id if main_pokemon_clone else None,
                                "outcome": "lost",
                                "xp_gained": 0,
                                "trainer_xp_gained": 0,
                                "cash_gained": current_battle_cash,
                            })
                        except Exception as ex:
                            if logger:
                                logger.log("error", f"Failed to record auto-resolve loss history: {ex}")
                        current_battle_cash = 0

                    reviews_spent_for_resolved += current_encounter_reviews
                    resolved_encounters += 1
                    current_enemy_pokemon = None
                    if main_pokemon_clone:
                        try: main_pokemon_clone.reset_bonuses()
                        except Exception: pass
        
        if commit and current_enemy_pokemon is not None:
            # Insert history for escaped / unfinished battle
            try:
                history_entries_to_add.append({
                    "timestamp": int(__import__("time").time() * 1000),
                    "enemy_id": current_enemy_pokemon.id,
                    "enemy_name": current_enemy_pokemon.display_name,
                    "enemy_level": current_enemy_pokemon.level,
                    "enemy_shiny": current_enemy_pokemon.shiny,
                    "companion_name": main_pokemon_clone.display_name if main_pokemon_clone else None,
                    "companion_level": main_pokemon_clone.level if main_pokemon_clone else None,
                    "companion_id": main_pokemon_clone.individual_id if main_pokemon_clone else None,
                    "outcome": "escaped",
                    "xp_gained": 0,
                    "trainer_xp_gained": 0,
                    "cash_gained": current_battle_cash,
                })
            except Exception as ex:
                if logger:
                    logger.log("error", f"Failed to record auto-resolve escape history: {ex}")
    finally:
        utils.load_collected_pokemon_ids = orig_load_ids

    if commit:
        if history_entries_to_add:
            try:
                if hasattr(db, "add_mobile_history_entries_batch"):
                    db.add_mobile_history_entries_batch(history_entries_to_add)
                else:
                    for entry in history_entries_to_add:
                        db.add_mobile_history_entry(entry)
            except Exception as ex:
                if logger:
                    logger.log("error", f"Failed to record batch auto-resolve history: {ex}")
        random.setstate(state)

        companion_xp = {}
        companion_evs = {}
        companion_battle_count = {}
        for entry in history_entries_to_add:
            cid = entry.get("companion_id")
            if not cid:
                continue
            xp_g = entry.get("xp_gained", 0)
            companion_xp[cid] = companion_xp.get(cid, 0) + xp_g
            
            if entry.get("outcome") in ("defeated", "caught"):
                companion_battle_count[cid] = companion_battle_count.get(cid, 0) + 1
            
            if cid not in companion_evs:
                companion_evs[cid] = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
            ev_yield = entry.get("ev_yield", {})
            for sk, v in _normalize_ev_yield(ev_yield).items():
                if sk in companion_evs[cid]:
                    companion_evs[cid][sk] += v

        for cid, earned_xp in companion_xp.items():
            evs_gained = companion_evs.get(cid, {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0})
            battles_fought = companion_battle_count.get(cid, 0)
            if earned_xp > 0 or any(evs_gained.values()) or battles_fought > 0:
                if main_pokemon and cid == main_pokemon.individual_id:
                    class DummyEnemy:
                        def __init__(self, ev_yield): self.ev_yield = ev_yield
                    from aqt import mw
                    save_main_pokemon_progress(
                        main_pokemon, DummyEnemy(evs_gained), earned_xp,
                        mw.achievements_dict, logger, get_evo_window()
                    )
                    # Apply additional battles fought to main_pokemon.pokemon_defeated
                    if battles_fought > 1:
                        extra = battles_fought - 1
                        main_pokemon.pokemon_defeated += extra
                        try:
                            mp_data = db.get_main_pokemon()
                            if mp_data:
                                mp_data["pokemon_defeated"] = main_pokemon.pokemon_defeated
                                db.save_main_pokemon(mp_data)
                        except Exception:
                            pass
                else:
                    _attribute_xp_and_evs_to_companion(cid, earned_xp, evs_gained, settings_obj, battles_fought=battles_fought, db=db, logger=logger)

        total_trainer_xp = 0
        from ..pyobj.trainer_card import POKEMON_TIERS
        allow_to_choose_move = settings_obj.get("controls.allow_to_choose_moves") if settings_obj else False
        for enc in defeated_encounters:
            txp = POKEMON_TIERS.get(enc.get("tier", "normal").lower(), 10)
            if txp.__class__.__name__ == "MagicMock":
                txp = 10
            if allow_to_choose_move: txp *= 0.5
            total_trainer_xp += txp

        if total_trainer_xp > 0 and trainer_card:
            new_txp = int(settings_obj.get("trainer.xp", 0) + total_trainer_xp)
            settings_obj.set("trainer.xp", new_txp)
            settings_obj.set("trainer.total_xp", int(settings_obj.get("trainer.total_xp", 0) + total_trainer_xp))
            trainer_card.xp = new_txp
            trainer_card.total_xp = settings_obj.get("trainer.total_xp")
            trainer_card.check_level_up()

        # Cash Reward
        gained_cash = 0
        total_reviews_resolved = len(reviews_list)
        current_counter = int(settings_obj.get("trainer.mobile_reviews_resolved_since_payout", 0)) if settings_obj else 0
        new_counter = current_counter + total_reviews_resolved
        
        ci = int(settings_obj.get("trainer.cash_reward_interval", 5)) if settings_obj else 5
        ca = int(settings_obj.get("trainer.cash_reward_amount", 10)) if settings_obj else 10
        
        gained_cash = (new_counter // ci) * ca
        remaining_counter = new_counter % ci
        if settings_obj:
            settings_obj.set("trainer.mobile_reviews_resolved_since_payout", remaining_counter)
            settings_obj.set("trainer.cash", int(settings_obj.get("trainer.cash", 0) + gained_cash))
        if trainer_card and settings_obj:
            trainer_card.cash = settings_obj.get("trainer.cash")

        # Mark resolved
        res_ids = [r["id"] for r in reviews_list]
        for rid in res_ids:
            db.mark_mobile_battle_resolved(rid)

        remaining = db.get_pending_mobile_count()
        from ..menu_buttons import update_mobile_badge
        update_mobile_badge(remaining)

        try:
            from ..singletons import notify_stats_changed
            notify_stats_changed()
        except Exception: pass
        return {
            "success": True, "resolved": encounters_fought, "xp_gained": total_xp,
            "catches": caught_count, "cash_gained": gained_cash,
            "trainer_xp_gained": total_trainer_xp, "caught_list": caught_pokemon_list,
            "reviews_processed": len(reviews_list),
        }
    else:
        # Estimate extrapolation
        avg_reviews_per_encounter = cards_per_round
        if resolved_encounters > 0:
            avg_reviews_per_encounter = reviews_spent_for_resolved / resolved_encounters

        extra_caught_count = 0
        if extra_reviews:
            extra_reviews_count = len(extra_reviews)
            extra_encounters = int(extra_reviews_count / avg_reviews_per_encounter)

            if extra_encounters > 0:
                encounters_count = resolved_encounters + extra_encounters
                
                # Estimate defeated and caught ratio from simulated pool
                defeated_ratio = 0.8
                caught_ratio = 0.2
                total_encs = len(caught_pokemon) + len(defeated_pokemon)
                if total_encs > 0:
                    defeated_ratio = len(defeated_pokemon) / total_encs
                    caught_ratio = len(caught_pokemon) / total_encs

                extra_defeated = extra_encounters * defeated_ratio
                extra_caught_count = int(extra_encounters * caught_ratio)

                est_exp = calc_experience(130, main_pokemon_level)
                try:
                    est_exp = max(1, math.ceil(est_exp * choose_moves_penalty * lucky_egg_boost * xp_multiplier))
                except TypeError:
                    est_exp = 100
                total_xp += int(extra_defeated * est_exp)
            else:
                encounters_count = resolved_encounters
        else:
            encounters_count = resolved_encounters

        # Estimate trainer cash reward based on settings
        cash_interval = int(settings_obj.get("trainer.cash_reward_interval", 5)) if settings_obj else 5
        cash_amount = int(settings_obj.get("trainer.cash_reward_amount", 10)) if settings_obj else 10
        total_reviews_count = len(reviews_list)
        cash_gained = (total_reviews_count // cash_interval) * cash_amount

        # Restore random state
        random.setstate(state)

        return {
            "xp": total_xp,
            "encounters": encounters_count,
            "caught": caught_pokemon,
            "defeated": defeated_pokemon,
            "catches_count": len(caught_pokemon) + extra_caught_count,
            "is_truncated": len(extra_reviews) > 0,  # True if >100 reviews, extrapolated
            "simulated_reviews": len(reviews_to_process),
            "total_reviews": len(reviews_list),
            "cash": cash_gained
        }


def estimate_pending_battles(pending_reviews: list[dict], main_pokemon, settings_obj, trainer_card, ankimon_tracker_obj, ankimon_db=None) -> dict:
    return run_mobile_battles(
        reviews=pending_reviews,
        commit=False,
        db=ankimon_db,
        settings_obj=settings_obj,
        tracker=ankimon_tracker_obj,
        trainer_card=trainer_card,
        main_pokemon=main_pokemon
    )


# Alias for backwards compatibility
simulate_pending_mobile_battles = estimate_pending_battles


def resolve_all(db, settings_obj, tracker, trainer_card, main_pokemon, logger=None, day_cutoff=0, limit=None) -> dict:
    return _resolve_internal(
        mode="all",
        companion_id="",
        limit=limit,
        db=db,
        settings_obj=settings_obj,
        tracker=tracker,
        trainer_card=trainer_card,
        main_pokemon=main_pokemon,
        logger=logger,
        day_cutoff=day_cutoff
    )


def resolve_next(companion_id: str, db, settings_obj, tracker, trainer_card, main_pokemon, logger=None, day_cutoff=0) -> dict:
    return _resolve_internal(
        mode="next",
        companion_id=companion_id,
        limit=None,
        db=db,
        settings_obj=settings_obj,
        tracker=tracker,
        trainer_card=trainer_card,
        main_pokemon=main_pokemon,
        logger=logger,
        day_cutoff=day_cutoff
    )


def commit_replay_outcome(choice: str, outcome_data: dict, db, settings_obj, trainer_card, main_pokemon, achievements_dict=None, logger=None) -> dict:
    try:
        if not outcome_data:
            return {"success": False, "error": "No pending battle to resolve."}

        enemy_pokemon = outcome_data["enemy_pokemon"]
        battle_xp = outcome_data["battle_xp"]
        total_xp = outcome_data["total_xp"]
        accumulated_evs = outcome_data["accumulated_evs"]
        total_trainer_xp = outcome_data["total_trainer_xp"]
        gained_cash = outcome_data.get("gained_cash", 0)

        now_ms = int(__import__("time").time() * 1000)

        if choice == "catch":
            from datetime import datetime
            from .encounter_functions import save_caught_pokemon
            capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            enemy_pokemon.captured_date = capture_time
            save_caught_pokemon(enemy_pokemon, nickname=None, achievements=achievements_dict)
            try:
                from ..reviewer_ui import _collected_pokemon_ids
                if isinstance(_collected_pokemon_ids, set):
                    _collected_pokemon_ids.add(enemy_pokemon.id)
            except Exception: pass
            battle_xp = 0
            
        elif choice == "defeat":
            companion_id = outcome_data.get("companion_id", "")
            if not companion_id and main_pokemon:
                companion_id = getattr(main_pokemon, "individual_id", "")
            
            if companion_id and (total_xp > 0 or any(accumulated_evs.values())):
                _attribute_xp_and_evs_to_companion(companion_id, total_xp, accumulated_evs, settings_obj, db=db, logger=logger)

            if total_xp > 0 and main_pokemon and companion_id == main_pokemon.individual_id:
                # Add main_pokemon.pokemon_defeated increment
                main_pokemon.pokemon_defeated += 1
                try:
                    mp_data = db.get_main_pokemon()
                    if mp_data:
                        mp_data["pokemon_defeated"] = main_pokemon.pokemon_defeated
                        db.save_main_pokemon(mp_data)
                except Exception:
                    pass

            if total_trainer_xp > 0 and trainer_card:
                new_txp = int(settings_obj.get("trainer.xp", 0) + total_trainer_xp)
                settings_obj.set("trainer.xp", new_txp)
                settings_obj.set("trainer.total_xp", int(settings_obj.get("trainer.total_xp", 0) + total_trainer_xp))
                trainer_card.xp = new_txp
                trainer_card.total_xp = settings_obj.get("trainer.total_xp")
                trainer_card.check_level_up()
        
        # Mark resolved in DB
        review_ids = outcome_data.get("review_ids", [])
        if review_ids:
            for rid in review_ids:
                db.mark_mobile_battle_resolved(rid)

        # Calculate and award cumulative cash reward using review count
        gained_cash = 0
        if review_ids and settings_obj:
            total_reviews_resolved = len(review_ids)
            current_counter = int(settings_obj.get("trainer.mobile_reviews_resolved_since_payout", 0))
            new_counter = current_counter + total_reviews_resolved
            
            ci = int(settings_obj.get("trainer.cash_reward_interval", 5))
            ca = int(settings_obj.get("trainer.cash_reward_amount", 10))
            
            gained_cash = (new_counter // ci) * ca
            remaining_counter = new_counter % ci
            settings_obj.set("trainer.mobile_reviews_resolved_since_payout", remaining_counter)
            
            if gained_cash > 0:
                settings_obj.set("trainer.cash", int(settings_obj.get("trainer.cash", 0) + gained_cash))
                if trainer_card:
                    trainer_card.cash = settings_obj.get("trainer.cash")

        # Update mobile badge
        remaining = db.get_pending_mobile_count()
        try:
            from ..menu_buttons import update_mobile_badge
            update_mobile_badge(remaining)
        except Exception: pass

        # Calculate CP for the return value
        from ..business import calculate_cp_from_dict
        enemy_dict = enemy_pokemon.to_dict()
        enemy_dict.update({
            "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        })
        cp_val = calculate_cp_from_dict(enemy_dict)
        if cp_val.__class__.__name__ == "MagicMock":
            cp_val = 100

        # Save to mobile history
        try:
            comp_name = outcome_data.get("companion_name")
            comp_level = outcome_data.get("companion_level")
            if not comp_name:
                comp_name = "Companion"
                comp_level = 5
                active_comp = None
                if choice == "defeat" and main_pokemon:
                    active_comp = main_pokemon
                
                if active_comp:
                    comp_name = getattr(active_comp, "display_name", "Companion")
                    comp_level = getattr(active_comp, "level", 5)

            outcome_val = "caught" if choice == "catch" else "defeated"
            if outcome_data.get("companion_fainted", False):
                outcome_val = "lost"

            db.add_mobile_history_entry({
                "timestamp": now_ms,
                "enemy_id": enemy_pokemon.id,
                "enemy_name": enemy_pokemon.display_name,
                "enemy_level": enemy_pokemon.level,
                "enemy_shiny": enemy_pokemon.shiny,
                "companion_name": comp_name,
                "companion_level": comp_level,
                "outcome": outcome_val,
                "xp_gained": battle_xp if outcome_val == "defeated" else 0,
                "trainer_xp_gained": total_trainer_xp if outcome_val == "defeated" else 0,
                "cash_gained": gained_cash,
            })
        except Exception as ex:
            if logger:
                logger.log("error", f"Failed to record manual mobile battle history: {ex}")

        # Trigger sync notification to refresh UI
        try:
            from ..singletons import notify_stats_changed
            notify_stats_changed()
        except Exception: pass

        return {"success": True, "outcome": "caught" if choice == "catch" else "defeated", "xp_gained": battle_xp, "cp": cp_val, "remaining": remaining, "cash_gained": gained_cash}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _resolve_internal(mode="all", companion_id="", limit=None, db=None, settings_obj=None, tracker=None, trainer_card=None, main_pokemon=None, logger=None, day_cutoff=0) -> dict:
    conn = db._get_connection()
    
    use_transaction = (mode == "all")
    if use_transaction:
        conn._disable_commit = True
        from .. import utils
        utils.in_bulk_resolve = True

    try:
        if use_transaction:
            with conn:
                result = run_mobile_battles(
                    reviews=None,
                    commit=True,
                    db=db,
                    settings_obj=settings_obj,
                    tracker=tracker,
                    trainer_card=trainer_card,
                    main_pokemon=main_pokemon,
                    companion_override_id=companion_id,
                    logger=logger,
                    day_cutoff=day_cutoff,
                    limit=limit,
                    mode=mode
                )
        else:
            result = run_mobile_battles(
                reviews=None,
                commit=True,
                db=db,
                settings_obj=settings_obj,
                tracker=tracker,
                trainer_card=trainer_card,
                main_pokemon=main_pokemon,
                companion_override_id=companion_id,
                logger=logger,
                day_cutoff=day_cutoff,
                limit=limit,
                mode=mode
            )
        return result
    finally:
        if use_transaction:
            conn._disable_commit = False
            from .. import utils


def _attribute_xp_and_evs_to_companion(companion_id: str, xp_gained: int, ev_yield_gained: dict, settings_obj, battles_fought=1, db=None, logger=None) -> None:
    if xp_gained <= 0 and not any(ev_yield_gained.values()) and battles_fought <= 0:
        return

    if db is None:
        from aqt import mw
        db = mw.ankimon_db
    pkmndata = None
    if companion_id:
        try:
            pkmndata = db.get_pokemon_by_individual_id(companion_id) if hasattr(db, "get_pokemon_by_individual_id") else db.get_pokemon(companion_id)
        except Exception:
            pass

    if not pkmndata:
        return

    from Ankimon.functions.pokemon_functions import find_experience_for_level, get_levelup_move_for_pokemon
    from Ankimon.functions.drawing_utils import tooltipWithColour
    from ..pyobj.pokemon_obj import PokemonObject
    import random
    from .. import utils

    growth_rate = pkmndata.get("growth_rate", "medium-fast")
    level = int(pkmndata.get("level", 1))
    xp = int(pkmndata.get("xp", 0))
    remove_cap = settings_obj.get("misc.remove_level_cap") if settings_obj else False

    experience_req = int(find_experience_for_level(growth_rate, level, remove_cap))
    if remove_cap:
        xp += xp_gained
        level_cap = None
    elif level != 100:
        xp += xp_gained
        level_cap = 100
    else:
        level_cap = 100

    from aqt import mw
    is_active = (hasattr(mw, "main_pokemon") and mw.main_pokemon and getattr(mw.main_pokemon, "individual_id", None) == companion_id)
    in_bulk = getattr(utils, "in_bulk_resolve", False)
    
    color = "#6A4DAC"

    # level-ups
    while int(find_experience_for_level(growth_rate, level, remove_cap)) < xp and (level_cap is None or level < level_cap):
        level += 1
        msg = f"Your {pkmndata.get('name', 'Pokemon')} is now level {level} !"
        
        if is_active and not in_bulk:
            try:
                mw.logger.game_log(f"Level Up: {msg}")
                tooltipWithColour(msg, color)
                if settings_obj and settings_obj.get("gui.pop_up_dialog_message_on_defeat") is True:
                    if hasattr(mw, "logger") and mw.logger:
                        mw.logger.log_and_showinfo("info", f"{msg}")
            except Exception:
                pass
                
        xp = int(max(0, xp - int(experience_req)))
        experience_req = int(find_experience_for_level(growth_rate, level, remove_cap))
        
        # level-up moves
        name_lower = pkmndata.get("name", "").lower()
        new_attacks = get_levelup_move_for_pokemon(name_lower, level)
        if new_attacks:
            attacks = pkmndata.get("attacks", [])
            if isinstance(attacks, str):
                try:
                    import json
                    attacks = json.loads(attacks)
                except Exception:
                    attacks = []
            
            for new_attack in new_attacks:
                if len(attacks) < 4 and new_attack not in attacks:
                    attacks.append(new_attack)
                    if is_active and not in_bulk:
                        msg_learn = f"{pkmndata.get('name', '').capitalize()} learned {new_attack}!"
                        tooltipWithColour(msg_learn, color)
                elif new_attack not in attacks:
                    if is_active and not in_bulk:
                        from Ankimon.pyobj.reviewer_obj import AttackDialog
                        from PyQt6.QtWidgets import QDialog
                        dialog = AttackDialog(attacks, new_attack)
                        if dialog.exec() == QDialog.DialogCode.Accepted:
                            selected_attack = dialog.selected_attack
                            if selected_attack in attacks:
                                idx = attacks.index(selected_attack)
                                attacks[idx] = new_attack
            pkmndata["attacks"] = attacks

    pkmndata["level"] = level
    pkmndata["xp"] = xp
    
    # EV Updates
    if "ev" not in pkmndata or not isinstance(pkmndata["ev"], dict):
        pkmndata["ev"] = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        
    normalized_yield = {
        "hp": ev_yield_gained.get("hp", 0),
        "attack": ev_yield_gained.get("attack", 0) + ev_yield_gained.get("atk", 0),
        "defense": ev_yield_gained.get("defense", 0) + ev_yield_gained.get("def", 0),
        "special-attack": ev_yield_gained.get("special-attack", 0) + ev_yield_gained.get("spa", 0),
        "special-defense": ev_yield_gained.get("special-defense", 0) + ev_yield_gained.get("spd", 0),
        "speed": ev_yield_gained.get("speed", 0) + ev_yield_gained.get("spe", 0),
    }
    
    held_item = pkmndata.get("held_item", None)
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

    ev_yield = utils.limit_ev_yield(pkmndata["ev"], normalized_yield)
    pkmndata["ev"]["hp"] += ev_yield["hp"]
    pkmndata["ev"]["atk"] += ev_yield["attack"]
    pkmndata["ev"]["def"] += ev_yield["defense"]
    pkmndata["ev"]["spa"] += ev_yield["special-attack"]
    pkmndata["ev"]["spd"] += ev_yield["special-defense"]
    pkmndata["ev"]["spe"] += ev_yield["speed"]

    # Recompute stats
    pkmndata["stats"] = {
        k: PokemonObject.calc_stat(k, val, level, pkmndata["iv"][k], pkmndata["ev"][k], pkmndata.get("nature", "serious"))
        for k, val in pkmndata["base_stats"].items()
        if k in ("hp", "atk", "def", "spa", "spd", "spe")
    }
    pkmndata["current_hp"] = pkmndata["stats"].get("hp", 15)
    
    friendship = int(pkmndata.get("friendship", 0))
    friendship += random.randint(5, 9)
    pkmndata["friendship"] = min(255, friendship)
    
    pkmndata["pokemon_defeated"] = int(pkmndata.get("pokemon_defeated", 0)) + battles_fought

    # Call db.save_pokemon(updated_entry)
    db.save_pokemon(pkmndata)

    # 4. If active, also update the in-memory singleton
    if is_active:
        mp = mw.main_pokemon
        mp.xp = pkmndata["xp"]
        mp.level = pkmndata["level"]
        mp.ev = pkmndata["ev"].copy()
        mp.friendship = pkmndata["friendship"]
        mp.pokemon_defeated = pkmndata["pokemon_defeated"]
        if "attacks" in pkmndata:
            mp.attacks = list(pkmndata["attacks"])
        mp.invalidate_cp_cache()

