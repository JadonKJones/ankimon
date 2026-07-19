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


def migrate_credentials_from_db():
    """
    Migrate leaderboard credentials from the legacy database to the settings system.
    
    This function performs a one-time migration of username and API key from
    the old database storage to the new settings-based storage system. It
    checks if credentials exist in the database and whether they have already
    been migrated to settings to avoid overwriting existing settings data.
    
    The migration runs during Anki startup and ensures a smooth transition
    for users who previously configured leaderboard credentials using the
    legacy system.
    
    Returns:
        None: Migration status is logged to console; failures are caught
            and logged without interrupting the startup process.
    
    Note:
        - Function exits early if database or settings services are unavailable
        - Only migrates if database has credentials AND settings don't
        - After migration, the legacy database entries are cleared to prevent
          the old credentials from ever resurrecting over future edits
        - The leaderboard enabled/disabled state is preserved automatically
    """
    if services.db is None or services.settings is None:
        return
    
    try:
        # Check if we have credentials in database
        username = services.db.get_user_data("username")
        api_key = services.db.get_user_data("api_key")
        
        # Normalize None values to empty strings for comparison
        username = "" if username is None else str(username)
        api_key = "" if api_key is None else str(api_key)
        
        # Check if we have them in settings already
        settings_username = services.settings.get("leaderboard.username", "")
        settings_api_key = services.settings.get("leaderboard.api_key", "")
        
        # If db has credentials, migrate them to settings (only if not already set)
        if username and api_key:
            if not settings_username:
                services.settings.set("leaderboard.username", username)
            if not settings_api_key:
                services.settings.set("leaderboard.api_key", api_key)
            
            # Clear legacy database entries after successful migration
            # The condition is guaranteed true here because we checked username and api_key above
            services.db.set_user_data("username", "")
            services.db.set_user_data("api_key", "")
            print("Ankimon: Migrated and cleared legacy leaderboard credentials")
            
    except Exception as e:
        print(f"Ankimon: Error migrating leaderboard credentials: {e}")
