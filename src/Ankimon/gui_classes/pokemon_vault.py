import math
import json
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any

from aqt import mw
from aqt.qt import (
    Qt,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QScrollArea,
    QFrame,
    QSplitter,
    QPixmap,
    QIcon,
    QTimer,
    QColor,
    QPropertyAnimation,
    QEasingCurve,
    QGraphicsDropShadowEffect,
    QTabWidget,
    QMenu,
    QSize,
    QProgressBar,
    QWidget,
)

from PyQt6.QtCore import pyqtSignal

from ..pyobj.pokemon_obj import PokemonObject
from ..pyobj.reviewer_obj import Reviewer_Manager
from ..pyobj.test_window import TestWindow
from ..pyobj.translator import Translator
from ..pyobj.settings import Settings
from ..pyobj.InfoLogger import ShowInfoLogger
from ..functions.sprite_functions import get_sprite_path
from ..utils import load_custom_font, is_alive
from ..resources import addon_dir
from ..business import calculate_cp_from_dict

# --- CONSTANTS ---

TYPE_COLORS: Dict[str, Tuple[int, int, int]] = {
    "Normal":   (168, 168, 120),
    "Fire":     (240, 128,  48),
    "Water":    ( 48, 144, 240),
    "Electric": (248, 208,  48),
    "Grass":    (120, 200,  80),
    "Ice":      (152, 216, 216),
    "Fighting": (192,  48,  40),
    "Poison":   (160,  64, 160),
    "Ground":   (224, 192,  80),
    "Flying":   (168, 144, 240),
    "Psychic":  (248,  88, 136),
    "Bug":      (168, 184,  32),
    "Rock":     (184, 160,  56),
    "Ghost":    (112,  88, 152),
    "Dragon":   (112,  56, 248),
    "Dark":     (112,  88,  72),
    "Steel":    (184, 184, 208),
    "Fairy":    (240, 182, 188),
}

STAT_COLORS = {
    "hp":  "#ff6b6b",
    "atk": "#ffa94d",
    "def": "#ffd43b",
    "spa": "#74c0fc",
    "spd": "#a9e34b",
    "spe": "#da77f2",
}

@dataclass(frozen=True)
class VaultFilterState:
    search: str = ""
    type_filter: str = "All"
    gen_filter: str = "All"
    tier_filter: str = "All"
    shiny: bool = False
    favorites: bool = False
    holding_item: bool = False
    sort_key: str = "Date Caught"
    sort_asc: bool = False
    db_name: str = ""

# --- WIDGETS ---

