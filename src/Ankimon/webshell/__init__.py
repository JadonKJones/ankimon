"""Web-shell host scaffolding (Stage A): the QWebEngine frame + live-update bridge.

Thin re-export surface; all logic lives in :mod:`.host` and :mod:`.live_update`.
Deferred Stage-B leaf screens mount into :class:`WebShellHost`.
"""

from .host import WebShellHost
from .live_update import LiveUpdateBridge

__all__ = ["WebShellHost", "LiveUpdateBridge"]
