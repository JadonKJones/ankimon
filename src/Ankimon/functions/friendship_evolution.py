"""Friendship- and time-of-day-based evolution helpers.

Single source of truth for the in-game day/night clock, a species' friendship
evolution(s), whether a Pokémon is ready to evolve right now, and triggering that
evolution via :class:`EvoWindow`. Friendship evolutions live in
``pokemon_evolution.csv`` as level-up rows (``evolution_trigger_id == 1``) with a
positive ``minimum_happiness`` and an optional ``time_of_day``; the legacy
level-up code skips them because their ``minimum_level`` is blank.

Settings are read through the service registry (``services.settings``), fetched
per call rather than cached at import time so a registry that is populated after
this module loads is always seen.
"""

from __future__ import annotations

import functools
from datetime import datetime, timedelta, timezone
from typing import Any, NamedTuple, Optional

from .pokedex_functions import (
    pokemon_evolves_from_id,
    return_name_for_id,
    rows_for_key_in_table,
)
from ..resources import poke_evo_path
from ..services import services

# Reference value for friendship progress bars: the bar reads "full" at this
# value, and it's the fallback bar denominator for species with no friendship
# evolution. NOTE: friendship is NOT capped here — it keeps climbing past 400 as
# a flex stat (the bar just stays full; the raw number is what grows).
MAX_FRIENDSHIP = 400


class FriendshipEvolution(NamedTuple):
    """A single friendship-based evolution (immutable, hashable, cacheable).

    Attributes:
        evo_id: National Pokédex id of the evolved species.
        evo_name: Capitalised display name of the evolved species.
        min_happiness: Friendship value required to evolve.
        time_of_day: ``"day"``, ``"night"``, or ``None`` (no time requirement).
        known_move_type: Optional string matching a required move type (e.g. "Fairy").
    """

    evo_id: int
    evo_name: str
    min_happiness: int
    time_of_day: Optional[str]
    known_move_type: Optional[str] = None


class LevelEvolution(NamedTuple):
    """A single plain level-up evolution (counterpart to :class:`FriendshipEvolution`).

    Attributes:
        evo_id: National Pokédex id of the evolved species.
        evo_name: Capitalised display name of the evolved species.
        min_level: Level required to evolve.
        time_of_day: ``"day"``, ``"night"``, or ``None`` if the level-up
            evolution has no time-of-day requirement (e.g. Cosmoem -> Solgaleo
            by day / Lunala at night, both at Lv53).
    """

    evo_id: int
    evo_name: str
    min_level: int
    time_of_day: Optional[str] = None


def _now_in_configured_tz() -> datetime:
    """Return the current time in the user's configured time zone.

    Auto-detect (default) uses the device's local time via ``datetime.now()``;
    when ``evolution.timezone_auto`` is off, a fixed ``evolution.timezone_offset``
    (hours, clamped to ±14) is applied instead.
    """
    settings_obj = services.settings  # registry-backed; no singletons/aqt import

    if settings_obj.get("evolution.timezone_auto", True):
        return datetime.now()
    try:
        offset = float(settings_obj.get("evolution.timezone_offset", 0.0))
    except (TypeError, ValueError):
        offset = 0.0
    offset = max(-14.0, min(14.0, offset))  # clamp to the valid UTC range
    return datetime.now(timezone(timedelta(hours=offset)))


def _format_utc_offset(offset: float) -> str:
    """Format a UTC offset in hours, e.g. ``UTC+5:30`` / ``UTC-5`` / ``UTC+0``."""
    sign = "-" if offset < 0 else "+"
    hours, minutes = divmod(int(round(abs(offset) * 60)), 60)
    return f"UTC{sign}{hours}:{minutes:02d}" if minutes else f"UTC{sign}{hours}"


def _coerce_hour(value: Any, default: int) -> int:
    """Coerce a configured day/night boundary hour to an ``int`` in ``0-23``.

    The bounds are advanced (non-UI) config, so a hand-edited value can be a
    string / ``None`` / junk; fall back to ``default`` and clamp rather than raise.
    """
    try:
        hour = int(value)
    except (TypeError, ValueError):
        return default
    return max(0, min(23, hour))


