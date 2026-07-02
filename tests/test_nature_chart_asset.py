"""Tier-1 asset checks for the nature chart (inventory row F43).

``addon_files/nature_chart.html`` is an exp-only static asset consumed by
``gui_entities.NatureTableWidget.show_nature_chart`` through the
``resources.nature_chart_html_path`` constant (landed by F38). These tests are
Qt-free so they run in the aqt-free Tier-1 environment: they pin that the
shipped asset exists, that the resources constant points at it, and that the
chart covers all 25 natures.
"""

from pathlib import Path

# All 25 official natures; the 5 neutral ones are rendered as "--- (Neutral) ---".
ALL_NATURES = [
    "Adamant",
    "Bashful",
    "Bold",
    "Brave",
    "Calm",
    "Careful",
    "Docile",
    "Gentle",
    "Hardy",
    "Hasty",
    "Impish",
    "Jolly",
    "Lax",
    "Lonely",
    "Mild",
    "Modest",
    "Naive",
    "Naughty",
    "Quiet",
    "Quirky",
    "Rash",
    "Relaxed",
    "Sassy",
    "Serious",
    "Timid",
]
NEUTRAL_NATURES = {"Bashful", "Docile", "Hardy", "Quirky", "Serious"}


def _asset_path() -> Path:
    return (
        Path(__file__).parent.parent
        / "src"
        / "Ankimon"
        / "addon_files"
        / "nature_chart.html"
    )


def test_nature_chart_asset_exists():
    assert _asset_path().is_file()


def test_resources_constant_points_at_the_asset():
    from Ankimon import resources

    assert Path(resources.nature_chart_html_path) == _asset_path()
    assert Path(resources.nature_chart_html_path).is_file()


def test_nature_chart_lists_all_25_natures():
    html = _asset_path().read_text(encoding="utf-8")
    for nature in ALL_NATURES:
        assert f"<b>{nature}</b>" in html, f"missing nature row: {nature}"
    # The 5 neutral natures span both stat columns instead of naming stats.
    assert html.count("--- (Neutral) ---") == len(NEUTRAL_NATURES)


def test_nature_chart_names_the_boosted_and_hindered_stat_columns():
    html = _asset_path().read_text(encoding="utf-8")
    assert "Boosted Stat (+10%)" in html
    assert "Hindered Stat (-10%)" in html
