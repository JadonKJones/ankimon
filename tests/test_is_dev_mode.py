"""Tier-1 contract for utils.is_dev_mode() (the developer-mode gate).

The helper is the single source of truth behind the developer-only menu entries
(Switch Account / Encounter Rate Simulator) and the reviewer test hotkey. It must
read misc.developer_mode through the settings seam and default to False (dev
tools hidden) when settings are missing or the read raises.

Qt-free: uses the real Ankimon.utils (conftest keeps it real) and swaps only
services.settings, so nothing Qt is constructed. The import is done inside the
fixture — after conftest's autouse restore has re-established the Ankimon package
with its __path__ (other test modules clobber that stub at their import time).
"""

import pytest


@pytest.fixture
def dev(monkeypatch):
    import Ankimon.utils as utils_mod
    from Ankimon.utils import is_dev_mode

    store = {}

    class _Settings:
        def get(self, key, default=None):
            return store.get(key, default)

    monkeypatch.setattr(utils_mod.services, "settings", _Settings())
    return is_dev_mode, store


def test_dev_mode_true_when_flag_enabled(dev):
    is_dev_mode, store = dev
    store["misc.developer_mode"] = True
    assert is_dev_mode() is True


def test_dev_mode_false_when_flag_disabled(dev):
    is_dev_mode, store = dev
    store["misc.developer_mode"] = False
    assert is_dev_mode() is False


def test_dev_mode_defaults_false_when_key_absent(dev):
    is_dev_mode, _ = dev
    # Nothing set — the helper must default to hidden dev tools.
    assert is_dev_mode() is False


def test_dev_mode_false_and_no_raise_when_settings_broken(monkeypatch):
    import Ankimon.utils as utils_mod
    from Ankimon.utils import is_dev_mode

    class _Broken:
        def get(self, *a, **k):
            raise RuntimeError("settings not ready")

    monkeypatch.setattr(utils_mod.services, "settings", _Broken())
    assert is_dev_mode() is False
