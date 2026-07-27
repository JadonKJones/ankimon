"""
Browser hooks for Badge 11 detection and tracking.

This module monitors browser operations that affect card suspension status and
tag modifications. It detects when cards are unsuspended or have their 'leech'
tag removed, which are prerequisites for earning Badge 11. The hooks trigger
the badge eligibility check after relevant operations, updating the candidate
set for future review-based badge awarding.

For efficiency, only operations that can affect Badge 11 eligibility trigger
the expensive check. The module supports reload safety by preventing duplicate
hook registrations during add-on reloads.
"""

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
# These operations change suspension status or tags, which may create candidates
# for Badge 11 (cards that were previously suspended or leeched)
_RELEVANT_OPERATIONS = {
    'suspend_cards',
    'unsuspend_cards',
    'add_tags',
    'remove_tags',
    'set_tags',
    'clear_tags',
}


def on_browser_will_remove_selected(browser):
    """
    Fallback hook called before cards are removed from the browser.
    
    This is a less efficient alternative to browser_operation_did_execute,
    triggered on every removal operation. It checks for Badge 11 candidates
    by scanning all cards for state changes.
    
    Args:
        browser: The browser instance performing the removal operation.
    """
    try:
        check_unleeched_cards(
            services.col if services.col is not None else mw.col,
            services.db,
            getattr(services, 'achievements', None),
        )
    except Exception:
        # Silently fail to preserve Anki functionality
        pass


def on_operation_did_execute(operation_name, *args, **kwargs):
    """
    Hook called after any browser operation executes.
    
    Only runs the badge eligibility check for operations that affect
    suspension status or tags (which impact Badge 11 eligibility).
    This provides a more efficient mechanism than checking on every
    selection or removal, as it triggers only on relevant state changes.
    
    Args:
        operation_name: The name of the executed operation (e.g., 'unsuspend_cards').
        *args, **kwargs: Additional arguments passed by the hook.
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
        # Silently fail to preserve Anki functionality
        pass


def register_browser_hooks():
    """
    Register browser hooks for Badge 11 detection.
    
    This function sets up the browser hooks needed to track card state changes
    that could make cards eligible for Badge 11. It prioritizes the more
    efficient browser_operation_did_execute hook when available, falling back
    to browser_will_remove_selected for older Anki versions.
    
    Implements reload safety (F31) by removing previously registered hooks
    before appending new ones. This prevents duplicate processing when the
    add-on is reloaded during the same Anki session.
    
    The hooks are stored in the services registry to survive module re-execution
    and enable proper cleanup during reloads.
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
