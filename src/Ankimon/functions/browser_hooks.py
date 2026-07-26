from aqt import gui_hooks, mw
from .badges_functions import check_unleeched_cards
from ..services import services

try:
    from aqt.browser import Browser  # noqa: F401
    HAS_BROWSER_IMPORT = True
except ImportError:
    HAS_BROWSER_IMPORT = False


def on_browser_did_change_row(browser):
    """Called when the selected row changes in the browser."""
    try:
        check_unleeched_cards(
            services.col if services.col is not None else mw.col,
            services.db,
            getattr(services, 'achievements', None),
        )
    except Exception:
        pass


def on_browser_will_remove_selected(browser):
    """Called before cards are removed."""
    try:
        check_unleeched_cards(
            services.col if services.col is not None else mw.col,
            services.db,
            getattr(services, 'achievements', None),
        )
    except Exception:
        pass


def register_browser_hooks():
    """Register browser hooks for Badge 11 detection."""
    if hasattr(gui_hooks, 'browser_did_change_row'):
        gui_hooks.browser_did_change_row.append(on_browser_did_change_row)
    
    if hasattr(gui_hooks, 'browser_will_remove_selected'):
        gui_hooks.browser_will_remove_selected.append(on_browser_will_remove_selected)
