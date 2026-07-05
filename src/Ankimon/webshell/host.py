"""
webshell/host.py — the QWebEngine web-shell HOST frame (Stage A scaffolding).

Extracted from BRRRR_Experimental's monolithic ``AnkimonItemsWeb`` (which hard-wired
all seven concrete screens + their bridges into one class). This is the FRAME ONLY:

  * a ``QStackedWidget`` container that holds mounted screens,
  * a nav dropdown that switches between them,
  * a shared :class:`LiveUpdateBridge` (the QWebChannel push channel),
  * a generic ``mount(screen_id, view, ...)`` API,

and DELIBERATELY zero concrete screens. The individual screens (Items/Shop/Bag/
Settings/Profile/Team/Ankidex/Mobile) are deferred Stage-B leaves that each call
``host.mount(...)`` to appear in this existing shell.

QWebChannel wiring uses the current PyQt6 API confirmed via Context7:
``QWebChannel(page); channel.registerObject(name, obj); page.setWebChannel(channel)``
— transport exposed to JS as ``qt.webChannelTransport`` (one channel per page).

Kept out of the addon's live boot path: nothing in the base imports this module, so
importing the addon never loads QtWebEngine. A Stage-B web-shell leaf wires it in.

NOTE (as shipped): the live Ankimon web shell is ``ankimon_items_web.shop_obj``'s
``AnkimonItemsWeb``, which grew its own inline nav-stack + live-update path
(``_live_refreshers`` / ``refresh_live_screen``) rather than mounting onto this
frame. So this scaffolding is currently unused by production code and is exercised
only by ``tests/test_scaffolding_smoke.py``. Consolidating the two mechanisms
(fold ``AnkimonItemsWeb`` onto ``WebShellHost``/``LiveUpdateBridge`` or retire this
frame) is a deferred web-shell-owning cleanup — don't assume this is the live path.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .live_update import LiveUpdateBridge


class WebShellHost(QDialog):
    """The reusable web-shell window: a nav dropdown over a stack of screens.

    Screens are added with :meth:`mount`. A screen may be any ``QWidget`` (e.g. a
    trivial placeholder) or a ``QWebEngineView``; when it is a web view, its page is
    wired to a fresh ``QWebChannel`` exposing the shared live-update bridge plus any
    screen-specific bridge objects the caller supplies.
    """

    def __init__(
        self,
        parent=None,
        *,
        live_bridge: Optional[LiveUpdateBridge] = None,
        title: str = "Ankimon",
    ):
        super().__init__(parent)
        self.setWindowTitle(title)

        self._live_bridge = (
            live_bridge if live_bridge is not None else LiveUpdateBridge()
        )
        self._screens: dict[str, tuple[int, QWidget]] = {}
        self._channels: dict[str, object] = {}  # keep QWebChannel refs alive

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._nav = QComboBox()
        self._nav.currentIndexChanged.connect(self._on_nav_changed)
        layout.addWidget(self._nav)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

    # --- public API ---------------------------------------------------------

    @property
    def live_bridge(self) -> LiveUpdateBridge:
        """The shared push channel; ``notify_stats_changed`` fans out to screens."""
        return self._live_bridge

    def mount(
        self,
        screen_id: str,
        view: QWidget,
        *,
        label: Optional[str] = None,
        bridges: Optional[dict] = None,
    ) -> int:
        """Add ``view`` as a screen and return its stack index.

        ``bridges`` maps extra QWebChannel object names to QObjects (screen-specific
        back-ends). The shared live-update bridge is always registered as ``live``.
        Wiring a QWebChannel is only attempted for ``QWebEngineView`` screens."""
        if screen_id in self._screens:
            raise ValueError(f"screen_id {screen_id!r} is already mounted")

        self._wire_web_channel(screen_id, view, bridges)

        index = self._stack.addWidget(view)
        self._nav.addItem(label or screen_id, screen_id)
        self._screens[screen_id] = (index, view)
        return index

    def show_screen(self, screen_id: str) -> None:
        """Switch the visible screen (and keep the nav dropdown in sync)."""
        index, _ = self._screens[screen_id]
        self._stack.setCurrentIndex(index)
        if self._nav.currentIndex() != index:
            self._nav.setCurrentIndex(index)

    def screen_ids(self) -> list[str]:
        return list(self._screens.keys())

    def notify_stats_changed(self, payload: Optional[dict] = None) -> None:
        """Convenience: push a stat change to every mounted web screen."""
        self._live_bridge.notify_stats_changed(payload)

    # --- internals ----------------------------------------------------------

    def _wire_web_channel(
        self, screen_id: str, view: QWidget, bridges: Optional[dict]
    ) -> None:
        """If ``view`` is a QWebEngineView, attach a channel exposing the bridges.

        Imported lazily so the class is usable with plain-``QWidget`` stub screens
        even in an environment without QtWebEngine."""
        try:
            from PyQt6.QtWebChannel import QWebChannel
            from PyQt6.QtWebEngineWidgets import QWebEngineView
        except Exception:
            return
        if not isinstance(view, QWebEngineView):
            return

        page = view.page()
        channel = QWebChannel(page)
        channel.registerObject("live", self._live_bridge)
        for name, obj in (bridges or {}).items():
            channel.registerObject(name, obj)
        page.setWebChannel(channel)
        self._channels[screen_id] = channel  # prevent GC while the screen lives

    def _on_nav_changed(self, index: int) -> None:
        if 0 <= index < self._stack.count():
            self._stack.setCurrentIndex(index)
