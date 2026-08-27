"""Regression: the web bag's Pokemon picker must offer trade-with-item evolutions.

The trap this guards against: ``AnkimonItemsWeb.get_pokemon_choices`` re-implements
the evolution-eligibility test inline (deliberately — it runs per-Pokemon and must
stay free of file I/O) instead of calling ``check_evolution_by_item``. The two
copies drifted: the canonical helper accepts ``evoType`` in ``("useItem", "trade")``
while the picker's copy only accepted ``"useItem"``, even though the comment above
it claims to mirror the canonical logic.

``shop.js`` filters the picker to ``c.e === 1`` for evolution items, so an unflagged
Pokemon does not merely sort lower — it vanishes from the list. That made every
trade-with-held-item evolution unusable from the bag (reported as "Rhydon doesn't
appear when I click the Protector"), while the Protector itself was still consumed
and refunded, so the item looked broken rather than the picker.

The final test pins the two implementations to each other, so a future edit to one
that is not mirrored in the other fails here rather than in a player's save.
"""

import importlib
import json
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

_SRC = Path(__file__).parent.parent / "src"
_POKEDEX = json.loads(
    (_SRC / "Ankimon" / "data_files" / "pokedex.json").read_text(encoding="utf-8")
)


def _normalize(name):
    """Strip the punctuation that separates pokedex display names from keys."""
    return (
        (name or "")
        .lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("'", "")
        .replace(".", "")
        .replace(":", "")
    )


def _trade_item_species():
    """Every plain-form species that evolves from a trade-with-held-item.

    Read out of the real ``pokedex.json`` rather than hard-coded, so a data update
    that adds one automatically widens the sweep. Regional forms are skipped: their
    eligibility depends on ``misc.active_region``, which is a separate branch.
    """
    cases = []
    for evo_key, evo in _POKEDEX.items():
        if evo.get("evoType") != "trade" or not evo.get("evoItem"):
            continue
        if evo.get("evoRegion"):
            continue
        prevo = _POKEDEX.get(_normalize(evo.get("prevo")))
        if not prevo:
            continue
        prevo_id = prevo.get("actual_id") or prevo.get("species_id")
        # pokedex.json spells items for display ("Deep Sea Scale", "King's Rock");
        # the bag passes items.csv identifiers ("deep-sea-scale", "kings-rock").
        item_identifier = evo["evoItem"].lower().replace("'", "").replace(" ", "-")
        cases.append(
            pytest.param(prevo.get("name"), prevo_id, item_identifier, id=f"{evo_key}")
        )
    return cases


TRADE_ITEM_SPECIES = _trade_item_species()


@pytest.fixture(scope="module")
def shop_obj():
    """Import the real web-shell host once, headlessly.

    Only the package stubs conftest already installs are needed; everything else
    (pokedex cache, items.csv, the CP formula) is loaded for real so the test
    exercises the shipped data. No mock is left in ``sys.modules``: the module
    imported here is the genuine one, and the ``services`` seam is swapped
    per-test with an auto-reverting ``patch.object``.
    """
    for pkg in (
        "Ankimon",
        "Ankimon.functions",
        "Ankimon.pyobj",
        "Ankimon.ankimon_items_web",
    ):
        mod = sys.modules.get(pkg)
        if mod is None or not hasattr(mod, "__path__"):
            mod = types.ModuleType(pkg)
            mod.__path__ = [str(_SRC / pkg.replace(".", "/"))]
            mod.__package__ = pkg
            sys.modules[pkg] = mod
    try:
        return importlib.import_module("Ankimon.ankimon_items_web.shop_obj")
    except Exception as e:  # pragma: no cover - environment guard
        pytest.skip(f"web-shell host not importable headlessly: {e}")


class _StubHost:
    """The slice of ``AnkimonItemsWeb`` that ``get_pokemon_choices`` actually reads.

    Calling the method unbound against this avoids constructing a QDialog (and a
    QWebEngineView) for what is a pure data transform.
    """

    _pokemon_choices_cache = None
    item_window = None  # no active Pokemon; nothing gets the "m" flag

    def _categorize(self, item_name, is_tm):
        return "evolution"


def _stub_services(rows):
    class _DB:
        @staticmethod
        def get_all_pokemon():
            return rows

    class _Services:
        db = _DB
        settings = None  # -> no active region
        logger = None

    return _Services


def _pokemon(name, pokedex_id):
    """A collection row with the fields the picker reads (and nothing else)."""
    return {
        "individual_id": f"iid-{name}-{pokedex_id}",
        "id": pokedex_id,
        "name": name,
        "nickname": "",
        "level": 40,
        "base_stats": {"hp": 50, "atk": 50, "def": 50, "spa": 50, "spd": 50, "spe": 50},
        "iv": {},
        "ev": {},
    }


def _choices(shop_obj, rows, item_name):
    with patch.object(shop_obj, "services", _stub_services(rows)):
        result = shop_obj.AnkimonItemsWeb.get_pokemon_choices(_StubHost(), item_name)
    return {c["id"]: c for c in result["choices"]}


def test_rhydon_is_offered_the_protector(shop_obj):
    """The reported bug: Rhydon + Protector, the picker's list came back empty."""
    rhydon = _pokemon("Rhydon", 112)
    choices = _choices(shop_obj, [rhydon], "protector")

    assert choices[rhydon["individual_id"]].get("e") == 1


def test_use_item_evolutions_are_still_offered(shop_obj):
    """The other branch of the predicate must keep working (Gloom + Leaf Stone)."""
    gloom = _pokemon("gloom", 44)
    choices = _choices(shop_obj, [gloom], "leaf-stone")

    assert choices[gloom["individual_id"]].get("e") == 1


