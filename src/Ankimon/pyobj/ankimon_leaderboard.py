_HAVE_QT = False
try:
    from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
    from aqt.utils import showInfo
    from aqt import mw
    _HAVE_QT = True
except (ImportError, ModuleNotFoundError):
    class QDialog: pass
    def showInfo(*args, **kwargs): pass
    mw = None

from ..resources import user_path_credentials, mypokemon_path
from ..services import services
import requests

#ANKIMON_LEADERBOARD_API_URL = "https://ankimon.com/api/leaderboard"  # Replace with the actual API URL
ANKIMON_LEADERBOARD_API_URL = "https://leaderboard-api.ankimon.com/update_stats"  # Replace with the actual API URL

class ApiKeyDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Enter API Key and Username")
        self.setGeometry(100, 100, 300, 200)

        # Layout
        layout = QVBoxLayout()

        # Username input
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        # API Key input
        self.api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText("Paste your API key")
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)

        # Submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit)
        layout.addWidget(self.submit_button)

        # Set layout
        self.setLayout(layout)

    def submit(self):
        username = self.username_input.text()
        api_key = self.api_key_input.text()

        if username and api_key:
            credentials = {
                "username": username,
                "api_key": api_key
            }
            self.save_credentials(credentials)
            self.accept()  # Close the dialog if everything is entered
        else:
            showInfo("Both fields must be filled out.")

    def save_credentials(self, credentials):
        try:
            # Save the new credentials to the database
            for key, value in credentials.items():
                services.db.set_user_data(key, value)
            showInfo("Credentials saved successfully!")
        except Exception as e:
            showInfo(f"Error saving credentials: {e}")

def sync_data_to_leaderboard(data):
        if services.settings is None or services.db is None:
            return

        # First check if leaderboard is enabled in config
        if not services.settings.get("misc.leaderboard"):
            return

        try:
            # Load credentials from the database
            username = services.db.get_user_data("username")
            api_key = services.db.get_user_data("api_key")

            # Validate credentials
            if (not username or not api_key) and services.db.is_migrated():
                if services.logger:
                    services.logger.log("warning", "Missing credentials for Ankimon leaderboard.")
                return


            # Check if both username and api_key are available
            if username and api_key:
                request_data = {
                    "username": username,
                    "api_key": api_key,
                    "stats": data
                }

                def make_request():
                    try:
                        requests.post(
                            ANKIMON_LEADERBOARD_API_URL,
                            json=request_data,
                            timeout=10
                        )
                    except requests.exceptions.RequestException as e:
                        if services.logger:
                            services.logger.log("warning", f"Missing credentials for Ankimon leaderboard. Request exception: {e}")
                    except Exception as e:
                        if services.logger:
                            services.logger.log("warning", f"Missing credentials for Ankimon leaderboard. Exception: {e}")

                import threading
                thread = threading.Thread(target=make_request, daemon=True)
                thread.start()

        except Exception as e:
            if services.logger:
                services.logger.log("warning", f"Missing credentials for Ankimon leaderboard. Exception: {e}")



def show_api_key_dialog():
    dialog = ApiKeyDialog()  # Create the dialog instance
    dialog.exec()  # Show the dialog

