"""
boot_async.py — the async QueryOp startup-boot helper (Stage A scaffolding).

Re-fit from BRRRR_Experimental's ``start_asynchronous_startup`` pattern. It offloads
the heavy boot work (backup validation, folder/asset checks, first-encounter
generation) onto a background thread via Anki's ``QueryOp`` and marshals the result
back to a GUI-thread callback — so opening Anki never freezes on Ankimon's boot.

This is the reusable PRIMITIVE only. Wiring the addon's real boot sequence through
it (splitting ``__init__``/``startup`` into background + UI callbacks) is left to a
Stage-B step so main's proven synchronous boot is not disturbed in Stage A.

``QueryOp`` is Anki's own API; its contract (``op(col)`` runs off-thread, ``success``
runs on the GUI thread with the op's return value) is mirrored by the harness's
synchronous ``QueryOp`` fake, which lets a test drive this helper deterministically.
"""

from __future__ import annotations

from typing import Callable, Optional


def run_startup_boot(
    background_op: Callable[[], object],
    on_complete: Callable[[object], None],
    *,
    parent=None,
    query_op_cls=None,
    progress_label: Optional[str] = None,
):
    """Run ``background_op()`` off the GUI thread, then ``on_complete(result)`` on it.

    Parameters
    ----------
    background_op : no-arg callable executed on the background thread.
    on_complete   : callable receiving ``background_op``'s return value, on the GUI thread.
    parent        : the QueryOp parent (defaults to ``aqt.mw`` in production).
    query_op_cls  : the QueryOp class (defaults to ``aqt.operations.QueryOp``); inject a
                    synchronous fake in tests for determinism.
    progress_label: optional label shown in Anki's progress dialog.

    Returns whatever ``run_in_background()`` returns (``None`` in real Anki; the op
    result with the synchronous fake).
    """
    if query_op_cls is None:
        from aqt.operations import QueryOp as query_op_cls  # noqa: N806
    if parent is None:
        from aqt import mw as parent

    op = query_op_cls(
        parent=parent, op=lambda col: background_op(), success=on_complete
    )
    # with_progress is optional/chainable in both real aqt and the harness fake.
    try:
        op = op.with_progress(progress_label) if progress_label else op.with_progress()
    except Exception:
        pass
    return op.run_in_background()
