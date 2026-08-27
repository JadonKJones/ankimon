"""A QWidget must never be constructed without a QApplication.

Qt answers that by calling ``abort()`` — the process dies with SIGABRT and
"QWidget: Must construct a QApplication before a QWidget". That is not a Python
exception, so the ``try/except Exception`` wrappers the add-on uses as its
"headless is fine" guard cannot contain it. Those wrappers were written against
"PyQt6 is not installed"; they do not cover "PyQt6 is installed but nothing has
created an application", which is exactly the shape of a dev box running the
Tier-1 agent harness (AGENTS.md makes `python3 harness/check.py` the standard
pre-review check, and CI runs it on every PR).

`ShowInfoLogger.log_and_showinfo` is on the review path — `save_main_pokemon_
progress` calls it whenever a level-up move has to be replaced — so this took
out any headless play-through that got that far.
"""

import importlib
import sys
from types import SimpleNamespace

import pytest


@pytest.fixture
def logger_env(tmp_path):
    """A freshly imported ``InfoLogger`` sitting on a genuine ``PyQt6.QtWidgets``.

    Both halves matter, and both are about test isolation rather than the code
    under test: earlier suite modules replace ``PyQt6`` with a ``MagicMock``
    (so ``QApplication.instance()`` answers with a mock instead of ``None``,
    and the dialog class is a mock too) and may leave a stale ``InfoLogger``
    bound to it. Without this the tests silently pass or silently miss.
    """
    saved = {
        name: mod for name, mod in sys.modules.items() if name.split(".")[0] == "PyQt6"
    }
    for name in saved:
        del sys.modules[name]
    sys.modules.pop("Ankimon.pyobj.InfoLogger", None)
    try:
        widgets = importlib.import_module("PyQt6.QtWidgets")
        module = importlib.import_module("Ankimon.pyobj.InfoLogger")
    except Exception as e:  # pragma: no cover - environment guard
        sys.modules.update(saved)
        pytest.skip(f"headless Qt guard env not importable: {e}")

    logger = module.ShowInfoLogger(
        name=f"test-{tmp_path.name}", log_filename=str(tmp_path / "app.log")
    )
    # `module.events` is the bus the logger actually emits on — importing
    # `Ankimon.events` separately can hand back a different (mocked) object.
    yield SimpleNamespace(
        module=module, logger=logger, widgets=widgets, events=module.events
    )
    sys.modules.update(saved)


def test_log_and_showinfo_builds_no_dialog_without_an_application(
    monkeypatch, logger_env
):
    def _explode(*args, **kwargs):
        raise AssertionError("constructed a QMessageBox with no QApplication")

    monkeypatch.setattr(logger_env.widgets, "QMessageBox", _explode)
    monkeypatch.setattr(
        logger_env.widgets.QApplication, "instance", staticmethod(lambda: None)
    )

    # Must not raise, and must still record the message.
    logger_env.logger.log_and_showinfo("info", "hello from a headless run")


def test_log_and_showinfo_still_records_the_event_when_it_skips_the_dialog(
    monkeypatch, logger_env
):
    monkeypatch.setattr(
        logger_env.widgets.QApplication, "instance", staticmethod(lambda: None)
    )

    seen = []
    logger_env.events.enable(sink=seen.append)
    try:
        logger_env.logger.log_and_showinfo("warning", "still observable")
    finally:
        logger_env.events.disable()

    assert any(
        ev.get("type") == "log" and ev.get("message") == "still observable"
        for ev in seen
    ), "the structured event is the headless substitute for the popup"


def test_log_and_showinfo_shows_the_dialog_when_an_application_exists(
    monkeypatch, logger_env
):
    built = []

    class _MessageBox:
        Icon = logger_env.widgets.QMessageBox.Icon

        def setWindowTitle(self, *a):
            pass

        def setText(self, *a):
            pass

        def setIcon(self, *a):
            pass

        def exec(self):
            built.append(1)

    class _App:
        # pytest-qt's teardown hook calls processEvents() on the instance.
        def processEvents(self, *args, **kwargs):
            pass

    fake_app = _App()
    monkeypatch.setattr(logger_env.widgets, "QMessageBox", _MessageBox)
    monkeypatch.setattr(
        logger_env.widgets.QApplication, "instance", staticmethod(lambda: fake_app)
    )

    logger_env.logger.log_and_showinfo("info", "gui mode")
    assert built == [1], "the guard swallowed a legitimate GUI-mode popup"
