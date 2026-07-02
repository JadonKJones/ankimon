import os
import json
from aqt import QDialog, QVBoxLayout, QWebEngineView
from aqt.qt import Qt, QUrl, QFrame
from ..services import services
from ..functions import encounter_data


class Ankidex(QDialog):
    def __init__(self, addon_dir, ankimon_tracker):
        super().__init__()
        self.addon_dir = addon_dir
        self.ankimon_tracker = ankimon_tracker
        self.setWindowTitle("Ankidex")

        # Premium feel: larger default size
        # Disabled WA_TranslucentBackground to prevent heavy window-level repaint
        # flickering under Windows DWM when QWebEngineView re-composes or updates.
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowMinimizeButtonHint
        )
        self.resize(1200, 720)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.frame = QFrame()
        self.frame.setContentsMargins(0, 0, 0, 0)
        self.frame.setFrameStyle(QFrame.Shape.NoFrame)

        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)

        self.webview = QWebEngineView()
        # Enable remote debugging for development if needed
        # self.webview.page().settings().setAttribute(QWebEngineSettings.WebAttribute.DeveloperExtrasEnabled, True)

        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().setContentsMargins(0, 0, 0, 0)
        self.frame.layout().addWidget(self.webview)

        # Initial load
        self.webview.loadFinished.connect(self.update_ui_data)
        self.load_initial_html()

    def get_ankidex_data(self):
        """Fetches comprehensive collection data for Ankidex."""
        db = services.db
        settings = services.settings
        if not db:
            # Reload-safe: between a profile swap and the next populate() the
            # registry can be unpopulated (services.db is None). Serve an
            # empty-but-valid payload so the SPA still renders instead of
            # raising AttributeError on db.execute(...).
            return {
                "owned": [],
                "shinies": [],
                "seen": [],
                "encounterable": [],
                "prerequisites": {},
                "stats": {
                    "caughtCount": 0,
                    "releasedCount": 0,
                    "defeatedCount": 0,
                },
                "prefs": {
                    "viewMode": "grid",
                    "sortMode": "id-asc",
                    "spriteMode": "static",
                },
                "regional_data": {"boosts": {}, "forms": {}},
                "evolutionNote": "",
            }
        self.ankimon_tracker.get_ids_in_collection()

        # 1. Shiny Owned
        cursor = db.execute(
            "SELECT DISTINCT pokedex_id FROM captured_pokemon WHERE shiny = 1 AND pokedex_id IS NOT NULL"
        )
        shiny_owned_ids = [row[0] for row in cursor.fetchall()]

        # 1. Caught Status (Currently in collection OR released)
        # Currently owned
        cursor = db.execute(
            "SELECT pokedex_id FROM captured_pokemon WHERE pokedex_id IS NOT NULL"
        )
        caught_ids = {row[0] for row in cursor.fetchall()}

        # Released Pokémon (from history)
        cursor = db.execute(
            "SELECT DISTINCT json_extract(data, '$.id') FROM pokemon_history"
        )
        for row in cursor.fetchall():
            if row[0]:
                caught_ids.add(int(row[0]))

        # Explicitly recorded caught Pokémon (e.g. from evolutions or prior captures)
        if hasattr(db, "get_caught_ids"):
            try:
                caught_ids.update(db.get_caught_ids())
            except Exception:
                pass

        # 2. Seen Status (Encountered but not caught)
        seen_ids = set()
        if hasattr(db, "get_seen_ids"):
            seen_ids.update(db.get_seen_ids())
        else:
            seen_data = db.get_user_data("pokedex_seen", [])
            if isinstance(seen_data, list):
                seen_ids.update(set(seen_data))

        # Remove caught IDs from seen IDs to keep them strictly separate
        seen_ids = seen_ids - caught_ids

        # 3. Stats Summary
        total_caught_count = db.get_pokemon_count()
        cursor = db.execute(
            "SELECT SUM(CAST(json_extract(data, '$.pokemon_defeated') AS INTEGER)) FROM captured_pokemon"
        )
        defeated_caught = cursor.fetchone()[0] or 0

        cursor = db.execute(
            "SELECT COUNT(*), SUM(CAST(json_extract(data, '$.pokemon_defeated') AS INTEGER)) FROM pokemon_history"
        )
        row = cursor.fetchone()
        released_count = row[0] or 0
        defeated_released = row[1] or 0

        defeated_total = defeated_caught + defeated_released

        # 4. Encounterable IDs
        encounterable_ids = set()
        # Positive lists
        for list_name in [
            "LEGENDARY",
            "MYTHICAL",
            "BABY",
            "ULTRA",
            "NORMAL",
            "STARTERS",
            "MEGA",
            "GMAX",
        ]:
            l = getattr(encounter_data, list_name, [])
            encounterable_ids.update(l)

        # Explicit exclusions
        unavail = getattr(encounter_data, "UNAVAILABLE", [])
        for uid in unavail:
            if uid in encounterable_ids:
                encounterable_ids.remove(uid)

        # Add encounterable regional form IDs for the active region
        from ..functions.encounter_data import REGIONAL_FORMS

        active_region = settings.get("misc.active_region") if settings else None
        if active_region and active_region in REGIONAL_FORMS:
            encounterable_ids.update(REGIONAL_FORMS[active_region])

        # 5. Prerequisites
        prereqs = {}
        for k, v in encounter_data.PREREQUISITES.items():
            if isinstance(v, set):
                prereqs[str(k)] = list(v)
            elif isinstance(v, tuple) and len(v) == 2:
                # Handle ("OR", {1007, 1008})
                op, items = v
                prereqs[str(k)] = [op, list(items) if isinstance(items, set) else items]
            else:
                prereqs[str(k)] = v

        return {
            "owned": list(caught_ids),
            "shinies": shiny_owned_ids,
            "seen": list(seen_ids),
            "encounterable": list(encounterable_ids),
            "prerequisites": prereqs,
            "stats": {
                "caughtCount": total_caught_count,
                "releasedCount": released_count,
                "defeatedCount": defeated_total,
            },
            "prefs": {
                "viewMode": settings.get(
                    "ankidex.viewMode",
                    settings.get("pokedex_v2.viewMode", "grid"),
                )
                if settings
                else "grid",
                "sortMode": settings.get(
                    "ankidex.sortMode",
                    settings.get("pokedex_v2.sortMode", "id-asc"),
                )
                if settings
                else "id-asc",
                "spriteMode": settings.get(
                    "ankidex.spriteMode",
                    settings.get("pokedex_v2.spriteMode", "static"),
                )
                if settings
                else "static",
            },
            "regional_data": {
                "boosts": {
                    "kanto": [1],
                    "johto": [2],
                    "hoenn": [3],
                    "sinnoh": [4],
                    "unova": [5],
                    "kalos": [6],
                    "alola": [7],
                    "galar": [8],
                    "paldea": [9],
                    "hisui": [4, 8],
                },
                "forms": encounter_data.REGIONAL_FORM_REGION,
            },
            "evolutionNote": "Evolutions in Ankimon can trigger via Level, Friendship, Evolution Stones/Items, Time of Day, or knowing specific Moves.",
        }

    def load_initial_html(self):
        file_path = os.path.join(self.addon_dir, "ankidex", "ankidex.html").replace(
            "\\", "/"
        )
        url = QUrl.fromLocalFile(file_path)

        # Instead of URL query, we push data via JS
        self.webview.setUrl(url)

    def update_ui_data(self):
        """Pushes data to the frontend."""
        data = self.get_ankidex_data()
        data_js = json.dumps(data)

        js_code = f"if (window.initializeAnkidex) window.initializeAnkidex({data_js});"
        self.webview.page().runJavaScript(js_code)

    def show(self, *args):
        # Removed redundant update_ui_data() as it's called by showEvent()
        super().show()

    def showEvent(self, event):
        # Refresh data when window becomes visible
        self.update_ui_data()
        super().showEvent(event)

    def closeEvent(self, event):
        """Save UI preferences on close."""
        self.save_preferences()
        super().closeEvent(event)

    def save_preferences(self):
        def on_state_ready(state):
            if state and isinstance(state, dict) and services.settings:
                for key, val in state.items():
                    services.settings.set(f"ankidex.{key}", val)

        if self.webview:
            self.webview.page().runJavaScript(
                "if (window.getAnkidexState) window.getAnkidexState();", on_state_ready
            )