class VaultSlotWidget(QFrame):
    clicked = pyqtSignal(object)  # Emits the pokemon object
    right_clicked = pyqtSignal(object, object) # Emits (pokemon, pos)

    def __init__(self, pokemon: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.pokemon = pokemon
        self.setFixedSize(80, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("vaultSlot")
        self.setProperty("empty", "true" if pokemon is None else "false")
        self.setProperty("selected", "false")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.sprite_label = QLabel(self)
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.sprite_label)
        
        # Badges (Labels with absolute positioning)
        self.fav_badge = QLabel(self)
        self.fav_badge.setFixedSize(16, 16)
        self.fav_badge.hide()
        
        self.shiny_badge = QLabel(self)
        self.shiny_badge.setFixedSize(16, 16)
        self.shiny_badge.hide()
        
        self.item_badge = QLabel(self)
        self.item_badge.setFixedSize(8, 8)
        self.item_badge.hide()

        self._setup_hover_animation()
        self.refresh()

    def _setup_hover_animation(self):
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(4)
        self._shadow.setColor(QColor(88, 166, 255, 60))
        self._shadow.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow)

        self._anim = QPropertyAnimation(self._shadow, b"blurRadius")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        if self.pokemon:
            self._anim.setStartValue(self._shadow.blurRadius())
            self._anim.setEndValue(20)
            self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.pokemon:
            self._anim.setStartValue(self._shadow.blurRadius())
            self._anim.setEndValue(4)
            self._anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.pokemon:
            if event.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit(self.pokemon)
            elif event.button() == Qt.MouseButton.RightButton:
                self.right_clicked.emit(self.pokemon, event.globalPos())
        super().mousePressEvent(event)

    def refresh(self):
        if not self.pokemon:
            self.sprite_label.setPixmap(QPixmap())
            self.fav_badge.hide()
            self.shiny_badge.hide()
            self.item_badge.hide()
            self.setProperty("empty", "true")
            return

        self.setProperty("empty", "false")
        
        # Favorite badge
        if self.pokemon.get("is_favorite"):
            self.fav_badge.setText("★")
            self.fav_badge.setStyleSheet("color: #ffde00; font-size: 14px;")
            self.fav_badge.move(4, 4)
            self.fav_badge.show()
        else:
            self.fav_badge.hide()

        # Shiny badge
        if self.pokemon.get("shiny"):
            self.shiny_badge.setText("✦")
            self.shiny_badge.setStyleSheet("color: #ffde00; font-size: 14px;")
            self.shiny_badge.move(60, 4)
            self.shiny_badge.show()
        else:
            self.shiny_badge.hide()

        # Item badge
        if self.pokemon.get("held_item"):
            self.item_badge.setStyleSheet("background: white; border-radius: 4px;")
            self.item_badge.move(68, 68)
            self.item_badge.show()
        else:
            self.item_badge.hide()

    def set_sprite(self, pixmap: QPixmap):
        self.sprite_label.setPixmap(pixmap)

    def set_selected(self, selected: bool):
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class VaultFilterRail(QScrollArea):
    filters_changed = pyqtSignal(object) # Emits VaultFilterState

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFixedWidth(220)
        self.setObjectName("vaultFilterRail")
        
        container = QWidget()
        self.layout = QVBoxLayout(container)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(12, 12, 12, 12)
        
        # Search
        self.layout.addWidget(self._create_header("Search"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search name or nickname...")
        self.search_edit.setClearButtonEnabled(True)
        self.layout.addWidget(self.search_edit)
        
        # Type
        self.layout.addWidget(self._create_header("Type"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All"] + list(TYPE_COLORS.keys()))
        self.layout.addWidget(self.type_combo)
        
        # Generation
        self.layout.addWidget(self._create_header("Generation"))
        self.gen_combo = QComboBox()
        self.gen_combo.addItem("All")
        for i in range(1, 10):
            self.gen_combo.addItem(f"Gen {i}")
        self.layout.addWidget(self.gen_combo)
        
        # Tier
        self.layout.addWidget(self._create_header("Tier"))
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["All", "Normal", "Legendary", "Mythical", "Mega", "Gmax", "Fossil", "Baby"])
        self.layout.addWidget(self.tier_combo)
        
        # Attributes
        self.layout.addWidget(self._create_header("Attributes"))
        self.shiny_check = QCheckBox("Shiny only")
        self.fav_check = QCheckBox("Favorites")
        self.item_check = QCheckBox("Holding Item")
        self.layout.addWidget(self.shiny_check)
        self.layout.addWidget(self.fav_check)
        self.layout.addWidget(self.item_check)
        
        # Sort
        self.layout.addWidget(self._create_header("Sort By"))
        self.sort_key_combo = QComboBox()
        self.sort_key_combo.addItems([
            "Date Caught", "Pokédex #", "Name", "Level", "CP", 
            "IV Total", "EV Total", "HP", "ATK", "DEF", "Sp.ATK", "Sp.DEF", "SPE"
        ])
        self.layout.addWidget(self.sort_key_combo)
        
        self.sort_dir_btn = QPushButton("▼ Descending")
        self.sort_dir_btn.setCheckable(True)
        self.sort_dir_btn.setChecked(True)
        self.sort_dir_btn.clicked.connect(self._on_sort_dir_toggled)
        self.layout.addWidget(self.sort_dir_btn)
        
        self.layout.addStretch()
        
        self.clear_btn = QPushButton("Clear Filters")
        self.clear_btn.setObjectName("clearFiltersBtn")
        self.clear_btn.clicked.connect(self.clear_filters)
        self.layout.addWidget(self.clear_btn)
        
        self.setWidget(container)
        
        # Signals
        self.search_edit.textChanged.connect(self._on_filter_changed)
        self.type_combo.currentIndexChanged.connect(self._on_filter_changed)
        self.gen_combo.currentIndexChanged.connect(self._on_filter_changed)
        self.tier_combo.currentIndexChanged.connect(self._on_filter_changed)
        self.shiny_check.stateChanged.connect(self._on_filter_changed)
        self.fav_check.stateChanged.connect(self._on_filter_changed)
        self.item_check.stateChanged.connect(self._on_filter_changed)
        self.sort_key_combo.currentIndexChanged.connect(self._on_filter_changed)
        
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_filters)

    def _create_header(self, text: str):
        lbl = QLabel(text)
        lbl.setObjectName("sectionHeader")
        return lbl

    def _on_sort_dir_toggled(self):
        txt = "▼ Descending" if self.sort_dir_btn.isChecked() else "▲ Ascending"
        self.sort_dir_btn.setText(txt)
        self._on_filter_changed()

    def get_state(self) -> VaultFilterState:
        return VaultFilterState(
            search=self.search_edit.text(),
            type_filter=self.type_combo.currentText(),
            gen_filter=self.gen_combo.currentText(),
            tier_filter=self.tier_combo.currentText(),
            shiny=self.shiny_check.isChecked(),
            favorites=self.fav_check.isChecked(),
            holding_item=self.item_check.isChecked(),
            sort_key=self.sort_key_combo.currentText(),
            sort_asc=not self.sort_dir_btn.isChecked()
        )

    def _on_filter_changed(self):
        self._debounce_timer.start(300)

    def _emit_filters(self):
        state = VaultFilterState(
            search=self.search_edit.text(),
            type_filter=self.type_combo.currentText(),
            gen_filter=self.gen_combo.currentText(),
            tier_filter=self.tier_combo.currentText(),
            shiny=self.shiny_check.isChecked(),
            favorites=self.fav_check.isChecked(),
            holding_item=self.item_check.isChecked(),
            sort_key=self.sort_key_combo.currentText(),
            sort_asc=not self.sort_dir_btn.isChecked()
        )
        self.filters_changed.emit(state)

    def clear_filters(self):
        self.search_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.gen_combo.setCurrentIndex(0)
        self.tier_combo.setCurrentIndex(0)
        self.shiny_check.setChecked(False)
        self.fav_check.setChecked(False)
        self.item_check.setChecked(False)
        self.sort_key_combo.setCurrentIndex(0)
        self.sort_dir_btn.setChecked(True)
        self.sort_dir_btn.setText("▼ Descending")
        self._emit_filters()


class VaultInspectorPanel(QWidget):
    def __init__(self, reviewer_obj, parent=None):
        super().__init__(parent)
        self.reviewer_obj = reviewer_obj
        self.pokemon = None
        self.setMinimumWidth(360)
        self.setObjectName("vaultInspectorPanel")
        
        # Main layout for the panel
        self.panel_layout = QVBoxLayout(self)
        self.panel_layout.setContentsMargins(0, 0, 0, 0)
        self.panel_layout.setSpacing(0)
        
        # Scroll Area to handle vertical overflow
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setObjectName("inspectorScrollArea")
        
        self.content_widget = QWidget()
        self.content_widget.setObjectName("inspectorContent")
        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setContentsMargins(16, 12, 16, 12)
        self.layout.setSpacing(10)
        
        # Header block
        self.sprite_label = QLabel()
        self.sprite_label.setFixedSize(100, 100)
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.sprite_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        name_fav_layout = QHBoxLayout()
        self.name_label = QLabel("Select a Pokémon")
        self.name_label.setObjectName("inspectorName")
        self.fav_btn = QPushButton("☆")
        self.fav_btn.setFixedSize(32, 32)
        self.fav_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        name_fav_layout.addWidget(self.name_label)
        name_fav_layout.addStretch()
        name_fav_layout.addWidget(self.fav_btn)
        self.layout.addLayout(name_fav_layout)
        
        self.type_badges_layout = QHBoxLayout()
        self.type_badges_layout.setSpacing(6)
        self.layout.addLayout(self.type_badges_layout)
        
        # Progress block
        progress_layout = QHBoxLayout()
        self.lvl_label = QLabel("Lv. --")
        self.xp_label = QLabel("--- / ---")
        self.xp_label.setObjectName("inspectorSubtitle")
        progress_layout.addWidget(self.lvl_label)
        progress_layout.addStretch()
        progress_layout.addWidget(self.xp_label)
        self.layout.addLayout(progress_layout)
        
        self.xp_bar = QProgressBar()
        self.xp_bar.setObjectName("xpBar")
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setFixedHeight(6)
        self.layout.addWidget(self.xp_bar)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("inspectorTabs")
        
        # Tab 1: Stats
        self.stats_tab = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_tab)
        self.stats_layout.setSpacing(2)
        self.tabs.addTab(self.stats_tab, "Stats")
        
        # Tab 2: IVs / EVs
        self.iv_ev_tab = QWidget()
        self.iv_ev_layout = QGridLayout(self.iv_ev_tab)
        self.tabs.addTab(self.iv_ev_tab, "IVs / EVs")
        
        self.layout.addWidget(self.tabs)
        
        # Moves
        self.layout.addWidget(QLabel("Moves"))
        self.moves_grid = QGridLayout()
        self.moves_grid.setSpacing(8)
        self.layout.addLayout(self.moves_grid)
        
        # Metadata
        self.meta_label = QLabel()
        self.meta_label.setObjectName("metaLabel")
        self.layout.addWidget(self.meta_label)
        
        # Actions
        self.actions_layout = QHBoxLayout()
        self.main_btn = QPushButton("⚔ Set as Main")
        self.main_btn.setObjectName("actionBtn")
        self.item_btn = QPushButton("🎒 Held Item")
        self.item_btn.setObjectName("actionBtn")
        self.actions_layout.addWidget(self.main_btn)
        self.actions_layout.addWidget(self.item_btn)
        self.layout.addLayout(self.actions_layout)
        
        self.layout.addStretch()
        
        self.scroll.setWidget(self.content_widget)
        self.panel_layout.addWidget(self.scroll)
        
        self.main_btn.clicked.connect(self._on_main_clicked)
        self.item_btn.clicked.connect(self._on_item_clicked)
        self.fav_btn.clicked.connect(self._on_fav_clicked)
        
        self.clear()

    def _on_main_clicked(self):
        if self.pokemon:
            from ..singletons import update_main_pokemon
            mw.ankimon_db.set_main_pokemon(self.pokemon["individual_id"])
            update_main_pokemon()

    def _on_item_clicked(self):
        if self.pokemon:
            # Trigger a right-click style event or similar? 
            # Actually we can just call the grid's method if we have access, 
            # or better, just re-implement safely here.
            parent_window = self.window()
            if hasattr(parent_window, "grid"):
                parent_window.grid._on_held_item(self.pokemon)

    def _on_fav_clicked(self):
        if self.pokemon:
            parent_window = self.window()
            if hasattr(parent_window, "grid"):
                parent_window.grid._on_toggle_favorite(self.pokemon)
                self.fav_btn.setText("★" if self.pokemon.get("is_favorite") else "☆")

    def clear(self):
        self.pokemon = None
        self.sprite_label.setPixmap(QPixmap())
        self.name_label.setText("Select a Pokémon")
        self.fav_btn.hide()
        self._clear_layout(self.type_badges_layout)
        self.lvl_label.setText("Lv. --")
        self.xp_label.setText("--- / ---")
        self.xp_bar.setValue(0)
        self._clear_layout(self.stats_layout)
        self._clear_layout(self.iv_ev_layout)
        self._clear_layout(self.moves_grid)
        self.meta_label.setText("")
        self.main_btn.setEnabled(False)
        self.item_btn.setEnabled(False)

    def _clear_layout(self, layout):
        if not layout: return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    @staticmethod
    def _format_display_name(nickname: Optional[str], species: str, form: Optional[str]) -> str:
        # 1. Strip Mega/Gmax suffixes from species
        base_species = species
        suffixes = ["-Mega-X", "-Mega-Y", "-Mega", "-Gmax"]
        for s in suffixes:
            if base_species.endswith(s):
                base_species = base_species[:-len(s)]
                break
        
        # 2. Prepend prefix
        display_name = base_species
        if form:
            if "Mega-X" in form: display_name = f"Mega {base_species} X"
            elif "Mega-Y" in form: display_name = f"Mega {base_species} Y"
            elif "Mega" in form: display_name = f"Mega {base_species}"
            elif "Gmax" in form: display_name = f"Gigantamax {base_species}"
        
        # 3. Handle nickname
        if nickname and nickname.lower() != species.lower() and nickname.lower() != display_name.lower():
            return f"{nickname} ({display_name})"
        return display_name

    def update_pokemon(self, pokemon: Dict[str, Any], pixmap: QPixmap):
        self.pokemon = pokemon
        self.sprite_label.setPixmap(pixmap)
        
        # Name & Type
        display_name = self._format_display_name(
            pokemon.get("nickname"), pokemon["name"], pokemon.get("form")
        )
        self.name_label.setText(display_name)
        
        self.fav_btn.show()
        self.fav_btn.setText("★" if pokemon.get("is_favorite") else "☆")
        
        self._clear_layout(self.type_badges_layout)
        for t in pokemon["type"]:
            badge = QLabel(t.upper())
            rgb = TYPE_COLORS.get(t, (100, 100, 100))
            badge.setStyleSheet(f"""
                background-color: rgba({rgb[0]},{rgb[1]},{rgb[2]},180);
                border-radius: 8px; padding: 2px 8px; color: white;
                font-size: 10px; font-weight: bold;
            """)
            self.type_badges_layout.addWidget(badge)
        self.type_badges_layout.addStretch()
        
        # XP
        lvl = pokemon["level"]
        self.lvl_label.setText(f"Lv. {lvl}")
        xp = pokemon.get("xp", 0)
        growth_rate = pokemon.get("growth_rate", "medium")
        try:
            from ..functions.pokemon_functions import find_experience_for_level
            xp_current_lvl = int(find_experience_for_level(growth_rate, lvl))
            xp_next_lvl = int(find_experience_for_level(growth_rate, lvl + 1))
            progress = max(0, xp - xp_current_lvl)
            total_req = max(1, xp_next_lvl - xp_current_lvl)
            self.xp_label.setText(f"{progress:,} / {total_req:,}")
            self.xp_bar.setMaximum(total_req)
            self.xp_bar.setValue(min(progress, total_req))
        except:
            self.xp_label.setText(f"{xp:,} XP")
            self.xp_bar.setMaximum(100)
            self.xp_bar.setValue(0)
            
        # Stats
        self._update_stats_tab(pokemon)
        self._update_iv_ev_tab(pokemon)
        
        # Moves
        self._clear_layout(self.moves_grid)
        moves = pokemon.get("attacks", [])
        for i in range(4):
            move_name = moves[i] if i < len(moves) else "—"
            chip = QLabel(move_name.replace("-", " ").title())
            chip.setObjectName("moveChip")
            chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.moves_grid.addWidget(chip, i // 2, i % 2)
            
        # Metadata
        date = pokemon.get("captured_date", "Unknown")
        short_id = str(pokemon.get("individual_id", ""))[:8]
        self.meta_label.setText(f"Caught: {date}\nID: {short_id}")
        
        self.main_btn.setEnabled(True)
        self.item_btn.setEnabled(True)

    def _update_stats_tab(self, pokemon):
        self._clear_layout(self.stats_layout)
        nature = pokemon.get("nature", "serious")
        
        # Get calculated stats (already in dict or computed via PokemonObject)
        stats = pokemon.get("stats", {})
        
        for key in ["hp", "atk", "def", "spa", "spd", "spe"]:
            val = stats.get(key, 0)
            row = QHBoxLayout()
            
            label = QLabel(key.upper())
            label.setFixedWidth(40)
            
            val_label = QLabel(str(val))
            val_label.setFixedWidth(40)
            val_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            # Nature color
            if key != "hp":
                try:
                    from ..pyobj.pokemon_obj import PokemonObject
                    mult = PokemonObject.get_nature_stat_mult(key, nature)
                    if mult > 1.0: val_label.setStyleSheet("color: #ff7b72;")
                    elif mult < 1.0: val_label.setStyleSheet("color: #79c0ff;")
                except: pass
            
            bar = QProgressBar()
            bar.setObjectName("statBar")
            bar.setTextVisible(False)
            bar.setMaximum(400)
            bar.setValue(min(val, 400))
            bar.setStyleSheet(f"QProgressBar::chunk {{ background: {STAT_COLORS[key]}; border-radius: 3px; }}")
            
            row.addWidget(label)
            row.addWidget(val_label)
            row.addWidget(bar)
            self.stats_layout.addLayout(row)
            
        nature_txt = f"Nature: {nature.title()}"
        ability_txt = f"Ability: {pokemon.get('ability', 'None').title()}"
        self.stats_layout.addSpacing(8)
        self.stats_layout.addWidget(QLabel(nature_txt))
        self.stats_layout.addWidget(QLabel(ability_txt))

    def _update_iv_ev_tab(self, pokemon):
        self._clear_layout(self.iv_ev_layout)
        ivs = pokemon.get("iv", {})
        evs = pokemon.get("ev", {})
        
        self.iv_ev_layout.addWidget(QLabel("STAT"), 0, 0)
        self.iv_ev_layout.addWidget(QLabel("IV"), 0, 1)
        self.iv_ev_layout.addWidget(QLabel("EV"), 0, 2)
        
        for i, key in enumerate(["hp", "atk", "def", "spa", "spd", "spe"]):
            iv = ivs.get(key, 0)
            ev = evs.get(key, 0)
            
            self.iv_ev_layout.addWidget(QLabel(key.upper()), i + 1, 0)
            
            iv_lbl = QLabel(str(iv))
            if iv == 31: iv_lbl.setStyleSheet("color: #ffde00; font-weight: bold;")
            elif iv == 0: iv_lbl.setStyleSheet("color: #484f58;")
            self.iv_ev_layout.addWidget(iv_lbl, i + 1, 1)
            
            ev_bar = QProgressBar()
            ev_bar.setObjectName("statBar")
            ev_bar.setTextVisible(False)
            ev_bar.setMaximum(252)
            ev_bar.setValue(ev)
            ev_bar.setFixedHeight(8)
            ev_bar.setStyleSheet(f"QProgressBar::chunk {{ background: {STAT_COLORS[key]}; border-radius: 3px; }}")
            self.iv_ev_layout.addWidget(ev_bar, i + 1, 2)


class VaultGridWidget(QWidget):
    pokemon_selected = pyqtSignal(object, object) # pokemon, pixmap
    page_changed = pyqtSignal(int, int) # current, total

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pokemon_list = []
        self.slots = []
        self._pixmap_cache = {}
        self.current_page = 0
        self.total_pages = 1
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Grid
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(6)
        self.layout.addWidget(self.grid_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Empty state
        self.empty_label = QLabel("No Pokémon match your filters.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #8b949e; font-size: 14px; margin-top: 40px;")
        self.empty_label.hide()
        self.layout.addWidget(self.empty_label)
        
        # Navigation
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◄")
        self.prev_btn.setObjectName("boxNavBtn")
        self.prev_btn.setFixedSize(40, 32)
        self.next_btn = QPushButton("►")
        self.next_btn.setObjectName("boxNavBtn")
        self.next_btn.setFixedSize(40, 32)
        self.page_label = QLabel("Box 1 / 1")
        self.page_label.setObjectName("boxNavLabel")
        
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()
        self.layout.addLayout(nav_layout)
        
        self.prev_btn.clicked.connect(lambda: self.set_page(self.current_page - 1))
        self.next_btn.clicked.connect(lambda: self.set_page(self.current_page + 1))
        
        self._setup_grid()

    def _setup_grid(self):
        for i in range(30):
            slot = VaultSlotWidget()
            slot.clicked.connect(self._on_slot_clicked)
            slot.right_clicked.connect(self._on_slot_right_clicked)
            self.grid_layout.addWidget(slot, i // 5, i % 5)
            self.slots.append(slot)

    def _on_slot_clicked(self, pokemon):
        for s in self.slots:
            s.set_selected(s.pokemon == pokemon)
        
        # Get pixmap from cache
        cache_key = (pokemon["id"], pokemon.get("shiny", False), 64)
        pixmap = self._pixmap_cache.get(cache_key, QPixmap())
        self.pokemon_selected.emit(pokemon, pixmap)
        
        # Also update the inspector in the parent window directly for reliability
        win = self.window()
        if hasattr(win, "inspector"):
            win.inspector.update_pokemon(pokemon, pixmap)

    def _on_slot_right_clicked(self, pokemon, pos):
        menu = QMenu(self)
        menu.addAction("View Details", lambda: self._on_slot_clicked(pokemon))
        
        # Set as Main
        from ..singletons import update_main_pokemon
        def set_main():
            mw.ankimon_db.set_main_pokemon(pokemon["individual_id"])
            update_main_pokemon() # Refresh global state
            # No need to refresh vault unless we want a "Main" badge
        
        menu.addAction("⚔ Set as Main Pokémon", set_main)
        
        fav_label = "★ Remove Favorite" if pokemon.get("is_favorite") else "☆ Add to Favorites"
        menu.addAction(fav_label, lambda: self._on_toggle_favorite(pokemon))
        
        menu.addSeparator()
        item_label = "🎒 Remove Held Item" if pokemon.get("held_item") else "🎒 Give Held Item"
        menu.addAction(item_label, lambda: self._on_held_item(pokemon))
        
        menu.exec(pos)

    def _on_toggle_favorite(self, pokemon):
        full_pkmn = mw.ankimon_db.get_pokemon(pokemon["individual_id"])
        if full_pkmn:
            new_state = not full_pkmn.get("is_favorite", False)
            full_pkmn["is_favorite"] = new_state
            mw.ankimon_db.save_pokemon(full_pkmn)
            
            # Update local stub and refresh slots
            pokemon["is_favorite"] = new_state
            for s in self.slots:
                if s.pokemon and s.pokemon["individual_id"] == pokemon["individual_id"]:
                    s.refresh()
                    break

    def _on_held_item(self, pokemon_stub):
        full_pkmn = mw.ankimon_db.get_pokemon(pokemon_stub["individual_id"])
        if not full_pkmn: return
        
        from ..pyobj.pc_box import GiveItemWindow
        
        if full_pkmn.get("held_item"):
            # Remove
            pkmn_obj = PokemonObject.from_dict(full_pkmn)
            pkmn_obj.remove_held_item()
            # Update local stub
            pokemon_stub["held_item"] = None
        else:
            # Give
            items_list = mw.ankimon_db.get_all_items()
            items_names = []
            for item in items_list:
                item_data = item.get("data") or {}
                if item_data.get("type") is None:
                    items_names.append(item.get("item_name") or item_data.get("item", ""))
            items_names = [n for n in items_names if n]
            
            pkmn_obj = PokemonObject.from_dict(full_pkmn)
            
            def on_item_selected(item_name):
                pkmn_obj.give_held_item(item_name)
                # Update local stub
                pokemon_stub["held_item"] = item_name
                # Refresh slots
                for s in self.slots:
                    if s.pokemon and s.pokemon["individual_id"] == pokemon_stub["individual_id"]:
                        s.refresh()
                        break

            # Need logger from main window
            logger = getattr(mw, "logger", None)
            win = GiveItemWindow(items_names, on_item_selected, logger)
            win.exec()

        # Refresh slot
        for s in self.slots:
            if s.pokemon and s.pokemon["individual_id"] == pokemon_stub["individual_id"]:
                s.refresh()
                break

    def set_pokemon_list(self, pokemon_list: List[Dict[str, Any]]):
        self.pokemon_list = pokemon_list
        self.total_pages = max(1, math.ceil(len(pokemon_list) / 30))
        self.set_page(0)
        
        if not pokemon_list:
            self.grid_container.hide()
            self.empty_label.show()
        else:
            self.grid_container.show()
            self.empty_label.hide()

    def set_page(self, page: int):
        if page < 0: page = self.total_pages - 1
        elif page >= self.total_pages: page = 0
        
        self.current_page = page
        self.page_label.setText(f"Box {page + 1} / {self.total_pages}")
        self._refresh_slots()

    def _refresh_slots(self):
        start = self.current_page * 30
        page_items = self.pokemon_list[start : start + 30]
        
        for i, slot in enumerate(self.slots):
            pokemon = page_items[i] if i < len(page_items) else None
            slot.pokemon = pokemon
            slot.set_selected(False)
            slot.refresh()
            
            if pokemon:
                # Load/Cache pixmap
                cache_key = (pokemon["id"], pokemon.get("shiny", False), 64)
                if cache_key not in self._pixmap_cache:
                    path = get_sprite_path("front", "png", pokemon["id"], pokemon.get("shiny"), pokemon["gender"], pokemon["name"])
                    pixmap = QPixmap(str(path))
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self._pixmap_cache[cache_key] = pixmap
                
                slot.set_sprite(self._pixmap_cache[cache_key])

    def clear_cache(self):
        self._pixmap_cache.clear()


class PokemonVaultWindow(QDialog):
    def __init__(self, logger, translator, reviewer_obj, test_window, settings, main_pokemon, parent=mw):
        super().__init__(parent)
        self.logger = logger
        self.translator = translator
        self.reviewer_obj = reviewer_obj
        self.test_window = test_window
        self.settings = settings
        self.main_pokemon = main_pokemon
        
        self._last_filter_state = None
        
        self.setWindowTitle("Pokémon Vault")
        self.setMinimumSize(1000, 594)
        self.resize(1260, 684)
        
        self._setup_ui()
        self._apply_qss()
        
        # Initial load
        self.refresh_gui()

    def refresh_gui(self):
        """Standard refresh entry point for Ankimon windows."""
        self.grid.clear_cache()
        self._reload_data()

    def _reload_data(self):
        # 1. Build state
        current_state = self.filter_rail.get_state()
        db_name = mw.ankimon_db.db_path.name
        state_with_db = VaultFilterState(
            **{k: v for k, v in current_state.__dict__.items() if k != "db_name"},
            db_name=db_name
        )

        # 2. Build Query (Mirroring pc_box.py)
        query_parts = [
            "SELECT individual_id, name, level, pokedex_id as id, shiny as shiny, "
            "rowid as original_index, json_extract(data, '$.nickname') as nickname, "
            "json_extract(data, '$.gender') as gender, json_extract(data, '$.is_favorite') as is_favorite, "
            "json_extract(data, '$.held_item') as held_item, "
            "json_extract(data, '$.captured_date') as captured_date, "
            "json_extract(data, '$.iv') as iv_json, json_extract(data, '$.ev') as ev_json, "
            "json_extract(data, '$.base_stats') as base_stats_json, json_extract(data, '$.nature') as nature, "
            "json_extract(data, '$.type') as type_json, json_extract(data, '$.form') as form, "
            "json_extract(data, '$.xp') as xp, json_extract(data, '$.growth_rate') as growth_rate, "
            "json_extract(data, '$.attacks') as attacks_json, json_extract(data, '$.ability') as ability "
            "FROM captured_pokemon WHERE 1=1"
        ]
        params = []

        # Filters
        if state_with_db.search:
            search_text = f"%{state_with_db.search}%"
            query_parts.append("AND (name LIKE ? OR json_extract(data, '$.nickname') LIKE ?)")
            params.extend([search_text, search_text])

        if state_with_db.type_filter != "All":
            query_parts.append("AND json_extract(data, '$.type') LIKE ?")
            params.append(f"%{state_with_db.type_filter}%")

        if state_with_db.tier_filter != "All":
            query_parts.append("AND json_extract(data, '$.tier') = ?")
            params.append(state_with_db.tier_filter)

        if state_with_db.favorites:
            query_parts.append("AND json_extract(data, '$.is_favorite') = 1")

        if state_with_db.holding_item:
            query_parts.append("AND json_extract(data, '$.held_item') IS NOT NULL")

        if state_with_db.shiny:
            query_parts.append("AND shiny = 1")

        if state_with_db.gen_filter != "All":
            gen_idx = int(state_with_db.gen_filter.replace("Gen ", ""))
            gen_ranges = {
                1: (1, 151), 2: (152, 251), 3: (252, 386), 4: (387, 493),
                5: (494, 649), 6: (650, 721), 7: (722, 809), 8: (810, 905), 9: (906, 1025)
            }
            if gen_idx in gen_ranges:
                start_id, end_id = gen_ranges[gen_idx]
                query_parts.append("AND pokedex_id BETWEEN ? AND ?")
                params.extend([start_id, end_id])

        # Sorting logic (Mirroring pc_box.py)
        sort_key_str = state_with_db.sort_key.lower()
        direction = "ASC" if state_with_db.sort_asc else "DESC"
        use_python_sort = False
        
        stat_map = {
            "hp": "hp", "atk": "atk", "def": "def", "spa": "spa", "spd": "spd", "spe": "spe",
            "attack": "atk", "defense": "def", "sp.atk": "spa", "sp.def": "spd", "speed": "spe"
        }
        target_stat = stat_map.get(sort_key_str)

        if sort_key_str == "date caught":
            order_clause = f"ORDER BY original_index {direction}"
        elif sort_key_str == "name":
            order_clause = f"ORDER BY name {direction}, json_extract(data, '$.nickname') {direction}"
        elif sort_key_str == "level":
            order_clause = f"ORDER BY level {direction}"
        elif sort_key_str == "pokédex #":
            order_clause = f"ORDER BY pokedex_id {direction}"
        elif sort_key_str in ["cp", "iv total", "ev total"] or target_stat:
            use_python_sort = True
            order_clause = f"ORDER BY original_index {direction}"
        else:
            order_clause = f"ORDER BY original_index {direction}"

        query = " ".join(query_parts) + " " + order_clause

        try:
            cursor = mw.ankimon_db.execute(query, tuple(params))
            results = []
            for row in cursor.fetchall():
                iv = json.loads(row["iv_json"]) if row["iv_json"] else {}
                ev = json.loads(row["ev_json"]) if row["ev_json"] else {}
                base_stats = json.loads(row["base_stats_json"]) if row["base_stats_json"] else {}
                level = row["level"]
                nature = row["nature"] or "serious"
                
                # Pre-calculate actual stats
                stats = {}
                for s_key in ["hp", "atk", "def", "spa", "spd", "spe"]:
                    stats[s_key] = PokemonObject.calc_stat(
                        s_key, base_stats.get(s_key, 1), level, iv.get(s_key, 0), ev.get(s_key, 0), nature
                    )

                p = {
                    "original_index": row["original_index"],
                    "individual_id": row["individual_id"],
                    "id": row["id"],
                    "name": row["name"],
                    "nickname": row["nickname"],
                    "shiny": bool(row["shiny"]),
                    "level": level,
                    "gender": row["gender"],
                    "is_favorite": bool(row["is_favorite"]),
                    "held_item": row["held_item"],
                    "captured_date": row["captured_date"],
                    "iv": iv,
                    "ev": ev,
                    "base_stats": base_stats,
                    "stats": stats,
                    "nature": nature,
                    "type": json.loads(row["type_json"]) if row["type_json"] else [],
                    "form": row["form"],
                    "xp": row["xp"] or 0,
                    "growth_rate": row["growth_rate"] or "medium",
                    "attacks": json.loads(row["attacks_json"]) if row["attacks_json"] else [],
                    "ability": row["ability"] or "None",
                }
                
                if use_python_sort:
                    if sort_key_str == "iv total":
                        p["_sort_value"] = sum(p["iv"].values()) if isinstance(p["iv"], dict) else 0
                    elif sort_key_str == "ev total":
                        p["_sort_value"] = sum(p["ev"].values()) if isinstance(p["ev"], dict) else 0
                    elif target_stat:
                        base_val = p["base_stats"].get(target_stat, 1)
                        p["_sort_value"] = PokemonObject.calc_stat(target_stat, base_val, p["level"], p["iv"].get(target_stat, 0), p["ev"].get(target_stat, 0), p["nature"])
                    elif sort_key_str == "cp":
                        p["_sort_value"] = calculate_cp_from_dict(p)
                
                results.append(p)

            if use_python_sort:
                results.sort(key=lambda x: x.get("_sort_value", 0), reverse=not state_with_db.sort_asc)

            self.grid.set_pokemon_list(results)
            self._last_filter_state = state_with_db

        except Exception as e:
            self.logger.log("error", f"Vault: Error fetching data: {e}")
            import traceback
            traceback.print_exc()
            self.grid.set_pokemon_list([])

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setObjectName("vaultToolbar")
        self.toolbar.setFixedHeight(48)
        toolbar_layout = QHBoxLayout(self.toolbar)
        
        title = QLabel("🗄 Pokémon Vault")
        title.setObjectName("vaultTitle")
        toolbar_layout.addWidget(title)
        toolbar_layout.addStretch()
        
        self.layout.addWidget(self.toolbar)
        
        # Main Splitter (Rail | (Grid | Inspector))
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(1)
        
        self.filter_rail = VaultFilterRail()
        self.filter_rail.filters_changed.connect(self._on_filters_changed)
        self.main_splitter.addWidget(self.filter_rail)
        
        # Inner Splitter (Grid | Inspector)
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.content_splitter.setHandleWidth(1)
        
        self.grid = VaultGridWidget()
        self.grid.pokemon_selected.connect(self._on_pokemon_selected)
        self.content_splitter.addWidget(self.grid)
        
        self.inspector = VaultInspectorPanel(self.reviewer_obj)
        self.content_splitter.addWidget(self.inspector)
        
        # Split ratios: Rail (fixed 220), Grid 55%, Inspector 45%
        self.content_splitter.setSizes([600, 400])
        
        self.main_splitter.addWidget(self.content_splitter)
        self.layout.addWidget(self.main_splitter)

    def _apply_qss(self):
        self.setStyleSheet("""
            /* ── WINDOW ─────────────────────────────────────────────────── */
            PokemonVaultWindow {
                background-color: #0d1117;
                color: #e6edf3;
            }

            /* ── TOOLBAR ─────────────────────────────────────────────────── */
            #vaultToolbar {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #161b22, stop:1 #0d1117);
                border-bottom: 1px solid rgba(255,255,255,12);
                padding: 0 16px;
            }
            #vaultTitle {
                font-size: 15px;
                font-weight: 700;
                color: #e6edf3;
                letter-spacing: 0.5px;
            }
            #boxNavLabel {
                font-size: 13px;
                color: #8b949e;
            }
            #boxNavBtn {
                background: rgba(255,255,255,8);
                border: 1px solid rgba(255,255,255,15);
                border-radius: 6px;
                color: #e6edf3;
                padding: 4px 12px;
                font-size: 13px;
            }
            #boxNavBtn:hover { background: rgba(255,255,255,16); }
            #boxNavBtn:pressed { background: rgba(255,255,255,6); }

            /* ── FILTER RAIL ─────────────────────────────────────────────── */
            #vaultFilterRail {
                background: #0d1117;
                border: none;
                border-right: 1px solid rgba(255,255,255,10);
            }
            #sectionHeader {
                font-size: 10px;
                font-weight: 700;
                color: #8b949e;
                text-transform: uppercase;
                letter-spacing: 1.2px;
                margin-top: 12px;
                margin-bottom: 4px;
            }
            QLineEdit {
                background: rgba(255,255,255,8);
                border: 1px solid rgba(255,255,255,18);
                border-radius: 8px;
                padding: 6px 10px;
                color: #e6edf3;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: rgba(88,166,255,100);
                background: rgba(88,166,255,10);
            }
            QComboBox {
                background: rgba(255,255,255,8);
                border: 1px solid rgba(255,255,255,18);
                border-radius: 8px;
                padding: 5px 10px;
                color: #e6edf3;
                font-size: 12px;
                min-height: 28px;
            }
            QComboBox::drop-down { border: none; }
            QCheckBox {
                color: #c9d1d9;
                font-size: 12px;
                spacing: 8px;
            }
            #clearFiltersBtn {
                background: rgba(248,81,73,20);
                border: 1px solid rgba(248,81,73,60);
                border-radius: 8px;
                color: rgba(248,81,73,220);
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 600;
            }

            /* ── GRID ────────────────────────────────────────────────────── */
            VaultGridWidget { background: #0d1117; }
            #vaultSlot {
                background: rgba(255,255,255,6);
                border: 1px solid rgba(255,255,255,10);
                border-radius: 10px;
            }
            #vaultSlot:hover {
                background: rgba(255,255,255,12);
                border: 1px solid rgba(120,200,255,80);
            }
            #vaultSlot[selected="true"] {
                border: 2px solid rgba(88,166,255,200);
                background: rgba(88,166,255,12);
            }
            #vaultSlot[empty="true"] {
                background: transparent;
                border: 1px dashed rgba(255,255,255,12);
            }

            /* ── INSPECTOR ────────────────────────────────────────────────── */
            #vaultInspectorPanel {
                background: rgba(255,255,255,4);
                border-left: 1px solid rgba(255,255,255,10);
            }
            #inspectorScrollArea, #inspectorContent {
                background: transparent;
            }
            #inspectorName { font-size: 18px; font-weight: 700; }
            #inspectorSubtitle { font-size: 12px; color: #8b949e; }
            #xpBar { background: rgba(255,255,255,10); border: none; border-radius: 3px; }
            #xpBar::chunk { background: #58a6ff; border-radius: 3px; }
            #statBar { background: rgba(255,255,255,10); border: none; border-radius: 3px; }
            
            QTabWidget::pane { border: 1px solid rgba(255,255,255,12); border-radius: 8px; background: rgba(255,255,255,4); }
            QTabBar::tab { background: transparent; color: #8b949e; padding: 6px 16px; font-weight: 600; }
            QTabBar::tab:selected { color: #e6edf3; border-bottom: 2px solid #58a6ff; }
            
            #moveChip {
                background: rgba(255,255,255,8);
                border: 1px solid rgba(255,255,255,15);
                border-radius: 6px;
                padding: 3px 10px;
                font-size: 12px;
                color: #c9d1d9;
            }
            #actionBtn {
                background: rgba(88,166,255,15);
                border: 1px solid rgba(88,166,255,60);
                border-radius: 8px;
                color: #58a6ff;
                padding: 7px 14px;
                font-weight: 600;
            }
            #metaLabel { font-size: 11px; color: #484f58; }
        """)

    def _on_filters_changed(self, state: VaultFilterState):
        self._last_filter_state = state
        self._reload_data()

    def _on_pokemon_selected(self, pokemon, pixmap):
        self.inspector.update_pokemon(pokemon, pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Handle Inspector collapse logic
        if self.width() < 900:
            pass
