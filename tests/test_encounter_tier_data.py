"""Characterization test for F38 — encounter tier data expansion + nature-chart path.

F38 is a pure-data leaf: it adds alternate-form dex IDs to the Legendary and
Mythical encounter tiers in ``POKEMON_TIERS`` and adds the ``nature_chart_html_path``
resource constant. There is no ``mw`` access and no seam wiring — the observable
contract is simply the membership of ``resources.POKEMON_TIERS`` and the resolved
path constant.

The module is loaded directly from its file (not via ``import Ankimon.resources``)
so the test runs in the Qt-free Tier-1 environment: ``Ankimon/__init__.py`` imports
``aqt`` which is absent there, whereas ``resources.py`` itself only needs stdlib
(``pathlib``/``os``/``json``).

A cross-file drift guard against ``functions/encounter_data.py`` (whose lists
drive wild-encounter generation) is included at the bottom; it self-skips until
the F22 encounter overhaul replaces that file — see its docstring.
"""

import importlib.util
from pathlib import Path

import pytest

# --- Golden expectations (the "seed -> output" of this data leaf) ----------------

# Alternate-form dex IDs relocated INTO the Legendary tier (commit 8c795df9).
LEGENDARY_NEW_FORMS = {
    10245,  # dialgaorigin
    10246,  # palkiaorigin
    10007,  # giratinaorigin
    10019,  # tornadustherian
    10020,  # thundurustherian
    10021,  # landorustherian
    10249,  # enamorustherian
    10181,  # zygarde10
    10191,  # urshifurapidstrike
}

# Alternate-form dex IDs relocated INTO the Mythical tier (commit 8c795df9).
MYTHICAL_NEW_FORMS = {
    10001,  # deoxysattack
    10002,  # deoxysdefense
    10003,  # deoxysspeed
    10006,  # shayminsky
    10024,  # keldeoresolute
    10018,  # meloettapirouette
}

PECHARUNT = 1025  # Gen 9 mythical, lives in "Mythical" (not "Ultra").


def _load_resources():
    """Load ``src/Ankimon/resources.py`` in isolation (no package __init__, no aqt)."""
    resources_path = (
        Path(__file__).resolve().parents[1] / "src" / "Ankimon" / "resources.py"
    )
    spec = importlib.util.spec_from_file_location(
        "ankimon_resources_f38_probe", resources_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def resources():
    return _load_resources()


def test_nature_chart_html_path(resources):
    path = resources.nature_chart_html_path
    assert path.name == "nature_chart.html"
    assert path.parent.name == "addon_files"


def test_legendary_tier_has_new_forms(resources):
    legendary = resources.POKEMON_TIERS["Legendary"]
    missing = sorted(LEGENDARY_NEW_FORMS - set(legendary))
    assert not missing, f"Legendary tier missing form IDs: {missing}"


def test_mythical_tier_has_new_forms(resources):
    mythical = resources.POKEMON_TIERS["Mythical"]
    missing = sorted(MYTHICAL_NEW_FORMS - set(mythical))
    assert not missing, f"Mythical tier missing form IDs: {missing}"


def test_pecharunt_is_mythical_not_ultra(resources):
    assert PECHARUNT in resources.POKEMON_TIERS["Mythical"]
    assert PECHARUNT not in resources.POKEMON_TIERS["Ultra"]


def test_f38_ids_are_not_duplicated(resources):
    """Every ID F38 introduces (and Pecharunt) must live in exactly one tier.

    This is scoped to the F38-added IDs on purpose: the base data has unrelated
    pre-existing cross-tier overlaps (e.g. regional-form ranges) that are out of
    scope for this leaf and must not be regressed into a false failure here.
    """
    f38_ids = LEGENDARY_NEW_FORMS | MYTHICAL_NEW_FORMS | {PECHARUNT}
    membership = {}
    for tier, ids in resources.POKEMON_TIERS.items():
        for dex_id in ids:
            if dex_id in f38_ids:
                membership.setdefault(dex_id, []).append(tier)
    dupes = {k: v for k, v in membership.items() if len(v) > 1}
    assert not dupes, f"F38 IDs listed in multiple tiers: {dupes}"


# --- Cross-file drift guard: resources.POKEMON_TIERS vs functions/encounter_data --


def _load_encounter_data():
    """Load ``src/Ankimon/functions/encounter_data.py`` in isolation.

    Like ``resources.py`` it is loaded straight from its file: the module is
    pure data (no imports at all), so this stays Qt-free and does not trigger
    ``Ankimon/__init__``'s ``aqt`` import.
    """
    encounter_data_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "Ankimon"
        / "functions"
        / "encounter_data.py"
    )
    spec = importlib.util.spec_from_file_location(
        "ankimon_encounter_data_f38_probe", encounter_data_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_encounter_data_agrees_with_pokemon_tiers_on_f38_ids():
    """Wild-encounter lists must agree with ``POKEMON_TIERS`` on F38's IDs.

    Wild encounters are generated from the ``LEGENDARY``/``MYTHICAL`` lists in
    ``functions/encounter_data.py`` (via ``get_random_pokemon_in_tier``), while
    tier classification (badges/achievements on capture) reads
    ``resources.POKEMON_TIERS`` — the two files must agree on the F38 IDs or
    tier-based logic diverges.

    The base ``encounter_data.py`` predates the F22 encounter overhaul: it
    contains none of the F38 alternate-form IDs and still lists Pecharunt under
    ``LEGENDARY`` (a discrepancy that predates this PR). F22 — a Wave-2 unit,
    not yet ported — replaces that file with exp's version, which already
    matches this PR (all form IDs present; Pecharunt in ``MYTHICAL``). Until
    then this check self-skips; the moment any F38 form ID appears in
    ``encounter_data.py`` it arms and enforces full consistency, so a partial
    F22 port fails loudly instead of drifting silently.

    Scope note: consistency is asserted only between ``LEGENDARY`` and
    ``MYTHICAL``. Exp's ``encounter_data.py`` intentionally also lists some of
    these IDs elsewhere (e.g. 10191 in ``UNAVAILABLE``, all of them as
    ``PREREQUISITES`` keys) — those memberships are F22 semantics, not drift.
    """
    encounter_data = _load_encounter_data()
    legendary = set(encounter_data.LEGENDARY)
    mythical = set(encounter_data.MYTHICAL)
    form_ids = LEGENDARY_NEW_FORMS | MYTHICAL_NEW_FORMS
    if not form_ids & (legendary | mythical):
        pytest.skip(
            "functions/encounter_data.py predates the F22 encounter overhaul "
            "(no F38 form IDs present yet); this consistency guard arms "
            "automatically once F22 lands"
        )
    missing_legendary = sorted(LEGENDARY_NEW_FORMS - legendary)
    assert not missing_legendary, (
        f"encounter_data.LEGENDARY is missing form IDs: {missing_legendary}"
    )
    missing_mythical = sorted(MYTHICAL_NEW_FORMS - mythical)
    assert not missing_mythical, (
        f"encounter_data.MYTHICAL is missing form IDs: {missing_mythical}"
    )
    cross_listed = sorted(
        (LEGENDARY_NEW_FORMS & mythical) | (MYTHICAL_NEW_FORMS & legendary)
    )
    assert not cross_listed, (
        f"form IDs listed in the wrong encounter_data tier: {cross_listed}"
    )
    assert PECHARUNT in mythical, "Pecharunt must be MYTHICAL in encounter_data"
    assert PECHARUNT not in legendary, (
        "Pecharunt must not remain in encounter_data.LEGENDARY once F22 lands"
    )
