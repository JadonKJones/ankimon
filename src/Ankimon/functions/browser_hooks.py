from aqt import gui_hooks, mw
from aqt.browser import Browser
from .badges_functions import check_unleeched_cards
from ..services import services


def on_browser_did_change_row(browser: Browser):
    """Called when the selected row changes in the browser."""
    try:
        check_unleeched_cards(
            services.col if services.col is not None else mw.col,
            services.db,
            getattr(services, 'achievements', None),
        )
    except Exception:
        pass


def on_browser_will_remove_selected(browser: Browser):
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
    # Hook available in Anki 2.1+
    if hasattr(gui_hooks, 'browser_did_change_row'):
        gui_hooks.browser_did_change_row.append(on_browser_did_change_row)
    
    # Hook available in newer Anki versions
    if hasattr(gui_hooks, 'browser_will_remove_selected'):
        gui_hooks.browser_will_remove_selected.append(on_browser_will_remove_selected)
    
    # Fallback for older versions: use browser_did_fetch (if available)
    if hasattr(gui_hooks, 'browser_did_fetch'):
        gui_hooks.browser_did_fetch.append(on_browser_did_change_row)
