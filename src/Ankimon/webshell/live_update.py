"""
webshell/live_update.py — the screen-agnostic QWebChannel live-update bridge.

Stage A scaffolding, extracted from BRRRR_Experimental's ``singletons.notify_stats_changed``
pattern and lifted OUT of ``singletons.py`` (which repo rules require to stay
logic-free). This is the shared push channel: a single :class:`LiveUpdateBridge`
QObject is registered on every mounted web screen's :class:`QWebChannel`, and any
Python code that changes cash / xp / level / caught-count calls
``notify_stats_changed(...)`` to push the new values to whichever web screens are
live — no full page reload, no per-screen wiring.

The concrete web SCREENS that subscribe to this bridge (Items/Shop/Profile/Team/
Mobile …) are deferred Stage-B leaves; the bridge itself is in-base scaffolding so
those leaves can mount onto an existing push channel.

Signature verified against current PyQt6 docs (Context7): a ``pyqtSignal`` on a
QObject registered via ``QWebChannel.registerObject`` is published to the JS side,
which connects to it through ``qwebchannel.js`` over ``qt.webChannelTransport``.
"""

from __future__ import annotations

import json

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class LiveUpdateBridge(QObject):
    """Bridges Python stat changes to live web screens.

    JS usage (in a mounted screen, after the standard qwebchannel handshake)::

        new QWebChannel(qt.webChannelTransport, function (channel) {
            channel.objects.live.stats_changed.connect(function (payloadJson) {
                applyStats(JSON.parse(payloadJson));
            });
        });
    """

    # Emitted with a JSON string so the payload crosses the channel as one plain
    # argument (dicts/ints/strings all survive json round-tripping unambiguously).
    stats_changed = pyqtSignal(str)

    def notify_stats_changed(self, payload: dict | None = None) -> None:
        """Push ``payload`` (cash/xp/level/caught/…) to every subscribed screen.

        Safe to call from anywhere on the GUI thread; a no-arg call emits ``{}``,
        which screens treat as a generic 'refetch your state' nudge."""
        self.stats_changed.emit(json.dumps(payload or {}))

    @pyqtSlot()
    def request_refresh(self) -> None:
        """Invoked from JS when a freshly-loaded screen wants the current state.

        In the base this simply re-emits an empty nudge; a Stage-B screen/back-end
        overrides or connects richer producers. Present so the JS↔Python contract
        (an invokable slot exists) is stable for leaves to rely on."""
        self.notify_stats_changed({})
