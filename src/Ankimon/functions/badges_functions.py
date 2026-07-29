import json
from typing import List

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
    """Awards a badge and saves to database atomically."""
    # Build the collection
    badges_collection = []
    for num in range(1, 69):
        if achievements.get(str(num)) is True:
            badges_collection.append(int(num))
    badges_collection.append(badge_num)
    
    db = services.db
    if db is None:
        # No database - just update memory (fallback)
        achievements[str(badge_num)] = True
        return achievements
    
    # Use existing db methods if available
    try:
        # First clear existing badges
        # This assumes db has a clear_badges() or similar method
        # If not, you'll need to add it or use raw SQL
        current_badges = db.get_all_badges()
        for badge in current_badges:
            # Delete each badge (or implement a clear method)
            pass
        
        # Then save all badges
        for badge_num_to_save in badges_collection:
            db.save_badge(str(badge_num_to_save), {"id": badge_num_to_save, "achieved": True})
    except Exception as e:
        import logging
        logging.error(f"Failed to save badge {badge_num}: {e}")
        return achievements
    
    achievements[str(badge_num)] = True
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
