"""Tier-1 contract for the reviewer bottom-bar 'Cycle Team' button (F34).

reviewer_ui._linkHandler_wrap already routes pycmd('team_cycle') to the team
cycler and _bottomHTML_wrap computes a TeamCycleKey tooltip, but until a button
actually emits pycmd('team_cycle') that branch/tooltip are unreachable (team
cycling only worked via the '9' hotkey). This pins that the bottom-bar template
carries the click entry point, matching the Catch/Defeat buttons.

texts.py is pure string constants; load it directly so the test is independent
of the shared Ankimon package-stub state other test modules leave behind.
"""

import importlib.util
from pathlib import Path

_texts_path = Path(__file__).parent.parent / "src" / "Ankimon" / "texts.py"
_spec = importlib.util.spec_from_file_location("_ankimon_texts_under_test", _texts_path)
_texts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_texts)

_bottomHTML_template = _texts._bottomHTML_template


def test_team_cycle_button_wired_into_bottom_bar():
    assert "pycmd('team_cycle')" in _bottomHTML_template


def test_team_cycle_button_uses_the_tooltip_key():
    # The TeamCycleKey placeholder must be referenced so _bottomHTML_wrap's
    # computed tooltip value actually reaches the rendered button.
    assert "%(TeamCycleKey)s" in _bottomHTML_template


def test_catch_and_defeat_buttons_still_present():
    # Guard: adding the third button must not disturb the existing two.
    assert "pycmd('catch')" in _bottomHTML_template
    assert "pycmd('defeat')" in _bottomHTML_template
