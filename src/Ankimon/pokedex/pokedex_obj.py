import os
import json
from aqt import QDialog, QVBoxLayout, QWebEngineView, mw
from PyQt6.QtCore import QUrlQuery
from aqt.qt import Qt, QFile, QUrl, QFrame, QPushButton
from aqt.utils import showInfo


class Pokedex(QDialog):
    def __init__(self, addon_dir, ankimon_tracker):
        super().__init__()
        self.addon_dir = addon_dir
        self.ankimon_tracker = ankimon_tracker
        self.setWindowTitle("Pokedex - Ankimon")

        # Remove default background to make it transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1000, 850)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.frame = QFrame()
        self.frame.setContentsMargins(0, 0, 0, 0)
        self.frame.setFrameStyle(QFrame.Shape.NoFrame)

        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)

        self.webview = QWebEngineView()
        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().setContentsMargins(0, 0, 0, 0)
        self.frame.layout().addWidget(self.webview)

        # Initial load
        self.load_initial_html()

    def get_pokedex_stats(self):
        self.ankimon_tracker.get_ids_in_collection()
        owned_pokemon_ids = self.ankimon_tracker.owned_pokemon_ids
        db = mw.ankimon_db

        total_caught_count = db.get_pokemon_count()
        
        cursor = db.execute("SELECT SUM(CAST(json_extract(data, '$.pokemon_defeated') AS INTEGER)) FROM captured_pokemon")
        defeated_caught = cursor.fetchone()[0] or 0

        cursor = db.execute("SELECT DISTINCT pokedex_id FROM captured_pokemon WHERE shiny = 1 AND pokedex_id IS NOT NULL")
        shiny_pokemon_ids = [row[0] for row in cursor.fetchall()]

        cursor = db.execute("SELECT COUNT(*), SUM(CAST(json_extract(data, '$.pokemon_defeated') AS INTEGER)) FROM pokemon_history")
        row = cursor.fetchone()
        released_count = row[0] or 0
        defeated_released = row[1] or 0

        defeated_count = defeated_caught + defeated_released
        seen_total = total_caught_count + released_count + defeated_count
        
        return owned_pokemon_ids, shiny_pokemon_ids, seen_total

    def load_initial_html(self):
        owned, shinies, seen = self.get_pokedex_stats()
        
        file_path = os.path.join(self.addon_dir, "pokedex", "pokedex.html").replace("\\", "/")
        url = QUrl.fromLocalFile(file_path)

        query = QUrlQuery()
        query.addQueryItem("numbers", ",".join(map(str, owned)))
        query.addQueryItem("shinies", ",".join(map(str, shinies)))
        query.addQueryItem("seen", str(seen))
        url.setQuery(query)

        self.webview.setUrl(url)

    def update_ui_data(self):
        owned, shinies, seen = self.get_pokedex_stats()
        # Convert lists to JS array strings
        owned_js = json.dumps(list(owned))
        shinies_js = json.dumps(list(shinies))
        
        js_code = f"if (window.updateData) window.updateData({owned_js}, {shinies_js}, {seen});"
        self.webview.page().runJavaScript(js_code)

    def show(self, *args):
        # Update data before showing
        self.update_ui_data()
        super().show()

    def showEvent(self, event):
        # Refresh data when window becomes visible
        self.update_ui_data()
        super().showEvent(event)
