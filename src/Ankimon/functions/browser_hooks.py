from aqt import gui_hooks, mw
from .badges_functions import check_unleeched_cards
from ..services import services

# Use a string type annotation to avoid runtime import of aqt.browser
# This prevents ModuleNotFoundError on Anki versions where aqt.browser doesn't exist
try:
    from aqt.browser import Browser  # noqa: F401
    HAS_BROWSER_IMPORT = True
except ImportError:
    HAS_BROWSER_IMPORT = False

# Reload safety (F31): track registered handlers on services to prevent duplicate registration
_HANDLER_RECORD = "_browser_hook_handlers"

# Operation types that can affect Badge 11 candidates
_RELEVANT_OPERATIONS = {
    'suspend_cards',
    'unsuspend_cards',
    'add_tags',
    'remove_tags',
    'set_tags',
    'clear_tags',
}


def on_browser_will_remove_selected(browser):
    """Called before cards are removed. Runs the badge check only on removal."""
    try:
        check_unleeched_cards(
            services.col if services.col is not None else mw.col,
            services.db,
            getattr(services, 'achievements', None),
        )
    except Exception:
        pass


def on_operation_did_execute(operation_name, *args, **kwargs):
    """
    Called after any browser operation executes.
    Only runs the expensive badge check for operations that affect 
    suspension status or tags (which impact Badge 11 eligibility).
    """
    # Skip if this operation doesn't affect Badge 11 candidates
    if operation_name not in _RELEVANT_OPERATIONS:
        return
    
    try:
        check_unleeched_cards(
            services.col if services.col is not None else mw.col,
            services.db,
            getattr(services, 'achievements', None),
        )
    except Exception:
        pass


def register_browser_hooks():
    """
    Register browser hooks for Badge 11 detection.
    Reload-safe: removes previously registered hooks before appending new ones.
    """
    # Remove previous registration first (F31 pattern)
    for hook, handler in getattr(services, _HANDLER_RECORD, ()):
        try:
            hook.remove(handler)
        except (ValueError, AttributeError):
            # Handler may already be removed - that's fine
            pass

    handlers = []

    # Use operation_did_execute for efficient Badge 11 checking
    # This only runs on actual state-changing operations, not on every selection
    if hasattr(gui_hooks, 'browser_operation_did_execute'):
        handlers.append((gui_hooks.browser_operation_did_execute, on_operation_did_execute))
    elif hasattr(gui_hooks, 'browser_will_remove_selected'):
        # Fallback: only check on removal if operation hook isn't available
        handlers.append((gui_hooks.browser_will_remove_selected, on_browser_will_remove_selected))

    # Register all handlers
    for hook, handler in handlers:
        hook.append(handler)
    
    # Store the handlers for reload safety
    setattr(services, _HANDLER_RECORD, handlers)