def test_wrong_item_is_not_offered(shop_obj):
    """Eligibility is still per-item: Rhydon does not evolve with a Leaf Stone."""
    rhydon = _pokemon("Rhydon", 112)
    choices = _choices(shop_obj, [rhydon], "leaf-stone")

    assert "e" not in choices[rhydon["individual_id"]]


def test_species_without_an_item_evolution_is_not_offered(shop_obj):
    """A Pokemon with no item evolution at all stays unflagged."""
    pikachu = _pokemon("pikachu", 25)
    choices = _choices(shop_obj, [pikachu], "protector")

    assert "e" not in choices[pikachu["individual_id"]]


@pytest.mark.parametrize("prevo_name,prevo_id,item_identifier", TRADE_ITEM_SPECIES)
def test_picker_agrees_with_canonical_helper(
    shop_obj, prevo_name, prevo_id, item_identifier
):
    """Both implementations must accept every trade-with-item evolution.

    Ankimon has no trading, so these species are evolved by applying the held item
    directly — ``check_evolution_by_item`` has always resolved them. Asserting the
    picker against the helper (rather than against a hard-coded list) is what makes
    a future one-sided edit fail here.
    """
    item_id = shop_obj.return_id_for_item_name(item_identifier)
    assert item_id, f"{item_identifier} is missing from items.csv"

    assert shop_obj.check_evolution_by_item(prevo_id, item_id), (
        f"canonical helper no longer resolves {prevo_name} + {item_identifier}"
    )

    mon = _pokemon(prevo_name, prevo_id)
    choices = _choices(shop_obj, [mon], item_identifier)

    assert choices[mon["individual_id"]].get("e") == 1, (
        f"web bag picker hides {prevo_name} when using {item_identifier}"
    )


# --------------------------------------------------------------------------- #
# Gender-gated item evolutions must agree with the canonical helper too.
#
# ``check_evolution_by_item`` learned the CSV ``gender_id`` gate (Gallade needs
# a male Kirlia, Froslass a female Snorunt), and ``Check_Evo_Item`` — which is
# what ``handle_use_with_target`` ultimately calls — now passes the selected
# Pokemon's gender. The picker's inline copy had to learn it as well: shop.js
# filters this list to ``e === 1``, so leaving it out means the bag offers the
# player exactly the Pokemon the use is about to refuse with "This Pokemon does
# not need this item."
# --------------------------------------------------------------------------- #
_DAWN_STONE = "dawn-stone"


def _gendered(name, pokedex_id, gender):
    mon = _pokemon(name, pokedex_id)
    mon["gender"] = gender
    return mon


def test_male_kirlia_is_offered_the_dawn_stone(shop_obj):
    mon = _gendered("Kirlia", 281, "M")
    choices = _choices(shop_obj, [mon], _DAWN_STONE)
    assert choices[mon["individual_id"]].get("e") == 1


def test_female_kirlia_is_not_offered_the_dawn_stone(shop_obj):
    # Gallade (475) is the only Dawn Stone target Kirlia has, and it is male-only.
    mon = _gendered("Kirlia", 281, "F")
    choices = _choices(shop_obj, [mon], _DAWN_STONE)
    assert "e" not in choices[mon["individual_id"]]


def test_female_snorunt_is_offered_the_dawn_stone(shop_obj):
    mon = _gendered("Snorunt", 361, "F")
    choices = _choices(shop_obj, [mon], _DAWN_STONE)
    assert choices[mon["individual_id"]].get("e") == 1


def test_male_snorunt_is_not_offered_the_dawn_stone(shop_obj):
    mon = _gendered("Snorunt", 361, "M")
    choices = _choices(shop_obj, [mon], _DAWN_STONE)
    assert "e" not in choices[mon["individual_id"]]


def test_missing_gender_keeps_the_historical_no_check_behavior(shop_obj):
    # Old saves without a stored gender must not lose access to the evolution.
    mon = _pokemon("Kirlia", 281)  # no "gender" key at all
    choices = _choices(shop_obj, [mon], _DAWN_STONE)
    assert choices[mon["individual_id"]].get("e") == 1


def test_genderless_value_degrades_to_no_check(shop_obj):
    for junk in ("Genderless", "N", "", "x"):
        mon = _gendered("Kirlia", 281, junk)
        choices = _choices(shop_obj, [mon], _DAWN_STONE)
        assert choices[mon["individual_id"]].get("e") == 1, junk


def test_ungated_item_evolution_ignores_gender(shop_obj):
    # A Thunder Stone on Pikachu carries no gender_id row; both sexes qualify.
    for gender in ("M", "F"):
        mon = _gendered("pikachu", 25, gender)
        choices = _choices(shop_obj, [mon], "thunder-stone")
        assert choices[mon["individual_id"]].get("e") == 1, gender


@pytest.mark.parametrize(
    "name,pokedex_id,gender,expected",
    [
        ("Kirlia", 281, "M", 475),
        ("Snorunt", 361, "F", 478),
        ("Kirlia", 281, "F", None),
        ("Snorunt", 361, "M", None),
    ],
)
def test_picker_agrees_with_canonical_helper_on_gender(
    shop_obj, name, pokedex_id, gender, expected
):
    """Pin the two implementations to each other on the gender branch as well."""
    item_id = shop_obj.return_id_for_item_name(_DAWN_STONE)
    assert item_id, "dawn-stone is missing from items.csv"

    helper = shop_obj.check_evolution_by_item(pokedex_id, item_id, gender=gender)
    assert helper == expected

    mon = _gendered(name, pokedex_id, gender)
    choices = _choices(shop_obj, [mon], _DAWN_STONE)
    flagged = choices[mon["individual_id"]].get("e") == 1

    assert flagged is (expected is not None), (
        f"picker and helper disagree for a {gender} {name}"
    )
