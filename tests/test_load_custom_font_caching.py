"""load_custom_font() used to call QFontDatabase.addApplicationFont() on
every single call — with no caching, a brand-new duplicate font entry got
registered every time, even for a file already registered (confirmed live:
20 uncached calls returned 20 distinct font ids — Qt's own
QFontDatabase.families() never shows the duplication, so that can't be used
to detect it; only the call count / returned ids can). Since this function
runs on every battle-scene redraw, a real play session could pile up
thousands of duplicate registrations, eventually bloating Qt's font database
until fontconfig's internal font-set sort crashed with a stack overflow
(observed as a SIGSEGV inside FcFontSetSort). Fixed by registering each font
file exactly once.
"""

import pytest


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


def test_repeated_calls_register_the_font_file_only_once(qapp, monkeypatch):
    import Ankimon.utils as ankimon_utils
    from PyQt6.QtGui import QFontDatabase

    calls = []
    real_add = QFontDatabase.addApplicationFont

    def spy_add(path):
        calls.append(path)
        return real_add(path)

    monkeypatch.setattr(QFontDatabase, "addApplicationFont", staticmethod(spy_add))
    # The cache is a module-level set, shared across the whole process —
    # reset it so an earlier test's registration doesn't hide a regression.
    monkeypatch.setattr(ankimon_utils, "_registered_fonts", set())

    for _ in range(20):
        font = ankimon_utils.load_custom_font(20, 0)
        assert font is not None

    assert len(calls) == 1, (
        f"expected exactly 1 addApplicationFont() call across 20 load_custom_font() "
        f"calls for the same font file, got {len(calls)}"
    )


def test_different_language_fonts_each_register_once(qapp, monkeypatch):
    """language=1 (Western) and language=0 (default) use different font
    files — both should still register at most once each, not per-call."""
    import Ankimon.utils as ankimon_utils
    from PyQt6.QtGui import QFontDatabase

    calls = []
    real_add = QFontDatabase.addApplicationFont

    def spy_add(path):
        calls.append(path)
        return real_add(path)

    monkeypatch.setattr(QFontDatabase, "addApplicationFont", staticmethod(spy_add))
    monkeypatch.setattr(ankimon_utils, "_registered_fonts", set())

    for _ in range(10):
        ankimon_utils.load_custom_font(20, 0)
        ankimon_utils.load_custom_font(20, 1)

    # At most one registration per distinct underlying font file.
    assert len(calls) == len(set(calls))
