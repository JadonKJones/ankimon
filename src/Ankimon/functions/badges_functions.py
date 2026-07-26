import json
from typing import List, Set, Dict

from ..resources import badgebag_path
from ..services import services


def get_achieved_badges() -> List[int]:
    """Gets list of achieved badge IDs from the database."""
    db = services.db
    
    if db.is_migrated():
        badges = db.get_all_badges()
        # Filter for only achieved badges
        return [int(b["badge_id"]) for b in badges if b.get("achieved") in [True, 1, "true", "True"]]
    
    # Fallback to JSON for backwards compatibility
    try:
        with open(badgebag_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def populate_achievements_from_badges(achievements):
    """Populates achievements dict from stored badges."""
    try:
        for badge_num in get_achieved_badges():
            achievements[str(badge_num)] = True
    except Exception:
        pass
    return achievements


def check_for_badge(achievements, rec_badge_num):
    return achievements.get(str(rec_badge_num), False)


def save_badges(badges_collection: List[int]):
    """Saves badges collection to the database."""
    db = services.db
    
    # Clear existing badges and save new ones
    # Each badge is saved with its ID as the key
    for badge_num in badges_collection:
        db.save_badge(str(badge_num), {"id": badge_num, "achieved": True})


def receive_badge(badge_num, achievements):
    """Awards a badge and saves to database."""
    achievements[str(badge_num)] = True
    badges_collection = []
    for num in range(1, 69):
        if achievements.get(str(num)) is True:
            badges_collection.append(int(num))
    save_badges(badges_collection)
    return achievements


def handle_review_count_achievement(review_count, achievements):
    milestones = {
        100: 1,
        200: 2,
        300: 3,
        500: 4,
    }
    badge_to_award = milestones.get(review_count)
    if badge_to_award and not check_for_badge(achievements, badge_to_award):
        achievements = receive_badge(badge_to_award, achievements)

    return achievements

def get_pending_badge_11_candidates(db) -> Set[str]:
    """
    Retrieves stored note IDs that are candidates for Badge 11.
    These are cards that have been either:
    - Unsuspended (was suspended before)
    - Untagged (had 'leech' tag removed)
    But haven't been reviewed yet.
    """
    try:
        row = db.execute("SELECT value FROM metadata WHERE key = 'badge_11_candidates'").fetchone()
        if row and row[0]:
            return set(json.loads(row[0]))
    except Exception:
        pass
    return set()


def save_pending_badge_11_candidates(db, candidates: Set[str]):
    """Saves pending Badge 11 candidates to metadata."""
    _save_metadata(db, 'badge_11_candidates', list(candidates))


def _save_metadata(db, key: str, value):
    """Helper to upsert a key-value pair into the metadata table."""
    try:
        value_str = json.dumps(value) if not isinstance(value, str) else value
        conn = db._get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            (key, value_str),
        )
        conn.commit()
    except Exception:
        pass


def _get_metadata(db, key: str, default=None):
    """Helper to retrieve a value from the metadata table."""
    try:
        row = db.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
        if row and row[0]:
            return json.loads(row[0])
    except Exception:
        pass
    return default


def check_unleeched_cards(col, db, achievements):
    """
    Tracks cards that were previously leeches or suspended.
    
    Badge 11 is awarded when EITHER condition is met:
    1. A suspended card was unsuspended
    OR
    2. A card with the 'leech' tag had the tag removed
    
    AND the card is reviewed at least once after the change.
    
    Cards that meet condition 1 or 2 are stored as "candidates"
    until they are reviewed.
    """
    if not col or not db or not achievements:
        return

    # Skip if badge already awarded
    if check_for_badge(achievements, 11):
        return

    try:
        # Get current suspended card IDs
        suspended_cids = set()
        for cid in col.db.list("SELECT id FROM cards WHERE queue = -1"):
            suspended_cids.add(str(cid))

        # Get the note ID for each suspended card
        suspended_nids = set()
        for cid in suspended_cids:
            note_id = col.db.scalar("SELECT nid FROM cards WHERE id = ?", int(cid))
            if note_id:
                suspended_nids.add(str(note_id))

        # Get current cards with leech tag
        current_leech_nids = {str(nid) for nid in col.find_notes("tag:leech")}

        # Load stored tracking data
        stored_candidates = get_pending_badge_11_candidates(db)

        # --- Check for newly unsuspended cards (Condition 1) ---
        # We need to compare with previously stored suspended cards
        prev_suspended_nids = _get_metadata(db, 'prev_suspended_nids', set())

        # Find cards that WERE suspended but ARE NOT suspended anymore
        newly_unsuspended = prev_suspended_nids - suspended_nids

        # Add these as candidates (unless they already are)
        for nid in newly_unsuspended:
            # Verify the card still exists
            if col.db.scalar("SELECT id FROM notes WHERE id = ?", int(nid)):
                stored_candidates.add(str(nid))

        # Save current suspended IDs for next comparison
        _save_metadata(db, 'prev_suspended_nids', list(suspended_nids))

        # --- Check for newly untagged cards (Condition 2) ---
        # Load previously leeched cards from metadata
        prev_leech_nids = _get_metadata(db, 'prev_leech_nids', set())

        # Find cards that WERE leeched but ARE NOT leeched anymore
        newly_untagged = prev_leech_nids - current_leech_nids

        # Add these as candidates (unless they already are)
        for nid in newly_untagged:
            # Verify the card still exists
            if col.db.scalar("SELECT id FROM notes WHERE id = ?", int(nid)):
                stored_candidates.add(str(nid))

        # Save current leech IDs for next comparison
        _save_metadata(db, 'prev_leech_nids', list(current_leech_nids))

        # Save updated candidates
        save_pending_badge_11_candidates(db, stored_candidates)

        # Note: Badge 11 is NOT awarded here.
        # It will be awarded when the card is reviewed
        # (see check_and_award_badge_11_on_review below)

    except Exception:
        # Silent fail - don't break Anki functionality
        pass


def check_and_award_badge_11_on_review(col, db, achievements, card_id):
    """
    Called when a card is reviewed.
    If the card is in the candidates list, award Badge 11.
    """
    if not col or not db or not achievements:
        return

    if check_for_badge(achievements, 11):
        return

    try:
        # Get the note ID for this card
        note_id = col.db.scalar("SELECT nid FROM cards WHERE id = ?", card_id)
        if not note_id:
            return

        note_id_str = str(note_id)

        # Get pending candidates
        candidates = get_pending_badge_11_candidates(db)

        # If this card is a candidate, award the badge
        if note_id_str in candidates:
            # Remove from candidates (cleanup)
            candidates.remove(note_id_str)
            save_pending_badge_11_candidates(db, candidates)

            # Award Badge 11
            receive_badge(11, achievements)

    except Exception:
        pass


def update_leech_tracking_on_review(col, db, achievements, card_id):
    """
    Called after a card is reviewed to check if it qualifies for Badge 11.
    This should be called from answerCard_after in card_hooks.py.
    """
    check_and_award_badge_11_on_review(col, db, achievements, card_id)
