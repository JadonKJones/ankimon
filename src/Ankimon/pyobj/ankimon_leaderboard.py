import threading
import requests
from ..services import services

ANKIMON_LEADERBOARD_API_URL = "https://leaderboard-api.ankimon.com/update_stats"


def sync_data_to_leaderboard(data):
    """
    Synchronize player statistics with the Ankimon leaderboard server.
    
    This function retrieves leaderboard credentials from the settings system
    and sends a POST request to the leaderboard API with the provided stats.
    The network request is executed in a background thread to prevent UI
    freezing during network operations.
    
    Args:
        data (dict): A dictionary containing the player's statistics to be
            synchronized with the leaderboard. The structure should match
            what the leaderboard API expects.
    
    Returns:
        None: Results are logged to console; failures are handled silently
            with console output rather than user-facing dialogs.
    
    Note:
        - The function exits early if leaderboard sync is disabled in settings
        - Credentials are read from settings (not the legacy database)
        - Network timeouts are set to 10 seconds
        - All exceptions are caught and logged to console
    """
    
    # First check if leaderboard is enabled in config
    if services.settings is None or not services.settings.get("misc.leaderboard"):
        return

    try:
        # Get credentials from settings (NOT from database)
        username = services.settings.get("leaderboard.username", "")
        api_key = services.settings.get("leaderboard.api_key", "")

        # Validate credentials
        if not username or not api_key:
            # Silent fail - user can configure credentials in Settings > Leaderboard
            print("Ankimon: Leaderboard sync skipped - credentials missing in settings")
            return

        request_data = {
            "username": username,
            "api_key": api_key,
            "stats": data
        }

        def send_request():
            """
            Send the network request to the leaderboard API.
            
            This inner function executes the actual HTTP POST request and handles
            any network-related exceptions. It runs in a background thread to
            avoid blocking the main GUI thread.
            
            Returns:
                None: Results and errors are logged to console.
            """
            try:
                # Send POST request to leaderboard API
                response = requests.post(
                    ANKIMON_LEADERBOARD_API_URL,
                    json=request_data,
                    timeout=10  # Add timeout to prevent hanging
                )

                if response.status_code == 200:
                    print("Ankimon: Data synced to leaderboard successfully")
                else:
                    print(f"Ankimon: Failed to sync data - Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Ankimon: Leaderboard sync network error: {e}")
            except Exception as e:
                print(f"Ankimon: Unexpected leaderboard error: {e}")

        # Offload the network request to a background thread to prevent UI freezing
        threading.Thread(target=send_request, daemon=True).start()

    except Exception as e:
        print(f"Ankimon: Unexpected error preparing leaderboard sync: {e}")


def migrate_credentials_from_db() -> bool:
    """Atomically move legacy leaderboard credentials into Settings.

    Existing Settings values win per field. The database transaction stores any
    missing replacements and retires the corresponding legacy rows together, so
    a write failure cannot destroy the user's original credentials.
    """
    if services.db is None or services.settings is None:
        return False

    migrated = services.db.migrate_user_data_to_config(
        {
            "username": "leaderboard.username",
            "api_key": "leaderboard.api_key",
        }
    )
    if not migrated:
        return False

    # The DB transaction has already persisted these values. Update the live
    # Settings object in place without issuing a second, non-atomic write.
    services.settings.config.update(migrated)
    services.settings.compute_gui_config()
    print("Ankimon: Migrated and cleared legacy leaderboard credentials")
    return True