def _coerce_int(value: Any, default: int) -> int:
    """Coerce a Pokémon stat (friendship / level) to an ``int``.

    The SQLite store can hand these back as JSON strings (``"160"``) via trades /
    imports / migrations; fall back to ``default`` for ``None`` / non-numeric junk
    rather than raising on later arithmetic.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_time_of_day(now: Optional[datetime] = None) -> str:
    """Return the current in-game time of day as ``"day"`` or ``"night"``.

    The day window is ``[day_start_hour, night_start_hour)`` (defaults 6-18, so
    night spans midnight); everything else is night. A misconfigured
    ``day_start_hour >= night_start_hour`` just yields an always-night window.

    Args:
        now: Optional :class:`datetime` to evaluate; defaults to the configured
            time zone. Useful for testing.

    Returns:
        ``"day"`` or ``"night"``.
    """
    settings_obj = services.settings  # registry-backed; no singletons/aqt import

    moment = now if now is not None else _now_in_configured_tz()
    hour = moment.hour
    day_start = _coerce_hour(settings_obj.get("evolution.day_start_hour", 6), 6)
    night_start = _coerce_hour(settings_obj.get("evolution.night_start_hour", 18), 18)
    return "day" if day_start <= hour < night_start else "night"


def current_time_label(now: Optional[datetime] = None) -> str:
    """Return a human-readable label for the current time of day.

    Examples:
        ``"☀️ Day · 09:12"`` or, with a manual time zone,
        ``"🌙 Night · 21:34 · UTC-5"``.

    Args:
        now: Optional :class:`datetime`. When omitted, the user's configured
            time zone is used.

    Returns:
        A short, emoji-prefixed label including the current ``HH:MM`` time (and
        the UTC offset when a manual time zone is configured).
    """
    settings_obj = services.settings  # registry-backed; no singletons/aqt import

    moment = now if now is not None else _now_in_configured_tz()
    time_of_day = get_time_of_day(moment)
    icon = "☀️ Day" if time_of_day == "day" else "🌙 Night"
    label = f"{icon} · {moment.strftime('%H:%M')}"
    if not settings_obj.get("evolution.timezone_auto", True):
        try:
            offset = float(settings_obj.get("evolution.timezone_offset", 0.0))
            label += f" · {_format_utc_offset(offset)}"
        except (TypeError, ValueError):
            pass
    return label


def _is_plain_level_row(row: dict) -> bool:
    """Return ``True`` if a CSV row is a plain level-up evolution.

    A "plain level-up" row has ``evolution_trigger_id == 1``, a positive
    ``minimum_level`` and *no* friendship requirement (blank/zero
    ``minimum_happiness``). It is used to detect evolved species that are already
    reachable by levelling up, so the friendship helper can leave those to the
    level path (see :func:`get_friendship_evolutions_for_species`).
    """
    try:
        if int(row.get("evolution_trigger_id", 0)) != 1:
            return False
    except (TypeError, ValueError):
        return False
    try:
        if int(row.get("minimum_happiness", "") or 0) > 0:
            return False
    except (TypeError, ValueError):
        pass
    try:
        return int(row.get("minimum_level", "")) > 0
    except (TypeError, ValueError):
        return False


@functools.lru_cache(maxsize=None)
def get_friendship_evolutions_for_species(
    pokemon_id: int,
) -> tuple[FriendshipEvolution, ...]:
    """Return all friendship evolutions for a species, sorted by evolved id.

    Scans every CSV row of each evolved form (not first-match — that would miss
    e.g. Eevee -> Sylveon, whose blank row precedes its friendship row) and keeps
    those with a positive ``minimum_happiness``. Forms also reachable by a plain
    level-up are left to the level path (see :func:`_is_plain_level_row`) so a
    classic level-up evolution isn't silently changed. ``lru_cache``d on
    ``pokemon_id`` (the CSV is static for the process lifetime; the returned
    ``NamedTuple``s are immutable, so the cached tuple is safe to share).

    Args:
        pokemon_id: National Pokédex id of the *pre-evolution* species.

    Returns:
        A tuple of :class:`FriendshipEvolution` entries sorted by ``evo_id``;
        empty if the species has no friendship evolution.
    """
    evolutions: list[FriendshipEvolution] = []
    for evo in pokemon_evolves_from_id(pokemon_id):
        # An evolved species can have several rows (one per evolution method), so
        # scan them all and keep the one carrying a positive minimum_happiness.
        # check_key_in_table's first-match would miss e.g. Sylveon, whose blank
        # row precedes its friendship row in the CSV.
        rows = rows_for_key_in_table("evolved_species_id", evo, poke_evo_path)
        # If this evolved species is also reachable by levelling up, leave it to
        # the level path instead of offering a friendship evolution. The bundled
        # CSV carries no Pokémon *form* data, so it conflates e.g. Kantonian
        # Meowth (level 28) and Alolan Meowth (friendship) onto the same evolved
        # id (Persian); preferring friendship there would silently change a
        # classic level-up evolution. Scoping friendship evolution to species
        # that evolve *purely* by friendship (Eevee, Golbat, Pichu, Riolu, ...)
        # keeps the feature focused and leaves existing level evolutions intact.
        if any(_is_plain_level_row(r) for r in rows):
            continue
        for row in rows:
            try:
                min_happiness = int(row.get("minimum_happiness", ""))
            except (TypeError, ValueError):
                continue
            if min_happiness <= 0:
                continue

            time_raw = (row.get("time_of_day") or "").strip().lower()
            time_of_day = time_raw if time_raw in ("day", "night") else None

            known_move_type = None
            try:
                type_id = int(row.get("known_move_type_id", ""))
                # In Gen 6+, Fairy is type 18.
                _type_map = {
                    1: "Normal", 2: "Fighting", 3: "Flying", 4: "Poison",
                    5: "Ground", 6: "Rock", 7: "Bug", 8: "Ghost", 9: "Steel",
                    10: "Fire", 11: "Water", 12: "Grass", 13: "Electric",
                    14: "Psychic", 15: "Ice", 16: "Dragon", 17: "Dark", 18: "Fairy"
                }
                known_move_type = _type_map.get(type_id)
            except (TypeError, ValueError):
                pass

            name = return_name_for_id(int(evo))
            evo_name = name.capitalize() if name else str(evo)

            evolutions.append(
                FriendshipEvolution(
                    evo_id=int(evo),
                    evo_name=evo_name,
                    min_happiness=min_happiness,
                    time_of_day=time_of_day,
                    known_move_type=known_move_type,
                )
            )
            break  # one friendship row per evolved species is enough

    evolutions.sort(key=lambda e: e.evo_id)
    return tuple(evolutions)


@functools.lru_cache(maxsize=None)
def get_level_evolutions_for_species(
    pokemon_id: int,
) -> tuple[LevelEvolution, ...]:
    """Return all plain level-up evolutions for a species, sorted by evolved id.

    Prioritises the form-aware ``pokedex.json`` data (so regional forms such as
    Alolan Marowak / Galarian Weezing and move- or defeat-based evolutions such
    as Mr. Mime and Pawmot are surfaced with their real ``actual_id``), then
    falls back to the bundled ``pokemon_evolution.csv`` for species that carry no
    ``pokedex.json`` evolution data. Only plain level-up rows are kept
    (``evolution_trigger_id == 1`` with a positive ``minimum_level`` and no
    friendship requirement) so the two helpers never double-count a row; the
    friendship helper handles ``minimum_happiness`` rows. ``lru_cache``d on
    ``pokemon_id`` (both data sources are static for the process lifetime).

    Args:
        pokemon_id: National Pokédex id of the *pre-evolution* species.

    Returns:
        A tuple of :class:`LevelEvolution` entries sorted by ``evo_id``; empty if
        the species has no plain level-up evolution.
    """
    # Lazy imports: keep them local so tests may monkeypatch the pokedex cache /
    # id lookup on ``pokedex_functions`` without a stale module-level binding.
    from .pokedex_functions import (
        _load_pokedex_cache,
        safe_int,
        search_pokedex_by_id,
    )

    evolutions: list[LevelEvolution] = []

    # 1. PRIORITY: form-aware evolution from pokedex.json. This carries the
    #    regional/mega/gmax forms (and their real actual_id), move-based
    #    (levelMove) and defeat-based (minimumDefeated) methods that the base
    #    species CSV cannot express.
    pokedex_data = _load_pokedex_cache()
    internal_name = search_pokedex_by_id(pokemon_id)

    if internal_name in pokedex_data:
        evo_list = pokedex_data[internal_name].get("evos")
        if evo_list:
            for target_evo_name in evo_list:
                normalized = (
                    target_evo_name.lower()
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("'", "")
                    .replace(".", "")
                    .replace(":", "")
                )
                target_data = pokedex_data.get(normalized) or pokedex_data.get(
                    target_evo_name.lower()
                )
                if not target_data:
                    continue

                # In Smogon-style pokedex.json, evoLevel is stored on the
                # evolved species.
                min_level = safe_int(target_data.get("evoLevel"))
                evo_type = target_data.get("evoType")
                condition = (target_data.get("evoCondition") or "").lower()
                target_id = safe_int(
                    target_data.get("actual_id") or target_data.get("species_id")
                )

                # Move-based (levelMove) and defeat-based (minimumDefeated)
                # evolutions have no fixed evoLevel; treat them as eligible from
                # Lv1 so the readiness path can gate them on the move / count.
                is_eligible = min_level > 0
                if evo_type == "levelMove" or condition == "minimumdefeated":
                    is_eligible = True
                    if min_level <= 0:
                        min_level = 1

                if target_id > 0 and is_eligible:
                    time_of_day = None
                    if "day" in condition:
                        time_of_day = "day"
                    elif "night" in condition:
                        time_of_day = "night"

                    evolutions.append(
                        LevelEvolution(
                            evo_id=target_id,
                            evo_name=target_data.get("name", target_evo_name),
                            min_level=min_level,
                            time_of_day=time_of_day,
                        )
                    )

        # A species listed in pokedex.json is authoritative for its evolutions
        # (the CSV conflates regional forms onto one id), so return its results
        # even when empty rather than falling through to the CSV.
        evolutions.sort(key=lambda e: e.evo_id)
        return tuple(evolutions)

    # 2. LEGACY FALLBACK: species CSV lookup for anything absent from pokedex.json.
    for evo in pokemon_evolves_from_id(pokemon_id):
        # Scan every row for this evolved species and keep the first that is a
        # plain level-up row. An evolved species may carry several method rows
        # (e.g. a level-up row *and* a friendship row), so first-match would pick
        # the wrong one when the level row isn't listed first.
        for row in rows_for_key_in_table("evolved_species_id", evo, poke_evo_path):
            # Level-up trigger only (item/trade/etc. evolutions are out of scope).
            try:
                trigger_id = int(row.get("evolution_trigger_id", 0))
            except (TypeError, ValueError):
                continue
            if trigger_id != 1:
                continue

            # Exclude friendship evolutions — those are handled by the friendship
            # helper and must not be double-counted here.
            try:
                min_happiness = int(row.get("minimum_happiness", "") or 0)
            except (TypeError, ValueError):
                min_happiness = 0
            if min_happiness > 0:
                continue

            try:
                min_level = int(row.get("minimum_level", ""))
            except (TypeError, ValueError):
                continue
            if min_level <= 0:
                continue

            time_raw = (row.get("time_of_day") or "").strip().lower()
            time_of_day = time_raw if time_raw in ("day", "night") else None

            name = return_name_for_id(int(evo))
            evo_name = name.capitalize() if name else str(evo)

            evolutions.append(
                LevelEvolution(
                    evo_id=int(evo),
                    evo_name=evo_name,
                    min_level=min_level,
                    time_of_day=time_of_day,
                )
            )
            break  # one level-up row per evolved species is enough

    evolutions.sort(key=lambda e: e.evo_id)
    return tuple(evolutions)


def _select_evolution(
    evos: tuple[FriendshipEvolution, ...], time_of_day: str, known_move_types: set[str] = frozenset()
) -> FriendshipEvolution:
    """Pick the most appropriate friendship evolution for the current time.

    Prefers an evolution whose move-type requirement (if any) is met.
    Then prefers one eligible right now (its ``time_of_day`` matches, or it
    has none); among those, an explicitly time-gated row beats a blank-time one,
    then lowest ``evo_id``. If none is eligible now, falls back to the lowest
    ``evo_id`` so the UI can still show e.g. "waiting for Night".

    Args:
        evos: Non-empty tuple from :func:`get_friendship_evolutions_for_species`.
        time_of_day: Current time of day (``"day"`` or ``"night"``).
        known_move_types: A set of types known by the Pokémon.

    Returns:
        The chosen :class:`FriendshipEvolution`.
    """
    # Only keep evolutions whose move requirement (if any) is met.
    move_eligible = [
        e for e in evos
        if e.known_move_type is None or e.known_move_type.lower() in known_move_types
    ]
    # If a move-based evolution like Sylveon meets its requirement, it gets priority
    # over standard time-of-day evolutions like Espeon/Umbreon in official games.
    # So we'll prefer evolutions that actually have a move requirement first,
    # and then fall back to time-of-day rules among the rest.
    if move_eligible:
        evos_to_consider = move_eligible
    else:
        evos_to_consider = list(evos)

    move_specific = [e for e in evos_to_consider if e.known_move_type is not None]
    if move_specific:
        # If we met a move condition, prefer it directly (e.g. Sylveon beats Espeon).
        # We can just return the one with the lowest evo_id among those.
        return min(move_specific, key=lambda e: e.evo_id)

    eligible_now = [e for e in evos_to_consider if e.time_of_day in (time_of_day, None)]
    if eligible_now:
        # Prefer explicit-time rows (e.g. Espeon@day) over blank-time rows, then
        # lowest evo_id. ``time_of_day is None`` sorts last via the bool key.
        return min(eligible_now, key=lambda e: (e.time_of_day is None, e.evo_id))
    # Nothing matches the current time; still return a representative.
    return min(evos_to_consider, key=lambda e: e.evo_id)


def evolution_readiness(pokemon: Any, now: Optional[datetime] = None) -> dict:
    """Compute manual-evolution readiness for a single Pokémon.

    Covers both friendship/time and plain level-up evolutions, so the PC's
    "Evolve now" button and ✨ badge work for either. Friendship takes precedence
    (``method="friendship"``); otherwise a level-up evolution is considered
    (``method="level"``), else ``method=None``. Accepts a dict or an object with
    ``id`` / ``friendship`` / ``everstone`` / ``level`` (missing -> 0 / False / 1).

    Args:
        pokemon: A Pokémon dict or object.
        now: Optional :class:`datetime` for the time-of-day check.

    Returns:
        A readiness dict with keys: ``evolvable, ready, method, evo_id,
        evo_name, min_happiness, current_friendship, friendship_remaining,
        required_time, time_ok, status_text, bar_max, rejected``. ``bar_max``
        defaults to :data:`MAX_FRIENDSHIP` outside the friendship path.
    """
    if isinstance(pokemon, dict):
        species_id = pokemon.get("id")
        friendship = _coerce_int(pokemon.get("friendship", 0), 0)
        everstone = pokemon.get("everstone", False)
        evolution_rejected = pokemon.get("evolution_rejected", False)
        level = _coerce_int(pokemon.get("level", 1), 1)
    else:
        species_id = getattr(pokemon, "id", None)
        friendship = _coerce_int(getattr(pokemon, "friendship", 0), 0)
        everstone = getattr(pokemon, "everstone", False)
        evolution_rejected = getattr(pokemon, "evolution_rejected", False)
        level = _coerce_int(getattr(pokemon, "level", 1), 1)

    time_of_day = get_time_of_day(now)

    not_evolvable = {
        "evolvable": False,
        "ready": False,
        "method": None,
        "evo_id": None,
        "evo_name": None,
        "min_happiness": None,
        "current_friendship": friendship,
        "friendship_remaining": 0,
        "required_time": None,
        "time_ok": True,
        "status_text": "",
        "bar_max": MAX_FRIENDSHIP,
        "rejected": False,
    }

    if species_id is None:
        return not_evolvable
    try:
        species_id = int(species_id)
    except (TypeError, ValueError):
        # A malformed/non-numeric id can't be matched against the integer CSV
        # ids; treat it like a missing id rather than raising on the hot path.
        return not_evolvable

    evos = get_friendship_evolutions_for_species(species_id)
    if not evos:
        # No friendship evolution — fall back to a plain level-up evolution so
        # the manual "Evolve now" path covers level evolvers too (auto level-ups
        # are still handled by check_evolution_for_pokemon; this is for mons that
        # rejected, hold an Everstone, or were caught above their evolve level).
        return _level_readiness(
            species_id=species_id,
            level=level,
            everstone=everstone,
            friendship=friendship,
            evolution_rejected=evolution_rejected,
            not_evolvable=not_evolvable,
            time_of_day=time_of_day,
            pokemon=pokemon,
        )

    # Collect known move types to check move-based friendship requirements (e.g. Sylveon)
    known_move_types = set()
    from .pokedex_functions import find_details_move

    attacks = []
    if isinstance(pokemon, dict):
        attacks = pokemon.get("attacks") or []
    elif pokemon is not None:
        attacks = getattr(pokemon, "attacks", []) or []

    for attack_name in attacks:
        if isinstance(attack_name, str):
            move_details = find_details_move(attack_name)
            if move_details and "type" in move_details:
                known_move_types.add(move_details["type"].lower())

    chosen = _select_evolution(evos, time_of_day, known_move_types)
    evo_id = chosen.evo_id
    evo_name = chosen.evo_name
    min_happiness = chosen.min_happiness
    required_time = chosen.time_of_day

    friendship_remaining = max(0, min_happiness - friendship)
    time_ok = required_time is None or required_time == time_of_day
    ready = (not everstone) and friendship >= min_happiness and time_ok

    status_text = _build_status_text(
        everstone=everstone,
        ready=ready,
        evo_name=evo_name,
        friendship_remaining=friendship_remaining,
        required_time=required_time,
        time_ok=time_ok,
        time_of_day=time_of_day,
        rejected=evolution_rejected,
    )

    return {
        "evolvable": True,
        "ready": ready,
        "method": "friendship",
        "evo_id": evo_id,
        "evo_name": evo_name,
        "min_happiness": min_happiness,
        "current_friendship": friendship,
        "friendship_remaining": friendship_remaining,
        "required_time": required_time,
        "time_ok": time_ok,
        "status_text": status_text,
        "bar_max": min_happiness,
        "rejected": evolution_rejected,
    }


def _active_region() -> Optional[str]:
    """Return the player's active region, or ``None`` for "No Region"/unset.

    Read through the service seam (``services.settings``); a missing/blank value
    or a ``"No Region"`` sentinel means "no regional preference" and is folded to
    ``None``. Never raises on the hot PC-render path.
    """
    try:
        region = services.settings.get("misc.active_region")
    except Exception:
        return None
    if region:
        region = str(region).strip()
    if not region or region == "No Region":
        return None
    return region


def _filter_evolutions_by_region(
    level_evos: tuple[LevelEvolution, ...],
    active_region: Optional[str],
) -> list[LevelEvolution]:
    """Prefer regional-form targets that match the active region.

    A target with an ``evoRegion`` is kept only when it matches ``active_region``.
    A target with no ``evoRegion`` (the base form) is kept unless a *sibling*
    evolution's ``evoRegion`` matches the active region (in which case the
    regional form supersedes the base form — e.g. under Alola, Cubone prefers
    Alolan Marowak over Kantonian Marowak). Returns the surviving list (may be
    empty; callers fall back to the unfiltered list when so).
    """
    from .pokedex_functions import _load_pokedex_cache, search_pokedex_by_id

    pokedex_data = _load_pokedex_cache()

    def region_of(evo: LevelEvolution) -> Optional[str]:
        name = search_pokedex_by_id(evo.evo_id)
        data = pokedex_data.get(name)
        return data.get("evoRegion") if data else None

    def matches_active(region: Optional[str]) -> bool:
        return bool(
            region and active_region and active_region.lower() == region.lower()
        )

    filtered: list[LevelEvolution] = []
    for evo in level_evos:
        target_region = region_of(evo)
        if target_region:
            if matches_active(target_region):
                filtered.append(evo)
        else:
            # Base form: drop it only when a sibling regional form matches the
            # active region (the regional form supersedes it).
            has_matching_regional_sibling = any(
                matches_active(region_of(other)) for other in level_evos
            )
            if not has_matching_regional_sibling:
                filtered.append(evo)
    return filtered


def _level_readiness(
    *,
    species_id: int,
    level: int,
    everstone: bool,
    friendship: int,
    evolution_rejected: bool,
    not_evolvable: dict,
    time_of_day: str,
    pokemon: Any = None,
) -> dict:
    """Compute readiness for a plain level-up evolution.

    Called by :func:`evolution_readiness` when the species has no friendship
    evolution; returns ``not_evolvable`` unchanged if it has no level-up evolution
    either. Ignores ``evolution_rejected`` (the manual button still shows) but
    DOES enforce the region preference (``misc.active_region``), any
    ``time_of_day`` requirement, a required ``levelMove`` (e.g. Mr. Mime needs
    Mimic) and a ``minimumDefeated`` count (e.g. Pawmot needs 100 defeats):
    ``ready = (not everstone) and level >= min_level and time_ok and knows_move
    and defeated_ok``.

    Returns:
        A readiness dict with ``method="level"`` (or ``not_evolvable``).
    """
    from .pokedex_functions import _load_pokedex_cache, safe_int, search_pokedex_by_id

    level_evos = get_level_evolutions_for_species(species_id)
    if not level_evos:
        return not_evolvable

    # Prefer the regional-form target that matches the active region (falls back
    # to the full set when the region filter would leave nothing).
    filtered = _filter_evolutions_by_region(level_evos, _active_region())
    if filtered:
        level_evos = tuple(filtered)

    # Among the surviving targets prefer one eligible right now (its time matches
    # or it has no time requirement); an explicit-time row beats a blank-time one.
    eligible_now = [e for e in level_evos if e.time_of_day in (time_of_day, None)]
    if eligible_now:
        chosen = min(eligible_now, key=lambda e: (e.time_of_day is None, e.evo_id))
    else:
        chosen = min(level_evos, key=lambda e: e.evo_id)

    evo_name = chosen.evo_name
    min_level = chosen.min_level
    required_time = chosen.time_of_day

    time_ok = required_time is None or required_time == time_of_day
    ready = (not everstone) and level >= min_level and time_ok

    # Move-based (levelMove) and defeat-based (minimumDefeated) gating from the
    # evolved species' pokedex.json data.
    knows_move = True
    required_move = None
    defeated_ok = True
    required_defeated = None
    defeated_count = 0
    pokedex_data = _load_pokedex_cache()
    target_name = search_pokedex_by_id(chosen.evo_id)
    target_data = pokedex_data.get(target_name)
    if target_data:
        if target_data.get("evoType") == "levelMove":
            required_move = target_data.get("evoMove")
            if required_move:
                knows_move = False
                attacks = []
                if isinstance(pokemon, dict):
                    attacks = pokemon.get("attacks") or []
                elif pokemon is not None:
                    attacks = getattr(pokemon, "attacks", []) or []
                needle = required_move.lower().replace(" ", "").replace("-", "")
                if any(
                    str(a).lower().replace(" ", "").replace("-", "") == needle
                    for a in attacks
                ):
                    knows_move = True

        condition = (target_data.get("evoCondition") or "").lower()
        if condition == "minimumdefeated":
            required_defeated = safe_int(target_data.get("evoDefeated"))
            if required_defeated > 0:
                if isinstance(pokemon, dict):
                    defeated_count = safe_int(pokemon.get("pokemon_defeated", 0))
                elif pokemon is not None:
                    defeated_count = safe_int(getattr(pokemon, "pokemon_defeated", 0))
                defeated_ok = defeated_count >= required_defeated

    if not knows_move or not defeated_ok:
        ready = False

    if everstone:
        status_text = "Everstone prevents evolution"
    elif not knows_move and required_move:
        status_text = f"Needs to learn {required_move} to evolve"
    elif not defeated_ok and required_defeated:
        status_text = (
            f"Needs to defeat {required_defeated} enemies to evolve "
            f"(current: {defeated_count})"
        )
    elif ready and evolution_rejected:
        status_text = "Evolution rejected — tap Evolve now to override"
    elif ready:
        status_text = f"Ready to evolve into {evo_name}!"
    elif level >= min_level and not time_ok and required_time is not None:
        status_text = (
            f"Ready — waiting for {required_time.capitalize()} "
            f"(now {time_of_day.capitalize()})"
        )
    else:
        if required_move:
            status_text = f"Evolves into {evo_name} knowing {required_move}"
        else:
            status_text = f"Evolves into {evo_name} at Lv{min_level}"
        if required_time is not None:
            status_text += f" · needs {required_time.capitalize()}"

    return {
        "evolvable": True,
        "ready": ready,
        "method": "level",
        "evo_id": chosen.evo_id,
        "evo_name": evo_name,
        "min_happiness": None,
        "current_friendship": friendship,
        "friendship_remaining": 0,
        "required_time": required_time,
        "time_ok": time_ok,
        "status_text": status_text,
        "bar_max": MAX_FRIENDSHIP,
        "rejected": evolution_rejected,
    }


def _build_status_text(
    *,
    everstone: bool,
    ready: bool,
    evo_name: str,
    friendship_remaining: int,
    required_time: Optional[str],
    time_ok: bool,
    time_of_day: str,
    rejected: bool = False,
) -> str:
    """Build the human-readable readiness line shown in the UI.

    Examples:
        - ``"Everstone prevents evolution"``
        - ``"Evolution rejected — tap Evolve now to override"``
        - ``"Ready to evolve into Espeon!"``
        - ``"Ready — waiting for Night (now Day)"``
        - ``"40 friendship to evolve into Espeon · needs Day"``
    """
    if everstone:
        return "Everstone prevents evolution"

    if ready and rejected:
        return "Evolution rejected — tap Evolve now to override"

    if ready:
        return f"Ready to evolve into {evo_name}!"

    # Friendship is high enough but the time of day is wrong.
    if friendship_remaining == 0 and not time_ok and required_time is not None:
        return (
            f"Ready — waiting for {required_time.capitalize()} "
            f"(now {time_of_day.capitalize()})"
        )

    # Still needs more friendship.
    text = f"{friendship_remaining} friendship to evolve into {evo_name}"
    if required_time is not None:
        text += f" · needs {required_time.capitalize()}"
    return text


def check_friendship_evolution_for_pokemon(
    individual_id,
    pokemon_id,
    evo_window,
    everstone: bool = False,
    friendship: int = 0,
    evolution_rejected: bool = False,
    now: Optional[datetime] = None,
) -> Optional[int]:
    """Prompt a friendship (or defeat-milestone) evolution for a Pokémon if ready.

    Honors the ``evolution.friendship_time_enabled`` toggle, the Everstone, and a
    prior rejection. When ready, opens :meth:`EvoWindow.ask_pokemon_evo`.

    Two evolution kinds auto-prompt through this victory-time checker:

    * friendship/time evolutions (``method == "friendship"``); and
    * ``minimumDefeated`` evolutions (a subset of ``method == "level"`` — e.g.
      Pawmo -> Pawmot after 100 defeats), whose defeat count is read from the DB.

    Plain level-up evolutions are NOT auto-prompted here (those are handled by
    ``check_evolution_for_pokemon`` on level-up; the manual PC button covers the
    rest), so a level-ready Pokémon without a defeat milestone stays silent.

    Returns:
        The evolved species id if the evolution was triggered, else ``None``.
    """
    settings_obj = services.settings  # registry-backed; no singletons/aqt import

    if (
        not settings_obj.get("evolution.friendship_time_enabled", True)
        or everstone
        or evolution_rejected
    ):
        return None

    # Defeat count for minimumDefeated evolutions (Pawmo/Rellor): read via the DB
    # seam, guarded so a missing/unavailable store degrades to 0 rather than
    # raising on the victory hot path.
    pokemon_defeated = 0
    try:
        db = services.db
        if db is not None and hasattr(db, "get_pokemon"):
            record = db.get_pokemon(individual_id)
            if record:
                pokemon_defeated = record.get("pokemon_defeated", 0)
    except Exception:
        pokemon_defeated = 0

    shim = {
        "id": pokemon_id,
        "friendship": friendship,
        "everstone": everstone,
        "pokemon_defeated": pokemon_defeated,
    }
    readiness = evolution_readiness(shim, now)

    # 1. Friendship/time evolution auto-prompts here.
    if readiness["method"] == "friendship" and readiness["ready"]:
        evo_window.ask_pokemon_evo(individual_id, pokemon_id, readiness["evo_id"])
        return readiness["evo_id"]

    # 2. minimumDefeated evolution auto-prompts on the victory milestone. A plain
    # level-ready Pokémon (no defeat condition) is deliberately NOT prompted here.
    if readiness["method"] == "level" and readiness["ready"]:
        from .pokedex_functions import _load_pokedex_cache, search_pokedex_by_id

        pokedex_data = _load_pokedex_cache()
        target_data = pokedex_data.get(search_pokedex_by_id(readiness["evo_id"]))
        if (
            target_data
            and (target_data.get("evoCondition") or "").lower() == "minimumdefeated"
        ):
            evo_window.ask_pokemon_evo(individual_id, pokemon_id, readiness["evo_id"])
            return readiness["evo_id"]

    return None
