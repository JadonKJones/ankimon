# Core File Appendix

Preserving rich detail from the most important files so future agent turns do not need to rediscover them from scratch.

## Ankimon/resources.py
*   **Why it was selected**: High structural centrality. It acts as a `glue` layer and is imported by 75 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 480 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from pathlib import Path
import os
import json

addon_dir = Path(__file__).parents[0]

#safe route for updates
user_path = addon_dir / "user_files"
user_path_data = addon_dir / "user_files" / "data_files"
user_path_sprites = addon_dir / "user_files" / "sprites"
user_path_credentials = addon_dir / "user_files" / "data.json"
manifest_path = addon_dir / "manifest.json"

font_path = addon_dir / "addon_files"

# Assign Pokemon Image folder directory name
pkmnimgfolder = addon_dir / "user_files" / "sprites"
backdefault = addon_dir / "user_files" / "sprites" / "back_default"
frontdefault = addon_dir / "user_files" / "sprites" / "front_default"
#Assign saved Pokemon Directory
mypokemon_path = addon_dir / "user_files" / "mypokemon.json"
mainpokemon_path = addon_dir / "user_files" / "mainpokemon.json"
pokemon_history_path = addon_dir / "user_files" / "pokemon_history.json"
battlescene_path = addon_dir / "addon_sprites" / "battle_scenes"
trainer_sprites_path = addon_dir / "addon_sprites" / "trainers"
battlescene_path_without_dialog = addon_dir / "addon_sprites" / "battle_scenes_without_dialog"
battle_ui_path = addon_dir / "pkmnbattlescene - UI_transp"
type_style_file = addon_dir / "addon_files" / "types.json"
next_lvl_file_path = addon_dir / "addon_files" / "ExpPokemonAddon.csv"
berries_path = addon_dir / "user_files" / "sprites" / "berries"
background_dialog_image_path  = addon_dir / "background_dialog_image.png"
pokeball_path = addon_dir / "addon_files" / "pokeball.png"
pokedex_image_path = addon_dir / "addon_sprites" / "pokedex_template.jpg"
evolve_image_path = addon_dir / "addon_sprites" / "evo_temp.jpg"
learnset_path = addon_dir / "user_files" / "data_files" / "learnsets.json"
pokedex_path = addon_dir / "user_files" / "data_files" / "pokedex.json"
stats_csv = addon_dir / "user_files" / "data_files" / "pokemon_stats.csv"
moves_file_path = addon_dir / "user_files" / "data_files" / "moves.json"
move_names_file_path = addon_dir / "user_files" / "data_files" / "move_names.json"
items_path = addon_dir / "user_files" / "sprites" / "items"
badges_path = addon_dir / "user_files" / "sprites" / "badges"
itembag_path = addon_dir / "user_files" / "items.json"
badgebag_path = addon_dir / "user_files" / "badges.json"
pokenames_lang_path = addon_dir / "user_files" / "data_files" / "pokemon_species_names.csv"
pokedesc_lang_path = addon_dir / "user_files" / "data_files" / "pokemon_species_flavor_text.csv"
poke_evo_path = addon_dir / "user_files" / "data_files" / "pokemon_evolution.csv"
poke_species_path = addon_dir / "user_files" / "data_files" / "pokemon_species.csv"
eff_chart_html_path = addon_dir / "addon_files" / "eff_chart_html.html"
effectiveness_chart_file_path = addon_dir / "addon_files" / "eff_chart.json"
table_gen_id_html_path = addon_dir / "addon_files" / "table_gen_id.html"
icon_path = addon_dir / "addon_files" / "pokeball.png"
sound_list_path = addon_dir / "addon_files" / "sound_list.json"
badges_list_path = addon_dir / "addon_files" / "badges.json"
items_list_path = addon_dir / "addon_files" / "items.json"
rate_path = addon_dir / "user_files" / "rate_this.json"
csv_file_items = addon_dir / "user_files" / "data_files" / "item_names.csv"
csv_file_descriptions = addon_dir / "user_files" / "data_files" / "item_flavor_text.csv"
csv_file_items_cost = addon_dir / "user_files" / "data_files" / "items.csv"
pokemon_csv = addon_dir / "user_files" / "data_files" / "pokemon.csv"
pokemon_tm_learnset_path = addon_dir / "user_files" / "data_files" / "pokemon_tm_learnset.json"
pokeapi_db_path = addon_dir / "user_files" / "ankimon.db"

#effect sounds paths
hurt_normal_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtNormal.mp3"
hurt_noteff_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtNotEffective.mp3"
hurt_supereff_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtSuper.mp3"
ownhplow_sound_path = addon_dir / "addon_sprites" / "sounds" / "OwnHpLow.mp3"
hpheal_sound_path = addon_dir / "addon_sprites" / "sounds" / "HpHeal.mp3"
fainted_sound_path = addon_dir / "addon_sprites" / "sounds" / "Fainted.mp3"

#utils
json_file_structure = addon_dir / "addon_files" / "folder_structure.json"

#move ui paths
type_icon_path_resources = addon_dir / "addon_sprites" / "Types"

team_pokemon_path = addon_dir / "user_files" / "team.json"

#lang routes
lang_path = addon_dir / "lang"
lang_path_de = addon_dir / "lang" / "de_text.json"
lang_path_ch = addon_dir / "lang" / "ch_text.json"
lang_path_en = addon_dir / "lang" / "en_text.json"
lang_path_fr = addon_dir / "lang" / "fr_text.json"
lang_path_jp = addon_dir / "lang" / "jp_text.json"
lang_path_sp = addon_dir / "lang" / "sp_text.json"
lang_path_it = addon_dir / "lang" / "it_text.json"
lang_path_cz = addon_dir / "lang" / "cz_text.json"
lang_path_po = addon_dir / "lang" / "po_text.json"
lang_path_kr = addon_dir / "lang" / "kr_text.json"
lang_path_es_latam = addon_dir / "lang" / "es_latam_text.json"

#backup_routes
backup_root = addon_dir / "user_files" / "backups"
backup_folder_1 = backup_root / "backup_1"
backup_folder_2 = backup_root / "backup_2"
backup_folders = [os.path.join(backup_root, f"backup_{i}") for i in range(1, 4)]

#detect add-on version
try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    addon_ver = manifest.get("version", "unknown")
except Exception:
    addon_ver = "unknown"

#note if it is an experimental build
IS_EXPERIMENTAL_BUILD = addon_ver.endswith("-E")


POKEMON_TIERS = {
  "Normal": [
    # Generation 1
    10, 11, 12,	# caterpie, metapod, butterfree
    13, 14, 15,	# weedle, kakuna, beedrill
    16, 17, 18,	# pidgey, pidgeotto, pidgeot
    19, 20, 21,	# rattata, raticate, spearow
    22, 23, 24,	# fearow, ekans, arbok
    25, 26, 27,	# pikachu, raichu, sandshrew
    28, 29, 30,	# sandslash, nidoran-f, nidorina
    31, 32, 33,	# nidoqueen, nidoran-m, nidorino
    34, 35, 36,	# nidoking, clefairy, clefable
    37, 38, 39,	# vulpix, ninetales, jigglypuff
    40, 41, 42,	# wigglytuff, zubat, golbat
    43, 44, 45,	# oddish, gloom, vileplume
    46, 47, 48,	# paras, parasect, venonat
    49, 50, 51,	# venomoth, diglett, dugtrio
    52, 53, 54,	# meowth, persian, psyduck
    55, 56, 57,	# golduck, mankey, primeape
    58, 59, 60,	# growlithe, arcanine, poliwag
    61, 62, 63,	# poliwhirl, poliwrath, abra
    64, 65, 66,	# kadabra, alakazam, machop
    67, 68, 69,	# machoke, machamp, bellsprout
    70, 71, 72,	# weepinbell, victreebel, tentacool
    73, 74, 75,	# tentacruel, geodude, graveler
    76, 77, 78,	# golem, ponyta, rapidash
    79, 80, 81,	# slowpoke, slowbro, magnemite
    82, 83, 84,	# magneton, farfetchd, doduo
    85, 86, 87,	# dodrio, seel, dewgong
    88, 89, 90,	# grimer, muk, shellder
    91, 92, 93,	# cloyster, gastly, haunter
    94, 95, 96,	# gengar, onix, drowzee
    97, 98, 99,	# hypno, krabby, kingler
    100, 101, 102,	# voltorb, electrode, exeggcute
    103, 104, 105,	# exeggutor, cubone, marowak
    106, 107, 108,	# hitmonlee, hitmonchan, lickitung
    109, 110, 111,	# koffing, weezing, rhyhorn
    112, 113, 114,	# rhydon, chansey, tangela
    115, 116, 117,	# kangaskhan, horsea, seadra
    118, 119, 120,	# goldeen, seaking, staryu
    121, 122, 123,	# starmie, mr-mime, scyther

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def ensure_ankimon_infrastructure(base_path, base_user_path):
```


## Ankimon/addon_files/lib/pypresence/utils.py
*   **Why it was selected**: High structural centrality. It acts as a `glue` layer and is imported by 75 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
"""Util functions that are needed but messy."""
import asyncio
import json
import os
import sys
import tempfile
import time
import socket

from .exceptions import PyPresenceException


def remove_none(d: dict):
    for item in d.copy():
        if isinstance(d[item], dict):
            if len(d[item]):
                d[item] = remove_none(d[item])
            if not len(d[item]):
                del d[item]
        elif d[item] is None:
            del d[item]
    return d


def test_ipc_path(path):
    '''Tests an IPC pipe to ensure that it actually works'''
    if sys.platform == 'win32' or sys.platform == 'win64':
        with open(path):
            return True
    else:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(path)
            return True


# Returns on first IPC pipe matching Discord's
def get_ipc_path(pipe=None):
    ipc = 'discord-ipc-'
    if pipe is not None:
        ipc = f"{ipc}{pipe}"

    if sys.platform in ('linux', 'darwin'):
        tempdir = os.environ.get('XDG_RUNTIME_DIR') or (f"/run/user/{os.getuid()}" if os.path.exists(f"/run/user/{os.getuid()}") else tempfile.gettempdir())
        paths = ['.', 'snap.discord', 'app/com.discordapp.Discord', 'app/com.discordapp.DiscordCanary']
    elif sys.platform == 'win32':
        tempdir = r'\\?\pipe'
        paths = ['.']
    else:
        return

    for path in paths:
        full_path = os.path.abspath(os.path.join(tempdir, path))
        if sys.platform == 'win32' or os.path.isdir(full_path):
            for entry in os.scandir(full_path):
                if entry.name.startswith(ipc) and os.path.exists(entry) and test_ipc_path(entry.path):
                    return entry.path


def get_event_loop(force_fresh=False):
    if force_fresh:
        return asyncio.new_event_loop()
    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()
    if running.is_closed():
        return asyncio.new_event_loop()
    return running

```


## Ankimon/functions/drawing_utils.py
*   **Why it was selected**: High structural centrality. It acts as a `utility` layer and is imported by 73 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 77 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from typing import Optional

from aqt import mw
from aqt.qt import QPainter, QLabel, Qt, sip
from PyQt6.QtGui import QColor, QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QPoint, QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QFrame

from ..pyobj.pokemon_obj import PokemonObject


def tooltipWithColour(
    msg, color, x=0, y=20, xref=1, parent=None, width=0, height=0, centered=False
):
    reviewer_text_message_box = mw.settings_obj.get("gui.reviewer_text_message_box")
    period = int(
        mw.settings_obj.get("gui.reviewer_text_message_box_time") * 1000
    )  # time for pop up message

    class CustomLabel(QLabel):
        def mousePressEvent(self, evt):
            evt.accept()
            self.hide()

    aw = parent or QApplication.activeWindow()
    if aw is None:
        return

    if color == "#6A4DAC":
        y_offset = 40
    elif color == "#F7DC6F":
        y_offset = -40
    elif color == "#F0B27A":
        y_offset = -40
    elif color == "#D2B4DE":
        y_offset = -40
    else:
        y_offset = 0

    if reviewer_text_message_box != False:
        x = aw.mapToGlobal(QPoint(x + round(aw.width() / 2), 0)).x()
        y = aw.mapToGlobal(QPoint(0, aw.height() - (180 + y_offset))).y()
        lab = CustomLabel(aw)
        lab.setFrameShape(QFrame.Shape.StyledPanel)
        lab.setLineWidth(2)
        lab.setWindowFlags(Qt.WindowType.ToolTip)
        lab.setText(msg)
        lab.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        if width > 0:
            lab.setFixedWidth(width)
        if height > 0:
            lab.setFixedHeight(height)

        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(color))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
        lab.setPalette(p)
        lab.show()
        lab.move(QPoint(x - round(lab.width() * 0.5 * xref), y))
        try:
            QTimer.singleShot(
                period, lambda: lab.hide() if lab and not sip.isdeleted(lab) else None
            )
        except:
            QTimer.singleShot(
                3000, lambda: lab.hide() if lab and not sip.isdeleted(lab) else None
            )
        mw.logger.log_and_showinfo("game", msg)


def draw_gender_symbols(
    main_pokemon: PokemonObject,
    enemy_pokemon: PokemonObject,
    painter: QPainter,
    pos_main_pkmn: Optional[tuple[int, int]] = None,
    pos_enemy: Optional[tuple[int, int]] = None,
) -> None:
    """Draw gender symbols for the main and enemy Pokémon on the given painter canvas.

    This function draws gender symbols (♂ for male, ♀ for female) next to the main and enemy Pokémon
    on a canvas using the QPainter object. The gender symbols are drawn at specified positions,
    or default positions if none are provided.

    Args:
        main_pokemon (PokemonObject): The main Pokémon object whose gender symbol will be drawn.
        enemy_pokemon (PokemonObject): The enemy Pokémon object whose gender symbol will be drawn.
        painter (QPainter): The QPainter object used to draw on the canvas.
        pos_main_pkmn (Optional[tuple[int, int]], optional): The (x, y) position where the main
            Pokémon's gender symbol will be drawn. Defaults to aNone.
        pos_enemy (Optional[tuple[int, int]], optional): The (x, y) position where the enemy
            Pokémon's gender symbol will be drawn. Defaults to None.

    Returns:
        None: This function modifies the state of the QPainter object but does not return any value.
    """
    get_gender_symbol = lambda gender: {"M": "♂", "F": "♀"}.get(
        gender, ""
    )  # Gets gender symbol. Returns "" by default
    get_pen_color = lambda gender: (
        QColor(20, 100, 210) if gender == "M" else QColor(210, 20, 20)
    )  # Blue if "M", else Red

    enemy_pokemon_gender_symbol = get_gender_symbol(enemy_pokemon.gender)
    main_pokemon_gender_symbol = get_gender_symbol(main_pokemon.gender)

    color_backup = (
        painter.pen().color()
    )  # Saving the pen's color to reset it after drawing gender symbols

    painter.setPen(
        get_pen_color(enemy_pokemon.gender)
    )  # Text color of the gender symbol
    pos = pos_enemy or (175, 64)
    painter.drawText(pos[0], pos[1], enemy_pokemon_gender_symbol)

    painter.setPen(
        get_pen_color(main_pokemon.gender)
    )  # Text color of the gender symbol
    pos = pos_main_pkmn or (457, 196)
    painter.drawText(pos[0], pos[1], main_pokemon_gender_symbol)

    painter.setPen(
        color_backup
    )  # Going back to the color we had before drawing gender symbols


def draw_stat_boosts(
    main_pokemon: PokemonObject,
    enemy_pokemon: PokemonObject,
    painter: QPainter,
    pos_for_main_pkmn: Optional[tuple[int, int]] = None,
    pos_for_enemy: Optional[tuple[int, int]] = None,
) -> None:
    """Draws visual indicators of stat boosts for two Pokémon using QPainter.

    This function displays the stat boosts (e.g., ATK, DEF, SpA) for both a main Pokémon
    and an enemy Pokémon on a GUI. Each non-neutral boost is represented as a colored rectangle
    containing an abbreviated stat name and its corresponding multiplier.

    Args:
        main_pokemon (PokemonObject): The player's Pokémon whose stat boosts will be drawn.
        enemy_pokemon (PokemonObject): The opposing Pokémon whose stat boosts will be drawn.
        painter (QPainter): The QPainter object used to draw the boost indicators.
        pos_for_main_pkmn (Optional[tuple[int, int]]): The top-left position (x, y) to draw
            the main Pokémon's boosts. If None, nothing will be drawn for the main Pokémon.
        pos_for_enemy (Optional[tuple[int, int]]): The top-left position (x, y) to draw
            the enemy Pokémon's boosts. If None, nothing will be drawn for the enemy Pokémon.

    Returns:

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def tooltipWithColour(
    class CustomLabel(QLabel):
        def mousePressEvent(self, evt):
def draw_gender_symbols(
def draw_stat_boosts(
```


## Ankimon/utils.py
*   **Why it was selected**: High structural centrality. It acts as a `glue` layer and is imported by 72 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 788 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import os
from pathlib import Path
import requests
import json
import random
import csv
import base64
from typing import Any, Optional

from aqt import mw
from aqt.utils import showWarning, showInfo

from aqt.qt import QFontDatabase, QFont, QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from .pyobj.settings import Settings
from .pyobj.InfoLogger import ShowInfoLogger

from .functions.battle_functions import calculate_hp
from .functions.pokedex_functions import find_details_move, search_pokedex

from .pyobj.error_handler import show_warning_with_traceback
from .resources import (
    battlescene_path,
    berries_path,
    items_path,
    csv_file_items_cost,
    csv_file_descriptions,
    font_path,
    hurt_normal_sound_path,
    hurt_noteff_sound_path,
    hurt_supereff_sound_path,
    hpheal_sound_path,
    ownhplow_sound_path,
    fainted_sound_path,
    addon_dir,
    POKEMON_TIERS,
    pokedex_path,
)
from .move_names import format_move_name


audio_output = QAudioOutput()
media_player = QMediaPlayer()
media_player.setAudioOutput(audio_output)

with open(pokedex_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    POKEMON_NAME_LOOKUP = {x: data[x]["name"] for x in data}


def format_pokemon_name(name: str) -> str:
    """
    Look up the official Pokémon name using the normalized key.
    Falls back to capitalizing if not found.
    """
    key = name.replace(" ", "").replace("-", "").replace("_", "").lower()
    return POKEMON_NAME_LOOKUP.get(key, name.capitalize())


def check_folders_exist(parent_directory, folder):
    folder_path = os.path.join(parent_directory, folder)
    return os.path.isdir(folder_path)


def check_file_exists(folder, filename):
    file_path = os.path.join(folder, filename)
    return os.path.isfile(file_path)


def test_online_connectivity(
    url="https://raw.githubusercontent.com/Unlucky-Life/ankimon/main/update_txt.md",
    timeout=5,
):
    try:
        # Attempt to get the URL
        response = requests.get(url, timeout=timeout)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            return True
    except:
        # Connection error means no internet connectivity
        return False


# Define the hook function
def addon_config_editor_will_display_json(text: str) -> str:
    """
    This function modifies the JSON configuration text before displaying it to the user.
    It replaces the values for the keys "pokemon_collection" and "mainpokemon".

    Args:
        text (str): The JSON configuration text.

    Returns:
        str: The modified JSON configuration text.
    """
    try:
        # Parse the JSON text
        config = json.loads(text)
        if "mainpokemon" in config:
            # showInfo(f"{config}")
            showInfo(
                "This Configuration is old and wont be used anymore. \n Please use the Settings Window in the Ankimon Menu => Settings"
            )
            # mw.settings_ankimon.show_window()
            # dont show all mainpokemon and mypokemon information in config
            if "pokemon_collection" in config:
                del config["pokemon_collection"]
            if "mainpokemon" in config:
                del config["mainpokemon"]
            if "trainer.cash" in config:
                del config["trainer.cash"]

            # Convert back to JSON string
            modified_text = json.dumps(config, indent=4)
            return modified_text
        return text
    except (requests.RequestException, json.JSONDecodeError):
        # Handle JSON parsing or network errors
        return text


# Function to read the content of the local file
def read_local_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return None


# Function to check if the file exists on GitHub and read its content
def read_github_file(url):
    response = requests.get(url)

    if response.status_code == 200:
        # File exists, parse the Markdown content
        content = response.text
        return content
    else:
        return None


# Function to check if the content of the two files is the same
def compare_files(local_content, github_content):
    return local_content == github_content



... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def format_pokemon_name(name: str) -> str:
def check_folders_exist(parent_directory, folder):
def check_file_exists(folder, filename):
def test_online_connectivity(
def addon_config_editor_will_display_json(text: str) -> str:
def read_local_file(file_path):
def read_github_file(url):
def compare_files(local_content, github_content):
def write_local_file(file_path, content):
def read_html_file(file_path):
def random_battle_scene():
def random_berries():
def filter_item_sprites(string):
def random_item():
def daily_item_list():
def give_item(item_name: str, item_type: Optional[str] = None):
def get_item_price(item_name, file_path=csv_file_items_cost):
def get_item_id(item_name, file_path=csv_file_items_cost):
def random_fossil():
def count_items_and_rewrite():
def get_item_description(item_name, language_id):
def load_custom_font(font_size, language):
def get_all_sprites(directory):
def play_effect_sound(settings_obj, sound_type):
def save_error_code(error_code, logger=None):
def get_main_pokemon_data():
def play_sound(enemy_pokemon_id: int, settings_obj: Settings):
def load_collected_pokemon_ids() -> set:
def limit_ev_yield(
def iv_rand_gauss(mu: float = 15, sigma: float = 5) -> int:
def get_ev_spread(mode: str = "random") -> dict[str, int]:
def get_tier_by_id(pokemon_id: int) -> Optional[str]:
def safe_get_random_move(
def png_to_base64(path: str) -> str:
def close_anki():
```


## Ankimon/gui_classes/choose_trainer_sprite_graphical.py
*   **Why it was selected**: High structural centrality. It acts as a `UI surface` layer and is imported by 60 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QGridLayout, QWidget, QScrollArea, QPushButton
from PyQt6.QtGui import QIcon
from aqt import mw
from ..utils import get_all_sprites
from ..resources import trainer_sprites_path
import os

class TrainerSpriteGraphicalDialog(QDialog):
    def __init__(self, settings_obj, parent=mw):
        super().__init__(parent)
        self.setWindowTitle("Choose Your Trainer Sprite")
        self.settings = settings_obj
        self.trainer_sprites = sorted(get_all_sprites(trainer_sprites_path))
        self.setModal(True)

        # Layout
        layout = QVBoxLayout()

        # Label
        label = QLabel("Choose your trainer sprite:")
        layout.addWidget(label)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Grid Widget
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        scroll_area.setWidget(grid_widget)

        # Populate Grid
        self.populate_grid()

        # Set layout
        self.setLayout(layout)
        self.setMinimumSize(910, 600)

    def populate_grid(self):
        col = 0
        row = 0
        last_letter = ''
        for sprite_name in self.trainer_sprites:
            if sprite_name[0].lower() != last_letter:
                last_letter = sprite_name[0].lower()
                col = 0
                row += 1

            sprite_path = os.path.join(trainer_sprites_path, sprite_name + ".png")
            if os.path.exists(sprite_path):
                # Create a widget to hold the button and label
                item_widget = QWidget()
                item_layout = QVBoxLayout(item_widget)
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                button = QPushButton()
                button.setIcon(QIcon(sprite_path))
                button.setIconSize(QSize(100, 100))
                button.setFixedSize(QSize(110, 110))
                button.clicked.connect(lambda _, s=sprite_name: self.on_sprite_clicked(s))
                item_layout.addWidget(button)

                formatted_name = self.format_sprite_name(sprite_name)
                name_label = QLabel(formatted_name)
                name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                item_layout.addWidget(name_label)

                self.grid_layout.addWidget(item_widget, row, col)
                col += 1
                if col >= 6:
                    col = 0
                    row += 1

    def format_sprite_name(self, name):
        return ' '.join(word.capitalize() for word in name.split('-'))

    def on_sprite_clicked(self, sprite_name):
        self.settings.set("trainer.sprite", sprite_name)
        self.accept()

```


## Ankimon/classes/choose_move_dialog.py
*   **Why it was selected**: High structural centrality. It acts as a `UI surface` layer and is imported by 59 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ..functions.pokedex_functions import find_details_move
from ..move_names import format_move_name
import random

class MoveSelectionDialog(QDialog):
    def __init__(self, mainpokemon_attacks):
        super().__init__()

        # Dialog settings
        self.setWindowTitle("Select a Move")
        self.resize(300, 200)
        self.selected_move = random.choice(mainpokemon_attacks)
        self.mainpokemon_attacks = mainpokemon_attacks

        # Create and set layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add a title label
        title_label = QLabel("Press a number (1-4) or click to select a move:")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # Add labels for each move
        self.move_labels = []
        for index, move in enumerate(mainpokemon_attacks):
            move_detail = find_details_move(move)
            move_name = format_move_name(move_detail.get('name', move))
            move_label = QLabel(f"{index + 1}. {move_name}({move_detail.get('basePower', 'Unknown')}): {move_detail.get('shortDesc', 'Unknown')}")
            move_label.setToolTip(f"{move_detail.get('desc', 'No description available')}")
            move_label.setFont(QFont("Arial", 12))
            move_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            move_label.setStyleSheet("border: 1px solid #ccc; border-radius: 0px;")  # Removed padding, reduced border-radius
            move_label.mousePressEvent = self.create_mouse_press_handler(index)
            move_label.setFixedHeight(20)  # Example fixed height for thinner labels
            layout.addWidget(move_label)
            self.move_labels.append(move_label)


    def create_mouse_press_handler(self, index):
        def handle_mouse_press(event):
            self.select_move(index)
        return handle_mouse_press

    def select_move(self, index):
        """Handle move selection and close the dialog."""
        self.selected_move = self.mainpokemon_attacks[index]
        self.accept()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for move selection."""
        key = event.key()
        if Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            move_index = key - Qt.Key.Key_1  # Convert key to list index
            if 0 <= move_index < len(self.mainpokemon_attacks):
                self.select_move(move_index)

```


## Ankimon/poke_engine/data/scripts/parse_random_battle_raw_sets.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 58 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
"""
Parses a text file with lines containing the format:
    pkmn_name|level|move1|move2|move3|move4|ability|item

Creates a JSON file with the data arranged in a way that the bot can use to understand
This was made for the purposes of random battles
"""

import json
from copy import deepcopy
import constants
from showdown.engine.helpers import normalize_name

fp = "../../sets.txt"
pokedex_path = "../pokedex.json"


all_pokemon_dict = dict()


def add_thing_to_dict_or_increment(d, second_key, thing):
    if thing in d[second_key]:
        d[second_key][thing] += 1
    else:
        d[second_key][thing] = 1


with open(pokedex_path, 'r') as f:
    pokedex = json.load(f)


with open(fp, 'r') as f:
    lines = f.readlines()

for l in lines:
    split_lines = l.strip().split('|')
    if len(split_lines) != 8:
        continue
    pkmn = split_lines[0]
    level = int(split_lines[1])
    if pkmn in ['unown', 'ditto']:
        moves = [split_lines[2]]
        ability = split_lines[3]
        item = split_lines[4]
    else:
        moves = split_lines[2:6]
        ability = split_lines[6]
        item = split_lines[7]

    if item.endswith("ite") and item != "eviolite":
        pkmn = pkmn + "mega"
        ability = normalize_name(pokedex[pkmn]["most_likely_ability"])
    elif item.endswith("itex"):
        pkmn = pkmn + "megax"
        ability = normalize_name(pokedex[pkmn]["most_likely_ability"])
    elif item.endswith("itey"):
        pkmn = pkmn + "megay"
        ability = normalize_name(pokedex[pkmn]["most_likely_ability"])

    identifier = "{}".format(pkmn)
    if identifier in all_pokemon_dict:
        all_pokemon_dict[identifier][constants.COUNT] += 1
    else:
        all_pokemon_dict[identifier] = {constants.SETS: dict(), constants.MOVES: dict(), constants.ABILITIES: dict(), constants.ITEMS: dict(), constants.COUNT: 1}

    this_pkmn_dict = all_pokemon_dict[identifier]
    for i, m in enumerate(moves[:]):
        if m == 'return':
            m = 'return102'
            moves[i] = 'return102'
        add_thing_to_dict_or_increment(this_pkmn_dict, constants.MOVES, m)

    this_set = "|".join(sorted(moves))  # + "|" + ability + "|" + item

    moves_identifier = "|".join(sorted(moves))

    add_thing_to_dict_or_increment(this_pkmn_dict, constants.ABILITIES, ability)
    add_thing_to_dict_or_increment(this_pkmn_dict, constants.ITEMS, item)
    add_thing_to_dict_or_increment(this_pkmn_dict, constants.SETS, this_set)


# change raw numbers to percentages
new_json = deepcopy(all_pokemon_dict)
for k, v in all_pokemon_dict.items():
    count = v['count']
    for move_name, move_count in v['moves'].items():
        new_json[k]['moves'][move_name] = round(move_count * 100 / count, 3)

    for item_name, item_count in v['items'].items():
        new_json[k]['items'][item_name] = round(item_count * 100 / count, 3)

    for ability_name, ability_count in v['abilities'].items():
        new_json[k]['abilities'][ability_name] = round(ability_count * 100 / count, 3)

    for set_name, set_count in v['sets'].items():
        new_json[k]['sets'][set_name] = round(set_count * 100 / count, 3)


# put values in list instead of dict
final_json = deepcopy(new_json)
for k, v in new_json.items():
    final_json[k]['abilities'] = list()
    for name, value in v['abilities'].items():
        final_json[k]['abilities'].append(
            (name, value)
        )
    final_json[k]['items'] = list()
    for name, value in v['items'].items():
        final_json[k]['items'].append(
            (name, value)
        )
    final_json[k]['moves'] = list()
    for name, value in v['moves'].items():
        final_json[k]['moves'].append(
            (name, value)
        )
    final_json[k]['spreads'] = [
        (
            "serious",
            "85,85,85,85,85,85",
            100.0
        )
    ]

# dont use ditto sets
final_json.pop("ditto", None)


# dont include pkmn not in pokedex (sometimes the raw file has errors)
for k, v in deepcopy(final_json).items():
    if k not in pokedex:
        final_json.pop(k)


with open("out.json", 'w') as f:
    json.dump(final_json, f, indent=4, sort_keys=True)

```


## Ankimon/pyobj/error_handler.py
*   **Why it was selected**: High structural centrality. It acts as a `state container` layer and is imported by 48 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 109 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import os
import re
import json
import random
import traceback
import requests
import platform
import sys
from pathlib import Path
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from aqt import mw
from anki.buildinfo import version as anki_version

# Path configurations
addon_dir = Path(__file__).parents[1]
pyobj_path = addon_dir / "pyobj"
manifest_path = addon_dir / "manifest.json"

def get_environment_info() -> str:
    """Collect add-on, Anki, Python, and OS version information."""
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        addon_ver = manifest.get("version", "unknown")
    except Exception:
        addon_ver = "unknown"

    py_ver = sys.version.split()[0]
    os_info = platform.platform()
    return f"Ankimon v{addon_ver} | Anki {anki_version} | Python {py_ver} | {os_info}"

def set_image_from_url(label: QLabel, url: str, width: int = 140) -> None:
    """Load and display an image from URL in a QLabel."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        image = QImage()
        image.loadFromData(response.content)
        pixmap = QPixmap.fromImage(image)
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        else:
            label.setText("Image failed to load")
    except Exception:
        label.setText("Image failed to load")

def scrub_traceback(tb_text: str) -> str:
    """Sanitize traceback text by removing user paths."""
    username = os.path.expanduser("~").split(os.sep)[-1]
    patterns = [
        rf"/home/{username}",
        rf"/Users/{username}",
        rf"[A-Z]:/Users/{username}",
        rf"[A-Z]:\\Users\\{username}",
        rf"/usr/home/{username}",
        rf"/export/home/{username}",
    ]
    for pattern in patterns:
        tb_text = re.sub(pattern, "/home/USER", tb_text, flags=re.IGNORECASE)
    return tb_text

def load_error_images(json_path: Path) -> Dict[str, str]:
    """Load and select random error image metadata."""
    default_image = {"path": "", "credit": "", "url": ""}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            error_images = json.load(f)
        return random.choice(error_images)
    except Exception as e:
        mw.logger.log("error", f"Failed to load error images: {str(e)}")
        return default_image

def create_error_label(message: str, exception: Exception) -> QLabel:
    """Create error label with just the message and exception (no environment info)."""
    html = (
        f"<span style='font-size:32px; color:#ffcc00; vertical-align:middle;'>&#9888;</span> "
        f"<span style='font-size:15px; font-weight:600; vertical-align:middle;'>{message}</span><br>"
        f"<pre style='font-size:12px; margin-top:6px; color:#a0a0a0;'>"
        f"{str(exception)}"
        "</pre>"
    )
    label = QLabel(html)
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setWordWrap(True)
    return label

def create_credit_label(chosen_image: Dict[str, str]) -> Optional[QLabel]:
    """Create image credit label with optional link."""
    if not chosen_image.get("credit") or not chosen_image.get("url"):
        return None

    label = QLabel(f'<a href="{chosen_image["url"]}">{chosen_image["credit"]}</a>')
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setOpenExternalLinks(True)
    label.setAlignment(Qt.AlignmentFlag.AlignRight)
    label.setStyleSheet("font-size:10px; color:#aaa;")
    label.setWordWrap(True)
    label.setFixedWidth(140)
    label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
    return label

def build_dialog_ui(dialog: QDialog, message: str, exception: Exception,
                   chosen_image: Dict[str, str]) -> None:
    """Construct dialog UI layout without environment info display."""
    main_layout = QHBoxLayout(dialog)
    main_layout.setContentsMargins(24, 18, 24, 18)
    main_layout.setSpacing(18)

    # Left panel (error information)
    left_layout = QVBoxLayout()
    left_layout.setSpacing(10)
    left_layout.addWidget(create_error_label(message, exception))

    # Friendly message
    friendly_label = QLabel("<i>But no worries, just stay cool!</i> 😎")
    friendly_label.setStyleSheet("color: #a6dcef; font-size: 13px; margin-bottom: 2px;")
    friendly_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    friendly_label.setWordWrap(True)
    left_layout.addWidget(friendly_label)

    # Report links
    links = (
        '<a href="https://discord.gg/rGNywfX436"><b>Report on Discord</b></a> | '
        '<a href="https://github.com/Unlucky-Life/ankimon/issues">Report on GitHub</a>'
    )
    links_label = QLabel(links)
    links_label.setTextFormat(Qt.TextFormat.RichText)
    links_label.setOpenExternalLinks(True)
    links_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    links_label.setStyleSheet("margin-bottom: 4px; font-size: 12px;")
    left_layout.addWidget(links_label)

    # Action buttons
    button_layout = QHBoxLayout()
    for btn in [("Copy Debug Info", "copy"), ("OK", "ok")]:
        button = QPushButton(btn[0])
        button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        button.setObjectName(btn[1])
        button_layout.addWidget(button)
    left_layout.addLayout(button_layout)

    # Right panel (image and credit)
    right_layout = QVBoxLayout()
    right_layout.setSpacing(6)

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def get_environment_info() -> str:
def set_image_from_url(label: QLabel, url: str, width: int = 140) -> None:
def scrub_traceback(tb_text: str) -> str:
def load_error_images(json_path: Path) -> Dict[str, str]:
def create_error_label(message: str, exception: Exception) -> QLabel:
def create_credit_label(chosen_image: Dict[str, str]) -> Optional[QLabel]:
def build_dialog_ui(dialog: QDialog, message: str, exception: Exception,
def setup_dialog_style(dialog: QDialog) -> None:
def show_warning_with_traceback(
    def copy_debug_info():
```


## Ankimon/functions/ankimon_hooks_to_poke_engine.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 45 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 311 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import random
from collections import defaultdict
import copy
import traceback
from typing import Union

from ..poke_engine import constants
from ..singletons import ankimon_tracker_obj, settings_obj
import math

from ..poke_engine.battle import Move
from ..poke_engine.objects import Pokemon, State, StateMutator, Side
from ..poke_engine.helpers import normalize_name
from ..poke_engine.find_state_instructions import get_all_state_instructions
from ..pyobj.error_handler import show_warning_with_traceback

def reset_stat_boosts(pokemon: Pokemon) -> Pokemon:
    """
    Resets all stat boosts of a given Pokemon to zero.

    Args:
        pokemon (Pokemon): The Pokemon whose stat boosts will be reset.

    Returns:
        Pokemon: The same Pokemon object with all stat boosts reset to zero.
    """
    pokemon.attack_boost = 0
    pokemon.defense_boost = 0
    pokemon.special_attack_boost = 0
    pokemon.special_defense_boost = 0
    pokemon.speed_boost = 0
    pokemon.accuracy_boost = 0
    pokemon.evasion_boost = 0
    return pokemon

def reset_side(pokemon: Pokemon, side_conditions: Union[dict, None]=None) -> Side:
    """
    Resets and returns a new Side object for the given Pokemon with default or provided side conditions.

    If no side conditions are provided, a default set with all conditions initialized to zero is used.

    Args:
        pokemon (Pokemon): The active Pokemon for the side.
        side_conditions (Union[dict, None], optional): A dictionary of side conditions to apply.
            If None, defaults to all conditions set to zero.

    Returns:
        Side: A new Side object with the specified active Pokemon, an empty reserve,
              default wish and future sight settings, and the given or default side conditions.
    """
    if side_conditions is None:
        side_conditions = defaultdict(int, {
            'stealthrock': 0,
            'spikes': 0,
            'toxicspikes': 0,
            'tailwind': 0,
            'reflect': 0,
            'lightscreen': 0,
            'auroraveil': 0,
            'protect': 0,
        })
    side = Side(
        active=pokemon,
        reserve={},
        wish=(0, 0),
        side_conditions=side_conditions,
        future_sight=(0, 0),
    )
    return side

def simulate_battle_with_poke_engine(
    main_pokemon: Pokemon,
    enemy_pokemon: Pokemon,
    main_move: str,
    enemy_move: str,
    mutator_full_reset: int,
    state: Union[State, None]=None,
    ):
    """
    Simulates a battle between two Pokémon using the poke-engine if available.
    The function selects the Pokémon moves (either provided or random), handles state changes,
    and applies battle instructions based on the current battle state. The function then
    computes and returns the battle results, including damage dealt, missed moves,
    and the updated battle state.

    Args:
        main_pokemon (Pokemon): The user's active Pokémon.
        enemy_pokemon (Pokemon): The opponent's active Pokémon.
        main_move (str or None): The move chosen by the user's Pokémon. If None, a random move will be selected.
        enemy_move (str or None): The move chosen by the opponent's Pokémon. If None, a random move will be selected.
        new_state (State): The current battle state, including the Pokémon's stats, field conditions, etc.
        mutator_full_reset (int): A flag controlling whether the battle state should be reset.

    Returns:
        tuple: A tuple containing:
            - battle_info (dict): A dictionary with the battle header and instructions for each Pokémon move.
            - new_state (State): The updated battle state after the battle simulation.
            - dmg_from_enemy_move (int): The damage dealt to the user's Pokémon by the enemy.
            - dmg_from_user_move (int): The damage dealt to the enemy's Pokémon by the user.
            - mutator_full_reset (int): The flag indicating if the battle state was reset.

    Raises:
        Exception: If any unexpected error occurs during the simulation, the traceback will be printed.

    Notes:
        - If no moves are provided for the Pokémon, a random move is selected.
        - The outcome of the battle is determined based on probability, with weights reflecting typical battle mechanics.
        - The function prints a summary of the battle result, including damage dealt and whether any moves missed.
        - The state mutator is applied to update the battle state after the moves are resolved.
    """

    # If no move is provided, use a random move
    if main_move is None and main_pokemon.attacks:
        main_move = random.choice(main_pokemon.attacks)
    if enemy_move is None and enemy_pokemon.attacks:
        enemy_move = random.choice(enemy_pokemon.attacks)
    if not main_move:
        main_move = "Splash"
    if not enemy_move:
        enemy_move = "Splash"


    if (state is not None) and (state.user.active.id != main_pokemon.name.lower()):
        mutator_full_reset = 1 # reset AFTER Pokemon is changed !
    if mutator_full_reset not in (0, 1):
        mutator_full_reset = 1

    try:
        main_move_normalized = normalize_name(main_move)
        enemy_move_normalized = normalize_name(enemy_move)


        # Store only the chosen outcome
        battle_header = {
            'user': {
                'name': main_pokemon.name,
                'level': main_pokemon.level,
                'move': main_move
            },
            'opponent': {
                'name': enemy_pokemon.name,
                'level': enemy_pokemon.level,
                'move': enemy_move
            }
        }

        # Create Pokemon objects
        main_pokemon_poke_engine = main_pokemon.to_poke_engine_Pokemon()
        enemy_pokemon_poke_engine = enemy_pokemon.to_poke_engine_Pokemon()


... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def reset_stat_boosts(pokemon: Pokemon) -> Pokemon:
def reset_side(pokemon: Pokemon, side_conditions: Union[dict, None]=None) -> Side:
def simulate_battle_with_poke_engine(
def diff_states(state_before, state_after, path="", changes=None):
def print_state_changes(changes):
```


## Ankimon/functions/battle_functions.py
*   **Why it was selected**: High structural centrality. It acts as a `utility` layer and is imported by 44 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 519 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import copy
import json
from ..poke_engine import constants
from ..pyobj.error_handler import show_warning_with_traceback
from ..move_names import format_move_name

def update_pokemon_battle_status(battle_info: dict, enemy_pokemon, main_pokemon):
    """
    Update Pokemon battle status and volatile status based on battle instructions.
    HP is now handled by the main battle loop to ensure a single source of truth.
    This function now only processes status changes.
    """
    if not isinstance(battle_info, dict) or 'instructions' not in battle_info:
        return False, False

    instructions = battle_info.get('instructions', [])
    if not instructions:
        return False, False

    enemy_status_changed = False
    main_status_changed = False

    try:
        # Initialize volatile_status sets if they don't exist
        if not hasattr(enemy_pokemon, 'volatile_status'):
            enemy_pokemon.volatile_status = set()
        if not hasattr(main_pokemon, 'volatile_status'):
            main_pokemon.volatile_status = set()

        for instr in instructions:
            # Skip malformed instructions or instructions this function doesn't handle
            if not isinstance(instr, (list, tuple)) or len(instr) < 2:
                continue

            action = instr[0]
            target = instr[1]

            # This function only handles status, not damage or heal
            if action in [constants.MUTATOR_DAMAGE, constants.MUTATOR_HEAL]:
                continue

            status_value = instr[2] if len(instr) >= 3 else None

            # Handle regular status application
            if action == constants.MUTATOR_APPLY_STATUS and status_value:
                if target == 'opponent':
                    if enemy_pokemon.battle_status != status_value:
                        enemy_pokemon.battle_status = status_value
                        enemy_status_changed = True
                elif target == 'user':
                    if main_pokemon.battle_status != status_value:
                        main_pokemon.battle_status = status_value
                        main_status_changed = True

            # Handle regular status removal
            elif action == constants.MUTATOR_REMOVE_STATUS:
                if target == 'opponent':
                    if enemy_pokemon.battle_status != 'fighting':
                        enemy_pokemon.battle_status = 'fighting'
                        enemy_status_changed = True
                elif target == 'user':
                    if main_pokemon.battle_status != 'fighting':
                        main_pokemon.battle_status = 'fighting'
                        main_status_changed = True

            # Handle volatile status application
            elif action == constants.MUTATOR_APPLY_VOLATILE_STATUS and status_value:
                if target == 'opponent':
                    if status_value not in enemy_pokemon.volatile_status:
                        enemy_pokemon.volatile_status.add(status_value)
                        enemy_status_changed = True
                elif target == 'user':
                    if status_value not in main_pokemon.volatile_status:
                        main_pokemon.volatile_status.add(status_value)
                        main_status_changed = True

            # Handle volatile status removal
            elif action == constants.MUTATOR_REMOVE_VOLATILE_STATUS and status_value:
                if target == 'opponent':
                    if status_value in enemy_pokemon.volatile_status:
                        enemy_pokemon.volatile_status.discard(status_value)
                        enemy_status_changed = True
                elif target == 'user':
                    if status_value in main_pokemon.volatile_status:
                        main_pokemon.volatile_status.discard(status_value)
                        main_status_changed = True

        # Final check for fainted status based on the already-updated HP from the main loop
        if hasattr(enemy_pokemon, 'hp') and enemy_pokemon.hp <= 0:
            if enemy_pokemon.battle_status != 'fainted':
                enemy_pokemon.battle_status = 'fainted'
                enemy_pokemon.volatile_status = set() # Clear volatiles on faint
                enemy_status_changed = True

        if hasattr(main_pokemon, 'hp') and main_pokemon.hp <= 0:
            if main_pokemon.battle_status != 'fainted':
                main_pokemon.battle_status = 'fainted'
                main_pokemon.volatile_status = set() # Clear volatiles on faint
                main_status_changed = True

        return enemy_status_changed, main_status_changed

    except Exception as e:
        # Use the existing error handler if available, otherwise print
        try:
            from ..pyobj.error_handler import show_warning_with_traceback
            show_warning_with_traceback(e, "Failed to update pokemon battle status")
        except ImportError:
            print(f"ERROR in update_pokemon_battle_status: {e}")
        return False, False


def _process_battle_effects(
    instructions: list,  # Keep for compatibility but won't use
    translator,
    main_pokemon=None,
    enemy_pokemon=None,
    current_state=None,
    changes=None
) -> list:
    """
    Process battle changes with Pokemon names and persistent effect messages.
    This version uses the changes variable instead of instructions to generate messages.
    """
    if not changes or not isinstance(changes, list):
        return []

    effect_messages = []

    def get_pokemon_name(target_side: str) -> str:
        if target_side == 'user':
            return main_pokemon.name.capitalize() if (main_pokemon and hasattr(main_pokemon, 'name')) else "Your Pokemon"
        else:
            return enemy_pokemon.name.capitalize() if (enemy_pokemon and hasattr(enemy_pokemon, 'name')) else "Enemy Pokemon"

    def normalize_status_name(status_name: str) -> str:
        return status_name.lower().replace('_', '').replace(' ', '').replace('-', '')

    def safe_translate(key: str, **kwargs) -> str:
        try:
            if translator:
                result = translator.translate(key, **kwargs)
                if result and result.strip():
                    return result
        except (KeyError, AttributeError, Exception) as e:
            print(f"Translation error for key '{key}': {e}")

        if 'pokemon_name' in kwargs and 'status_name' in kwargs:
            if 'apply' in key or 'still' in key:
                return f"{kwargs['pokemon_name']} is affected by {kwargs['status_name']}!"

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def update_pokemon_battle_status(battle_info: dict, enemy_pokemon, main_pokemon):
def _process_battle_effects(
    def get_pokemon_name(target_side: str) -> str:
    def normalize_status_name(status_name: str) -> str:
    def safe_translate(key: str, **kwargs) -> str:
    def check_persistent_effects():
def validate_pokemon_status(pokemon):
def process_battle_data(
def _handle_special_battle_status(main_pokemon, battle_status: str, translator) -> str:
def calculate_hp(base_stat_hp, level, ev, iv):
```


## Ankimon/poke_engine/helpers.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 44 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 62 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import math
from . import constants

from .data import all_move_json


natures = {
    'lonely': {
        'plus': constants.ATTACK,
        'minus': constants.DEFENSE
    },
    'adamant': {
        'plus': constants.ATTACK,
        'minus': constants.SPECIAL_ATTACK
    },
    'naughty': {
        'plus': constants.ATTACK,
        'minus': constants.SPECIAL_DEFENSE
    },
    'brave': {
        'plus': constants.ATTACK,
        'minus': constants.SPEED
    },
    'bold': {
        'plus': constants.DEFENSE,
        'minus': constants.ATTACK
    },
    'impish': {
        'plus': constants.DEFENSE,
        'minus': constants.SPECIAL_ATTACK
    },
    'lax': {
        'plus': constants.DEFENSE,
        'minus': constants.SPECIAL_DEFENSE
    },
    'relaxed': {
        'plus': constants.DEFENSE,
        'minus': constants.SPEED
    },
    'modest': {
        'plus': constants.SPECIAL_ATTACK,
        'minus': constants.ATTACK
    },
    'mild': {
        'plus': constants.SPECIAL_ATTACK,
        'minus': constants.DEFENSE
    },
    'rash': {
        'plus': constants.SPECIAL_ATTACK,
        'minus': constants.SPECIAL_DEFENSE
    },
    'quiet': {
        'plus': constants.SPECIAL_ATTACK,
        'minus': constants.SPEED
    },
    'calm': {
        'plus': constants.SPECIAL_DEFENSE,
        'minus': constants.ATTACK
    },
    'gentle': {
        'plus': constants.SPECIAL_DEFENSE,
        'minus': constants.DEFENSE
    },
    'careful': {
        'plus': constants.SPECIAL_DEFENSE,
        'minus': constants.SPECIAL_ATTACK
    },
    'sassy': {
        'plus': constants.SPECIAL_DEFENSE,
        'minus': constants.SPEED
    },
    'timid': {
        'plus': constants.SPEED,
        'minus': constants.ATTACK
    },
    'hasty': {
        'plus': constants.SPEED,
        'minus': constants.DEFENSE
    },
    'jolly': {
        'plus': constants.SPEED,
        'minus': constants.SPECIAL_ATTACK
    },
    'naive': {
        'plus': constants.SPEED,
        'minus': constants.SPECIAL_DEFENSE
    },
}


def get_pokemon_info_from_condition(condition_string: str):
    if constants.FNT in condition_string:
        return 0, 0, None

    split_string = condition_string.split("/")
    hp = int(split_string[0])
    if any(s in condition_string for s in constants.NON_VOLATILE_STATUSES):
        maxhp, status = split_string[1].split(' ')
        maxhp = int(maxhp)
        return hp, maxhp, status
    else:
        maxhp = int(split_string[1])
        return hp, maxhp, None


def normalize_name(name):
    return name\
        .replace(" ", "")\
        .replace("-", "")\
        .replace(".", "")\
        .replace("\'", "")\
        .replace("%", "")\
        .replace("*", "")\
        .replace(":", "")\
        .strip()\
        .lower()\
        .encode('ascii', 'ignore')\
        .decode('utf-8')


def set_makes_sense(nature, spread, item, ability, moves):
    if item in constants.CHOICE_ITEMS and any(all_move_json[m.name][constants.CATEGORY] not in constants.DAMAGING_CATEGORIES and m.name != 'trick' for m in moves):
        return False
    return True


def spreads_are_alike(s1, s2):
    if s1[0] != s2[0]:
        return False

    s1 = [int(v) for v in s1[1].split(',')]
    s2 = [int(v) for v in s2[1].split(',')]

    diff = [abs(i-j) for i, j in zip(s1, s2)]

    # 24 is arbitrarily chosen as the threshold for EVs to be "alike"
    return all(v < 24 for v in diff)


def remove_duplicate_spreads(list_of_spreads):
    new_spreads = list()

    for s1 in list_of_spreads:
        if not any(spreads_are_alike(s1, s2) for s2 in new_spreads):
            new_spreads.append(s1)

    return new_spreads


def update_stats_from_nature(stats, nature):

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def get_pokemon_info_from_condition(condition_string: str):
def normalize_name(name):
def set_makes_sense(nature, spread, item, ability, moves):
def spreads_are_alike(s1, s2):
def remove_duplicate_spreads(list_of_spreads):
def update_stats_from_nature(stats, nature):
def common_pkmn_stat_calc(stat: int, iv: int, ev: int, level: int):
def calculate_stats(base_stats, level, ivs=(31,) * 6, evs=(85,) * 6, nature='serious'):
```


## Ankimon/poke_engine/tests/test_helpers.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 44 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 60 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest

from poke_engine.battle import Move
from poke_engine.helpers import get_pokemon_info_from_condition
from poke_engine.helpers import normalize_name
from poke_engine.helpers import set_makes_sense
from poke_engine.helpers import spreads_are_alike
from poke_engine.helpers import remove_duplicate_spreads
from poke_engine.objects import State


class TestBattleIsOver(unittest.TestCase):
    def setUp(self):
        self.state_json = {'user': {'active': {'id': 'keldeo', 'level': 100, 'hp': 323, 'maxhp': 344, 'ability': 'justified', 'item': None, 'baseStats': {'hp': 91, 'attack': 72, 'defense': 90, 'special-attack': 129, 'special-defense': 90, 'speed': 108}, 'attack': 201, 'defense': 237, 'special-attack': 315, 'special-defense': 237, 'speed': 273, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 1, 'special_defense_boost': 1, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'calmmind', 'disabled': False, 'current_pp': 31}, {'id': 'hydropump', 'disabled': False, 'current_pp': 7}, {'id': 'secretsword', 'disabled': False, 'current_pp': 15}, {'id': 'taunt', 'disabled': False, 'current_pp': 32}], 'types': ['water', 'fighting'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': True}, 'reserve': {'landorustherian': {'id': 'landorustherian', 'level': 100, 'hp': 319, 'maxhp': 340, 'ability': 'intimidate', 'item': None, 'baseStats': {'hp': 89, 'attack': 145, 'defense': 90, 'special-attack': 105, 'special-defense': 80, 'speed': 91}, 'attack': 347, 'defense': 237, 'special-attack': 267, 'special-defense': 217, 'speed': 239, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32}, {'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'explosion', 'disabled': False, 'current_pp': 8}, {'id': 'swordsdance', 'disabled': False, 'current_pp': 32}], 'types': ['ground', 'flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}, 'tornadustherian': {'id': 'tornadustherian', 'level': 100, 'hp': 362, 'maxhp': 320, 'ability': 'regenerator', 'item': None, 'baseStats': {'hp': 79, 'attack': 100, 'defense': 80, 'special-attack': 110, 'special-defense': 90, 'speed': 121}, 'attack': 257, 'defense': 217, 'special-attack': 277, 'special-defense': 237, 'speed': 299, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'hurricane', 'disabled': False, 'current_pp': 16}, {'id': 'defog', 'disabled': False, 'current_pp': 24}, {'id': 'knockoff', 'disabled': False, 'current_pp': 32}, {'id': 'uturn', 'disabled': False, 'current_pp': 32}], 'types': ['flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}, 'diancie': {'id': 'diancie', 'level': 100, 'hp': 241, 'maxhp': 262, 'ability': 'clearbody', 'item': None, 'baseStats': {'hp': 50, 'attack': 100, 'defense': 150, 'special-attack': 100, 'special-defense': 150, 'speed': 50}, 'attack': 257, 'defense': 357, 'special-attack': 257, 'special-defense': 357, 'speed': 157, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'moonblast', 'disabled': False, 'current_pp': 24}, {'id': 'diamondstorm', 'disabled': False, 'current_pp': 8}, {'id': 'substitute', 'disabled': False, 'current_pp': 16}, {'id': 'endeavor', 'disabled': False, 'current_pp': 8}], 'types': ['rock', 'fairy'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}, 'victini': {'id': 'victini', 'level': 100, 'hp': 341, 'maxhp': 362, 'ability': 'victorystar', 'item': None, 'baseStats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100, 'special-defense': 100, 'speed': 100}, 'attack': 257, 'defense': 257, 'special-attack': 257, 'special-defense': 257, 'speed': 257, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'vcreate', 'disabled': False, 'current_pp': 8}, {'id': 'boltstrike', 'disabled': False, 'current_pp': 8}, {'id': 'uturn', 'disabled': False, 'current_pp': 32}, {'id': 'finalgambit', 'disabled': False, 'current_pp': 8}], 'types': ['psychic', 'fire'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}, 'bisharp': {'id': 'bisharp', 'level': 100, 'hp': 271, 'maxhp': 292, 'ability': 'defiant', 'item': None, 'baseStats': {'hp': 65, 'attack': 125, 'defense': 100, 'special-attack': 60, 'special-defense': 70, 'speed': 70}, 'attack': 307, 'defense': 257, 'special-attack': 177, 'special-defense': 197, 'speed': 197, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'knockoff', 'disabled': False, 'current_pp': 32}, {'id': 'ironhead', 'disabled': False, 'current_pp': 24}, {'id': 'suckerpunch', 'disabled': False, 'current_pp': 8}, {'id': 'swordsdance', 'disabled': False, 'current_pp': 32}], 'types': ['dark', 'steel'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}}, 'wish': (0, 0), 'futuresight': (0, 0), 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'opponent': {'active': {'id': 'manaphy', 'level': 100, 'hp': 86.88, 'maxhp': 362, 'ability': 'hydration', 'item': 'Leftovers', 'baseStats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100, 'special-defense': 100, 'speed': 100}, 'attack': 257, 'defense': 257, 'special-attack': 257, 'special-defense': 257, 'speed': 257, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 6, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'tailglow', 'disabled': False, 'current_pp': 32}], 'types': ['water'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': True}, 'reserve': {'mamoswine': {'id': 'mamoswine', 'level': 100, 'hp': 382, 'maxhp': 382, 'ability': None, 'item': None, 'baseStats': {'hp': 110, 'attack': 130, 'defense': 80, 'special-attack': 70, 'special-defense': 60, 'speed': 80}, 'attack': 317, 'defense': 217, 'special-attack': 197, 'special-defense': 177, 'speed': 217, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['ice', 'ground'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}, 'alakazam': {'id': 'alakazam', 'level': 100, 'hp': 272, 'maxhp': 272, 'ability': None, 'item': None, 'baseStats': {'hp': 55, 'attack': 50, 'defense': 45, 'special-attack': 135, 'special-defense': 95, 'speed': 120}, 'attack': 157, 'defense': 147, 'special-attack': 327, 'special-defense': 247, 'speed': 297, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['psychic'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}, 'stakataka': {'id': 'stakataka', 'level': 100, 'hp': 284, 'maxhp': 284, 'ability': 'beastboost', 'item': None, 'baseStats': {'hp': 61, 'attack': 131, 'defense': 211, 'special-attack': 53, 'special-defense': 101, 'speed': 13}, 'attack': 319, 'defense': 479, 'special-attack': 163, 'special-defense': 259, 'speed': 83, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['rock', 'steel'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}, 'moltres': {'id': 'moltres', 'level': 100, 'hp': 342, 'maxhp': 342, 'ability': None, 'item': None, 'baseStats': {'hp': 90, 'attack': 100, 'defense': 90, 'special-attack': 125, 'special-defense': 85, 'speed': 90}, 'attack': 257, 'defense': 237, 'special-attack': 307, 'special-defense': 227, 'speed': 237, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['fire', 'flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}, 'gliscor': {'id': 'gliscor', 'level': 100, 'hp': 312, 'maxhp': 312, 'ability': None, 'item': None, 'baseStats': {'hp': 75, 'attack': 95, 'defense': 125, 'special-attack': 45, 'special-defense': 75, 'speed': 95}, 'attack': 247, 'defense': 307, 'special-attack': 147, 'special-defense': 207, 'speed': 247, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['ground', 'flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85), 'terastallized': False}}, 'wish': (0, 0), 'futuresight': (0, 0), 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'weather': None, 'field': None, 'forceSwitch': False, 'wait': False, 'trickroom': False}
        self.state = State.from_dict(self.state_json)

    def test_returns_true_when_all_pokemon_for_user_are_dead(self):
        self.state.user.active.hp = 0
        for pkmn in self.state.user.reserve.values():
            pkmn.hp = 0

        self.assertTrue(self.state.battle_is_finished())

    def test_returns_true_when_all_pokemon_for_opponent_are_dead(self):
        self.state.opponent.active.hp = 0
        for pkmn in self.state.opponent.reserve.values():
            pkmn.hp = 0

        self.assertTrue(self.state.battle_is_finished())

    def test_returns_false_when_all_pokemon_are_alive(self):
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_only_active_is_dead(self):
        self.state.opponent.active.hp = 0
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_only_reserve_are_dead(self):
        for pkmn in self.state.user.reserve.values():
            pkmn.hp = 0
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_all_pokemon_are_alive_for_opponent(self):
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_only_active_is_dead_for_opponent(self):
        self.state.opponent.active.hp = 0
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_only_reserve_are_dead_for_opponent(self):
        for pkmn in self.state.opponent.reserve.values():
            pkmn.hp = 0
        self.assertFalse(self.state.battle_is_finished())


class TestSpreadsAreAlike(unittest.TestCase):
    def test_two_similar_spreads_are_alike(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('jolly', '0,0,4,252,0,252')

        self.assertTrue(spreads_are_alike(s1, s2))

    def test_different_natures_are_not_alike(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('modest', '0,0,4,252,0,252')

        self.assertFalse(spreads_are_alike(s1, s2))

    def test_custom_is_not_the_same_as_max_values(self):
        s1 = ('jolly', '16,0,0,252,0,240')
        s2 = ('modest', '0,0,4,252,0,252')

        self.assertFalse(spreads_are_alike(s1, s2))

    def test_very_similar_returns_true(self):
        s1 = ('modest', '16,0,0,252,0,240')
        s2 = ('modest', '28,0,4,252,0,252')

        self.assertTrue(spreads_are_alike(s1, s2))


class TestRemoveDuplicateSpreads(unittest.TestCase):
    def test_only_one_spread_remains_when_all_are_alike(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('jolly', '0,0,4,252,0,252')
        s3 = ('jolly', '0,4,0,252,0,252')
        s4 = ('jolly', '4,0,0,252,0,252')

        spreads = [s1, s2, s3, s4]

        expected_result = [s1]

        self.assertEqual(expected_result, remove_duplicate_spreads(spreads))

    def test_different_spreads_remain(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('adamant', '0,0,4,252,0,252')
        s3 = ('jolly', '0,4,0,252,0,252')
        s4 = ('jolly', '4,0,0,252,0,252')

        spreads = [s1, s2, s3, s4]

        expected_result = [s1, s2]

        self.assertEqual(expected_result, remove_duplicate_spreads(spreads))

    def test_all_spreads_remain(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('adamant', '0,0,4,252,0,252')
        s3 = ('jolly', '0,108,0,148,0,252')
        s4 = ('adamant', '104,0,0,152,0,252')

        spreads = [s1, s2, s3, s4]

        expected_result = [s1, s2, s3, s4]

        self.assertEqual(expected_result, remove_duplicate_spreads(spreads))


class TestSetMakesSense(unittest.TestCase):
    def test_standard_set_makes_sense(self):
        nature = 'jolly'
        spread = '0,0,0,252,4,252'
        item = 'unknown_item'
        ability = 'intimidate'
        moves = []

        self.assertTrue(set_makes_sense(nature, spread, item, ability, moves))

    def test_swordsdance_with_choiceband_does_not_make_sense(self):
        nature = 'jolly'
        spread = '0,0,0,252,4,252'
        item = 'choiceband'
        ability = 'intimidate'
        moves = [Move('swordsdance')]

        self.assertFalse(set_makes_sense(nature, spread, item, ability, moves))

    def test_nastyplot_with_choicespecs_does_not_make_sense(self):
        nature = 'jolly'
        spread = '0,0,0,252,4,252'
        item = 'choicespecs'
        ability = 'intimidate'
        moves = [Move('nastyplot')]

        self.assertFalse(set_makes_sense(nature, spread, item, ability, moves))

    def test_multiple_move_nastyplot_with_choicespecs_does_not_make_sense(self):
        nature = 'jolly'
        spread = '0,0,0,252,4,252'

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestBattleIsOver(unittest.TestCase):
    def setUp(self):
    def test_returns_true_when_all_pokemon_for_user_are_dead(self):
    def test_returns_true_when_all_pokemon_for_opponent_are_dead(self):
    def test_returns_false_when_all_pokemon_are_alive(self):
    def test_returns_false_when_only_active_is_dead(self):
    def test_returns_false_when_only_reserve_are_dead(self):
    def test_returns_false_when_all_pokemon_are_alive_for_opponent(self):
    def test_returns_false_when_only_active_is_dead_for_opponent(self):
    def test_returns_false_when_only_reserve_are_dead_for_opponent(self):
class TestSpreadsAreAlike(unittest.TestCase):
    def test_two_similar_spreads_are_alike(self):
    def test_different_natures_are_not_alike(self):
    def test_custom_is_not_the_same_as_max_values(self):
    def test_very_similar_returns_true(self):
class TestRemoveDuplicateSpreads(unittest.TestCase):
    def test_only_one_spread_remains_when_all_are_alike(self):
    def test_different_spreads_remain(self):
    def test_all_spreads_remain(self):
class TestSetMakesSense(unittest.TestCase):
    def test_standard_set_makes_sense(self):
    def test_swordsdance_with_choiceband_does_not_make_sense(self):
    def test_nastyplot_with_choicespecs_does_not_make_sense(self):
    def test_multiple_move_nastyplot_with_choicespecs_does_not_make_sense(self):
    def test_trick_with_scarf_makes_sense(self):
class TestNormalizeName(unittest.TestCase):
    def test_removes_nonascii_characters(self):
class TestGetPokemonInfoFromCondition(unittest.TestCase):
    def setUp(self):
    def test_basic_case(self):
    def test_burned_case(self):
    def test_poisoned_case(self):
    def test_fainted_case(self):
```


## Ankimon/poke_engine/data/helpers.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 44 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from .. import constants

from .. import data
from ..data import pokedex
from ..data.parse_smogon_stats import get_smogon_stats_file_name
from ..data.parse_smogon_stats import get_pokemon_information

from ..data.parse_smogon_stats import MOVES_STRING
from ..data.parse_smogon_stats import SPREADS_STRING
from ..data.parse_smogon_stats import ABILITY_STRING
from ..data.parse_smogon_stats import ITEM_STRING

import logging
logger = logging.getLogger(__name__)


# these items will either reveal themselves automatically, or do not have a meaningful impact to the bot
# therefore, we do not want to assign them to a pokemon as a guess
PASS_ITEMS = {
    'leftovers',
    'focussash',
    'blacksludge',
    'airballoon'
}

# these abilities either reveal themselves automatically, or do not have a meaningful impact to the bot
# therefore, we do not want to assign them to a pokemon as a guess
PASS_ABILITIES = {
    'moldbreaker',
    'pressure',
    'trace',
    'download'
}

MAX_STANDARD_BATTLE_MOVES = 6


def get_pokemon_sets(pkmn):
    try:
        return data.pokemon_sets[pkmn]
    except KeyError:
        possible_names = [p for p in data.pokemon_sets if pkmn.startswith(p)]
        if not possible_names:
            raise KeyError
        else:
            new_name = possible_names[0]
            logger.debug("{} not in the sets lookup, using {} instead".format(pkmn, new_name))
            return data.pokemon_sets[new_name]


def get_all_possible_moves_for_random_battle(pkmn_name, known_moves):
    try:
        sets = data.random_battle_sets[pkmn_name]
    except KeyError:
        logger.warning("{} not in the random-battle sets lookup".format(pkmn_name))
        return []

    new_moves = list()
    for key in sets[constants.SETS]:
        this_set_moves = key.split('|')
        if all(m in this_set_moves for m in known_moves):
            for m in filter(lambda x: x not in new_moves + known_moves, this_set_moves):
                new_moves.append(m)

    if not new_moves:
        for m, _ in sets[constants.MOVES]:
            if m not in known_moves:
                new_moves.append(m)

    return new_moves


def get_most_likely_ability_for_random_battle(pkmn_name):
    try:
        sets = data.random_battle_sets[pkmn_name]
    except KeyError:
        logger.warning("{} not in the random-battle sets lookup".format(pkmn_name))
        return None

    abilities = sets[constants.ABILITIES]
    if not abilities:
        logger.warning("{} has no abilities in the random-battle lookup!")
        return None

    best_ability = None
    best_value = float('-inf')
    for ability, value in sorted(abilities, key=lambda x: x[1], reverse=True):
        if value > best_value and ability not in PASS_ABILITIES:
            best_value = value
            best_ability = ability

    return best_ability


def get_most_likely_item_for_random_battle(pkmn_name):
    try:
        sets = data.random_battle_sets[pkmn_name]
    except KeyError:
        logger.warning("{} not in the random-battle sets lookup".format(pkmn_name))
        return None

    best_item = None
    best_value = float('-inf')
    for item, value in sets[constants.ITEMS]:
        if value > best_value and item not in PASS_ITEMS:
            best_item = item
            best_value = value

    return best_item


def get_all_likely_moves(pkmn_name, known_moves):
    try:
        sets = get_pokemon_sets(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return get_all_possible_moves_for_random_battle(pkmn_name, known_moves)

    new_move_count = MAX_STANDARD_BATTLE_MOVES - len(known_moves)
    moves_added = 0
    new_moves = list()
    for m in [mv[0] for mv in sets[MOVES_STRING]]:
        if m not in known_moves:
            new_moves.append(m)
            moves_added += 1
        if moves_added == new_move_count:
            return new_moves

    return new_moves


def get_most_likely_ability(pkmn_name):
    try:
        sets = get_pokemon_sets(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup, using random battle abilities".format(pkmn_name))
        return get_most_likely_ability_for_random_battle(pkmn_name)

    return sets[ABILITY_STRING][0][0]


def get_most_likely_item(pkmn_name):
    try:
        sets = get_pokemon_sets(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup, using random battle items".format(pkmn_name))
        return get_most_likely_item_for_random_battle(pkmn_name)

    for item in [i[0] for i in sets[ITEM_STRING]]:
        if item not in PASS_ITEMS:
            return item
    else:
        return None


def get_most_likely_spread(pkmn_name):
    try:
        sets = get_pokemon_sets(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return 'serious', "85,85,85,85,85,85", 0

    return sets[SPREADS_STRING][0]


def get_standard_battle_sets(battle_mode, pokemon_names=None):
    if any(battle_mode.endswith(s) for s in constants.SMOGON_HAS_STATS_PAGE_SUFFIXES):
        smogon_stats_file_name = get_smogon_stats_file_name(battle_mode)
        logger.debug("Making HTTP request to {} for usage stats".format(smogon_stats_file_name))
        smogon_usage_data = get_pokemon_information(smogon_stats_file_name, pkmn_names=pokemon_names)
    else:
        # use ALL data for a mode like battle-factory
        logger.debug("Making HTTP request for ALL usage stats\nplease wait...")
        ubers_data = get_pokemon_information(get_smogon_stats_file_name("gen9ubers"), pkmn_names=pokemon_names)
        ou_data = get_pokemon_information(get_smogon_stats_file_name("gen9ou"), pkmn_names=pokemon_names)
        uu_data = get_pokemon_information(get_smogon_stats_file_name("gen9uu"), pkmn_names=pokemon_names)
        ru_data = get_pokemon_information(get_smogon_stats_file_name("gen9ru"), pkmn_names=pokemon_names)
        nu_data = get_pokemon_information(get_smogon_stats_file_name("gen9nu"), pkmn_names=pokemon_names)
        pu_data = get_pokemon_information(get_smogon_stats_file_name("gen9pu"), pkmn_names=pokemon_names)
        lc_data = get_pokemon_information(get_smogon_stats_file_name("gen9lc"), pkmn_names=pokemon_names)

        smogon_usage_data = lc_data
        for pkmn_data in [pu_data, nu_data, ru_data, uu_data, ou_data, ubers_data]:
            for pkmn_name in pkmn_data:
                if pkmn_name not in smogon_usage_data:
                    smogon_usage_data[pkmn_name] = pkmn_data[pkmn_name]

    return smogon_usage_data


def get_mega_pkmn_name(pkmn_name):
    mega_name = "{}mega".format(pkmn_name)
    if mega_name in pokedex:
        return mega_name
    elif mega_name + "x" in pokedex:  # for megas with two evolutions, return the x version
        return mega_name + "x"
    return None

```


## Ankimon/poke_engine/special_effects/abilities/before_move.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 44 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from ...data import pokedex
from ... import constants
from ...helpers import calculate_stats


def stancechange(state, attacking_side, attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_pokemon.id in ['aegislash', 'aegislashblade']:
        if attacking_move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES:
            change_stats_into = 'aegislashblade'
        elif attacking_move[constants.ID] == 'kingsshield':
            change_stats_into = 'aegislash'
        else:
            return None

        new_stats = calculate_stats(
            pokedex[change_stats_into][constants.BASESTATS],
            attacking_pokemon.level,
            nature=attacking_pokemon.nature,
            evs=attacking_pokemon.evs
        )

        return [
            (
                constants.MUTATOR_CHANGE_STATS,
                attacking_side,
                (
                    attacking_pokemon.maxhp,
                    new_stats[constants.ATTACK],
                    new_stats[constants.DEFENSE],
                    new_stats[constants.SPECIAL_ATTACK],
                    new_stats[constants.SPECIAL_DEFENSE],
                    attacking_pokemon.speed
                ),
                (
                    attacking_pokemon.hp,
                    attacking_pokemon.attack,
                    attacking_pokemon.defense,
                    attacking_pokemon.special_attack,
                    attacking_pokemon.special_defense,
                    attacking_pokemon.speed
                )
            )

        ]
    return None


def protean(state, attacking_side, attacking_move, attacking_pokemon, defending_pokemon):
    if (
        [attacking_move[constants.TYPE]] != attacking_pokemon.types and
        constants.TYPECHANGE not in attacking_pokemon.volatile_status
    ):
        return [
            (
                constants.MUTATOR_CHANGE_TYPE,
                attacking_side,
                [attacking_move[constants.TYPE]],
                attacking_pokemon.types
            ),
            (
                constants.MUTATOR_APPLY_VOLATILE_STATUS,
                attacking_side,
                constants.TYPECHANGE
            )
        ]


libero = protean


def ability_before_move(ability_name, state, attacking_side, attacking_move, attacking_pokemon, defending_pokemon):
    try:
        return globals()[ability_name](state, attacking_side, attacking_move, attacking_pokemon, defending_pokemon)
    except KeyError:
        return None

```


## Ankimon/functions/pokedex_functions.py
*   **Why it was selected**: High structural centrality. It acts as a `utility` layer and is imported by 43 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 501 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from typing import Literal
from ..resources import (
    pokedex_path,
    pokedesc_lang_path,
    pokenames_lang_path,
    learnset_path,
    moves_file_path,
    poke_evo_path,
    poke_species_path,
    csv_file_items_cost,
    stats_csv,
    pokemon_csv,
)
from aqt.utils import showWarning
from aqt import mw
import json
import random
import csv
from ..pyobj.error_handler import show_warning_with_traceback

GROWTH_RATES = {
    1: "slow",
    2: "medium",
    3: "fast",
    4: "medium-slow",
    5: "slow-then-very-fast",
    6: "fast-then-very-slow"
}

STATS = {
    1: "hp",
    2: "attack",
    3: "defense",
    4: "special-attack",
    5: "special-defense",
    6: "speed",
}

def _normalize_language_id(language):
    """Map unsupported language IDs to a fallback that exists in data files."""
    try:
        lang = int(language)
    except Exception:
        return 9  # default to English on any parsing issue
    if lang == 14:  # Spanish (LatAm) falls back to Spanish data
        return 7
    return lang


def special_pokemon_names_for_min_level(name):
    if name == "flabébé":
        return "flabebe"
    elif name == "sirfetch'd":
        return "sirfetchd"
    elif name == "farfetch'd":
        return "farfetchd"
    elif name == "porygon-z":
        return "porygonz"
    elif name == "kommo-o":
        return "kommoo"
    elif name == "hakamo-o":
        return "hakamoo"
    elif name == "jangmo-o":
        return "jangmoo"
    elif name == "mr. rime":
        return "mrrime"
    elif name == "mr. mime":
        return "mrmime"
    elif name == "mime jr.":
        return "mimejr"
    elif name == "nidoran♂":
        return "nidoranm"
    elif name == "nidoran":
        return "nidoranf"
    elif name == "keldeo[e]":
        return "keldeo"
    elif name == "mew[e]":
        return "mew"
    elif name == "deoxys[e]":
        return "deoxys"
    elif name == "jirachi[e]":
        return "jirachi"
    elif name == "arceus[e]":
        return "arceus"
    elif name == "shaymin[e]":
        return "shaymin-land"
    elif name == "darkrai [e]":
        return "darkrai"
    elif name == "manaphy[e]":
        return "manaphy"
    elif name == "phione[e]":
        return "phione"
    elif name == "celebi[e]":
        return "celebi"
    elif name == "magearna[e]":
        return "magearna"
    elif name == "type: null" or name == "type-null":
        return "typenull"
    elif name == "ho-oh":
        return "hooh"
    elif name == "tapu-koko":
        return "tapukoko"
    elif name == "tapu-lele":
        return "tapulele"
    elif name == "tapu-bulu":
        return "tapubulu"
    elif name == "tapu-fini":
        return "tapufini"
    elif name == "ting-lu":
        return "tinglu"
    elif name == "chien-pao":
        return "chienpao"
    elif name == "wo-chien":
        return "wochien"
    elif name == "chi-yu":
        return "chiyu"
    else:
        return name


def search_pokedex(pokemon_name, variable):
    try:
        pokemon_name = special_pokemon_names_for_min_level(pokemon_name)
        with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)

        # Create a copy of the name to modify
        current_name = pokemon_name

        while True:
            # 1. Try to find a match with the current name
            if current_name in pokedex_data:
                pokemon_info = pokedex_data[current_name]
                var = pokemon_info.get(variable)
                if var is not None:
                    return var

            # 2. If no match, find the last hyphen
            last_hyphen_index = current_name.rfind("-")

            # 3. If no hyphen is found, we can't shorten the name anymore.
            if last_hyphen_index == -1:
                break

            # 4. Remove the suffix and try again in the next iteration
            current_name = current_name[:last_hyphen_index]

        # 5. If no match was ever found, return an empty list
        return []


... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def _normalize_language_id(language):
def special_pokemon_names_for_min_level(name):
def search_pokedex(pokemon_name, variable):
def search_pokedex_by_id(species_id):
def get_mainpokemon_evo(pokemon_name):
def get_growth_rate(species_id: int) -> str:
def get_base_experience(actual_id: int) -> int:
def get_effort_values(actual_id: int) -> dict[str, int]:
def get_pokemon_descriptions(species_id, language):
def get_pokemon_diff_lang_name(pokemon_id: int, language: int):
def extract_ids_from_file():
def find_details_move(move_name: str) -> dict:
def get_pokemon_evolution_data_all(pokemon_id, file_path=poke_evo_path):
def check_evolution_by_item(pokemon_id, item_id, file_path=poke_evo_path):
def check_evolution_for_pokemon(
def check_if_evolution_exists(pokemon_id):
def pokemon_evolves_from_id(pokemon_id):
def get_pokemon_evolution_data(pokemon_id):
def check_key_in_table(column_name, value, file_path):
def return_name_for_id(pokemon_id):
def return_id_for_item_name(item_name):
```


## Ankimon/poke_engine/tests/test_battle_mechanics.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 13926 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
"""
TestBattleMechanics is the main Pokemon engine test class
All battle mechanics are tested in this TestCase
"""


import unittest
from unittest import mock

from poke_engine.config import ShowdownConfig
from poke_engine import constants
from collections import defaultdict
from copy import deepcopy
from poke_engine.objects import TransposeInstruction
from poke_engine.find_state_instructions import get_all_state_instructions
from poke_engine.find_state_instructions import remove_duplicate_instructions
from poke_engine.find_state_instructions import lookup_move
from poke_engine.find_state_instructions import user_moves_first
from poke_engine.objects import State
from poke_engine.objects import Pokemon
from poke_engine.objects import Side
from poke_engine.battle import Pokemon as StatePokemon
from poke_engine.objects import StateMutator


class TestBattleMechanics(unittest.TestCase):
    def setUp(self):
        ShowdownConfig.damage_calc_type = "average"  # some tests may override this
        self.state = State(
                        Side(
                            Pokemon.from_state_pokemon_dict(StatePokemon("raichu", 73).to_dict()),
                            {
                                "xatu": Pokemon.from_state_pokemon_dict(StatePokemon("xatu", 81).to_dict()),
                                "starmie": Pokemon.from_state_pokemon_dict(StatePokemon("starmie", 81).to_dict()),
                                "gyarados": Pokemon.from_state_pokemon_dict(StatePokemon("gyarados", 81).to_dict()),
                                "dragonite": Pokemon.from_state_pokemon_dict(StatePokemon("dragonite", 81).to_dict()),
                                "hitmonlee": Pokemon.from_state_pokemon_dict(StatePokemon("hitmonlee", 81).to_dict()),
                            },
                            (0, 0),
                            defaultdict(lambda: 0),
                            (0,"some_pkmn")
                        ),
                        Side(
                            Pokemon.from_state_pokemon_dict(StatePokemon("aromatisse", 81).to_dict()),
                            {
                                "yveltal": Pokemon.from_state_pokemon_dict(StatePokemon("yveltal", 73).to_dict()),
                                "slurpuff": Pokemon.from_state_pokemon_dict(StatePokemon("slurpuff", 73).to_dict()),
                                "victini": Pokemon.from_state_pokemon_dict(StatePokemon("victini", 73).to_dict()),
                                "toxapex": Pokemon.from_state_pokemon_dict(StatePokemon("toxapex", 73).to_dict()),
                                "bronzong": Pokemon.from_state_pokemon_dict(StatePokemon("bronzong", 73).to_dict()),
                            },
                            (0, 0),
                            defaultdict(lambda: 0),
                            (0,"some_pkmn")
                        ),
                        None,
            None,
            False
                    )

        self.mutator = StateMutator(self.state)

    def test_two_pokemon_switching(self):
        bot_move = "switch xatu"
        opponent_move = "switch yveltal"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'user', 'raichu', 'xatu'),
                    ('switch', 'opponent', 'aromatisse', 'yveltal')
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_powder_move_into_tackle_produces_correct_states(self):
        bot_move = "sleeppowder"
        opponent_move = "tackle"
        self.state.opponent.active.types = ['grass']
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.USER, 35)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_superpower_correctly_unboosts_opponent(self):
        bot_move = "splash"
        opponent_move = "superpower"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.USER, 101),
                    (constants.MUTATOR_BOOST, constants.OPPONENT, constants.ATTACK, -1),
                    (constants.MUTATOR_BOOST, constants.OPPONENT, constants.DEFENSE, -1),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_psyshock_damage_is_the_same_regardless_of_spdef_boost(self):
        bot_move = "psyshock"
        opponent_move = "splash"
        self.state.opponent.active.special_defense_boost = 0
        instructions_without_spdef_boost = get_all_state_instructions(self.mutator, bot_move, opponent_move)

        self.state.opponent.active.special_defense_boost = 6
        instructions_when_spdef_is_maxed = get_all_state_instructions(self.mutator, bot_move, opponent_move)

        self.assertEqual(instructions_without_spdef_boost, instructions_when_spdef_is_maxed)

    def test_bodypress_damage_is_the_same_regardless_of_attack(self):
        bot_move = "bodypress"
        opponent_move = "splash"
        self.state.user.active.attack_boost = 0
        instructions_with_0_attack_boost = get_all_state_instructions(self.mutator, bot_move, opponent_move)

        self.state.user.active.attack_boost = 6
        instructions_with_6_attack_boost = get_all_state_instructions(self.mutator, bot_move, opponent_move)

        self.assertEqual(instructions_with_0_attack_boost, instructions_with_6_attack_boost)

    def test_bodypress_damage_is_different_with_different_defense_stats(self):
        bot_move = "bodypress"
        opponent_move = "splash"
        self.state.user.active.defense_boost = 0
        instructions_with_0_attack_boost = get_all_state_instructions(self.mutator, bot_move, opponent_move)

        self.state.user.active.defense_boost = 6
        instructions_with_6_attack_boost = get_all_state_instructions(self.mutator, bot_move, opponent_move)

        self.assertNotEqual(instructions_with_0_attack_boost, instructions_with_6_attack_boost)

    def test_powder_into_powder_gives_correct_states(self):
        bot_move = "sleeppowder"
        opponent_move = "sleeppowder"

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestBattleMechanics(unittest.TestCase):
    def setUp(self):
    def test_two_pokemon_switching(self):
    def test_powder_move_into_tackle_produces_correct_states(self):
    def test_superpower_correctly_unboosts_opponent(self):
    def test_psyshock_damage_is_the_same_regardless_of_spdef_boost(self):
    def test_bodypress_damage_is_the_same_regardless_of_attack(self):
    def test_bodypress_damage_is_different_with_different_defense_stats(self):
    def test_powder_into_powder_gives_correct_states(self):
    def test_focuspunch_into_non_damaging_move_gives_correct_states(self):
    def test_focuspunch_into_damaging_move_gives_correct_states(self):
    def test_whirlwind_removes_status_boosts(self):
    def test_pkmn_with_guarddog_cannot_be_dragged(self):
    def test_pkmn_with_goodasgold_cannot_be_dragged(self):
    def test_haze_removes_status_boosts(self):
    def test_haze_removes_status_boosts_for_both_sides(self):
    def test_boosting_move_into_haze(self):
    def test_clearsmog_removes_status_boosts(self):
    def test_seismic_toss_deals_damage_by_level(self):
    def test_ghost_immune_to_seismic_toss(self):
    def test_normal_immune_to_night_shade(self):
    def test_ground_immune_to_aurawheel(self):
    def test_ground_not_immune_to_aurawheel_when_morpeko_hangry_is_active(self):
    def test_contrary_boosts_leafstorm(self):
    def test_contact_move_into_static_results_in_two_states_where_one_is_paralysis(self):
    def test_contact_move_into_flamebody_results_in_two_states_where_one_is_burned(self):
    def test_protectivepads_protects_from_flamebody(self):
    def test_doubleshock_fails_if_user_is_not_electric(self):
    def test_doubleshock_changes_user_type(self):
    def test_fire_type_is_immune_to_flamebody_burn(self):
    def test_poinsoned_pokemon_cannot_be_burned_by_flamebody(self):
    def test_protectivepads_causes_static_to_not_trigger(self):
    def test_paralysis_from_same_turn_makes_flamebody_not_trigger(self):
    def test_electric_type_is_immune_to_static(self):
    def test_ground_type_is_not_immune_to_static(self):
    def test_move_missing_does_not_trigger_static(self):
    def test_non_contact_move_does_not_activate_static(self):
    def test_contrary_unboosts_meteormash(self):
    def test_dragondance_with_contrary(self):
    def test_strengthsap_lowers_attack_and_heals_user(self):
    def test_strengthsap_does_not_overheal(self):
    def test_strengthsap_when_targets_attack_is_lowered(self):
    def test_thickclub_with_random_pokemon_does_not_double_attack(self):
    def test_thickclub_with_marowak_doubles_attack(self):
    def test_thickclub_with_marowak_does_not_double_special_attack(self):
    def test_prankster_spore_does_not_work_on_dark_type(self):
    def test_prankster_physical_move_has_the_same_effect_on_dark_type(self):
    def test_prankster_glare_works_on_non_dark_type(self):
    def test_prankster_spore_works_on_non_dark_type(self):
    def test_sound_move_goes_through_substitute(self):
    def test_infiltrator_move_goes_through_sub(self):
    def test_substitute_breaks_when_pkmn_behind_it_has_1_health(self):
    def test_revelationdance_changes_type(self):
    def test_lowkick_does_damage_on_light_pokemon(self):
    def test_grassknot_does_damage_on_light_pokemon(self):
    def test_grassknot_does_damage_on_heavy_pokemon(self):
    def test_lowkick_does_damage_on_heavy_pokemon(self):
    def test_hydration_cures_sleep_at_end_of_turn_in_rain(self):
    def test_hydration_cures_poison_before_it_does_damage(self):
    def test_moonblast_boosts_opponent_with_contrary(self):
    def test_own_boost_does_not_affect_foulplay(self):
    def test_opponent_boost_does_affect_foulplay(self):
    def test_shellsmash_with_whiteherb_doesnt_lower_stats(self):
    def test_superfang_does_half_health(self):
    def test_ruination_does_half_health(self):
    def test_finalgambit_does_damage_equal_to_health_and_faints_user(self):
    def test_endeavor_brings_hp_to_equal(self):
    def test_endeavor_does_nothing_when_user_hp_greater_than_target_hp(self):
    def test_knockoff_does_more_damage_when_item_can_be_removed(self):
    def test_obstruct_protects(self):
    def test_using_futuresight_sets_futuresight_and_decrements_at_the_end_of_turn(self):
    def test_using_futuresight_does_nothing_if_futuresight_is_already_active(self):
    def test_sets_futuresight_even_if_opponent_has_it_active(self):
    def test_futuresight_damage_at_end_of_turn_from_reserve_pokemon(self):
    def test_futuresight_does_not_do_damage_to_dark_type(self):
    def test_futuresight_damage_at_end_of_turn_for_both_sides(self):
    def test_futuresight_damage_at_end_of_turn_from_active_pokemon(self):
    def test_futuresight_damage_halved_by_lightscreen(self):
    def test_futuresight_damage_is_boosted_by_terrain(self):
    def test_using_wish_sets_the_wish_value_to_half_of_the_users_max_health(self):
    def test_having_wish_causes_heal_at_the_end_of_the_turn(self):
    def test_wish_does_not_overheal(self):
    def test_wish_does_not_heal_when_active_pokemon_is_dead_but_still_decrements(self):
    def test_wish_cannot_be_used_while_wish_is_active(self):
    def test_wish_activating_at_full_hp_produces_no_instruction(self):
    def test_steel_beam_reduces_hp_by_half(self):
    def test_steel_beam_only_does_as_much_damage_as_the_user_has_hitpoints(self):
    def test_knockoff_does_not_amplify_damage_or_remove_item_for_mega(self):
    def test_knockoff_removes_item(self):
    def test_knockoff_missing_does_not_remove_item(self):
    def test_knockoff_does_not_amplify_damage_for_primal(self):
    def test_rest_heals_user_and_puts_to_sleep(self):
    def test_ghost_immune_to_superfang(self):
    def test_taunt_into_uturn_causes_taunt_to_be_removed_after_switching(self):
    def test_fast_uturn_results_in_switching_out_move_for_enemy(self):
    def test_fast_uturn_results_in_switching_out_for_bot(self):
    def test_fast_uturn_switch_into_choice_pkmn_does_not_lock_moves(self):
    def test_slow_uturn_results_in_switching_out_for_bot(self):
    def test_flipturn_causes_switch(self):
    def test_slow_uturn_results_in_switching_out_for_opponent(self):
    def test_uturn_works_with_multiple_states_before(self):
    def test_uturn_when_there_are_no_available_switches_works(self):
    def test_fast_voltswitch_results_in_switching_out_for_opponent(self):
    def test_immune_by_ability_does_not_allow_voltswitch(self):
    def test_ground_type_does_not_allow_voltswitch(self):
    def test_chillyreception_allows_switch(self):
    def test_snowscape(self):
    def test_parting_shot_allows_switch(self):
    def test_teleport_causes_switch_and_moves_second(self):
    def test_bellydrum_works_properly_in_basic_case(self):
    def test_bellydrum_kills_user_when_hp_is_less_than_half(self):
    def test_gryo_ball_does_damage(self):
    def test_gryo_ball_does_damage_when_speed_is_equal(self):
    def test_electro_ball_does_damage_when_speed_is_equal(self):
    def test_electro_ball_does_damage_when_speed_is_much_greater(self):
    def test_whirlwind_behaves_correctly_with_a_regular_move(self):
    def test_pokemon_boosting_into_roar(self):
    def test_accuracy_reduction_move(self):
    def test_accuracy_does_not_go_below_negative_6(self):
    def test_attack_does_not_go_above_6(self):
    def test_accuracy_reduction_move_into_tackle_causes_multiple_states(self):
    def test_accuracy_reduction_move_into_contrary_with_tackle_causes_one_state(self):
    def test_evasion_boosting_move(self):
    def test_evasion_boosting_move_causes_two_states(self):
    def test_evasion_boosting_move_with_contrary_causes_one_state(self):
    def test_accuracy_increase_does_not_produce_two_states(self):
    def test_pokemon_with_active_substitute_switching_into_phazing_move(self):
    def test_pokemon_with_active_substitute_switching_into_phazing_move_that_gets_reflected(self):
    def test_dragontail_behaves_well_with_regular_move(self):
    def test_whirlwind_removes_volatile_statuses(self):
    def test_whirlwind_creates_one_transposition_for_each_reserve_pokemon(self):
    def test_whirlwind_into_whirlwind_properly_does_nothing_for_second_whirlwind(self):
    def test_whirlwind_into_teleport_properly_does_nothing_for_the_teleport(self):
    def test_whirlwind_does_nothing_when_no_reserves_are_alive(self):
    def test_suckerpunch_into_tackle_makes_suckerpunch_hit(self):
    def test_substitute_into_weak_attack_does_not_remove_volatile_status(self):
    def test_substitute_into_strong_attack_removes_volatile_status(self):
    def test_substitute_fails_if_user_has_less_than_one_quarter_maxhp(self):
    def test_crosschop_missing_activates_blunder_policy(self):
    def test_willowisp_missing_activates_blunder_policy(self):
    def test_highjumpkick_causes_crash(self):
    def test_highjumpkick_causes_crash_with_previous_move(self):
    def test_highjumpkick_crash_when_switching_into_ghost(self):
    def test_suckerpunch_into_swordsdance_makes_suckerpunch_miss(self):
    def test_rockhead_removes_recoil_for_one_but_not_the_other(self):
    def test_glaiverush_adds_volatile(self):
    def test_having_glaiverush_volatile_doubles_damage(self):
    def test_quarkdriveatk_increases_physical_damage(self):
    def test_protosynthesisatk_increases_physical_damage(self):
    def test_quarkdriveatk_does_not_increase_special_damage(self):
    def test_protosynthesisatk_does_not_increase_special_damage(self):
    def test_quarkdrivespa_increases_special_damage(self):
    def test_quarkdrivespd_increases_special_defense(self):
    def test_quarkdrivedef_increases_defense(self):
    def test_quarkdrivedef_does_not_increase_spd(self):
    def test_having_glaiverush_volatile_makes_move_not_able_to_miss_against_you(self):
    def test_tripledive(self):
    def test_twinbeam(self):
    def test_tackle_into_ironbarbs_causes_recoil(self):
    def test_tackle_into_ironbarbs_causes_no_recoil_when_attacker_has_neutralizing_gas(self):
    def test_dynamax_cannon_does_double_damage_versus_dynamaxed(self):
    def test_dynamax_cannon_does_normal_damage_versus_non_dynamaxed(self):
    def test_noretreat_boosts_own_stats_and_starts_volatile_status(self):
    def test_noretreat_fails_when_user_has_volatile_status(self):
    def test_tarshot_lowers_speed_and_sets_volatile_status(self):
    def test_tarshot_increases_fire_damage(self):
    def test_dragondarts_does_double_damage(self):
    def test_geargrind_does_double_damage(self):
    def test_bonemerang_does_double_damage(self):
    def test_boltbeak_does_normal_damage_when_moving_second(self):
    def test_boltbeak_does_double_damage_when_opponent_switches(self):
    def test_boltbeak_does_double_damage_when_moving_first(self):
    def test_fishious_rend_does_normal_damage_when_moving_second(self):
    def test_fishious_rend_does_double_damage_when_moving_first(self):
    def test_tackle_into_roughskin_causes_recoil(self):
    def test_courtchange_swaps_rocks(self):
    def test_side_conditions_are_unmodified_after_instruction_generation(self):
    def test_courtchange_does_not_swap_zero_value_side_condition(self):
    def test_courtchange_swaps_rocks_and_spikes(self):
    def test_regular_damaging_move_with_speed_boost(self):
    def test_clangoroussoul(self):
    def test_clanorous_soul_fails_when_at_less_than_one_third_hp(self):
    def test_boosting_move_with_speedboost(self):
    def test_speed_boosting_move_with_speedboost(self):
    def test_clearbody_using_boost(self):
    def test_serenegrace(self):
    def test_serenegrace_on_paralyzed_pokemon(self):
    def test_fire_type_cannot_be_burned(self):
    def test_sheerforce_works_properly(self):
    def test_burned_with_guts_doubles_damage(self):
    def test_tintedlens_doubles_not_very_effective_damage(self):
    def test_fire_type_cannot_be_burned_from_secondary(self):
    def test_analytic_boosts_damage(self):
    def test_poisoning_move_shows_poison_damage_on_opponents_turn(self):
    def test_avalanche_into_switch_does_not_increase_avalanche_damage(self):
    def test_using_toxic_results_in_first_damage_to_be_one_sixteenth(self):
    def test_previously_existing_toxic_results_in_correct_damage(self):
    def test_switching_out_with_natural_cure_removes_status(self):
    def test_darkaura_boosts_damage(self):
    def test_stakeout_does_double_damage_versus_switch(self):
    def test_icescales_halves_special_damage(self):
    def test_icescales_does_not_halve_physical_damage(self):
    def test_corrosion_poisons_steel_types(self):
    def test_poison_move_into_steel_type_does_nothing(self):
    def test_pastelveil_prevents_poison(self):
    def test_punkrock_increases_sound_damage(self):
    def test_punkrock_decreases_sound_damage(self):
    def test_steelyspirit_boosts_steel_move(self):
    def test_steam_engine_boosts_speed_when_hit_by_water_move(self):
    def test_steamengine_does_not_overboost(self):
    def test_switching_into_pkmn_with_screen_cleaner_removes_screens_for_both_sides(self):
    def test_auroraveil_fails_without_hail(self):
    def test_auroraveil_works_in_hail(self):
    def test_pursuit_into_switch_causes_pursuit_to_happen_first_with_double_damage(self):
    def test_dying_when_being_pursuited(self):
    def test_opposite_pokemon_darkaura_boosts_damage(self):
    def test_aurabreak_prevents_dark_aura(self):
    def test_toxic_cannot_drop_below_0_hp(self):
    def test_stealthrock_produces_correct_instruction(self):
    def test_stoneaxe_produces_correct_instruction(self):
    def test_solarbeam_does_not_do_damage_but_sets_volatile_status(self):
    def test_fly_makes_user_invulnerable(self):
    def test_gust_can_hit_versus_fly(self):
    def test_gust_can_hit_versus_bounce(self):
    def test_fly_does_damage_on_second_turn(self):
    def test_bounce_does_damage_on_second_turn(self):
    def test_phantomforce_preparation_puts_user_in_semi_invulnerable_turn(self):
    def test_phantomforce_preparation_does_not_cause_lifeorb_damage(self):
    def test_phantomforce_versus_whirlwind(self):
    def test_surf_hits_through_dive(self):
    def test_phantomforce_does_damage_if_user_has_phantomforce_volatilestatus(self):
    def test_phantomforce_does_damage_if_user_has_phantomforce_volatilestatus_and_avoids_damage_if_it_is_slower(self):
    def test_phantomforce_does_not_stop_opponents_move_if_phantomforce_goes_second(self):
    def test_charged_solarbeam_executes_normally(self):
    def test_sun_does_not_require_solarbeam_charge(self):
    def test_growth_boosts_by_two_in_the_sun(self):
    def test_infiltrator_toxic_bypasses_sub(self):
    def test_poison_type_cannot_miss_toxic(self):
    def test_fly_without_z_crystal_charges(self):
    def test_desolate_land_makes_water_moves_fail(self):
    def test_stealthrock_produces_no_instructions_when_it_exists(self):
    def test_ceaselessedge_creates_spikes(self):
    def test_spikes_goes_to_3_layers(self):
    def test_reflect_halves_damage_when_used(self):
    def test_switch_into_toxicspikes_plus_damage(self):
    def test_switch_into_toxicspikes_plus_setting_rocks_from_opponent(self):
    def test_switch_into_side_with_rocks_and_spikes(self):
    def test_switch_into_side_with_rocks_and_spikes_when_one_kills(self):
    def test_spikes_into_rapid_spin_clears_the_spikes(self):
    def test_spikes_into_mortal_spin_clears_the_spikes(self):
    def test_spikes_into_tidyup_clears_the_spikes(self):
    def test_spikes_into_rapid_spin_does_not_clear_spikes_when_user_is_ghost_type(self):
    def test_defog_works_even_if_defender_is_ghost(self):
    def test_defog_removes_terrain(self):
    def test_icespinner_removes_terrain(self):
    def test_lastrespects_damage_boost(self):
    def test_populationbomb_damage_boost(self):
    def test_raging_bull_type_change(self):
    def test_defog_removes_terrain_and_spikes(self):
    def test_doubleironbash_does_double_damage(self):
    def test_stamina_increases_defence_when_hit_with_damaging_move(self):
    def test_stamina_does_not_increase_defence_when_hit_with_status_move(self):
    def test_stealthrock_into_switch(self):
    def test_fainting_pokemon_does_not_move(self):
    def test_negative_boost_inflictions(self):
    def test_reflect_halves_physical_damage(self):
    def test_reflect_does_not_halve_special_damage(self):
    def test_light_screen_halves_special_damage(self):
    def test_rain_doubles_water_damage(self):
    def test_rain_makes_hurricane_always_hit(self):
    def test_sun_doubles_fire_damage(self):
    def test_sand_properly_increses_special_defense_for_rock(self):
    def test_snow_properly_increses_defense_for_ice(self):
    def test_sand_does_not_increase_special_defense_for_ground(self):
    def test_lifeorb_gives_recoil(self):
    def test_blackglasses_boosts_dark_moves(self):
    def test_choice_band_boosts_damage(self):
    def test_eviolite_reduces_damage(self):
    def test_rocky_helmet_hurts_attacker(self):
    def test_taunt_sets_taunt_status(self):
    def test_taunt_volatile_status_prevents_non_damaging_move(self):
    def test_taunt_volatile_status_does_not_prevent_damaging_move(self):
    def test_switch_into_ninetales_starts_sun_weather(self):
    def test_switch_into_politoed_starts_rain_weather(self):
    def test_switch_into_electricsurge_starts_terrain(self):
    def test_switch_into_psychicsurge_starts_terrain(self):
    def test_queenlymajesty_stops_priority_move(self):
    def test_steelworker_boosts_steel_moves(self):
    def test_heavyslam_damage_for_10_times_the_weight(self, pokedex_mock):
    def test_heavyslam_damage_for_4_times_the_weight(self, pokedex_mock):
    def test_heavyslam_damage_for_the_same_weight(self, pokedex_mock):
    def test_heatcrash_damage_for_the_same_weight(self, pokedex_mock):
    def test_heatcrash_into_flashfire(self, pokedex_mock):
    def test_neuroforce_boosts_if_supereffective(self):
    def test_marvelscale_reduces_damage(self):
    def test_marvelscale_does_not_reduce_special_damage(self):
    def test_overcoat_protects_from_spore(self):
    def test_unaware_ignore_defense_boost(self):
    def test_unaware_ignore_special_defense_boost(self):
    def test_killing_a_pokemon_with_various_end_of_turn_action_items(self):
    def test_end_of_turn_instructions_execute_in_correct_order(self):
    def test_leftovers_healing(self):
    def test_flameorb_burns_at_end_of_turn(self):
    def test_fire_type_cannot_be_burned_by_flameorb(self):
    def test_toxicorb_toxics_the_user(self):
    def test_poison_type_cannot_be_toxiced_by_toxicorb(self):
    def test_flameorb_cannot_burn_paralyzed_pokemon(self):
    def test_solarpower_self_damage_at_the_end_of_the_turn(self):
    def test_raindish_heals_when_weather_is_rain(self):
    def test_dryskin_heals_when_weather_is_rain(self):
    def test_dryskin_damages_when_weather_is_sun(self):
    def test_dryskin_does_not_overkill(self):
    def test_raindish_does_not_overheal(self):
    def test_dryskin_does_not_overheal(self):
    def test_icebody_does_not_overheal(self):
    def test_icebody_healing(self):
    def test_leftovers_healing_with_speedboost(self):
    def test_both_leftovers_healing(self):
    def test_both_leftovers_healing_and_poison_damage(self):
    def test_leftovers_has_no_effect_when_at_full_hp(self):
    def test_fainted_pokemon_gets_no_speedboost_or_leftovers_heal(self):
    def test_killing_a_pokemon_with_poisonheal(self):
    def test_killing_a_pokemon_with_poison(self):
    def test_opponent_with_unaware_does_not_make_him_take_more_damage(self):
    def test_unaware_ignore_opponent_attack_boost(self):
    def test_unaware_on_attacker_does_not_reduce_damage(self):
    def test_overgrow_boosts_damage_below_one_third(self):
    def test_swarm_boosts_damage_below_one_third(self):
    def test_swarm_does_not_boost_when_at_half_health(self):
    def test_shieldsdown_with_50_percent_can_be_burned(self):
    def test_galewings_increases_priority(self):
    def test_galewings_does_not_increase_priority_when_hp_is_not_full(self):
    def test_sturdy_prevents_ohko(self):
    def test_sturdy_causes_no_damage_if_maxhp_is_1(self):
    def test_sturdy_mon_can_be_killed_when_not_at_maxhp(self):
    def test_justified_boosts_attack_versus_dark_move(self):
    def test_knocking_out_with_beastboost_gives_a_boost_to_highest_stat(self):
    def test_not_knocking_out_with_beastboost_does_not_increase_stat(self):
    def test_beastboost_prefers_attack_over_any_stat_when_tied(self):
    def test_beastboost_does_not_boost_beyond_6(self):
    def test_beastboost_will_boost_speed(self):
    def test_beastboost_prefers_special_defense_over_speed(self):
    def test_no_boost_from_non_damaging_dark_move(self):
    def test_infiltrator_goes_through_reflect(self):
    def test_secondary_poison_effect_with_shielddust(self):
    def test_sleep_versus_sweetveil(self):
    def test_sleep_versus_vitalspirit(self):
    def test_sleep_clause_prevents_multiple_pokemon_from_being_asleep(self):
    def test_fainted_pokemon_cannot_cause_sleepclause(self):
    def test_sandforce_with_steel_move_boosts_power(self):
    def test_sandforce_with_normal_move_has_no_boost(self):
    def test_sleep_versus_comatose(self):
    def test_quickfeet_boosts_speed(self):
    def test_triage_boosts_priority(self):
    def test_draining_move_into_liquidooze(self):
    def test_innerfocus_prevents_flinching(self):
    def test_defeatist_does_half_damage_at_less_than_half_health(self):
    def test_soundproof_immune_to_sound_move(self):
    def test_soundproof_immune_to_partingshot(self):
    def test_surgesurfer_boosts_speed(self):
    def test_weakarmor_activates_on_physical_move(self):
    def test_weakarmor_does_not_activate_on_status_move(self):
    def test_weakarmor_activates_on_physical_move_when_the_pokemon_uses_a_boosting_move(self):
    def test_weakarmor_does_not_activate_on_special_move(self):
    def test_magmastorm_residual_damage(self):
    def test_saltcure_residual_damage(self):
    def test_saltcure_residual_damage_on_water_type(self):
    def test_magmaarmor_prevents_frozen(self):
    def test_quickfeet_boost_ignores_paralysis(self):
    def test_secondary_poison_effect_with_immunity(self):
    def test_partingshot_into_competitive_boosts_special_attack_by_4(self):
    def test_calmmind_versus_competitive(self):
    def test_defog_into_competitive_boosts_special_attack_by_2(self):
    def test_defog_into_defiant_boosts_attack_by_2(self):
    def test_calmmind_into_defiant(self):
    def test_partingshot_into_defiant_boosts_attack_by_4(self):
    def test_memento_into_competitive(self):
    def test_memento_into_defiant(self):
    def test_moonblast_secondary_into_competitive(self):
    def test_moonblast_secondary_into_defiant(self):
    def test_switching_into_intimidate_into_competitive(self):
    def test_switching_with_quarkdrive_boosterenergy(self):
    def test_switching_with_protosynthesis_boosterenergy(self):
    def test_switching_with_protosynthesis_boosterenergy_boosting_attack(self):
    def test_switching_with_intimidate_into_clearamulet(self):
    def test_switching_into_intimidate_into_rattled(self):
    def test_switching_into_intimidate_into_defiant(self):
    def test_switching_with_intimidate_into_guarddog(self):
    def test_thunderwave_into_limber(self):
    def test_thunderwave_into_ground_type(self):
    def test_bodyslam_into_ground_type(self):
    def test_protean_changes_types_before_doing_damage(self):
    def test_protean_causes_attack_to_have_stab(self):
    def test_no_type_change_instruction_if_there_are_no_types_to_change(self):
    def test_no_type_change_instruction_if_user_gets_flinched(self):
    def test_there_is_a_type_change_instruction_if_a_protean_user_misses_due_to_accuracy(self):
    def test_non_damaging_move_causes_type_change_instruction(self):
    def test_using_ground_move_with_libero_makes_pokemon_immune_to_electric_move(self):
    def test_protean_does_not_activate_if_pkmn_has_volatilestatus(self):
    def test_being_flinched_does_not_result_in_type_change(self):
    def test_infestation_starts_volatile_status(self):
    def test_hustle(self):
    def test_ironfist(self):
    def test_damp_blocks_explosion_moves(self):
    def test_noguard(self):
    def test_refrigerate(self):
    def test_scrappy_hits_ghost(self):
    def test_strongjaw(self):
    def test_technician(self):
    def test_toughclaws(self):
    def test_gorillatactics_boost_damage(self):
    def test_hugepower(self):
    def test_reckless(self):
    def test_parentalbond(self):
    def test_sapsipper_with_leechseed(self):
    def test_sapsipper_with_leafblade(self):
    def test_thickfat(self):
    def test_contact_with_fluffy(self):
    def test_furcoat(self):
    def test_motordrive(self):
    def test_voltabsorb(self):
    def test_stormdrain(self):
    def test_fire_with_fluffy(self):
    def test_shieldsdown_with_25_percent_can_be_burned(self):
    def test_shieldsdown_with_75_percent_cannot_be_burned(self):
    def test_blaze_boosts_damage_below_one_third(self):
    def test_ember_cannot_burn_when_defender_has_covertcoak(self):
    def test_covertcloak_does_not_stop_poweruppunch_boost(self):
    def test_torrent_boosts_damage_below_one_third(self):
    def test_rockypayload(self):
    def test_goodasgold_versus_status_move(self):
    def test_fairywind_into_windrider(self):
    def test_using_tailwind_with_windrider(self):
    def test_goodasgold_versus_non_status_move(self):
    def test_using_move_with_choice_item_locks_other_moves(self):
    def test_switching_into_pkmn_with_choice_item_does_not_lock_other_moves(self):
    def test_being_dragged_into_pkmn_with_choice_item_does_not_lock_other_moves(self):
    def test_gorilla_tactics_locks_other_moves_even_without_choice_item(self):
    def test_gorilla_tactics_with_choice_item_locks_moves(self):
    def test_opponent_using_move_with_choice_item_locks_other_moves(self):
    def test_opponent_using_move_with_choice_item_locks_non_disabled_moves(self):
    def test_already_disabled_moves_are_not_disabled(self):
    def test_using_outrage_locks_other_moves(self):
    def test_using_ragingfury_locks_other_moves(self):
    def test_switch_move_with_choice_item(self):
    def test_switching_out_unlocks_locked_moves(self):
    def test_tanglinghair_drops_speed(self):
    def test_cottondown_drops_speed(self):
    def test_cottondown_drops_speed_for_non_contact_move(self):
    def test_vcreate_into_tanglinghair_drops_stats_correctly(self):
    def test_switch_into_grassysurge_starts_terrain(self):
    def test_switch_into_mistysurge_starts_terrain(self):
    def test_switch_into_politoed_does_not_start_rain_weather_when_desolate_land_is_active(self):
    def test_switch_into_politoed_does_not_start_rain_weather_when_rain_is_already_active(self):
    def test_switch_in_with_dauntless_shield_causes_defense_to_raise(self):
    def test_switch_in_with_intrepid_sword_causes_attack_to_raise(self):
    def test_switch_into_intimidate_causes_opponent_attack_to_lower(self):
    def test_innerfocus_immune_to_intimidate(self):
    def test_dousedrive_makes_waterabsorb_activate(self):
    def test_eartheater(self):
    def test_eartheater_versus_water_move(self):
    def test_thermalexchange_versus_fire_move(self):
    def test_thermalexchange_versus_water_move(self):
    def test_airballoon_makes_immune(self):
    def test_tabletsofruin_damage_reduction(self):
    def test_vesselofruin_damage_reduction(self):
    def test_swordofruin_damage_amp(self):
    def test_beadsofruin_damage_amp(self):
    def test_collisioncourse_supereffective_boost(self):
    def test_electrodrift_supereffective_boost(self):
    def test_fillet_away_boosts_if_health_allows(self):
    def test_fillet_away_fails_if_health_is_below_half(self):
    def test_weaknesspolicy_activates_on_super_effective_damage(self):
    def test_weaknesspolicy_does_not_activate_on_standard_damage(self):
    def test_weaknesspolicy_does_not_activate_on_resisted_damage(self):
    def test_weaknesspolicy_does_not_activate_on_status_move(self):
    def test_memories_change_multiattack_type(self):
    def test_multiattack_with_no_item_is_normal(self):
    def test_memories_change_multiattack_type_to_not_very_effective(self):
    def test_inflicting_with_leechseed_produces_sap_instruction(self):
    def test_leechseed_sap_does_not_overheal(self):
    def test_leechseed_sap_into_removing_protect_side_condition(self):
    def test_using_roost_with_choice_item(self):
    def test_using_sunnyday_sets_the_weather(self):
    def test_using_trick_swaps_items_with_opponent(self):
    def test_trick_fails_against_z_crystal(self):
    def test_trick_fails_against_sticky_hold(self):
    def test_switching_into_stickyweb_lowers_speed(self):
    def test_switching_into_stickyweb_with_whitesmoke_does_not_lower_speed(self):
    def test_charm_against_pokemon_with_clearbody(self):
    def test_charm_against_pokemon_with_clearamulet(self):
    def test_mysticwater_boosts_water_move(self):
    def test_charcoal_boosts_fire_move(self):
    def test_trick_fails_against_silvally_with_memory(self):
    def test_trick_fails_on_opponent_with_substitute(self):
    def test_trick_succeeds_when_user_is_behind_substitute(self):
    def test_trick_switches_when_user_has_no_item(self):
    def test_trick_switches_when_opponent_has_no_item(self):
    def test_double_no_item_produces_no_instructions(self):
    def test_opponent_move_locks_when_choicescarf_is_tricked(self):
    def test_switcheroo_behaves_the_same_as_trick(self):
    def test_bot_moves_are_not_locked_when_a_choice_item_is_tricked(self):
    def test_using_sunnyday_changes_the_weather_from_rain(self):
    def test_using_raindance_sets_the_weather(self):
    def test_using_raindance_sets_the_weather_correctly_as_a_second_move(self):
    def test_fainted_pkmn_doesnt_move(self):
    def test_has_no_effect_when_weather_is_already_active(self):
    def test_paralyzed_pokemon_reacts_properly_to_weather(self):
    def test_using_trickroom_sets_trickroom(self):
    def test_does_not_work_through_flinched(self):
    def test_faster_pkmn_does_not_flinch(self):
    def test_double_weather_move_sets_weathers_properly(self):
    def test_using_sandstorm_sets_the_weather(self):
    def test_sand_causes_correct_damage_to_kill(self):
    def test_hail_causes_correct_damage_to_kill(self):
    def test_using_hail_sets_the_weather(self):
    def test_switching_in_with_snowwarning_produces_correct_ice_weather_instruction(self):
    def test_switching_in_with_snowwarning_produces_correct_ice_weather_instruction(self):
    def test_switching_in_with_snowwarning_does_not_produce_instruction_if_weather_already_set(self):
    def test_using_sunnyday_in_heavyrain_does_not_change_weather(self):
    def test_using_sunnyday_into_solarbeam_causes_solarbeam_to_not_charge(self):
    def test_using_protect_adds_volatile_status_and_side_condition(self):
    def test_unseenfist_ignores_protect_with_contact_move(self):
    def test_unseenfist_does_not_ignore_protect_with_non_contact_move(self):
    def test_psyshock_boost_in_terrain(self):
    def test_expandingforce_power_boost_in_terrain(self):
    def test_risingvoltage_power_boost_in_terrain(self):
    def test_terrainpulse_fails_against_ground_type_in_electricterrain(self):
    def test_terrainpulse_fails_against_dark_type_in_psychicterrain(self):
    def test_terrainpulse_fails_against_ghost_type_without_terrain(self):
    def test_poltergeist_fails_against_target_with_no_item(self):
    def test_poltergeist_does_not_fail_against_target_with_an_unknown_item(self):
    def test_steelroller_works_in_terrain(self):
    def test_steelroller_fails_without_terrain_active(self):
    def test_meteorbeam_charges_on_the_first_turn(self):
    def test_meteorbeam_executes_when_volatile_status_is_active(self):
    def test_mistyexplosion_kills_user(self):
    def test_mistyexplosion_does_more_in_mistyterrain(self):
    def test_purifyingsalt_cannot_be_statused(self):
    def test_purifyingsalt_reduce_ghost_moves(self):
    def test_sharpness_with_slicing_move(self):
    def test_rocky_helmet_and_rough_skin_do_not_activate_on_protect(self):
    def test_baneful_bunker_has_the_same_effect_as_protect(self):
    def test_spiky_shield_has_the_same_effect_as_protect(self):
    def test_spiky_shield_into_non_contact_move(self):
    def test_spiky_shield_into_contact_move(self):
    def test_silktrap_into_contact_move(self):
    def test_silktrap_into_noncontact_move(self):
    def test_silktrap_into_crash_move(self):
    def test_spiky_shield_does_not_work_when_user_has_protect_side_condition(self):
    def test_spiky_shield_into_crash_attack(self):
    def test_non_contact_move_with_banefulbunker(self):
    def test_crash_move_with_banefulbunker(self):
    def test_baneful_bunker_cannot_be_used_when_protect_is_in_the_side_conditions(self):
    def test_baneful_bunker_with_contact_move_causes_poison(self):
    def test_only_first_protect_actives(self):
    def test_protect_cannot_be_used_when_it_exists_as_a_side_condition(self):
    def test_willowisp_misses_versus_protect(self):
    def test_protect_does_not_stop_weather_damage(self):
    def test_protect_does_not_stop_status_damage(self):
    def test_protect_behind_a_sub_works(self):
    def test_protect_does_not_stop_leechseed_damage(self):
    def test_protect_into_hjk_causes_crash_damage(self):
    def test_protect_and_hjk_interaction_when_protect_was_previously_used(self):
    def test_using_non_protect_move_causes_protect_side_condition_to_be_removed(self):
    def test_having_protect_volatile_status_causes_tackle_to_miss(self):
    def test_stealthrock_is_unaffected_by_protect(self):
    def test_move_without_protect_flag_goes_through_protect(self):
    def test_magicguard_does_not_take_leechseed_damage(self):
    def test_waterbubble_doubles_water_damage(self):
    def test_waterbubble_halves_fire_damage(self):
    def test_waterbubble_prevents_burn(self):
    def test_magicguard_does_not_take_poison_damage(self):
    def test_galvanize_boosts_normal_move_to_give_it_stab(self):
    def test_liquidvoice_boosts_sound_move_into_water_and_hits_ghost_type(self):
    def test_liquidvoice_versus_waterabsorb(self):
    def test_terablast_changes_type_if_terastallized(self):
    def test_galvanize_boosts_normal_move_without_stab(self):
    def test_leechseed_does_not_sap_when_dead(self):
    def test_misty_terrain_blocks_status(self):
    def test_misty_terrain_does_not_block_status_on_ungrounded_pkmn(self):
    def test_waking_up_produces_wake_up_instruction(self):
    def test_thawing_produces_thaw_instruction(self):
    def test_using_scald_while_frozen_always_thaws_user(self):
    def test_using_flareblitz_move_while_frozen_always_thaws_user(self):
    def test_being_hit_by_fire_move_while_frozen_always_thaws(self):
    def test_being_hit_by_fire_move_while_slower_while_frozen_always_thaws(self):
    def test_ice_type_cannot_be_frozen(self):
    def test_cannot_be_frozen_in_harsh_sunlight(self):
    def test_frozen_pokemon_versus_switch(self):
    def test_painsplit_properly_splits_health(self):
    def test_painsplit_does_not_overheal(self):
    def test_painsplit_does_not_overheal_enemy(self):
    def test_icebeam_into_scald(self):
    def test_electric_terrain_blocks_sleep(self):
    def test_electric_terrain_does_not_block_sleep_for_non_grounded(self):
    def test_aegislash_with_stancechange_has_stats_change_even_if_target_is_immune_to_move(self):
    def test_aegislash_stats_do_not_change_when_using_non_damaging_move(self):
    def test_aegislash_stats_change_when_using_kingsshield(self):
    def test_skill_link_increases_tailslap_damage(self):
    def test_scaleshot_damage_with_boosts(self):
    def test_pre_existing_leechseed_produces_sap_instruction(self):
    def test_pre_existing_leechseed_produces_sap_instruction_with_one_health_after_damage(self):
    def test_double_zap_cannon(self):
    def test_thunder_produces_all_states(self):
    def test_thunder_produces_all_states_with_damage_rolls_accounted_for(self):
    def test_flinching_move_versus_secondary_effect_produces_three_states(self):
    def test_switch_flying_into_earthquake(self):
    def test_thousandarrows_versus_ungrounded_pokemon_hits(self):
    def test_thousandarrows_versus_levitate_hits(self):
    def test_thousandarrows_versus_airballoon_hits(self):
    def test_magnetrise_versus_earthquake(self):
    def test_roost_volatilestatus_is_removed_at_end_of_turn(self):
    def test_roost_volatilestatus_makes_ground_move_hit_flying_type(self):
    def test_roost_volatilestatus_makes_ground_move_hit_pure_flying_type(self):
    def test_thousandarrows_versus_double_type_does_not_change_the_original_type_list(self):
    def test_flinching_as_second_move_does_not_produce_extra_state(self):
    def test_attack_into_healing_produces_one_state(self):
    def test_junglehealing_heals(self):
    def test_junglehealing_cures_status(self):
    def test_lunarblessing_heals(self):
    def test_lunarblessing_cures_status(self):
    def test_lifedew_healing(self):
    def test_morningsun_in_sunlight(self):
    def test_morningsun_in_sand(self):
    def test_shoreup_in_sand(self):
    def test_attack_into_healing_with_multiple_attack_damage_rolls(self):
    def test_fainted_pokemon_cannot_heal(self):
    def test_switch_into_rocks_does_neutral_damage(self):
    def test_switch_into_rock_does_no_damage_with_heavy_duty_boots(self):
    def test_switch_into_spike_does_no_damage_with_heavy_duty_boots(self):
    def test_stealthrock_into_magicbounce_properly_reflects(self):
    def test_magic_bounced_stealthrock_doesnt_exceed_one_level(self):
    def test_double_earthquake_with_double_levitate_does_nothing(self):
    def test_earthquake_hits_into_levitate_when_user_has_moldbreaker(self):
    def test_earthquake_hits_into_levitate_when_user_has_turboblaze(self):
    def test_fire_move_hits_flashfire_pokemon_when_user_has_moldbreaker(self):
    def test_rocks_can_be_used_versus_magic_bounce_when_user_has_moldbreaker(self):
    def test_paralyzed_pokemon_produces_two_states_when_trying_to_attack(self):
    def test_removes_flinch_status_when_pokemon_faints(self):
    def test_explosion_kills_the_user(self):
    def test_chloroblast(self):
    def test_hydrosteam_power_boosted_in_sun(self):
    def test_psyblade_boosted_in_terrain(self):
    def test_closecombat_kills_and_reduces_stats(self):
    def test_axekick_causes_crash_damage(self):
    def test_barbbarrage_double_damage_versus_poisoned(self):
    def test_willowisp_on_flashfire(self):
    def test_wellbakedbody_versus_fire_move(self):
    def test_priority_move_versus_armortail(self):
    def test_non_priority_move_versus_armortail(self):
    def test_ground_immune_to_thunderwave(self):
    def test_electric_immune_to_thunderwave(self):
class TestRemoveDuplicateInstructions(unittest.TestCase):
    def test_turns_two_identical_instructions_into_one(self):
    def test_does_not_combine_when_instructions_are_different(self):
    def test_combines_two_instructions_but_keeps_the_other(self):
    def test_combines_multiple_duplicates(self):
    def test_combines_two_instructions_but_keeps_many_others(self):
class TestUserMovesFirst(unittest.TestCase):
    def setUp(self):
    def test_bot_moves_first_when_move_priorities_are_the_same_and_it_is_faster(self):
    def test_grassyglide_goes_first_in_terrain(self):
    def test_grassyglide_does_not_go_first_without_terrain(self):
    def test_paralysis_reduces_speed_by_half(self):
    def test_opponent_moves_first_when_move_priorities_are_the_same_and_it_is_faster(self):
    def test_priority_causes_slower_to_move_first(self):
    def test_both_using_priority_causes_faster_to_move_first(self):
    def test_choice_scarf_causes_a_difference_in_effective_speed(self):
    def test_tailwind_doubling_speed(self):
    def test_tailwind_at_0_does_not_boost(self):
    def test_switch_always_moves_first(self):
    def test_double_switch_results_in_faster_moving_first(self):
    def test_prankster_results_in_status_move_going_first(self):
    def test_quickattack_still_goes_first_when_user_has_prankster(self):
    def test_prankster_does_not_result_in_tackle_going_first(self):
    def test_trickroom_results_in_slower_pokemon_going_first(self):
    def test_priority_move_goes_first_in_trickroom(self):
    def test_pursuit_moves_second_when_slower(self):
    def test_pursuit_moves_first_when_opponent_is_switching(self):
    def test_quarkdrivespe_boosts_speed_to_allow_moving_first(self):
    def test_protosynthesisspe_boosts_speed_to_allow_moving_first(self):
```


## Ankimon/poke_engine/tests/test_battle_modifiers.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 4042 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest
import json
from collections import defaultdict

from poke_engine import constants
from poke_engine.helpers import calculate_stats

from poke_engine.battle import Battle
from poke_engine.battle import Pokemon
from poke_engine.battle import Move
from poke_engine.battle import LastUsedMove
from poke_engine.battle import DamageDealt

from poke_engine.battle_modifier import request
from poke_engine.battle_modifier import terastallize
from poke_engine.battle_modifier import activate
from poke_engine.battle_modifier import prepare
from poke_engine.battle_modifier import switch_or_drag
from poke_engine.battle_modifier import clearallboost
from poke_engine.battle_modifier import heal_or_damage
from poke_engine.battle_modifier import swapsideconditions
from poke_engine.battle_modifier import move
from poke_engine.battle_modifier import boost
from poke_engine.battle_modifier import unboost
from poke_engine.battle_modifier import status
from poke_engine.battle_modifier import weather
from poke_engine.battle_modifier import curestatus
from poke_engine.battle_modifier import start_volatile_status
from poke_engine.battle_modifier import end_volatile_status
from poke_engine.battle_modifier import set_ability
from poke_engine.battle_modifier import set_opponent_ability_from_ability_tag
from poke_engine.battle_modifier import form_change
from poke_engine.battle_modifier import zpower
from poke_engine.battle_modifier import clearnegativeboost
from poke_engine.battle_modifier import check_speed_ranges
from poke_engine.battle_modifier import check_choicescarf
from poke_engine.battle_modifier import check_heavydutyboots
from poke_engine.battle_modifier import get_damage_dealt
from poke_engine.battle_modifier import singleturn
from poke_engine.battle_modifier import transform
from poke_engine.battle_modifier import update_battle
from poke_engine.battle_modifier import upkeep
from poke_engine.battle_modifier import inactive

from poke_engine.objects import boost_multiplier_lookup


# so we can instantiate a Battle object for testing
Battle.__abstractmethods__ = set()


class TestRequestMessage(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.active = Pokemon("pikachu", 100)
        self.request_json = {
            "active": [
                {
                    "moves": [
                        {
                            "move": "Storm Throw",
                            "id": "stormthrow",
                            "pp": 16,
                            "maxpp": 16,
                            "target": "normal",
                            "disabled": False
                        },
                        {
                            "move": "Ice Punch",
                            "id": "icepunch",
                            "pp": 24,
                            "maxpp": 24,
                            "target": "normal",
                            "disabled": False
                        },
                        {
                            "move": "Bulk Up",
                            "id": "bulkup",
                            "pp": 32,
                            "maxpp": 32,
                            "target": "self",
                            "disabled": False
                        },
                        {
                            "move": "Knock Off",
                            "id": "knockoff",
                            "pp": 32,
                            "maxpp": 32,
                            "target": "normal",
                            "disabled": False
                        }
                    ]
                }
            ],
            "side": {
                "name": "NiceNameNerd",
                "id": "p1",
                "pokemon": [
                    {
                        "ident": "p1: Throh",
                        "details": "Throh, L83, M",
                        "condition": "335/335",
                        "active": True,
                        "stats": {
                            "atk": 214,
                            "def": 189,
                            "spa": 97,
                            "spd": 189,
                            "spe": 122
                        },
                        "moves": [
                            "stormthrow",
                            "icepunch",
                            "bulkup",
                            "knockoff"
                        ],
                        "baseAbility": "moldbreaker",
                        "item": "leftovers",
                        "pokeball": "pokeball",
                        "ability": "moldbreaker"
                    },
                    {
                        "ident": "p1: Empoleon",
                        "details": "Empoleon, L77, F",
                        "condition": "256/256",
                        "active": False,
                        "stats": {
                            "atk": 137,
                            "def": 180,
                            "spa": 215,
                            "spd": 200,
                            "spe": 137
                        },
                        "moves": [
                            "icebeam",
                            "grassknot",
                            "scald",
                            "flashcannon"
                        ],
                        "baseAbility": "torrent",
                        "item": "choicespecs",
                        "pokeball": "pokeball",
                        "ability": "torrent"
                    },
                    {
                        "ident": "p1: Emboar",
                        "details": "Emboar, L79, M",
                        "condition": "303/303",
                        "active": False,
                        "stats": {

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestRequestMessage(unittest.TestCase):
    def setUp(self):
    def test_request_sets_force_switch_to_false(self):
    def test_force_switch_properly_sets_the_force_switch_flag(self):
    def test_wait_properly_sets_wait_flag(self):
    def test_wait_does_not_initialize_pokemon(self):
class TestSwitchOrDrag(unittest.TestCase):
    def setUp(self):
    def test_switch_properly_resets_types_when_pkmn_was_typechanged(self):
    def test_switch_does_not_reset_types_if_pkmn_has_been_terastallized(self):
    def test_switch_opponents_pokemon_successfully_creates_new_pokemon_for_active(self):
    def test_bot_switching_properly_heals_pokemon_if_it_had_regenerator(self):
    def test_bot_switching_with_regenerator_does_not_overheal(self):
    def test_fainted_pokemon_switching_does_not_heal(self):
    def test_nickname_attribute_is_set_when_switching(self):
    def test_switch_resets_toxic_count_for_opponent(self):
    def test_switch_resets_toxic_count_for_opponent_when_there_is_no_toxic_count(self):
    def test_switch_resets_toxic_count_for_user(self):
    def test_switch_opponents_pokemon_successfully_places_previous_active_pokemon_in_reserve(self):
    def test_switch_opponents_pokemon_creates_reserve_of_length_1_when_reserve_was_previously_empty(self):
    def test_switch_into_already_seen_pokemon_does_not_create_a_new_pokemon(self):
    def test_user_switching_causes_pokemon_to_switch(self):
    def test_user_switching_causes_active_pokemon_to_be_placed_in_reserve(self):
    def test_user_switching_removes_volatile_statuses(self):
    def test_already_seen_pokemon_is_the_same_object_as_the_one_in_the_reserve(self):
    def test_silvally_steel_replaces_silvally(self):
    def test_arceus_ghost_switching_in(self):
    def test_existing_boosts_on_opponents_active_pokemon_are_cleared_when_switching(self):
    def test_existing_boosts_on_bots_active_pokemon_are_cleared_when_switching(self):
    def test_switching_into_the_same_pokemon_does_not_put_that_pokemon_in_the_reserves(self):
    def test_switching_sets_last_move_to_none(self):
    def test_ditto_switching_sets_ability_to_none(self):
    def test_ditto_switching_sets_moves_to_empty_list(self):
    def test_ditto_switching_resets_stats(self):
    def test_ditto_switching_resets_boosts(self):
    def test_ditto_switching_resets_types(self):
class TestHealOrDamage(unittest.TestCase):
    def setUp(self):
    def test_sets_ability_when_the_information_is_present(self):
    def test_sets_ability_when_the_bot_is_damaged_from_opponents_ability(self):
    def test_sets_ability_when_the_opponent_is_damaged_from_bots_ability(self):
    def test_sets_item_when_it_causes_the_bot_damage(self):
    def test_sets_item_when_it_causes_the_opponent_damage(self):
    def test_does_not_set_item_when_item_is_none(self):
    def test_damage_sets_opponents_active_pokemon_to_correct_hp(self):
    def test_damage_sets_bots_active_pokemon_to_correct_hp(self):
    def test_damage_sets_bots_active_pokemon_to_correct_maxhp(self):
    def test_damage_sets_bots_active_pokemon_to_zero_hp(self):
    def test_fainted_message_properly_faints_opponents_pokemon(self):
    def test_damage_caused_by_an_item_properly_sets_opponents_item(self):
    def test_damage_caused_by_toxic_increases_side_condition_toxic_counter_for_opponent(self):
    def test_damage_caused_by_toxic_increases_side_condition_toxic_counter_for_user(self):
    def test_toxic_count_increases_to_2(self):
    def test_damage_caused_by_non_toxic_damage_does_not_increase_toxic_count(self):
    def test_healing_from_ability_sets_ability_to_opponent(self):
    def test_healing_from_ability_does_not_set_bots_ability(self):
    def test_healing_from_revivalblessing_for_opponent_pkmn(self):
    def test_healing_from_revivalblessing_for_bot_pkmn(self):
class TestActivate(unittest.TestCase):
    def setUp(self):
    def test_sets_item_when_poltergeist_activates(self):
    def test_sets_item_when_poltergeist_activates_and_move_is_lowercase(self):
    def test_sets_item_from_activate(self):
    def test_sets_ability_from_activate(self):
class TestPrepare(unittest.TestCase):
    def setUp(self):
    def test_prepare_sets_volatile_status_on_pokemon(self):
class TestClearAllBoosts(unittest.TestCase):
    def setUp(self):
    def test_clears_bots_boosts(self):
    def test_clears_opponents_boosts(self):
    def test_clears_opponents_and_botsboosts(self):
class TestMove(unittest.TestCase):
    def setUp(self):
    def test_adds_move_to_opponent(self):
    def test_does_not_set_move_for_magicbounch(self):
    def test_new_move_has_one_pp_less_than_max(self):
    def test_unknown_move_does_not_try_to_decrement(self):
    def test_add_revealed_move_does_not_add_move_twice(self):
    def test_decrements_seen_move_pp_if_seen_again(self):
    def test_properly_sets_last_used_move(self):
    def test_using_status_move_sets_can_have_assaultvest_to_false(self):
    def test_using_nonstatus_move_does_not_set_can_have_assultvest_to_false(self):
    def test_removes_volatilestatus_if_pkmn_has_it_when_using_move(self):
    def test_sets_can_have_choice_item_to_false_if_two_different_moves_are_used_when_the_pkmn_has_an_unknown_item(self):
    def test_using_a_boosting_status_move_sets_can_have_choice_item_to_false(self):
    def test_using_a_boosting_physical_move_does_not_set_can_have_choice_item_to_false(self):
    def test_using_a_boosting_special_move_does_not_set_can_have_choice_item_to_false(self):
    def test_sets_item_to_unknown_if_the_pokemon_has_choice_item_but_two_different_moves_are_used(self):
    def test_does_not_set_item_to_unknown_if_the_known_item_is_not_a_choice_item_and_two_different_moves_are_used(self):
    def test_does_not_set_can_have_choice_item_to_false_if_the_same_move_is_used_when_the_pkmn_has_an_unknown_item(self):
    def test_sets_can_have_choice_item_to_false_even_if_item_is_known(self):
    def test_sets_can_have_life_orb_to_false_if_damaging_move_is_used(self):
    def test_does_not_set_can_have_life_orb_to_false_if_pokemon_could_have_sheerforce(self):
    def test_does_not_set_can_have_life_orb_to_false_if_pokemon_could_have_magic_guard(self):
    def test_wish_sets_battler_wish(self):
    def test_failed_wish_does_not_set_wish(self):
class TestWeather(unittest.TestCase):
    def setUp(self):
    def test_starts_weather_properly(self):
    def test_sets_weather_ability_when_it_is_present(self):
class TestBoostAndUnboost(unittest.TestCase):
    def setUp(self):
    def test_opponent_boost_properly_updates_opponent_pokemons_boosts(self):
    def test_unboost_works_properly_on_opponent(self):
    def test_unboost_does_not_lower_below_negative_6(self):
    def test_unboost_lowers_one_when_it_hits_the_limit(self):
    def test_boost_does_not_lower_below_negative_6(self):
    def test_boost_lowers_one_when_it_hits_the_limit(self):
    def test_unboost_works_properly_on_user(self):
    def test_user_boosts_updates_properly(self):
    def test_multiple_boost_properly_updates(self):
class TestStatus(unittest.TestCase):
    def setUp(self):
    def test_opponents_active_pokemon_has_status_properly_set(self):
    def test_bots_active_pokemon_has_status_properly_set(self):
    def test_status_from_item_properly_sets_that_item(self):
class TestCureStatus(unittest.TestCase):
    def setUp(self):
    def test_curestatus_works_on_active_pokemon(self):
    def test_curestatus_works_on_active_pokemon_for_bot(self):
    def test_curestatus_works_on_reserve_pokemon(self):
class TestStartFutureSight(unittest.TestCase):
    def setUp(self):
    def test_sets_futuresight_on_side_that_used_the_move(self):
    def test_does_not_set_futuresight_as_a_volatilestatus(self):
class TestStartVolatileStatus(unittest.TestCase):
    def setUp(self):
    def test_volatile_status_is_set_on_opponent_pokemon(self):
    def test_flashfire_sets_ability_on_opponent(self):
    def test_flashfire_sets_ability_on_bot(self):
    def test_volatile_status_is_set_on_user_pokemon(self):
    def test_adds_volatile_status_from_move_string(self):
    def test_does_not_add_the_same_volatile_status_twice(self):
    def test_doubles_hp_when_dynamax_starts_for_opponent(self):
    def test_doubles_hp_when_dynamax_starts_for_bot(self):
    def test_terastallize(self):
    def test_terastallize_sets_new_type(self):
    def test_sets_ability(self):
    def test_typechange_starts_volatilestatus(self):
    def test_typechange_changes_the_type_of_the_user(self):
    def test_typechange_works_with_reflect_type(self):
    def test_typechange_from_multiple_types(self):
class TestEndVolatileStatus(unittest.TestCase):
    def setUp(self):
    def test_removes_volatile_status_from_opponent(self):
    def test_removes_volatile_status_from_user(self):
    def test_halves_opponent_hp_when_dynamax_ends(self):
    def test_halves_bots_hp_when_dynamax_ends(self):
class TestUpdateAbility(unittest.TestCase):
    def setUp(self):
    def test_sets_ability_for_opponent(self):
    def test_sets_ability_for_bot(self):
    def test_update_ability_from_ability_string_properly_updates_ability(self):
    def test_update_ability_from_ability_string_properly_updates_ability_for_bot(self):
class TestSwapSideConditions(unittest.TestCase):
    def setUp(self):
    def get_expected_empty_dict(self):
    def test_does_nothing_when_no_side_conditions_are_present(self):
    def test_swaps_one_layer_of_spikes(self):
    def test_swaps_one_layer_of_spikes_with_two_layers_of_spikes(self):
    def test_swaps_multiple_side_conditions_on_either_side(self):
class TestFormChange(unittest.TestCase):
    def setUp(self):
    def test_changes_with_formechange_message(self):
    def test_preserves_boosts(self):
    def test_preserves_status(self):
    def test_preserves_item(self):
    def test_preserves_base_name_when_form_changes(self):
    def test_removes_pokemon_from_reserve_if_it_is_in_there(self):
    def test_does_not_set_base_name_for_illusion_ending(self):
    def test_multiple_forme_changes_does_not_ruin_base_name(self):
class TestClearNegativeBoost(unittest.TestCase):
    def setUp(self):
    def test_clears_negative_boosts(self):
    def test_clears_multiple_negative_boosts(self):
    def test_does_not_clear_positive_boost(self):
    def test_clears_only_negative_boosts(self):
class TestZPower(unittest.TestCase):
    def setUp(self):
    def test_sets_item_to_none(self):
    def test_does_not_set_item_when_the_bot_moves(self):
class TestSingleTurn(unittest.TestCase):
    def setUp(self):
    def test_sets_protect_side_condition_for_opponent_when_used(self):
    def test_does_not_set_for_non_protect_move(self):
    def test_sets_protect_side_condition_for_bot_when_used(self):
    def test_sets_protect_side_condition_when_prefixed_by_move(self):
class TestTransform(unittest.TestCase):
    def setUp(self):
    def test_transform_into_switching_pokemon_properly_copies_the_pokemon_that_was_in_before_the_switch(self):
    def test_pokemon_with_nicknames_transform_properly(self):
    def test_transform_sets_stats_to_opposing_pokemons_stats(self):
    def test_transform_sets_ability_to_opposing_pokemons_ability(self):
    def test_transform_sets_moves_to_opposing_pokemons_moves(self):
    def test_transform_sets_types_to_opposing_pokemons_types(self):
    def test_transform_sets_boosts_to_opposing_pokemons_boosts(self):
    def test_transform_sets_transform_volatile_status(self):
class TestUpkeep(unittest.TestCase):
    def setUp(self):
    def test_reduces_protect_for_bot(self):
    def test_does_not_reduce_protect_when_it_is_0(self):
    def test_reduces_wish_if_it_is_larger_than_0_for_the_opponent(self):
    def test_reduces_wish_if_it_is_larger_than_0_for_the_bot(self):
    def test_does_not_reduce_wish_if_it_is_0(self):
    def test_reduces_future_sight_if_it_is_larger_than_0_for_the_bot(self):
    def test_does_not_reduce_future_sight_if_it_is_0(self):
class TestCheckSpeedRanges(unittest.TestCase):
    def setUp(self):
    def test_sets_minspeed_when_opponent_goes_first(self):
    def test_sets_maxspeed_when_opponent_goes_first_in_trickroom(self):
    def test_nothing_happens_with_priority_move_in_trickroom(self):
    def test_accounts_for_paralysis_when_calculating_speed_range(self):
    def test_accounts_for_paralysis_on_bots_side_when_calculating_speed_range(self):
    def test_accounts_for_tailwind_on_opponent_side_when_calculating_speed_ranges(self):
    def test_accounts_for_tailwind_on_bot_side_when_calculating_speed_ranges(self):
    def test_accounts_for_tailwind_on_both_side_when_calculating_speed_ranges(self):
    def test_does_not_set_minspeed_when_opponent_could_have_unburden_activated(self):
    def test_sets_maxspeed_when_bot_goes_first(self):
    def test_minspeed_is_not_set_when_rain_is_up_and_opponent_can_have_swiftswim(self):
    def test_minspeed_is_set_when_only_rain_is_up(self):
    def test_minspeed_is_set_when_rain_is_not_up_but_opponent_could_have_swiftswim(self):
    def test_minspeed_is_not_set_when_opponent_has_choicescarf(self):
    def test_minspeed_is_correctly_set_when_bot_has_choicescarf(self):
    def test_minspeed_is_correctly_set_when_bot_has_choicescarf_and_opponent_is_boosted(self):
    def test_minspeed_interaction_with_boosted_speed(self):
    def test_minspeed_interaction_with_bots_boosted_speed(self):
    def test_minspeed_interaction_with_bot_and_opponents_boosted_speed(self):
    def test_opponents_unknown_move_is_used_as_a_zero_priority_move(self):
    def test_bots_unknown_move_is_used_as_a_zero_priority_move(self):
    def test_opponent_has_unknown_choicescarf_causing_it_to_be_faster(self):
    def test_opponent_using_grassyglide_in_grassy_terrain_does_not_cause_minspeed_to_be_set(self):
    def test_bot_using_grassyglide_in_grassy_terrain_does_not_cause_maxspeed_to_be_set(self):
    def test_move_from_magicbounce_after_switching_does_not_set_speed_range(self):
class TestGuessChoiceScarf(unittest.TestCase):
    def setUp(self):
    def test_guesses_choicescarf_when_opponent_should_always_be_slower(self):
    def test_guesses_choicescarf_from_update_battle(self):
    def test_does_not_guess_choicescarf_when_opponent_could_have_prankster(self):
    def test_does_not_guess_choicescarf_when_opponent_is_speed_boosted(self):
    def test_does_not_guess_choicescarf_when_opponent_uses_grassyglide_in_grassy_terrain(self):
    def test_does_not_guess_choicescarf_when_bot_is_speed_unboosted(self):
    def test_does_not_guess_scarf_in_trickroom(self):
    def test_does_not_guess_scarf_under_trickroom_when_opponent_could_be_slower(self):
    def test_guesses_scarf_in_trickroom_when_opponent_cannot_be_slower(self):
    def test_unknown_moves_defaults_to_0_priority(self):
    def test_priority_move_with_unknown_move_does_not_cause_guess(self):
    def test_does_not_guess_item_when_bot_moves_first(self):
    def test_does_not_guess_item_when_moves_are_different_priority(self):
    def test_does_not_guess_item_when_opponent_can_be_faster(self):
    def test_swiftswim_causing_opponent_to_be_faster_results_in_not_guessing_choicescarf(self):
    def test_pokemon_possibly_having_swiftswim_in_rain_does_not_result_in_a_choicescarf_guess(self):
    def test_seismitoad_choicescarf_is_guessed_when_ability_has_been_revealed(self):
    def test_possible_surgesurfer_does_not_result_in_scarf_inferral(self):
    def test_surgesurfer_pokemon_choice_item_is_guessed_if_ability_is_revealed_to_be_otherwise(self):
    def test_pokemon_with_possible_quickfeet_does_not_have_choice_scarf_inferred(self):
    def test_pokemon_with_possible_quickfeet_does_have_choice_scarf_inferred_if_ability_revealed_to_something_else(self):
    def test_only_one_move_causes_no_item_to_be_guessed(self):
    def test_does_not_guess_choicescarf_when_item_is_none(self):
    def test_does_not_guess_choicescarf_when_item_is_known(self):
    def test_uses_randombattle_spread_when_guessing_for_randombattle(self):
    def test_choicescarf_is_not_checked_when_switching_happens(self):
class TestCheckHeavyDutyBoots(unittest.TestCase):
    def setUp(self):
    def test_basic_case_of_switching_in_and_not_taking_damage_sets_heavydutyboots(self):
    def test_parser_deals_with_empty_line(self):
    def test_parser_deals_with_empty_line_with_toxicspikes(self):
    def test_having_an_item_bypasses_this_check(self):
    def test_double_switch_where_other_side_takes_damage_does_not_set_hdb_for_the_first_side(self):
    def test_basic_case_of_switching_in_and_taking_damage_does_not_set_heavydutyboots(self):
    def test_basic_case_of_switching_in_and_taking_damage_sets_can_have_heavydutyboots_to_false(self):
    def test_not_taking_damage_from_spikes_sets_heavydutyboots(self):
    def test_taking_damage_from_spikes_does_not_set_heavydutyboots(self):
    def test_taking_damage_from_spikes_sets_can_have_heavydutyboots_to_false(self):
    def test_not_getting_poisoned_by_toxicspikes_sets_heavydutyboots(self):
    def test_getting_poisoned_by_two_layers_of_toxicspikes_does_not_set_heavydutyboots(self):
    def test_getting_toxiced_by_toxic_afterwards_still_sets_heavydutyboots(self):
    def test_toxicorb_poisoning_at_the_end_of_the_turn_does_not_infer_heavydutyboots(self):
    def test_having_airballoon_does_notcause_a_heavydutyboost_inferral(self):
    def test_flying_type_does_not_trigger_heavydutyboots_check_on_toxicspikes(self):
    def test_getting_poisoned_by_toxicspikes_does_not_set_heavydutyboots(self):
    def test_nothing_is_set_when_there_are_no_hazards_on_the_field(self):
    def test_pokemon_that_could_have_magicguard_does_not_set_heavydutyboots_when_no_damage_is_taken(self):
    def test_being_caught_in_stickyweb_does_not_set_set_heavydutyboots(self):
    def test_being_caught_in_stickyweb_sets_can_have_heavydutyboots_to_false(self):
    def test_not_being_caught_in_stickyweb_sets_item_to_heavydutyboots(self):
class TestInactive(unittest.TestCase):
    def setUp(self):
    def test_sets_time_to_15_seconds(self):
    def test_sets_to_60_seconds(self):
    def test_capture_group_failing(self):
    def test_capture_group_failing_but_message_starts_with_username(self):
    def test_different_inactive_message_does_not_change_time(self):
class TestInactiveOff(unittest.TestCase):
    def setUp(self):
    def test_turns_timer_off(self):
class TestGetDamageDealt(unittest.TestCase):
    def setUp(self):
    def test_assigns_damage_dealt_from_opponent_to_bot(self):
    def test_assigns_damage_when_bots_pokemon_has_no_last_used_move(self):
    def test_supereffective_damage_is_captured(self):
    def test_crit_sets_crit_flag(self):
    def test_stop_after_the_end_of_this_move(self):
    def test_does_not_assign_anything_when_move_does_no_damage(self):
    def test_does_not_catch_second_moves_damage_after_a_heal(self):
    def test_does_not_set_damage_when_status_move_occurs(self):
    def test_assigns_damage_from_move_that_causes_status_as_secondary(self):
    def test_assigns_damage_to_bot_on_faint(self):
    def test_assigns_damage_to_opponent_on_faint(self):
    def test_assigns_damage_to_opponent_on_faint_from_1_hp(self):
    def test_assigns_nothing_on_substitute(self):
    def test_lifeorb_does_not_assign_damage(self):
    def test_doing_damage_to_opponent_gets_correct_percentage(self):
    def test_entire_message_finishing(self):
class TestNoInit(unittest.TestCase):
    def setUp(self):
    def test_renames_battle_when_rename_message_occurs(self):
class TestCheckChoiceItem(unittest.TestCase):
    def setUp(self):
    def test_guesses_choiceband_for_basic_use_case(self):
    def test_min_roll_choiceband_guesses_correctly(self):
    def test_guesses_choiceband_when_bot_moves_first(self):
    def test_does_not_guess_choiceband_when_knockoff_is_used(self):
    def test_does_not_guess_choiceband_when_can_have_choice_item_is_false(self):
    def test_does_not_guess_choiceband_when_damage_is_typical(self):
    def test_does_not_guess_choiceband_when_opponent_crits(self):
    def test_does_not_guess_choiceband_when_bot_uses_shellsmash_just_before(self):
    def test_does_guess_choiceband_when_bot_shellsmashes_but_white_herb_clears_negative_boosts(self):
    def test_does_not_guess_choiceband_when_guts_flameorb_facade_is_used(self):
    def test_sets_can_not_have_band_or_specs_to_true_when_damage_is_too_low(self):
    def test_does_not_set_can_not_have_band_or_specs_to_true_when_damage_kills(self):
    def test_sets_can_not_have_specs_when_attack_is_special(self):
    def test_does_not_set_can_not_have_band_or_specs_to_true_when_pikachu_can_have_lightball(self):
    def test_does_not_infer_choice_item_when_pikachu_can_have_a_lightball(self):
    def test_does_not_guess_choiceband_when_suckerpunch_is_used(self):
    def test_does_not_guess_choiceband_when_pursuit_does_double_damage(self):
    def test_does_not_guess_choiceband_for_special_move(self):
    def test_guesses_choicespecs_for_basic_case_in_randombattle(self):
    def test_does_not_guess_choiceband_when_acrobatics_is_used(self):
```


## Ankimon/poke_engine/tests/test_instruction_generator.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 3282 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest
from poke_engine import constants
from poke_engine import instruction_generator
from poke_engine.battle import Pokemon as StatePokemon
from poke_engine.objects import StateMutator
from poke_engine.objects import State
from poke_engine.objects import Side
from poke_engine.objects import Pokemon
from poke_engine.objects import TransposeInstruction
from collections import defaultdict


class TestGetInstructionsFromFlinched(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instructions = TransposeInstruction(1, [], False)

    def test_flinch_sets_state_to_frozen_and_returns_one_state(self):
        defender = constants.USER

        self.state.user.active.volatile_status.add(constants.FLINCH)
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_flinched(mutator, defender, self.previous_instructions)

        flinch_instruction = (
            constants.MUTATOR_REMOVE_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )

        expected_instruction = TransposeInstruction(1.0, [flinch_instruction], True)

        self.assertEqual(expected_instruction, instructions)

    def test_flinch_being_false_does_not_freeze_the_state(self):
        defender = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_flinched(mutator, defender, self.previous_instructions)

        expected_instruction = TransposeInstruction(1.0, [], False)

        self.assertEqual(expected_instruction, instructions)


class TestGetInstructionsFromConditionsThatFreezeState(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.move = {constants.FLAGS: dict(), constants.ID: constants.DO_NOTHING_MOVE, constants.TYPE: 'normal'}

    def test_paralyzed_attacker_results_in_two_instructions(self):
        attacker = constants.OPPONENT
        defender = constants.USER
        self.state.opponent.active.status = constants.PARALYZED
        previous_instruction = TransposeInstruction(1.0, [], False)

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, self.move, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(1 - constants.FULLY_PARALYZED_PERCENT, [], False),
            TransposeInstruction(constants.FULLY_PARALYZED_PERCENT, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_attacker_results_in_two_instructions(self):
        attacker = constants.OPPONENT
        defender = constants.USER
        self.state.opponent.active.status = constants.FROZEN
        previous_instruction = TransposeInstruction(1.0, [], False)

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, self.move, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(constants.THAW_PERCENT, [('remove_status', 'opponent', 'frz')], False),
            TransposeInstruction(1 - constants.THAW_PERCENT, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_asleep_attacker_results_in_two_instructions(self):
        attacker = constants.OPPONENT
        defender = constants.USER
        self.state.opponent.active.status = constants.SLEEP
        previous_instruction = TransposeInstruction(1.0, [], False)

        mutator = StateMutator(self.state)

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestGetInstructionsFromFlinched(unittest.TestCase):
    def setUp(self):
    def test_flinch_sets_state_to_frozen_and_returns_one_state(self):
    def test_flinch_being_false_does_not_freeze_the_state(self):
class TestGetInstructionsFromConditionsThatFreezeState(unittest.TestCase):
    def setUp(self):
    def test_paralyzed_attacker_results_in_two_instructions(self):
    def test_frozen_attacker_results_in_two_instructions(self):
    def test_asleep_attacker_results_in_two_instructions(self):
    def test_powder_move_on_grass_type_does_nothing_and_freezes_the_state(self):
    def test_powder_move_used_by_asleep_pokemon_produces_correct_states(self):
    def test_powder_against_fire_has_no_effect(self):
class TestGetInstructionsFromDamage(unittest.TestCase):
    def setUp(self):
    def test_100_percent_move_returns_one_state(self):
    def test_100_percent_move_with_drain_heals_the_attacker(self):
    def test_100_percent_move_with_recoil_hurts_the_attacker(self):
    def test_95_percent_move_with_crash_hurts_the_attacker(self):
    def test_100_percent_move_that_does_no_damage_hurts_the_attacker(self):
    def test_95_percent_move_with_no_damage_causes_crash(self):
    def test_0_damage_move_with_50_accuracy_returns_one_state_that_is_frozen(self):
    def test_100_percent_killing_move_doesnt_drop_health_below_zero(self):
    def test_50_percent_move_returns_two_states_with_proper_percentages(self):
    def test_75_percent_move_returns_two_states_with_proper_percentages(self):
    def test_0_percent_move_returns_one_state_with_no_changes(self):
    def test_100_percent_move_returns_one_state_when_state_percentage_already_existed(self):
    def test_frozen_state_does_not_change(self):
class TestGetInstructionsFromSideConditions(unittest.TestCase):
    def setUp(self):
    def test_using_stealthrock_sets_side_condition(self):
    def test_using_spikes_sets_side_condition(self):
    def test_spikes_can_have_more_than_one(self):
    def test_spikes_stops_at_3(self):
    def test_using_stealthrock_into_side_already_containing_stealthrock_does_nothing(self):
class TestGetInstructionsFromHazardClearingMoves(unittest.TestCase):
    def setUp(self):
    def test_rapidspin_clears_stealthrocks(self):
    def test_rapidspin_clears_stealthrocks_and_spikes(self):
    def test_defog_clears_both_sides_side_conditions(self):
    def test_rapidspin_does_not_clear_reflect(self):
class TestGetInstructionsFromDirectStatusEffects(unittest.TestCase):
    def setUp(self):
    def test_100_percent_status_returns_one_state(self):
    def test_status_cannot_be_inflicted_on_pkmn_in_substitute(self):
    def test_75_percent_status_returns_two_states(self):
    def test_frozen_pokemon_cannot_be_burned(self):
    def test_sleep_clause_activates(self):
    def test_poison_type_cannot_be_poisoned(self):
    def test_switching_in_pokemon_cannot_be_statused_if_it_is_already_statused(self):
    def test_steel_type_cannot_be_poisoned(self):
    def test_frozen_state_cannot_be_changed(self):
class TestGetInstructionsFromBoosts(unittest.TestCase):
    def setUp(self):
    def test_no_boosts_results_in_one_unchanged_state(self):
    def test_boosts_cannot_exceed_max_boosts(self):
    def test_boosts_cannot_go_below_min_boosts(self):
    def test_boosts_cannot_go_below_min_boosts_with_previous_instruction_lowering_boost(self):
    def test_boosts_cannot_go_below_min_boosts_with_previous_instruction_lowering_boost_with_percentage_hit_not_1(self):
    def test_guaranteed_atk_boost_returns_one_state(self):
    def test_50_percent_boost_returns_two_states(self):
    def test_guaranteed_atk_boost_returns_one_state_when_attack_boost_already_existed(self):
    def test_pre_existing_boost_does_not_affect_new_boost(self):
    def test_multiple_new_boosts_with_multiple_pre_existing_boosts(self):
class TestGetInstructionsFromSpecialLogicMoves(unittest.TestCase):
    def setUp(self):
    def test_works_with_previous_instructions(self):
class TestGetInstructionsFromFlinchingMoves(unittest.TestCase):
    def setUp(self):
    def test_30_percent_flinching_move_returns_two_states(self):
    def test_100_percent_flinching_move_returns_one_state(self):
    def test_0_percent_flinching_move_returns_one_state(self):
    def test_pre_exising_percentage_propagates_downward(self):
class TestGetStateFromSwitch(unittest.TestCase):
    def setUp(self):
    def test_basic_switch_with_no_side_effects(self):
    def test_switching_into_pokemon_with_grassyseed_causes_that_seed_boost_to_occur_if_terrain_is_up(self):
    def test_seed_boost_doesnt_occur_if_stat_is_maxed(self):
    def test_switching_into_pokemon_with_psychicseed_causes_that_seed_boost_to_occur_if_terrain_is_up(self):
    def test_switch_unboosts_active_pokemon(self):
    def test_switch_into_stealth_rock_gives_damage_instruction(self):
    def test_regenerator_heals_one_third_hp(self):
    def test_regenerator_does_not_overheal(self):
    def test_switch_into_toxicspikes_causes_poison(self):
    def test_poison_switch_into_toxicspikes_clears_the_spikes(self):
    def test_poison_switch_into_two_toxicspikes_clears_the_spikes(self):
    def test_flying_poison_doesnt_clear_toxic_spikes(self):
    def test_switch_into_double_toxicspikes_causes_toxic(self):
    def test_flying_immune_to_toxicspikes(self):
    def test_switch_into_stick_web_drops_speed(self):
    def test_levitate_ability_does_not_cause_sticky_web_effect(self):
    def test_airballoon_item_does_not_cause_sticky_web_effect(self):
    def test_flying_switch_into_sticky_web_does_not_drop_speed(self):
    def test_switch_into_stealth_rock_with_1hp_gives_damage_instruction_of_1hp(self):
    def test_switch_into_stealth_rock_as_flying_does_more_damage(self):
    def test_switch_into_three_spikes_as_flying_does_nothing(self):
    def test_volatile_status_is_removed_on_switch_out(self):
    def test_toxic_count_is_reset_if_it_exists_on_switch_out(self):
    def test_switch_into_pokemon_with_drought_sets_weather(self):
    def test_switch_into_pokemon_with_drizze_sets_weather(self):
    def test_switch_into_pokemon_with_drizze_does_not_set_weather_when_desolate_land_is_active(self):
    def test_switch_into_pokemon_with_desolateland_sets_weather_when_primordial_sea_is_active(self):
    def test_switch_into_pokemon_with_primordialsea_sets_weather_when_desolateland_is_active(self):
    def test_switch_into_intimidate_lowers_opponent_attack(self):
    def test_switch_into_intimidate_does_not_lower_attack_when_already_at_negative_6(self):
class TestGetStateFromHealingMoves(unittest.TestCase):
    def setUp(self):
    def test_returns_one_state_with_health_recovered(self):
    def test_previous_instruction_affect_this_instruction(self):
    def test_previous_instructions_result_in_correct_recovery(self):
    def test_healing_does_not_exceed_max_health(self):
    def test_negative_healing(self):
    def test_frozen_state_does_not_change(self):
class TestGetStateFromVolatileStatus(unittest.TestCase):
    def setUp(self):
    def test_returns_one_state_with_volatile_status_set(self):
    def test_frozen_state_is_unaffected(self):
    def test_does_not_alter_pre_existing_volatile_status(self):
    def test_does_not_apply_duplicate_status(self):
    def test_does_not_apply_status_if_substitute_is_active_on_pokemon(self):
class TestGetStateFromStatusDamage(unittest.TestCase):
    def setUp(self):
    def test_poison_does_one_eigth_damage(self):
    def test_toxic_does_one_sixteenth_damage_when_toxic_count_is_zero_and_gives_toxic_count_instruction(self):
    def test_toxic_does_one_eighth_damage_when_toxic_count_is_one_and_gives_toxic_count_instruction(self):
    def test_toxic_does_one_quarter_damage_when_toxic_count_is_3_and_gives_toxic_count_instruction(self):
    def test_poison_only_does_one_damage_if_that_is_all_it_has(self):
    def test_leech_seed_saps_health(self):
    def test_leech_seed_only_saps_1_when_pokemon_has_1_hp(self):
    def test_leech_seed_does_not_overheal(self):
    def test_dying_from_poison_causes_leechseed_not_to_sap(self):
    def test_leftovers_causes_heal(self):
    def test_blacksludge_causes_heal(self):
    def test_leftovers_does_not_overheal(self):
    def test_blacksludge_does_not_overkill(self):
    def test_blacksludge_does_damage(self):
    def test_poisonheal_heals(self):
    def test_poison_damage_and_leftovers_heal_together(self):
    def test_poison_damage_and_leftovers_heal_together_when_poison_kills(self):
    def test_poison_killing_into_leechseed(self):
    def test_burn_killing_into_leechseed(self):
    def test_toxic_status_with_leftovers_when_toxic_kills(self):
    def test_faster_pokemon_dying_from_poison_into_leech_seed_from_other_side(self):
    def test_previous_instructions_are_interpreted_correctly(self):
    def test_sand_damages_pokemon(self):
    def test_ice_damages_pokemon(self):
    def test_sand_does_not_damage_steel_type(self):
    def test_hail_does_not_damage_ice_type(self):
    def test_double_leftovers_and_poison_and_weather_and_leechseed_executes_in_correct_order(self):
    def test_instructions_stop_when_weather_kills(self):
```


## Ankimon/poke_engine/tests/test_battle.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 1322 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest
from unittest import mock

from poke_engine import constants

from poke_engine.battle import LastUsedMove
from poke_engine.battle import Battle
from poke_engine.battle import Battler
from poke_engine.battle import Pokemon
from poke_engine.battle import Move


# so we can instantiate a Battle object for testing
Battle.__abstractmethods__ = set()


class TestPokemonInit(unittest.TestCase):
    def test_alternate_pokemon_name_initializes(self):
        name = 'florgeswhite'
        Pokemon(name, 100)


class TestGetPossibleMoves(unittest.TestCase):
    def test_gets_four_moves_when_none_are_known(self):
        p = Pokemon('pikachu', 100)

        moves = [
            ('move1', 95),
            ('move2', 94),
            ('move3', 93),
            ('move4', 92)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1', 'move2', 'move3', 'move4'],
            []
        )

        self.assertEqual(expected_result, moves)

    def test_gets_only_first_3_moves_when_one_move_is_known(self):
        p = Pokemon('pikachu', 100)
        p.moves = [
            Move('tackle')
        ]

        moves = [
            ('move1', 95),
            ('move2', 94),
            ('move3', 93),
            ('move4', 92)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1', 'move2', 'move3'],
            []
        )

        self.assertEqual(expected_result, moves)

    def test_chance_moves_are_not_affected_by_known_moves(self):
        p = Pokemon('pikachu', 100)
        p.moves = [
            Move('tackle')
        ]

        moves = [
            ('move1', 95),
            ('move2', 40),
            ('move3', 40),
            ('move4', 40)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1'],
            ['move2', 'move3', 'move4']
        )

        self.assertEqual(expected_result, moves)

    def test_chance_moves_are_not_guessed_if_known_plus_expected_equals_four(self):
        p = Pokemon('pikachu', 100)

        p.moves = [
            Move('tackle'),
            Move('splash'),
            Move('stringshot'),
        ]
        moves = [
            ('move1', 95),
            ('move2', 40),
            ('move3', 40),
            ('move4', 40)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1'],
            []
        )

        self.assertEqual(expected_result, moves)

    def test_does_not_get_already_revealed_move(self):
        p = Pokemon('pikachu', 100)

        p.moves = [
            Move('tackle'),
            Move('splash'),
            Move('stringshot'),
        ]
        moves = [
            ('tackle', 95),
            ('splash', 40),
            ('stringshot', 40),
            ('move4', 40)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            [],
            ['move4']
        )

        self.assertEqual(expected_result, moves)

    def test_does_not_get_already_revealed_move_and_guesses_expected_moves(self):
        p = Pokemon('pikachu', 100)

        p.moves = [
            Move('tackle'),
            Move('stringshot'),
        ]
        moves = [
            ('tackle', 95),
            ('splash', 85),
            ('stringshot', 40),
            ('move4', 40)
        ]

        moves = p.get_possible_moves(moves)


... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestPokemonInit(unittest.TestCase):
    def test_alternate_pokemon_name_initializes(self):
class TestGetPossibleMoves(unittest.TestCase):
    def test_gets_four_moves_when_none_are_known(self):
    def test_gets_only_first_3_moves_when_one_move_is_known(self):
    def test_chance_moves_are_not_affected_by_known_moves(self):
    def test_chance_moves_are_not_guessed_if_known_plus_expected_equals_four(self):
    def test_does_not_get_already_revealed_move(self):
    def test_does_not_get_already_revealed_move_and_guesses_expected_moves(self):
    def test_expected_plus_known_does_not_exceed_four_with_chance_moves(self):
    def test_gets_less_likely_moves_as_chance_moves(self):
    def test_does_not_get_moves_below_threshold(self):
class TestGetPossibleAbilities(unittest.TestCase):
    def test_gets_revealed_item_when_item_is_revealed(self):
    def test_gets_multiple_abilities(self):
    def test_does_not_exceed_threshold(self):
    def test_does_not_get_low_percentage_ability(self):
    def test_ignored_ability_in_pass_abilities(self):
class TestGetPossibleItems(unittest.TestCase):
    def test_gets_revealed_item_when_item_is_revealed(self):
    def test_gets_none_when_item_is_none(self):
    def test_gets_two_items_when_they_are_equally_likely(self):
    def test_stops_once_cumulative_percentage_exceeds_limit(self):
    def test_works_with_one_item(self):
    def test_ignores_item_in_pass_items(self):
    def test_does_not_guess_choice_item_when_can_have_choice_item_flag_is_false(self):
    def test_can_not_have_choice_specs_flag_does_not_affect_choice_band_guess(self):
    def test_does_not_guess_choice_band_when_can_not_have_band_or_specs_is_true(self):
    def test_guesses_choiceband_when_can_not_have_band_is_false(self):
    def test_does_not_guess_assultvest_when_can_have_assultvest_flag_is_false(self):
    def test_guesses_assultvest_when_can_have_assultvest_flag_is_true(self):
    def test_guesses_choice_item_when_can_have_choice_item_flag_is_true(self):
    def test_guesses_life_orb(self):
    def test_does_not_guess_lifeorb_when_can_have_lifeorb_is_false(self):
class TestConvertToMega(unittest.TestCase):
    def setUp(self):
    def test_changes_venusaur_to_its_mega_form(self):
    def test_preserves_previous_hitpoints(self):
    def test_preserves_previous_status_condition(self):
    def test_preserves_previous_boosts(self):
    def test_preserves_previous_moves(self):
    def test_converts_when_it_is_in_sets_lookup_and_check_sets_is_true(self):
    def test_converts_when_it_is_not_in_sets_lookup_and_check_sets_is_false(self):
    def test_does_not_convert_when_it_is_not_in_sets_lookup_and_check_sets_is_true(self):
    def test_does_not_convert_if_item_is_revealed(self):
    def test_does_not_convert_if_item_is_none(self):
class TestBattlerActiveLockedIntoMove(unittest.TestCase):
    def setUp(self):
    def test_choice_item_with_previous_move_used_by_this_pokemon_returns_true(self):
    def test_firstimpression_gets_locked_when_last_used_move_was_by_the_active_pokemon(self):
    def test_taunt_locks_status_move(self):
    def test_taunt_does_not_lock_physical_move(self):
    def test_taunt_does_not_lock_special_move(self):
    def test_taunt_with_multiple_moves(self):
    def test_calmmind_gets_locked_when_user_has_assaultvest(self):
    def test_tackle_is_not_disabled_when_user_has_assaultvest(self):
    def test_fakeout_gets_locked_when_last_used_move_was_by_the_active_pokemon(self):
    def test_firstimpression_is_not_disabled_when_the_last_used_move_was_a_switch(self):
    def test_fakeout_is_not_disabled_when_the_last_used_move_was_a_switch(self):
    def test_choice_item_with_previous_move_being_a_switch_returns_false(self):
    def test_non_choice_item_possession_returns_false(self):
class TestBattle(unittest.TestCase):
    def setUp(self):
    def test_gets_only_move_for_both_sides(self):
    def test_phantomforce_volatilestatus_makes_the_move_forced_for_user(self):
    def test_phantomforce_volatilestatus_makes_the_move_forced_for_opponent(self):
    def test_gets_multiple_moves_for_both_sides(self):
    def test_gets_one_switch_and_splash(self):
    def test_reviving_pokemon_must_choose_fainted_pokemon_to_switch(self):
    def test_reviving_pokemon_only_chooses_fainted_pokemon_to_switch(self):
    def test_gets_multiple_switches_and_splash(self):
    def test_gets_multiple_switches_and_multiple_moves(self):
    def test_ignores_moves_and_gives_opponent_no_option_when_user_active_is_dead(self):
    def test_ignores_moves_and_gives_opponent_no_option_when_force_switch_is_true(self):
    def test_gives_no_options_for_user_and_only_switches_for_opponent_when_wait_is_true(self):
    def test_gives_no_options_for_user_and_only_switches_for_opponent_when_opponent_active_is_dead(self):
    def test_double_fainted_active_pokemon(self):
    def test_opponent_has_no_moves_results_in_splash_or_switches(self):
    def test_opponent_has_moves_when_uturn_moves_first(self):
    def test_opponent_has_no_moves_when_uturn_moves_second(self):
    def test_opponent_has_no_moves_when_uturn_happens_after_switch(self):
    def test_opponent_has_no_moves_when_uturn_kills_and_opponent_has_not_moved_yet(self):
    def test_opponent_has_no_moves_when_uturn_kills_and_opponent_has_already_moved(self):
    def test_opponent_has_no_moves_when_uturn_kills_and_opponent_has_already_switched_in(self):
```


## Ankimon/poke_engine/instruction_generator.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 1235 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from copy import copy

from . import constants
import logging

from .damage_calculator import type_effectiveness_modifier
from .special_effects.abilities.on_switch_in import ability_on_switch_in
from .special_effects.items.on_switch_in import item_on_switch_in
from .special_effects.items.end_of_turn import item_end_of_turn
from .special_effects.abilities.end_of_turn import ability_end_of_turn
from .special_effects.moves.after_move import after_move
from .special_effects.moves import move_special_effect

logger = logging.getLogger(__name__)


opposite_side = {
    constants.USER: constants.OPPONENT,
    constants.OPPONENT: constants.USER
}


same_side_strings = [
    constants.SELF,
    constants.ALLY_SIDE
]


opposing_side_strings = [
    constants.NORMAL,
    constants.OPPONENT,
    constants.FOESIDE,
    constants.ALL_ADJACENT_FOES,
    constants.ALL_ADJACENT,
    constants.ALL,
]


accuracy_multiplier_lookup = {
    -6: 3/9,
    -5: 3/8,
    -4: 3/7,
    -3: 3/6,
    -2: 3/5,
    -1: 3/4,
    0: 3/3,
    1: 4/3,
    2: 5/3,
    3: 6/3,
    4: 7/3,
    5: 8/3,
    6: 9/3
}





def get_instructions_from_move_special_effect(mutator, attacking_side, attacking_pokemon, defending_pokemon, move_name, instructions):
    if instructions.frozen:
        return [instructions]

    try:
        special_logic_move_function = getattr(move_special_effect, move_name)
    except AttributeError:
        new_instructions = list()
    else:
        mutator.apply(instructions.instructions)
        new_instructions = special_logic_move_function(mutator, attacking_side, get_side_from_state(mutator.state, attacking_side), attacking_pokemon, defending_pokemon)
        new_instructions = new_instructions or list()
        mutator.reverse(instructions.instructions)

    for i in new_instructions:
        instructions.add_instruction(i)

    return [instructions]


def get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, affected_side, first_move, instruction):
    if instruction.frozen or not volatile_status:
        return [instruction]

    if affected_side in same_side_strings:
        affected_side = attacker
    elif affected_side in opposing_side_strings:
        affected_side = opposite_side[attacker]
    else:
        logger.critical("Invalid affected_side: {}".format(affected_side))
        return [instruction]

    side = get_side_from_state(mutator.state, affected_side)
    mutator.apply(instruction.instructions)
    if volatile_status in side.active.volatile_status:
        mutator.reverse(instruction.instructions)
        return [instruction]

    if can_be_volatile_statused(side, volatile_status, first_move) and volatile_status not in side.active.volatile_status:
        apply_status_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            affected_side,
            volatile_status
        )
        mutator.reverse(instruction.instructions)
        instruction.add_instruction(apply_status_instruction)
        if volatile_status == constants.SUBSTITUTE:
            instruction.add_instruction(
                (
                    constants.MUTATOR_DAMAGE,
                    affected_side,
                    side.active.maxhp * 0.25
                )
            )
    else:
        mutator.reverse(instruction.instructions)

    return [instruction]


def get_instructions_from_switch(mutator, attacker, switch_pokemon_name, instructions):
    if attacker not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    attacking_side = get_side_from_state(mutator.state, attacker)
    defending_side = get_side_from_state(mutator.state, opposite_side[attacker])
    mutator.apply(instructions.instructions)
    instruction_additions = remove_volatile_status_and_boosts_instructions(attacking_side, attacker)
    mutator.apply(instruction_additions)

    for move in filter(lambda x: x[constants.DISABLED] is True and x[constants.CURRENT_PP], attacking_side.active.moves):
        remove_disabled_instruction = (
            constants.MUTATOR_ENABLE_MOVE,
            attacker,
            move[constants.ID]
        )
        mutator.apply_one(remove_disabled_instruction)
        instruction_additions.append(remove_disabled_instruction)

    if attacking_side.active.ability == 'regenerator' and attacking_side.active.hp:
        hp_missing = attacking_side.active.maxhp - attacking_side.active.hp
        regenerator_instruction = (
            constants.MUTATOR_HEAL,
            attacker,
            int(min(1 / 3 * attacking_side.active.maxhp, hp_missing))
        )
        mutator.apply_one(regenerator_instruction)
        instruction_additions.append(regenerator_instruction)
    elif attacking_side.active.ability == 'naturalcure' and attacking_side.active.status is not None:
        naturalcure_instruction = (
            constants.MUTATOR_REMOVE_STATUS,
            attacker,

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def get_instructions_from_move_special_effect(mutator, attacking_side, attacking_pokemon, defending_pokemon, move_name, instructions):
def get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, affected_side, first_move, instruction):
def get_instructions_from_switch(mutator, attacker, switch_pokemon_name, instructions):
def get_instructions_from_flinched(mutator, attacker, instruction):
def get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, move, opponent_move, instruction):
def get_instructions_from_damage(mutator, defender, damage, accuracy, attacking_move, instruction):
def get_instructions_from_defenders_ability_after_move(mutator, move, ability_name, attacking_pokemon, attacker_string, instruction):
def get_instructions_from_side_conditions(mutator, attacker_string, side_string, condition, instruction):
def get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, instruction):
def get_instructions_from_status_effects(mutator, defender, status, accuracy, instruction):
def get_instructions_from_boosts(mutator, side_string, boosts, accuracy, instruction):
def get_instructions_from_flinching_moves(defender, accuracy, first_move, instruction):
def get_instructions_from_attacker_recovery(mutator, attacker_string, move, instruction):
def get_end_of_turn_instructions(mutator, instruction, bot_move, opponent_move, bot_moves_first):
def get_instructions_from_drag(mutator, attacking_side_string, move_target, instruction):
def get_instructions_from_boost_reset_moves(mutator, attacking_move, attacking_side_string, instruction):
def remove_volatile_status_and_boosts_instructions(side, side_string):
def get_side_from_state(state, side_string):
def can_be_volatile_statused(side, volatile_status, first_move):
def sleep_clause_activated(side, status):
def immune_to_status(state, defending_pkmn, attacking_pkmn, status):
def is_immune_to_freeze(state, pkmn):
def is_immune_to_burn(pkmn):
def is_immune_to_sleep(state, pkmn):
def is_immune_to_poison(attacking, defending):
def is_immune_to_paralysis(pkmn):
```


## Ankimon/poke_engine/battle_modifier.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 1105 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import re
import json
from copy import deepcopy
import logging

from . import constants
from .data import all_move_json
from .data import pokedex
from .battle import Pokemon
from .battle import LastUsedMove
from .battle import DamageDealt
from .battle import StatRange
from .helpers import normalize_name
from .helpers import get_pokemon_info_from_condition
from .helpers import calculate_stats
from .find_state_instructions import get_effective_speed
from .damage_calculator import calculate_damage
from .objects import boost_multiplier_lookup


logger = logging.getLogger(__name__)


MOVE_END_STRINGS = {'move', 'switch', 'upkeep', ''}


def can_have_priority_modified(battle, pokemon, move_name):
    return (
        "prankster" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()] or
        move_name == "grassyglide" and battle.field == constants.GRASSY_TERRAIN
    )


def can_have_speed_modified(battle, pokemon):
    return (
        (
            pokemon.item is None and
            "unburden" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.weather == constants.RAIN and
            pokemon.ability is None and
            "swiftswim" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.weather == constants.SUN and
            pokemon.ability is None and
            "chlorophyll" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.weather == constants.SAND and
            pokemon.ability is None and
            "sandrush" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.weather in constants.HAIL_OR_SNOW and
            pokemon.ability is None and
            "slushrush" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.field == constants.ELECTRIC_TERRAIN and
            pokemon.ability is None and
            "surgesurfer" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            pokemon.status == constants.PARALYZED and
            pokemon.ability is None and
            "quickfeet" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        )
    )


def find_pokemon_in_reserves(pkmn_name, reserves):
    for reserve_pkmn in reserves:
        if pkmn_name.startswith(reserve_pkmn.name) or reserve_pkmn.name.startswith(pkmn_name) or reserve_pkmn.base_name == pkmn_name:
            return reserve_pkmn
    return None


def find_reserve_pokemon_by_nickname(pkmn_nickname, reserves):
    for reserve_pkmn in reserves:
        if pkmn_nickname == reserve_pkmn.nickname:
            return reserve_pkmn
    return None


def is_opponent(battle,  split_msg):
    return not split_msg[2].startswith(battle.user.name)


def get_move_information(m):
    # Given a |move| line from the PS protocol, extract the user of the move and the move object
    try:
        split_move_line = m.split("|")
        return split_move_line[2], all_move_json[normalize_name(split_move_line[3])]
    except KeyError:
        logger.debug("Unknown move {} - using standard 0 priority move".format(normalize_name(m.split('|')[3])))
        return m.split('|')[2], {constants.ID: "unknown", constants.PRIORITY: 0}


def request(battle, split_msg):
    """Update the user's team given the battle JSON in split_msg[2]
       Also updates some battle meta-data such as rqid, force_switch, and wait"""
    if len(split_msg) >= 2:
        battle_json = json.loads(split_msg[2].strip('\''))
        logger.debug("Received battle JSON from server: {}".format(battle_json))
        battle.rqid = battle_json[constants.RQID]

        if battle_json.get(constants.FORCE_SWITCH):
            battle.force_switch = True
        else:
            battle.force_switch = False

        if battle_json.get(constants.WAIT):
            battle.wait = True
        else:
            battle.wait = False

        if not battle.wait:
            battle.request_json = battle_json


def inactive(battle, split_msg):
    regex_string = r"(\d+) sec this turn"
    if split_msg[2].startswith(constants.TIME_LEFT):
        capture = re.search(regex_string, split_msg[2])
        try:
            time_left = int(capture.group(1))
            battle.time_remaining = time_left
            logger.debug("Time left: {}".format(time_left))
        except ValueError:
            logger.warning("{} is not a valid int".format(capture.group(1)))
        except AttributeError:
            logger.warning("'{}' does not match the regex '{}'".format(split_msg[2], regex_string))


def inactiveoff(battle, _):
    battle.time_remaining = None


def switch_or_drag(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
        logger.debug("Opponent has switched - clearing the last used move")
    else:
        side = battle.user
        side.side_conditions[constants.TOXIC_COUNT] = 0

    if side.active is not None:
        # set the pkmn's types back to their original value if the types were changed

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def can_have_priority_modified(battle, pokemon, move_name):
def can_have_speed_modified(battle, pokemon):
def find_pokemon_in_reserves(pkmn_name, reserves):
def find_reserve_pokemon_by_nickname(pkmn_nickname, reserves):
def is_opponent(battle,  split_msg):
def get_move_information(m):
def request(battle, split_msg):
def inactive(battle, split_msg):
def inactiveoff(battle, _):
def switch_or_drag(battle, split_msg):
def heal_or_damage(battle, split_msg):
def faint(battle, split_msg):
def move(battle, split_msg):
def boost(battle, split_msg):
def unboost(battle, split_msg):
def status(battle, split_msg):
def activate(battle, split_msg):
def prepare(battle, split_msg):
def terastallize(battle, split_msg):
def start_volatile_status(battle, split_msg):
def end_volatile_status(battle, split_msg):
def curestatus(battle, split_msg):
def cureteam(battle, split_msg):
def weather(battle, split_msg):
def fieldstart(battle, split_msg):
def fieldend(battle, split_msg):
def sidestart(battle, split_msg):
def sideend(battle, split_msg):
def swapsideconditions(battle, _):
def set_item(battle, split_msg):
def remove_item(battle, split_msg):
def set_ability(battle, split_msg):
def set_opponent_ability_from_ability_tag(battle, split_msg):
def form_change(battle, split_msg):
def zpower(battle, split_msg):
def clearnegativeboost(battle, split_msg):
def clearallboost(battle, _):
def singleturn(battle, split_msg):
def upkeep(battle, _):
def mega(battle, split_msg):
def transform(battle, split_msg):
def turn(battle, split_msg):
def noinit(battle, split_msg):
def check_speed_ranges(battle, msg_lines):
def check_choicescarf(battle, msg_lines):
def get_damage_dealt(battle, split_msg, next_messages):
def check_choice_band_or_specs(battle, damage_dealt):
def check_heavydutyboots(battle, msg_lines):
def update_battle(battle, msg):
```


## Ankimon/poke_engine/battle.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 605 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import itertools
from collections import defaultdict
from collections import namedtuple
from copy import copy
from copy import deepcopy
from abc import ABC
from abc import abstractmethod

from . import constants
import logging

from . import data
from .data import all_move_json
from .data import pokedex
from .data.parse_smogon_stats import MOVES_STRING
from .data.parse_smogon_stats import SPREADS_STRING
from .data.parse_smogon_stats import ABILITY_STRING
from .data.parse_smogon_stats import ITEM_STRING
from .data.helpers import get_pokemon_sets
from .data.helpers import get_mega_pkmn_name
from .data.helpers import PASS_ITEMS
from .data.helpers import PASS_ABILITIES
from .data.helpers import get_all_likely_moves
from .data.helpers import get_most_likely_item
from .data.helpers import get_most_likely_ability
from .data.helpers import get_most_likely_spread
from .data.helpers import get_all_possible_moves_for_random_battle

from .objects import State
from .objects import Side
from .objects import Pokemon as TransposePokemon

from .helpers import remove_duplicate_spreads
from .helpers import get_pokemon_info_from_condition
from .helpers import set_makes_sense
from .helpers import normalize_name
from .helpers import calculate_stats


logger = logging.getLogger(__name__)


LastUsedMove = namedtuple('LastUsedMove', ['pokemon_name', 'move', 'turn'])
DamageDealt = namedtuple('DamageDealt', ['attacker', 'defender', 'move', 'percent_damage', 'crit'])
StatRange = namedtuple("Range", ["min", "max"])


# Based on the format, this dict controls which pokemon will be replaced during team preview
# Some pokemon's forms are not revealed in team preview
smart_team_preview = {
    "gen8ou": {
        "urshifu": "urshifurapidstrike"  # urshifu banned in gen8ou
    }
}


class Battle(ABC):

    def __init__(self, battle_tag):
        self.battle_tag = battle_tag
        self.user = Battler()
        self.opponent = Battler()
        self.weather = None
        self.field = None
        self.trick_room = False

        self.turn = False

        self.started = False
        self.rqid = None

        self.force_switch = False
        self.wait = False

        self.battle_type = None
        self.generation = None
        self.time_remaining = None

        self.request_json = None

    def initialize_team_preview(self, user_json, opponent_pokemon, battle_type):
        self.user.from_json(user_json, first_turn=True)
        self.user.reserve.insert(0, self.user.active)
        self.user.active = None

        for pkmn_string in opponent_pokemon:
            pokemon = Pokemon.from_switch_string(pkmn_string)

            if pokemon.name in smart_team_preview.get(battle_type, {}):
                new_pokemon_name = smart_team_preview[battle_type][pokemon.name]
                logger.info(
                    "Smart team preview: Replaced {} with {}".format(
                        pokemon.name,
                        new_pokemon_name
                    )
                )
                pokemon = Pokemon(new_pokemon_name, pokemon.level)

            self.opponent.reserve.append(pokemon)

        self.started = True
        self.rqid = user_json[constants.RQID]

    def during_team_preview(self):
        ...

    def start_non_team_preview_battle(self, user_json, opponent_switch_string):
        self.user.from_json(user_json, first_turn=True)

        pkmn_information = opponent_switch_string.split('|')[3]
        pkmn = Pokemon.from_switch_string(pkmn_information)
        self.opponent.active = pkmn

        self.started = True
        self.rqid = user_json[constants.RQID]

    def mega_evolve_possible(self):
        return (
                any(g in self.generation for g in constants.MEGA_EVOLVE_GENERATIONS)
        )

    def prepare_battles(self, guess_mega_evo_opponent=True, join_moves_together=False):
        """Returns a list of battles based on this one
        The battles have the opponent's reserve pokemon's unknowns filled in
        The opponent's active pokemon in each of the battles has a different set"""
        battle_copy = deepcopy(self)
        battle_copy.opponent.lock_moves()
        battle_copy.user.lock_active_pkmn_first_turn_moves()

        if battle_copy.user.active.can_mega_evo:
            # mega-evolving here gives the pkmn the random-battle spread (Serious + 85s)
            # unfortunately the correct spread is not stored anywhere as of this being written
            # this only happens on the turn the pkmn mega-evolves - the next turn will be fine
            battle_copy.user.active.forme_change(get_mega_pkmn_name(battle_copy.user.active.name))

        if guess_mega_evo_opponent and not battle_copy.opponent.mega_revealed() and self.mega_evolve_possible():
            check_in_sets = battle_copy.battle_type == constants.STANDARD_BATTLE
            battle_copy.opponent.active.try_convert_to_mega(check_in_sets=check_in_sets)

        # for reserve pokemon only guess their most likely item/ability/spread and guess all moves
        for pkmn in filter(lambda x: x.is_alive(), battle_copy.opponent.reserve):
            pkmn.guess_most_likely_attributes()

        try:
            pokemon_sets = get_pokemon_sets(battle_copy.opponent.active.name)
        except KeyError:
            logger.warning("No sets for {}, trying to find most likely attributes".format(battle_copy.opponent.active.name))
            battle_copy.opponent.active.guess_most_likely_attributes()
            return [battle_copy]


... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class Battle(ABC):
    def __init__(self, battle_tag):
    def initialize_team_preview(self, user_json, opponent_pokemon, battle_type):
    def during_team_preview(self):
    def start_non_team_preview_battle(self, user_json, opponent_switch_string):
    def mega_evolve_possible(self):
    def prepare_battles(self, guess_mega_evo_opponent=True, join_moves_together=False):
    def create_state(self):
    def get_all_options(self):
    def find_best_move(self):
class Battler:
    def __init__(self):
    def mega_revealed(self):
    def lock_active_pkmn_first_turn_moves(self):
    def lock_active_pkmn_status_moves_if_active_has_assaultvest(self):
    def choice_lock_moves(self):
    def taunt_lock_moves(self):
    def lock_moves(self):
    def from_json(self, user_json, first_turn=False):
    def get_switches(self, reviving=False):
    def to_dict(self):
class Pokemon:
    def __init__(self, name: str, level: int, nature="serious", evs=(85,) * 6):
    def forme_change(self, new_pkmn_name):
    def try_convert_to_mega(self, check_in_sets=False):
    def is_alive(self):
    def extract_nickname_from_pokemonshowdown_string(cls, ps_string):
    def from_switch_string(cls, switch_string, nickname=None):
    def set_spread(self, nature, evs):
    def add_move(self, move_name: str):
    def get_move(self, move_name: str):
    def set_likely_moves_unless_revealed(self):
    def set_most_likely_ability_unless_revealed(self):
    def set_most_likely_item_unless_revealed(self):
    def set_most_likely_spread(self):
    def guess_most_likely_attributes(self):
    def get_possible_spreads(self, spreads):
    def get_possible_items(self, items):
    def get_possible_abilities(self, abilities):
    def get_possible_moves(self, moves, battle_type=constants.STANDARD_BATTLE):
    def forced_move(self):
    def to_dict(self):
    def get_dummy(cls):
    def __eq__(self, other):
    def __repr__(self):
class Move:
    def __init__(self, name):
    def to_dict(self):
    def __eq__(self, other):
    def __repr__(self):
```


## Ankimon/poke_engine/objects.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 599 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from collections import defaultdict
from copy import copy

from . import constants
from .data import all_move_json


boost_multiplier_lookup = {
    -6: 2/8,
    -5: 2/7,
    -4: 2/6,
    -3: 2/5,
    -2: 2/4,
    -1: 2/3,
    0: 2/2,
    1: 3/2,
    2: 4/2,
    3: 5/2,
    4: 6/2,
    5: 7/2,
    6: 8/2
}


class State(object):
    __slots__ = ('user', 'opponent', 'weather', 'field', 'trick_room')

    def __init__(self, user, opponent, weather, field, trick_room):
        self.user = user
        self.opponent = opponent
        self.weather = weather
        self.field = field
        self.trick_room = trick_room

    def get_self_options(self, force_switch):
        forced_move = self.user.active.forced_move()
        if forced_move:
            return [forced_move]

        if force_switch:
            possible_moves = []
        else:
            possible_moves = [m[constants.ID] for m in self.user.active.moves if not m[constants.DISABLED]]

        if self.user.trapped(self.opponent.active):
            possible_switches = []
        else:
            possible_switches = self.user.get_switches()

        return possible_moves + possible_switches

    def get_opponent_options(self):
        forced_move = self.opponent.active.forced_move()
        if forced_move:
            return [forced_move]

        if self.opponent.active.hp <= 0:
            possible_moves = []
        else:
            possible_moves = [m[constants.ID] for m in self.opponent.active.moves if not m[constants.DISABLED]]

        if self.opponent.trapped(self.user.active):
            possible_switches = []
        else:
            possible_switches = self.opponent.get_switches()

        return possible_moves + possible_switches

    def get_all_options(self):
        force_switch = self.user.active.hp <= 0
        wait = self.opponent.active.hp <= 0

        # double faint or team preview
        if force_switch and wait:
            user_options = self.get_self_options(force_switch) or [constants.DO_NOTHING_MOVE]
            opponent_options = self.get_opponent_options() or [constants.DO_NOTHING_MOVE]
            return user_options, opponent_options

        if force_switch:
            opponent_options = [constants.DO_NOTHING_MOVE]
        else:
            opponent_options = self.get_opponent_options()

        if wait:
            user_options = [constants.DO_NOTHING_MOVE]
        else:
            user_options = self.get_self_options(force_switch)

        if not user_options:
            user_options = [constants.DO_NOTHING_MOVE]

        if not opponent_options:
            opponent_options = [constants.DO_NOTHING_MOVE]

        return user_options, opponent_options

    def battle_is_finished(self):
        # Returns:
        #    1 if the bot (self) has won
        #   -1 if the opponent has won
        #    False if the battle is not over

        if self.user.active.hp <= 0 and not any(pkmn.hp for pkmn in self.user.reserve.values()):
            return -1
        elif self.opponent.active.hp <= 0 and not any(pkmn.hp for pkmn in self.opponent.reserve.values()) and len(self.opponent.reserve) == 5:
            return 1

        return False

    @classmethod
    def from_dict(cls, state_dict):
        return State(
            Side.from_dict(state_dict[constants.USER]),
            Side.from_dict(state_dict[constants.OPPONENT]),
            state_dict[constants.WEATHER],
            state_dict[constants.FIELD],
            state_dict[constants.TRICK_ROOM]
        )

    def __repr__(self):
        return str(
            {
                constants.USER: self.user,
                constants.OPPONENT: self.opponent,
                constants.WEATHER: self.weather,
                constants.FIELD: self.field,
                constants.TRICK_ROOM: self.trick_room
            }
        )


class Side(object):
    __slots__ = ('active', 'reserve', 'wish', 'side_conditions', 'future_sight')

    def __init__(self, active, reserve, wish, side_conditions, future_sight):
        self.active = active
        self.reserve = reserve
        self.wish = wish
        self.side_conditions = side_conditions
        self.future_sight = future_sight

    def get_switches(self):
        switches = []
        for pkmn_name, pkmn in self.reserve.items():
            if pkmn.hp > 0:
                switches.append("{} {}".format(constants.SWITCH_STRING, pkmn_name))
        return switches

    def trapped(self, opponent_active):
        if self.active.item == 'shedshell' or 'ghost' in self.active.types:

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class State(object):
    def __init__(self, user, opponent, weather, field, trick_room):
    def get_self_options(self, force_switch):
    def get_opponent_options(self):
    def get_all_options(self):
    def battle_is_finished(self):
    def from_dict(cls, state_dict):
    def __repr__(self):
class Side(object):
    def __init__(self, active, reserve, wish, side_conditions, future_sight):
    def get_switches(self):
    def trapped(self, opponent_active):
    def from_dict(cls, side_dict):
    def __repr__(self):
class Pokemon(object):
    def __init__(
    def calculate_burn_multiplier(self):
    def get_highest_stat(self):
    def get_boost_from_boost_string(self, boost_string):
    def forced_move(self):
    def item_can_be_removed(self):
    def from_state_pokemon_dict(cls, d):
    def from_dict(cls, d):
    def calculate_boosted_stats(self):
    def is_grounded(self):
    def __repr__(self):
class TransposeInstruction:
    def __init__(self, percentage, instructions, frozen=False):
    def update_percentage(self, modifier):
    def add_instruction(self, instruction):
    def has_same_instructions_as(self, other):
    def __copy__(self):
    def __repr__(self):
    def __eq__(self, other):
class StateMutator:
    def __init__(self, state):
    def apply_one(self, instruction):
    def apply(self, instructions):
    def reverse(self, instructions):
    def get_side(self, side):
    def disable_move(self, side, move_name):
    def enable_move(self, side, move_name):
    def switch(self, side, _, switch_pokemon_name):
    def reverse_switch(self, side, previous_active, current_active):
    def apply_volatile_status(self, side, volatile_status):
    def remove_volatile_status(self, side, volatile_status):
    def damage(self, side, amount):
    def heal(self, side, amount):
    def boost(self, side, stat, amount):
    def unboost(self, side, stat, amount):
    def apply_status(self, side, status):
    def remove_status(self, side, _):
    def side_start(self, side, effect, amount):
    def reverse_side_start(self, side, effect, amount):
    def side_end(self, side, effect, amount):
    def reverse_side_end(self, side, effect, amount):
    def start_futuresight(self, side, pkmn_name, _):
    def reverse_start_futuresight(self, side, _, old_pkmn_name):
    def decrement_futuresight(self, side):
    def reverse_decrement_futuresight(self, side):
    def start_wish(self, side, health, _):
    def reserve_start_wish(self, side, _, previous_wish_amount):
    def decrement_wish(self, side):
    def reverse_decrement_wish(self, side):
    def start_weather(self, weather, _):
    def reverse_start_weather(self, _, old_weather):
    def start_field(self, field, _):
    def reverse_start_field(self, _, old_field):
    def end_field(self, _):
    def reverse_end_field(self, old_field):
    def toggle_trickroom(self):
    def change_types(self, side, new_types, _):
    def reverse_change_types(self, side, _, old_types):
    def change_item(self, side, new_item, _):
    def reverse_change_item(self, side, _, old_item):
    def change_stats(self, side, new_stats, _):
    def reverse_change_stats(self, side, _, old_stats):
```


## Ankimon/poke_engine/tests/test_initialize_battler.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 522 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest
from poke_engine.battle import Battler
from poke_engine.battle import Pokemon


class TestInitializeBattler(unittest.TestCase):
    def setUp(self):
        self.battler = Battler()

    def test_initialize_with_z_move_available(self):
        request_dict = {
          "active": [
            {
              "moves": [
                {
                  "move": "Swords Dance",
                  "id": "swordsdance",
                  "pp": 32,
                  "maxpp": 32,
                  "target": "self",
                  "disabled": False
                },
                {
                  "move": "Photon Geyser",
                  "id": "photongeyser",
                  "pp": 8,
                  "maxpp": 8,
                  "target": "normal",
                  "disabled": False
                },
                {
                  "move": "Earthquake",
                  "id": "earthquake",
                  "pp": 16,
                  "maxpp": 16,
                  "target": "allAdjacent",
                  "disabled": False
                },
                {
                  "move": "Stone Edge",
                  "id": "stoneedge",
                  "pp": 8,
                  "maxpp": 8,
                  "target": "normal",
                  "disabled": False
                }
              ],
              "canZMove": [
                None,
                {
                  "move": "Light That Burns the Sky",
                  "target": "normal"
                },
                None,
                None
              ]
            }
          ],
          "side": {
            "name": "BigBluePikachu",
            "id": "p2",
            "pokemon": [
              {
                "ident": "p2: Necrozma",
                "details": "Necrozma-Ultra",
                "condition": "152/335",
                "active": True,
                "stats": {
                  "atk": 433,
                  "def": 238,
                  "spa": 333,
                  "spd": 230,
                  "spe": 385
                },
                "moves": [
                  "swordsdance",
                  "photongeyser",
                  "earthquake",
                  "stoneedge"
                ],
                "baseAbility": "neuroforce",
                "item": "ultranecroziumz",
                "pokeball": "pokeball",
                "ability": "neuroforce"
              },
              {
                "ident": "p2: Groudon",
                "details": "Groudon",
                "condition": "386/386",
                "active": False,
                "stats": {
                  "atk": 336,
                  "def": 284,
                  "spa": 328,
                  "spd": 216,
                  "spe": 235
                },
                "moves": [
                  "overheat",
                  "stealthrock",
                  "precipiceblades",
                  "toxic"
                ],
                "baseAbility": "drought",
                "item": "redorb",
                "pokeball": "pokeball",
                "ability": "drought"
              },
              {
                "ident": "p2: Xerneas",
                "details": "Xerneas",
                "condition": "393/393",
                "active": False,
                "stats": {
                  "atk": 268,
                  "def": 226,
                  "spa": 397,
                  "spd": 233,
                  "spe": 297
                },
                "moves": [
                  "moonblast",
                  "focusblast",
                  "aromatherapy",
                  "thunder"
                ],
                "baseAbility": "fairyaura",
                "item": "choicescarf",
                "pokeball": "pokeball",
                "ability": "fairyaura"
              },
              {
                "ident": "p2: Darkrai",
                "details": "Darkrai",
                "condition": "281/281",
                "active": False,
                "stats": {
                  "atk": 194,
                  "def": 217,
                  "spa": 369,
                  "spd": 216,
                  "spe": 383
                },
                "moves": [
                  "nastyplot",
                  "darkpulse",
                  "hypnosis",
                  "thunder"
                ],
                "baseAbility": "baddreams",

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestInitializeBattler(unittest.TestCase):
    def setUp(self):
    def test_initialize_with_z_move_available(self):
    def test_initialize_with_hidden_power_produces_correct_hidden_power(self):
    def test_initialize_pokemon_with_no_item(self):
    def test_reviving_pokemon(self):
```


## Ankimon/poke_engine/constants.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 496 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
CHALLENGE_USER = "CHALLENGE_USER"
ACCEPT_CHALLENGE = "ACCEPT_CHALLENGE"
SEARCH_LADDER = "SEARCH_LADDER"
BOT_MODES = [CHALLENGE_USER, ACCEPT_CHALLENGE, SEARCH_LADDER]

STANDARD_BATTLE = "standard_battle"
RANDOM_BATTLE = "random_battle"

NO_TEAM_PREVIEW_GENS = {
    "gen1",
    "gen2",
    "gen3",
    "gen4"
}

PICK_SAFEST = "safest"
PICK_NASH_EQUILIBRIUM = "nash"

START_STRING = "|start"
RQID = 'rqid'
TEAM_PREVIEW_POKE = "poke"
START_TEAM_PREVIEW = "clearpoke"

MOVES = "moves"
ABILITIES = "abilities"
ITEMS = "items"
COUNT = "count"
SETS = "sets"

UNKNOWN_ITEM = "unknown_item"

UNKOWN_POKEMON_FORMES = ['silvally', 'arceus', 'genesect', 'urshifu']

SMOGON_HAS_STATS_PAGE_SUFFIXES = ["ubers", "ou", "uu", "ru", "nu", "pu", "lc", "oublitz", "nationaldexbeta", "nationaldex", "monotype"]

# a lookup for the opponent's name given the bot's name
# this has to do with the Pokemon-Showdown PROTOCOL
ID_LOOKUP = {
    "p1": "p2",
    "p2": "p1"
}

# mutator strings
MUTATOR_SWITCH = "switch"
MUTATOR_APPLY_VOLATILE_STATUS = "apply_volatile_status"
MUTATOR_REMOVE_VOLATILE_STATUS = "remove_volatile_status"
MUTATOR_DAMAGE = "damage"
MUTATOR_HEAL = "heal"
MUTATOR_BOOST = "boost"
MUTATOR_UNBOOST = "unboost"
MUTATOR_APPLY_STATUS = "apply_status"
MUTATOR_REMOVE_STATUS = "remove_status"
MUTATOR_SIDE_START = "side_start"
MUTATOR_SIDE_END = "side_end"
MUTATOR_WISH_START = "wish_start"
MUTATOR_WISH_DECREMENT = "wish_decrement"
MUTATOR_FUTURESIGHT_START = "futuresight_start"
MUTATOR_FUTURESIGHT_DECREMENT = "futuresight_decrement"
MUTATOR_FUTURESIGHT_END = "futuresight_end"
MUTATOR_DISABLE_MOVE = "disable_move"
MUTATOR_ENABLE_MOVE = "enable_move"
MUTATOR_WEATHER_START = "weather_start"
MUTATOR_WEATHER_END = "weather_end"
MUTATOR_FIELD_START = "field_start"
MUTATOR_FIELD_END = "field_end"
MUTATOR_TOGGLE_TRICKROOM = "toggle_trickroom"
MUTATOR_CHANGE_TYPE = "change_type"
MUTATOR_CHANGE_ITEM = "change_item"
MUTATOR_CHANGE_STATS = "change_stats"

# Core volatile status action constants (if not already present)
MUTATOR_APPLY_VOLATILE_STATUS = 'apply_volatile_status'
MUTATOR_REMOVE_VOLATILE_STATUS = 'remove_volatile_status'

# Charging moves
VOLATILE_SOLAR_BEAM = 'solar_beam'
VOLATILE_SKY_ATTACK = 'sky_attack'
VOLATILE_RAZOR_WIND = 'razor_wind'
VOLATILE_SKULL_BASH = 'skull_bash'
VOLATILE_FREEZE_SHOCK = 'freeze_shock'
VOLATILE_ICE_BURN = 'ice_burn'
VOLATILE_GEOMANCY = 'geomancy'

# Semi-invulnerable moves
VOLATILE_FLY = 'fly'
VOLATILE_DIG = 'dig'
VOLATILE_DIVE = 'dive'
VOLATILE_BOUNCE = 'bounce'
VOLATILE_PHANTOM_FORCE = 'phantom_force'
VOLATILE_SHADOW_FORCE = 'shadow_force'
VOLATILE_SKY_DROP = 'sky_drop'

# Binding moves
VOLATILE_WRAP = 'wrap'
VOLATILE_BIND = 'bind'
VOLATILE_FIRE_SPIN = 'fire_spin'
VOLATILE_WHIRLPOOL = 'whirlpool'
VOLATILE_SAND_TOMB = 'sand_tomb'
VOLATILE_MAGMA_STORM = 'magma_storm'
VOLATILE_INFESTATION = 'infestation'
VOLATILE_SNAP_TRAP = 'snap_trap'

# Type changes
VOLATILE_ROOST = 'roost'
VOLATILE_BURN_UP = 'burn_up'
VOLATILE_DOUBLE_SHOCK = 'double_shock'

# Move restrictions
VOLATILE_DISABLE = 'disable'
VOLATILE_ENCORE = 'encore'
VOLATILE_TAUNT = 'taunt'
VOLATILE_TORMENT = 'torment'
VOLATILE_IMPRISON = 'imprison'
VOLATILE_THROAT_CHOP = 'throat_chop'
VOLATILE_HEAL_BLOCK = 'heal_block'
VOLATILE_EMBARGO = 'embargo'

# Mental effects
VOLATILE_CONFUSION = 'confusion'
VOLATILE_INFATUATION = 'infatuation'

# Damage over time
VOLATILE_LEECH_SEED = 'leech_seed'
VOLATILE_CURSE_GHOST = 'curse_ghost'
VOLATILE_NIGHTMARE = 'nightmare'
VOLATILE_PERISH_SONG = 'perish_song'
VOLATILE_SALT_CURE = 'salt_cure'

# Protection effects
VOLATILE_SUBSTITUTE = 'substitute'
VOLATILE_ENDURE = 'endure'
VOLATILE_PROTECT = 'protect'
VOLATILE_BANEFUL_BUNKER = 'baneful_bunker'
VOLATILE_SPIKY_SHIELD = 'spiky_shield'
VOLATILE_KINGS_SHIELD = 'kings_shield'

# Positioning effects
VOLATILE_MAGNET_RISE = 'magnet_rise'
VOLATILE_TELEKINESIS = 'telekinesis'
VOLATILE_INGRAIN = 'ingrain'
VOLATILE_AQUA_RING = 'aqua_ring'
VOLATILE_SMACK_DOWN = 'smack_down'

# Multi-turn moves
VOLATILE_OUTRAGE = 'outrage'
VOLATILE_THRASH = 'thrash'
VOLATILE_PETAL_DANCE = 'petal_dance'
VOLATILE_ROLLOUT = 'rollout'
VOLATILE_ICE_BALL = 'ice_ball'
VOLATILE_UPROAR = 'uproar'

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
```


## Ankimon/poke_engine/find_state_instructions.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 42 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 347 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from copy import copy

from . import constants
from .config import ShowdownConfig
from .data import all_move_json

from . import instruction_generator
from .damage_calculator import _calculate_damage
from .objects import TransposeInstruction
from .special_effects.abilities.modify_attack_against import ability_modify_attack_against
from .special_effects.abilities.modify_attack_being_used import ability_modify_attack_being_used
from .special_effects.items.modify_attack_against import item_modify_attack_against
from .special_effects.items.modify_attack_being_used import item_modify_attack_being_used
from .special_effects.moves.modify_move import modify_attack_being_used
from .special_effects.abilities.before_move import ability_before_move
from .switch_out_moves import switch_out_move_triggered
from .switch_out_moves import get_best_switch_pokemon


def lookup_move(move_name):
    if move_name.startswith(constants.SWITCH_STRING + " "):
        split_move = move_name.split(" ")
        assert len(split_move) == 2, "Invalid switch string: {}".format(split_move)
        return {
            constants.SWITCH_STRING: split_move[1]
        }

    return all_move_json[move_name.lower()]


def get_effective_speed(state, side):
    boosted_speed = side.active.calculate_boosted_stats()[constants.SPEED]

    if state.weather == constants.SUN and side.active.ability == 'chlorophyll':
        boosted_speed *= 2
    elif state.weather == constants.RAIN and side.active.ability == 'swiftswim':
        boosted_speed *= 2
    elif state.weather == constants.SAND and side.active.ability == 'sandrush':
        boosted_speed *= 2
    elif state.weather in constants.HAIL_OR_SNOW and side.active.ability == 'slushrush':
        boosted_speed *= 2

    if state.field == constants.ELECTRIC_TERRAIN and side.active.ability == 'surgesurfer':
        boosted_speed *= 2

    if side.active.ability == 'unburden' and not side.active.item:
        boosted_speed *= 2
    elif side.active.ability == 'quickfeet' and side.active.status is not None:
        boosted_speed *= 1.5

    if side.side_conditions[constants.TAILWIND]:
        boosted_speed *= 2

    if 'choicescarf' == side.active.item:
        boosted_speed *= 1.5

    if constants.PARALYZED == side.active.status and side.active.ability != 'quickfeet':
        boosted_speed *= 0.5

    if any(vs in side.active.volatile_status for vs in ["quarkdrivespe", "protosynthesisspe"]):
        boosted_speed *= 1.5

    return int(boosted_speed)


def get_effective_priority(side, move, field):
    priority = move[constants.PRIORITY]
    if side.active.ability == 'prankster' and move[constants.CATEGORY] == constants.STATUS:
        priority += 1
    elif side.active.ability == 'galewings' and (side.active.hp == side.active.maxhp) and ('flying' in move[constants.TYPE]):
        priority += 1
    elif side.active.ability == 'triage' and constants.HEAL in move[constants.FLAGS]:
        priority += 3
    elif field == constants.GRASSY_TERRAIN and move[constants.ID] == 'grassyglide':
        priority += 1

    return priority


def user_moves_first(state, user_move, opponent_move):
    user_effective_speed = get_effective_speed(state, state.user)
    opponent_effective_speed = get_effective_speed(state, state.opponent)

    # both users selected a switch
    if constants.SWITCH_STRING in user_move and constants.SWITCH_STRING in opponent_move:
        return user_effective_speed > opponent_effective_speed

    # user selected a switch
    elif constants.SWITCH_STRING in user_move:
        if opponent_move[constants.ID] == 'pursuit':
            return False
        return True

    # opponent selected a switch
    elif constants.SWITCH_STRING in opponent_move:
        if user_move[constants.ID] == 'pursuit':
            return True
        return False

    user_priority = get_effective_priority(state.user, user_move, state.field)
    opponent_priority = get_effective_priority(state.opponent, opponent_move, state.field)

    if user_priority == opponent_priority:
        user_is_faster = user_effective_speed > opponent_effective_speed
        if state.trick_room:
            return not user_is_faster
        else:
            return user_is_faster

    if user_priority > opponent_priority:
        return True
    else:
        return False


def update_attacking_move(attacking_side, attacking_pokemon, defending_pokemon, attacking_move, defending_move, first_move, weather, terrain):
    # update the attacking move based on certain special-effects:
    #   - abilities
    #   - items
    #   - protect

    attacking_move = modify_attack_being_used(
        attacking_side,
        attacking_move,
        defending_move,
        attacking_pokemon,
        defending_pokemon,
        first_move,
        weather,
        terrain
    )

    attacking_move = ability_modify_attack_being_used(
        attacking_pokemon.ability,
        attacking_move,
        defending_move,
        attacking_pokemon,
        defending_pokemon,
        first_move,
        weather
    )

    attacking_move = item_modify_attack_being_used(
        attacking_pokemon.item,
        attacking_move,
        attacking_pokemon,
        defending_pokemon
    )

    attacking_move = ability_modify_attack_against(

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def lookup_move(move_name):
def get_effective_speed(state, side):
def get_effective_priority(side, move, field):
def user_moves_first(state, user_move, opponent_move):
def update_attacking_move(attacking_side, attacking_pokemon, defending_pokemon, attacking_move, defending_move, first_move, weather, terrain):
def cannot_use_move(attacking_pokemon, attacking_move):
def get_state_instructions_from_move(mutator, attacking_move, defending_move, attacker, defender, first_move, instructions):
def remove_duplicate_instructions(list_of_instructions):
def end_of_turn_triggered(user_move, opponent_move):
def get_all_state_instructions(mutator, user_move_string, opponent_move_string):
```


## Ankimon/poke_engine/tests/test_team_converter.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 41 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 104 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest

from poke_engine.teams.team_converter import single_pokemon_export_to_dict


class TestSinglePokemonExportToDict(unittest.TestCase):
    def setUp(self):
        self.expected_pkmn_dict = {
            "name": "",
            "species": "",
            "level": "",
            "gender": "",
            "item": "",
            "ability": "",
            "moves": [],
            "nature": "",
            "tera_type": "",
            "evs": {
                "hp": "",
                "atk": "",
                "def": "",
                "spa": "",
                "spd": "",
                "spe": "",
            },
        }

    def test_pokemon_with_item(self):
        export_string = (
            "Tyranitar @ Leftovers"
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'tyranitar'
        self.expected_pkmn_dict['item'] = 'leftovers'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_pokemon_with_level(self):
        export_string = (
            "Tyranitar\n"
            "Level: 5  "
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'tyranitar'
        self.expected_pkmn_dict['level'] = '5'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_pkmn_with_space_in_name(self):
        export_string = (
            "Mr. Mime"
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'mrmime'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_pkmn_with_space_in_name_with_gender(self):
        export_string = (
            "Mr. Mime (M)"
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'mrmime'
        self.expected_pkmn_dict['gender'] = 'M'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_pkmn_with_space_in_name_with_gender_and_item(self):
        export_string = (
            "Mr. Mime (M) @ Leftovers"
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'mrmime'
        self.expected_pkmn_dict['gender'] = 'M'
        self.expected_pkmn_dict['item'] = 'leftovers'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_pokemon_without_item(self):
        export_string = (
            "Tyranitar"
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'tyranitar'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_gendered_pokemon_with_item(self):
        export_string = (
            "Tyranitar (M) @ Leftovers"
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'tyranitar'
        self.expected_pkmn_dict['item'] = 'leftovers'
        self.expected_pkmn_dict['gender'] = 'M'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_gendered_pokemon_without_item(self):
        export_string = (
            "Tyranitar (M)"
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'tyranitar'
        self.expected_pkmn_dict['gender'] = 'M'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_pkmn_with_evs(self):
        export_string = (
            "Tyranitar\n"
            "EVs: 1 Atk / 2 Def / 3 Spa / 4 SpD / 5 Spe"
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'tyranitar'
        self.expected_pkmn_dict['evs']['atk'] = '1'
        self.expected_pkmn_dict['evs']['def'] = '2'
        self.expected_pkmn_dict['evs']['spa'] = '3'
        self.expected_pkmn_dict['evs']['spd'] = '4'
        self.expected_pkmn_dict['evs']['spe'] = '5'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_pkmn_with_ability(self):
        export_string = (
            "Tyranitar\n"
            "Ability: Sand Stream"
        )

        pkmn_dict = single_pokemon_export_to_dict(export_string)
        self.expected_pkmn_dict['name'] = 'tyranitar'
        self.expected_pkmn_dict['ability'] = 'sandstream'

        self.assertEqual(self.expected_pkmn_dict, pkmn_dict)

    def test_pkmn_with_nature(self):
        export_string = (
            "Tyranitar\n"
            "Adamant Nature"
        )


... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestSinglePokemonExportToDict(unittest.TestCase):
    def setUp(self):
    def test_pokemon_with_item(self):
    def test_pokemon_with_level(self):
    def test_pkmn_with_space_in_name(self):
    def test_pkmn_with_space_in_name_with_gender(self):
    def test_pkmn_with_space_in_name_with_gender_and_item(self):
    def test_pokemon_without_item(self):
    def test_gendered_pokemon_with_item(self):
    def test_gendered_pokemon_without_item(self):
    def test_pkmn_with_evs(self):
    def test_pkmn_with_ability(self):
    def test_pkmn_with_nature(self):
    def test_pkmn_with_moves(self):
    def test_pkmn_with_moves_in_random_places(self):
    def test_deals_with_nicknames(self):
    def test_deals_with_space_after_line(self):
    def test_deals_with_newline_after_line(self):
    def test_deals_with_carriagereturn_after_line(self):
    def test_parses_terra_type(self):
```


## Ankimon/singletons.py
*   **Why it was selected**: High structural centrality. It acts as a `glue` layer and is imported by 41 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 60 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
"""
singletons.py

This module groups up some of the global variables that originally wer ein the __init__.py.
This module, hopefully, does not have vocation to remain permanently. This is but a transition step
in the splitting of the __init__.py file.

More detailed explanation if needed:
- Any important classes/functions
- Special behaviors, assumptions, or usage notes

Author: Axil
Created: 2025-06-03 (YYY-MM-DD)
"""

import json
import uuid

from aqt import mw

from .pyobj.ankimon_tracker import AnkimonTracker
from .pyobj.settings import Settings
from .pyobj.settings_window import SettingsWindow
from .pyobj.pokemon_obj import PokemonObject
from .pyobj.InfoLogger import ShowInfoLogger
from .pyobj.trainer_card import TrainerCard
from .pyobj.translator import Translator
from .pyobj.test_window import TestWindow
from .pyobj.achievement_window import AchievementWindow
from .pyobj.settings_window import SettingsWindow
from .pyobj.ankimon_tracker_window import AnkimonTrackerWindow
from .pyobj.ankimon_shop import PokemonShopManager
from .pokedex.pokedex_obj import Pokedex
from .pyobj.reviewer_obj import Reviewer_Manager
from .pyobj.evolution_window import EvoWindow
from .pyobj.starter_window import StarterWindow
from .pyobj.item_window import ItemWindow
from .pyobj.pc_box import PokemonPC
from .pyobj.database_manager import get_db
from .gui_entities import (
    License,
    Credits,
    TableWidget,
    IDTableWidget,
    Pokedex_Widget,
    Version_Dialog,
)
from .functions.update_main_pokemon import update_main_pokemon
from .functions.badges_functions import populate_achievements_from_badges
from .resources import addon_dir

# start loggerobject for Ankimon
logger = ShowInfoLogger()

# Initialize the database (this also runs migrations on first startup)
ankimon_db = get_db(logger)

# Create the Settings object
settings_obj = Settings()

# Pass the correct attributes to SettingsWindow
settings_window = SettingsWindow(
    config=settings_obj.config,  # Use settings_obj.config instead of settings_obj.settings.config
    set_config_callback=settings_obj.set,
    save_config_callback=settings_obj.save_config,
    load_config_callback=settings_obj.load_config,
)

# Init Translator
translator = Translator(language=int(settings_obj.get("misc.language")))

# Not sure what this does, but from afar it looks like a bad idea
mw.settings_ankimon = settings_window
mw.logger = logger
mw.translator = translator
mw.settings_obj = settings_obj
mw.ankimon_db = ankimon_db  # Database singleton for global access

main_pokemon, mainpokemon_empty = update_main_pokemon()

enemy_pokemon = PokemonObject(
    name="Rattata",  # Name of the Pokémon
    shiny=False,  # Shiny status (False for normal appearance)
    id=19,  # ID number
    level=5,  # Level
    ability="Run Away",  # Ability specific to Rattata
    type=["Normal"],  # Type (Normal type for Rattata)
    stats={  # Base stats for Rattata
        "hp": 39,
        "atk": 52,
        "def": 43,
        "spa": 60,
        "spd": 50,
        "spe": 65,
        "xp": 101,
    },
    attacks=["Quick Attack", "Tackle", "Tail Whip"],  # Typical moves for Rattata
    base_experience=58,  # Base experience points
    growth_rate="medium-slow",  # Growth rate
    hp=30,  # Hit points (HP)
    ev={
        "hp": 3,
        "atk": 5,
        "def": 4,
        "spa": 1,
        "spd": 2,
        "spe": 3,
    },  # EVs (Effort Values) for stats
    iv={
        "hp": 27,
        "atk": 24,
        "def": 3,
        "spa": 24,
        "spd": 16,
        "spe": 21,
    },  # IVs (Individual Values) for stats
    gender="M",  # Gender
    battle_status="Fighting",  # Status during battle
    xp=0,  # XP (experience points)
    position=(5, 5),  # Position in battle
    tier="Normal",
    captured_date=None,
    individual_id=str(uuid.uuid4()),
)

# Create a sample trainer card to test
trainer_card = TrainerCard(
    logger,
    main_pokemon,
    settings_obj,
    trainer_name=settings_obj.get("trainer.name"),
    trainer_id="".join(filter(str.isdigit, str(uuid.uuid4()).replace("-", ""))),
    team="Pikachu (Level 25), Charizard (Level 50), Bulbasaur (Level 15)",
    league="Unranked",
)

ankimon_tracker_obj = AnkimonTracker(
    trainer_card=trainer_card,
)
# Set Pokémon in the tracker
ankimon_tracker_obj.set_main_pokemon(main_pokemon)
ankimon_tracker_obj.set_enemy_pokemon(enemy_pokemon)

# Create an instance of the MainWindow
test_window = TestWindow(
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    settings_obj=settings_obj,
    ankimon_tracker_obj=ankimon_tracker_obj,
    translator=translator,

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
```


## Ankimon/poke_engine/teams/team_converter.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 41 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from ..helpers import normalize_name


def json_to_packed(json_team):
    def from_json(j):
        return "{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{},{},{},{},{},{}".format(
            j['name'],
            j.get('species', ""),
            j['item'],
            j['ability'],
            ",".join(j['moves']),
            j.get('nature', ''),
            ','.join(str(x) for x in j['evs'].values()),
            j.get('gender', ''),
            ','.join(str(x) for x in j.get('ivs', {}).values()),
            j.get('shiny', ''),
            j.get('level', ''),
            j.get('happiness', ''),
            j.get('pokeball', ''),
            j.get('hiddenpowertype', ''),
            j.get('gigantamax', ''),
            j.get('dynamaxlevel', ''),
            j.get('tera_type', ''),
        )

    packed_team_string = "]".join(
        (from_json(p) for p in json_team)
    )
    return packed_team_string


def single_pokemon_export_to_dict(pkmn_export_string):
    def get_species(s):
        if '(' in s and ')' in s:
            species = s[s.find("(")+1:s.find(")")]
            return species
        return None

    pkmn_dict = {
        "name": "",
        "species": "",
        "level": "",
        "tera_type": "",
        "gender": "",
        "item": "",
        "ability": "",
        "moves": [],
        "nature": "",
        "evs": {
            "hp": "",
            "atk": "",
            "def": "",
            "spa": "",
            "spd": "",
            "spe": "",
        },
    }
    pkmn_info = pkmn_export_string.split('\n')
    name = pkmn_info[0].split('@')[0]
    if "(M)" in name:
        pkmn_dict["gender"] = "M"
        name = name.replace('(M)', '')
    if "(F)" in name:
        pkmn_dict["gender"] = "F"
        name = name.replace('(F)', '')
    species = get_species(name)
    if species:
        pkmn_dict["species"] = normalize_name(species)
        pkmn_dict["name"] = normalize_name(species)
    else:
        pkmn_dict["name"] = normalize_name(name.strip())
    if '@' in pkmn_info[0]:
        pkmn_dict["item"] = normalize_name(pkmn_info[0].split('@')[1])
    for line in map(str.strip, pkmn_info[1:]):
        if line.startswith('Ability: '):
            pkmn_dict["ability"] = normalize_name(line.split('Ability: ')[-1])
        elif line.startswith('Tera Type: '):
            pkmn_dict["tera_type"] = normalize_name(line.split('Tera Type: ')[-1])
        elif line.startswith('Level: '):
            pkmn_dict["level"] = normalize_name(line.split('Level: ')[-1])
        elif line.startswith('EVs: '):
            evs = line.split('EVs: ')[-1]
            for ev in evs.split('/'):
                ev = ev.strip()
                amount = normalize_name(ev.split(' ')[0])
                stat = normalize_name(ev.split(' ')[1])
                pkmn_dict['evs'][stat] = amount
        elif line.endswith('Nature'):
            pkmn_dict["nature"] = normalize_name(line.split('Nature')[0])
        elif line.startswith('-'):
            pkmn_dict["moves"].append(normalize_name(line[1:]))
    return pkmn_dict


def export_to_packed(export_string):
    team_dict = list()
    team_members = export_string.split('\n\n')
    for pkmn in filter(None, team_members):
        pkmn_dict = single_pokemon_export_to_dict(pkmn)
        team_dict.append(pkmn_dict)

    return json_to_packed(team_dict)

```


## Ankimon/poke_engine/tests/test_select_best_move.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 40 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 381 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest
from collections import defaultdict

from poke_engine import constants
from poke_engine.objects import State
from poke_engine.objects import Side
from poke_engine.objects import Pokemon
from poke_engine.battle import Pokemon as StatePokemon


class TestGetAllOptions(unittest.TestCase):
    def setUp(self):
        self.state = State(
                        Side(
                            Pokemon.from_state_pokemon_dict(StatePokemon("raichu", 73).to_dict()),
                            {
                                "xatu": Pokemon.from_state_pokemon_dict(StatePokemon("xatu", 81).to_dict()),
                                "starmie": Pokemon.from_state_pokemon_dict(StatePokemon("starmie", 81).to_dict()),
                                "gyarados": Pokemon.from_state_pokemon_dict(StatePokemon("gyarados", 81).to_dict()),
                                "dragonite": Pokemon.from_state_pokemon_dict(StatePokemon("dragonite", 81).to_dict()),
                                "hitmonlee": Pokemon.from_state_pokemon_dict(StatePokemon("hitmonlee", 81).to_dict()),
                            },
                            (0, 0),
                            defaultdict(lambda: 0),
                (0, 0)
                        ),
                        Side(
                            Pokemon.from_state_pokemon_dict(StatePokemon("aromatisse", 81).to_dict()),
                            {
                                "yveltal": Pokemon.from_state_pokemon_dict(StatePokemon("yveltal", 73).to_dict()),
                                "slurpuff": Pokemon.from_state_pokemon_dict(StatePokemon("slurpuff", 73).to_dict()),
                                "victini": Pokemon.from_state_pokemon_dict(StatePokemon("victini", 73).to_dict()),
                                "toxapex": Pokemon.from_state_pokemon_dict(StatePokemon("toxapex", 73).to_dict()),
                                "bronzong": Pokemon.from_state_pokemon_dict(StatePokemon("bronzong", 73).to_dict()),
                            },
                            (0, 0),
                            defaultdict(lambda: 0),
                (0, 0)
                        ),
                        None,
                        None,
                        False
                    )

        self.state.user.active.moves = [
            {constants.ID: 'tackle', constants.DISABLED: False},
            {constants.ID: 'charm', constants.DISABLED: False},
            {constants.ID: 'growl', constants.DISABLED: False},
            {constants.ID: 'stringshot', constants.DISABLED: False},
        ]
        self.state.opponent.active.moves = [
            {constants.ID: 'tackle', constants.DISABLED: False},
            {constants.ID: 'charm', constants.DISABLED: False},
            {constants.ID: 'growl', constants.DISABLED: False},
            {constants.ID: 'stringshot', constants.DISABLED: False},
        ]

    def test_returns_all_options_in_normal_situation(self):
        expected_options = (
            [
                'tackle',
                'charm',
                'growl',
                'stringshot',
                'switch xatu',
                'switch starmie',
                'switch gyarados',
                'switch dragonite',
                'switch hitmonlee'
            ],
            [
                'tackle',
                'charm',
                'growl',
                'stringshot',
                'switch yveltal',
                'switch slurpuff',
                'switch victini',
                'switch toxapex',
                'switch bronzong'
            ]
        )
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_partiallytrapped_removes_switch_options_for_bot(self):
        self.state.user.active.volatile_status.add(constants.PARTIALLY_TRAPPED)
        expected_options = (
            [
                'tackle',
                'charm',
                'growl',
                'stringshot'
            ],
            [
                'tackle',
                'charm',
                'growl',
                'stringshot',
                'switch yveltal',
                'switch slurpuff',
                'switch victini',
                'switch toxapex',
                'switch bronzong'
            ]
        )
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_partiallytrapped_removes_switch_options_for_opponent(self):
        self.state.opponent.active.volatile_status.add(constants.PARTIALLY_TRAPPED)
        expected_options = (
            [
                'tackle',
                'charm',
                'growl',
                'stringshot',
                'switch xatu',
                'switch starmie',
                'switch gyarados',
                'switch dragonite',
                'switch hitmonlee'
            ],
            [
                'tackle',
                'charm',
                'growl',
                'stringshot'
            ]
        )
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_bot_with_shadowtag_prevents_switch_options_for_opponent(self):
        self.state.user.active.ability = 'shadowtag'
        expected_options = (
            [
                'tackle',
                'charm',
                'growl',
                'stringshot',
                'switch xatu',
                'switch starmie',
                'switch gyarados',
                'switch dragonite',
                'switch hitmonlee'
            ],

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestGetAllOptions(unittest.TestCase):
    def setUp(self):
    def test_returns_all_options_in_normal_situation(self):
    def test_partiallytrapped_removes_switch_options_for_bot(self):
    def test_partiallytrapped_removes_switch_options_for_opponent(self):
    def test_bot_with_shadowtag_prevents_switch_options_for_opponent(self):
    def test_opponent_with_shadowtag_prevents_switch_options(self):
    def test_ghost_type_can_switch_out_versus_shadow_tag(self):
    def test_non_steel_can_switch_out_versus_magnetpull(self):
    def test_self_pokemon_with_phantomforce_volatilestatus_must_use_phantomforce(self):
    def test_opponent_pokemon_with_phantomforce_volatilestatus_must_use_phantomforce(self):
    def test_shedshell_can_always_switch(self):
    def test_bot_can_switch_as_flying_type_versus_arenatrap(self):
    def test_airballoon_allows_holder_to_switch(self):
    def test_arenatrap_traps_non_grounded(self):
    def test_steel_type_cannot_switch_out_versus_magnetpull(self):
    def test_returns_only_switches_for_user_and_nothing_for_opponent_when_user_active_is_dead(self):
    def test_returns_nothing_for_user_when_opponent_active_is_dead(self):
    def test_double_faint_returns_correct_decisions(self):
    def test_double_faint_with_no_reserve_pokemon_returns_correct_decisions(self):
```


## Ankimon/poke_engine/evaluate.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 40 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from . import constants
from .data import effectiveness


class Scoring:
    POKEMON_ALIVE_STATIC = 75
    POKEMON_HP = 100  # 100 points for 100% hp, 0 points for 0% hp. This is in addition to being alive
    POKEMON_HIDDEN = 10
    POKEMON_BOOSTS = {
        constants.ATTACK: 15,
        constants.DEFENSE: 15,
        constants.SPECIAL_ATTACK: 15,
        constants.SPECIAL_DEFENSE: 15,
        constants.SPEED: 25,
        constants.ACCURACY: 3,
        constants.EVASION: 3
    }

    POKEMON_BOOST_DIMINISHING_RETURNS = {
        -6: -3.3,
        -5: -3.15,
        -4: -3,
        -3: -2.5,
        -2: -2,
        -1: -1,
        0: 0,
        1: 1,
        2: 2,
        3: 2.5,
        4: 3,
        5: 3.15,
        6: 3.30,
    }

    POKEMON_STATIC_STATUSES = {
        constants.FROZEN: -40,
        constants.SLEEP: -25,
        constants.PARALYZED: -25,
        constants.TOXIC: -30,
        constants.POISON: -10,
        None: 0
    }

    MATCHUP_BONUS = 20

    @staticmethod
    def BURN(burn_multiplier):
        return -25*burn_multiplier

    POKEMON_VOLATILE_STATUSES = {
        constants.LEECH_SEED: -30,
        constants.SUBSTITUTE: 40,
        constants.CONFUSION: -20
    }

    STATIC_SCORED_SIDE_CONDITIONS = {
        constants.REFLECT: 20,
        constants.STICKY_WEB: -25,
        constants.LIGHT_SCREEN: 20,
        constants.AURORA_VEIL: 40,
        constants.SAFEGUARD: 5,
        constants.TAILWIND: 7,
    }

    POKEMON_COUNT_SCORED_SIDE_CONDITIONS = {
        constants.STEALTH_ROCK: -10,
        constants.SPIKES: -7,
        constants.TOXIC_SPIKES: -7,
    }


def evaluate_pokemon(pkmn):
    score = 0
    if pkmn.hp <= 0:
        return score

    score += Scoring.POKEMON_ALIVE_STATIC
    score += Scoring.POKEMON_HP * (float(pkmn.hp) / pkmn.maxhp)

    # boosts have diminishing returns
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.attack_boost] * Scoring.POKEMON_BOOSTS[constants.ATTACK]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.defense_boost] * Scoring.POKEMON_BOOSTS[constants.DEFENSE]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.special_attack_boost] * Scoring.POKEMON_BOOSTS[constants.SPECIAL_ATTACK]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.special_defense_boost] * Scoring.POKEMON_BOOSTS[constants.SPECIAL_DEFENSE]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.speed_boost] * Scoring.POKEMON_BOOSTS[constants.SPEED]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.accuracy_boost] * Scoring.POKEMON_BOOSTS[constants.ACCURACY]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.evasion_boost] * Scoring.POKEMON_BOOSTS[constants.EVASION]

    try:
        score += Scoring.POKEMON_STATIC_STATUSES[pkmn.status]
    except KeyError:
        # KeyError only happens when the status is BURN
        score += Scoring.BURN(pkmn.burn_multiplier)

    for vol_stat in pkmn.volatile_status:
        try:
            score += Scoring.POKEMON_VOLATILE_STATUSES[vol_stat]
        except KeyError:
            pass

    return round(score)


def evaluate(state):
    score = 0

    number_of_opponent_reserve_revealed = len(state.opponent.reserve) + 1
    bot_alive_reserve_count = len([p.hp for p in state.user.reserve.values() if p.hp > 0])
    opponent_alive_reserves_count = len([p for p in state.opponent.reserve.values() if p.hp > 0]) + (6-number_of_opponent_reserve_revealed)

    # evaluate the bot's pokemon
    score += evaluate_pokemon(state.user.active)
    for pkmn in state.user.reserve.values():
        this_pkmn_score = evaluate_pokemon(pkmn)
        score += this_pkmn_score

    # evaluate the opponent's visible pokemon
    score -= evaluate_pokemon(state.opponent.active)
    for pkmn in state.opponent.reserve.values():
        this_pkmn_score = evaluate_pokemon(pkmn)
        score -= this_pkmn_score

    # evaluate the side-conditions for the bot
    for condition, count in state.user.side_conditions.items():
        if condition in Scoring.STATIC_SCORED_SIDE_CONDITIONS:
            score += count * Scoring.STATIC_SCORED_SIDE_CONDITIONS[condition]
        elif condition in Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS:
            score += count * Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS[condition] * bot_alive_reserve_count

    # evaluate the side-conditions for the opponent
    for condition, count in state.opponent.side_conditions.items():
        if condition in Scoring.STATIC_SCORED_SIDE_CONDITIONS:
            score -= count * Scoring.STATIC_SCORED_SIDE_CONDITIONS[condition]
        elif condition in Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS:
            score -= count * Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS[condition] * opponent_alive_reserves_count

    try:
        matchup_score = Scoring.MATCHUP_BONUS * effectiveness[state.user.active.id][state.opponent.active.id]
        matchup_score -= Scoring.MATCHUP_BONUS * effectiveness[state.opponent.active.id][state.user.active.id]
        score += matchup_score
    except KeyError:
        pass

    return int(score)

```


## Ankimon/poke_engine/select_best_move.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 40 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import math
from collections import defaultdict

from . import constants

from .evaluate import evaluate
from .find_state_instructions import get_all_state_instructions


WON_BATTLE = 100


def remove_guaranteed_opponent_moves(score_lookup):
    """This method removes enemy moves from the score-lookup that do not give the bot a choice.
       For example - if the bot has 1 pokemon left, the opponent is faster, and can kill your active pokemon with move X
       then move X for the opponent will be removed from the score_lookup

       The bot behaves much better when it cannot see these types of decisions"""
    move_combinations = list(score_lookup.keys())
    if len(set(k[0] for k in move_combinations)) == 1:
        return score_lookup
    elif len(set(k[1] for k in move_combinations)) == 1:
        return score_lookup

    # find the opponent's moves where the bot has a choice
    opponent_move_scores = dict()
    opponent_decisions = set()
    for k, score in score_lookup.items():
        opponent_move = k[1]
        if opponent_move not in opponent_move_scores:
            opponent_move_scores[opponent_move] = score
        elif opponent_move in opponent_move_scores and score != opponent_move_scores[opponent_move] and not math.isnan(score):
            opponent_decisions.add(opponent_move)

    # re-create score_lookup with only the opponent's move acquired above
    new_opponent_decisions = dict()
    for k, v in score_lookup.items():
        if k[1] in opponent_decisions:
            new_opponent_decisions[k] = v

    return new_opponent_decisions


def pick_safest(score_lookup, remove_guaranteed=False):
    modified_score_lookup = score_lookup
    if remove_guaranteed:
        modified_score_lookup = remove_guaranteed_opponent_moves(score_lookup)
        if not modified_score_lookup:
            modified_score_lookup = score_lookup
    worst_case = defaultdict(lambda: (tuple(), float('inf')))
    for move_pair, result in modified_score_lookup.items():
        if worst_case[move_pair[0]][1] > result:
            worst_case[move_pair[0]] = move_pair, result

    safest = max(worst_case, key=lambda x: worst_case[x][1])
    return worst_case[safest]


def move_item_to_front_of_list(l, item):
    all_indicies = list(range(len(l)))
    this_index = l.index(item)
    all_indicies.remove(this_index)
    all_indicies.insert(0, this_index)
    return [l[i] for i in all_indicies]


def get_payoff_matrix(mutator, user_options, opponent_options, depth=2, prune=True):
    """
    :param mutator: a StateMutator object representing the state of the battle
    :param user_options: options for the bot
    :param opponent_options: options for the opponent
    :param depth: the remaining depth before the state is evaluated
    :param prune: specify whether or not to prune the tree
    :return: a dictionary representing the potential move combinations and their associated scores
    """

    winner = mutator.state.battle_is_finished()
    if winner:
        return {(constants.DO_NOTHING_MOVE, constants.DO_NOTHING_MOVE): evaluate(mutator.state) + WON_BATTLE*depth*winner}

    depth -= 1

    # if the battle is not over, but the opponent has no moves - we want to return the user options as moves
    # this is a special case in a random battle where the opponent's pokemon has fainted, but the opponent still
    # has reserves left that are unseen
    if opponent_options == [constants.DO_NOTHING_MOVE] and mutator.state.opponent.active.hp == 0:
        return {(user_option, constants.DO_NOTHING_MOVE): evaluate(mutator.state) for user_option in user_options}

    state_scores = dict()

    best_score = float('-inf')
    for i, user_move in enumerate(user_options):
        worst_score_for_this_row = float('inf')
        skip = False

        # opponent_options can change during the loop
        # using opponent_options[:] makes a copy when iterating to ensure no funny-business
        for j, opponent_move in enumerate(opponent_options[:]):
            if skip:
                state_scores[(user_move, opponent_move)] = float('nan')
                continue

            score = 0
            state_instructions = get_all_state_instructions(mutator, user_move, opponent_move)
            if depth == 0:
                for instructions in state_instructions:
                    mutator.apply(instructions.instructions)
                    t_score = evaluate(mutator.state)
                    score += (t_score * instructions.percentage)
                    mutator.reverse(instructions.instructions)

            else:
                for instructions in state_instructions:
                    this_percentage = instructions.percentage
                    mutator.apply(instructions.instructions)
                    next_turn_user_options, next_turn_opponent_options = mutator.state.get_all_options()
                    safest = pick_safest(get_payoff_matrix(mutator, next_turn_user_options, next_turn_opponent_options, depth=depth, prune=prune))
                    score += safest[1] * this_percentage
                    mutator.reverse(instructions.instructions)

            state_scores[(user_move, opponent_move)] = score

            if score < worst_score_for_this_row:
                worst_score_for_this_row = score

            if prune and score < best_score:
                skip = True

                # MOST of the time in pokemon, an opponent's move that causes a prune will cause a prune elsewhere
                # move this item to the front of the list to prune faster
                opponent_options = move_item_to_front_of_list(opponent_options, opponent_move)

        if worst_score_for_this_row > best_score:
            best_score = worst_score_for_this_row

    return state_scores

```


## Ankimon/poke_engine/data/parse_smogon_stats.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 40 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import logging
import ntpath
from datetime import datetime

import requests

from ..helpers import spreads_are_alike
from ..helpers import normalize_name

logger = logging.getLogger(__name__)

OTHER_STRING = "other"
MOVES_STRING = "moves"
ITEM_STRING = "items"
SPREADS_STRING = "spreads"
ABILITY_STRING = "abilities"
EFFECTIVENESS = "effectiveness"


def get_smogon_stats_file_name(game_mode, month_delta=1):
    """
    Gets the smogon stats url based on the game mode
    Uses the previous-month's statistics (pure Python implementation)
    """
    # Blitz handling remains the same
    if game_mode.endswith('blitz'):
        game_mode = game_mode[:-5]

    # Calculate previous month without dateutil
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month

    # Calculate previous month(s) using basic arithmetic
    total_months = year * 12 + month - 1  # -1 to make months 0-based
    total_months -= month_delta
    year = total_months // 12
    month = (total_months % 12) + 1  # Convert back to 1-based

    return f"https://www.smogon.com/stats/{year}-{month:02d}/chaos/{game_mode}-0.json"


def pokemon_is_similar(normalized_name, list_of_pkmn_names):
    return (  # Original implementation preserved
        any(normalized_name.startswith(n) for n in list_of_pkmn_names) or
        any(n.startswith(normalized_name) for n in list_of_pkmn_names)
    )


def get_pokemon_information(smogon_stats_url, pkmn_names=None):
    r = requests.get(smogon_stats_url)

    # Modified fallback calculation without relativedelta
    if r.status_code == 404:
        base_name = ntpath.basename(smogon_stats_url.replace('-0.json', ''))
        fallback_url = get_smogon_stats_file_name(base_name, month_delta=2)
        r = requests.get(fallback_url)

    infos = r.json()['data']
    final_infos = {}

    # Rest of the original implementation remains unchanged
    for pkmn_name, pkmn_information in infos.items():
        normalized_name = normalize_name(pkmn_name)

        if (
            pkmn_names and
            normalized_name not in pkmn_names and
            not pokemon_is_similar(normalized_name, pkmn_names)
        ):
            continue

        else:
            logger.debug("Adding {} to sets lookup for this battle".format(normalized_name))

        spreads = []
        items = []
        moves = []
        abilities = []
        matchup_effectiveness = {}
        total_count = pkmn_information['Raw count']
        final_infos[normalized_name] = {}

        for counter_name, counter_information in pkmn_information["Checks and Counters"].items():
            counter_name = normalize_name(counter_name)
            if counter_name in pkmn_names:
                matchup_effectiveness[counter_name] = round(1 - counter_information[1], 2)

        for spread, count in sorted(pkmn_information['Spreads'].items(), key=lambda x: x[1], reverse=True):
            percentage = round(100 * count / total_count, 2)
            if percentage > 0:
                nature, evs = [normalize_name(i) for i in spread.split(":")]
                evs = evs.replace("/", ",")
                for sp in spreads:
                    if spreads_are_alike(sp, (nature, evs)):
                        sp[2] += percentage
                        break
                else:
                    spreads.append([nature, evs, percentage])

        for item, count in pkmn_information['Items'].items():
            if count > 0:
                items.append((item, round(100*count / total_count, 2)))

        for move, count in pkmn_information['Moves'].items():
            if count > 0 and move and move.lower() != "nothing":
                moves.append((move, round(100*count / total_count, 2)))

        for ability, count in pkmn_information['Abilities'].items():
            if count > 0:
                abilities.append(
                    (ability, round(100 * count / total_count, 2))
                )

        final_infos[normalized_name][SPREADS_STRING] = sorted(spreads, key=lambda x: x[2], reverse=True)
        final_infos[normalized_name][ITEM_STRING] = sorted(items, key=lambda x: x[1], reverse=True)
        final_infos[normalized_name][MOVES_STRING] = sorted(moves, key=lambda x: x[1], reverse=True)
        final_infos[normalized_name][ABILITY_STRING] = sorted(abilities, key=lambda x: x[1], reverse=True)
        final_infos[normalized_name][EFFECTIVENESS] = matchup_effectiveness

    return final_infos

```


## Ankimon/poke_engine/tests/test_parse_smogon_stats.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 40 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest
from unittest import mock
from datetime import date

from poke_engine.data.parse_smogon_stats import get_smogon_stats_file_name


class TestGetSmogonStatsFileName(unittest.TestCase):
    def setUp(self):
        self.datetime_patch = mock.patch('poke_engine.data.parse_smogon_stats.datetime')
        self.addCleanup(self.datetime_patch.stop)
        self.datetime_mock = self.datetime_patch.start()

        self.current_date_mock = date(2019, 6, 5)

    def test_returns_single_digit_month_properly(self):
        self.datetime_mock.now.return_value = self.current_date_mock
        file_name = get_smogon_stats_file_name('gen7ou', month_delta=2)

        self.assertEqual('https://www.smogon.com/stats/2019-04/chaos/gen7ou-0.json', file_name)

    def test_works_with_double_digit_month(self):
        self.current_date_mock = date(2019, 11, 5)
        self.datetime_mock.now.return_value = self.current_date_mock
        file_name = get_smogon_stats_file_name('gen7ou', month_delta=2)

        self.assertEqual('https://www.smogon.com/stats/2019-09/chaos/gen7ou-0.json', file_name)

    def test_returns_previous_year_properly(self):
        self.current_date_mock = date(2019, 1, 5)
        self.datetime_mock.now.return_value = self.current_date_mock
        file_name = get_smogon_stats_file_name('gen7ou', month_delta=2)

        self.assertEqual('https://www.smogon.com/stats/2018-11/chaos/gen7ou-0.json', file_name)

```


## Ankimon/poke_engine/teams/load_team.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 40 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import random
import os
from .team_converter import export_to_packed

TEAM_JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teams")


def load_team(name):
    if name is None:
        return 'null'

    path = os.path.join(TEAM_JSON_DIR, "{}".format(name))
    if os.path.isdir(path):
        team_file_names = list()
        for f in os.listdir(path):
            full_path = os.path.join(path, f)
            if os.path.isfile(full_path) and not f.startswith('.'):
                team_file_names.append(full_path)
        file_path = random.choice(team_file_names)

    elif os.path.isfile(path):
        file_path = path
    else:
        raise ValueError("Path must be file or dir: {}".format(name))

    with open(file_path, 'r') as f:
        team_json = f.read()

    return export_to_packed(team_json)

```


## Ankimon/functions/battle_text_functions.py
*   **Why it was selected**: High structural centrality. It acts as a `utility` layer and is imported by 40 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
def effectiveness_text(effect_value):
    if effect_value == 0:
        effective_txt = "has missed."
    elif effect_value <= 0.5:
        effective_txt = "was not very effective."
    elif effect_value <= 1:
        effective_txt = "was effective."
    elif effect_value <= 1.5:
        effective_txt = "was very effective !"
    elif effect_value <= 2:
        effective_txt = "was super effective !"
    else:
        effective_txt = "was effective."
        #return None
    return effective_txt
```


## Ankimon/poke_engine/config.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 40 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
class _ShowdownConfig:
    damage_calc_type: str

    def __init__(self):
        self.damage_calc_type = 'all'


ShowdownConfig = _ShowdownConfig()

```


## Ankimon/poke_engine/tests/test_state_mutator.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 711 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest

from collections import defaultdict
from poke_engine import constants

from poke_engine.battle import Pokemon as StatePokemon
from poke_engine.objects import State, Side, Pokemon, StateMutator


class TestStatemutator(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                {
                    "rattata": Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    "charmander": Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    "squirtle": Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    "bulbasaur": Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    "pidgey": Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                },
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                {
                    "rattata": Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    "charmander": Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    "squirtle": Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    "bulbasaur": Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    "pidgey": Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                },
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.mutator = StateMutator(self.state)

    def test_switch_instruction_replaces_active(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.USER,
            "pikachu",
            "rattata"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual("rattata", self.state.user.active.id)

    def test_switch_instruction_replaces_active_for_opponent(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.OPPONENT,
            "pikachu",
            "rattata"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual("rattata", self.state.opponent.active.id)

    def test_switch_instruction_places_active_into_reserve(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.USER,
            "pikachu",
            "rattata"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        try:
            self.state.user.reserve["pikachu"]
        except KeyError:
            self.fail("`pikachu` is not in `self.reserve`")

    def test_reverse_switch_instruction_replaces_active(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.USER,
            "rattata",
            "pikachu"
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual("rattata", self.state.user.active.id)

    def test_apply_volatile_status_properly_applies_status(self):
        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.USER,
            "leechseed"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertIn("leechseed", self.state.user.active.volatile_status)

    def test_reverse_volatile_status_properly_removes_status(self):
        self.state.user.active.volatile_status.add("leechseed")
        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.USER,
            "leechseed"
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertNotIn("leechseed", self.state.user.active.volatile_status)

    def test_damage_is_properly_applied(self):
        instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        damage_taken = self.state.user.active.maxhp - self.state.user.active.hp

        self.assertEqual(50, damage_taken)

    def test_damage_is_properly_reversed(self):
        self.state.user.active.hp -= 50
        instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        damage_taken = self.state.user.active.maxhp - self.state.user.active.hp

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestStatemutator(unittest.TestCase):
    def setUp(self):
    def test_switch_instruction_replaces_active(self):
    def test_switch_instruction_replaces_active_for_opponent(self):
    def test_switch_instruction_places_active_into_reserve(self):
    def test_reverse_switch_instruction_replaces_active(self):
    def test_apply_volatile_status_properly_applies_status(self):
    def test_reverse_volatile_status_properly_removes_status(self):
    def test_damage_is_properly_applied(self):
    def test_damage_is_properly_reversed(self):
    def test_healing_is_properly_applied(self):
    def test_healing_is_properly_reversed(self):
    def test_boost_is_properly_applied(self):
    def test_boost_is_properly_reversed(self):
    def test_boost_is_properly_reversed_when_a_boost_previously_existed(self):
    def test_unboost_is_properly_applied(self):
    def test_unboost_is_properly_reversed(self):
    def test_apply_status_properly_applies_status(self):
    def test_apply_status_is_properly_reversed(self):
    def test_remove_status_properly_removes_status(self):
    def test_remove_status_is_properly_reversed(self):
    def test_side_start_is_properly_applied(self):
    def test_side_start_is_properly_reversed(self):
    def test_side_end_is_properly_applied(self):
    def test_side_end_is_properly_reversed(self):
    def test_disable_move(self):
    def test_reverse_disable_move(self):
    def test_enable_move(self):
    def test_reverse_enable_move(self):
    def test_setting_weather(self):
    def test_setting_weather_when_previous_weather_exists(self):
    def test_reversing_weather_when_previous_weather_exists(self):
    def test_reverse_setting_weather(self):
    def test_apply_and_reverse_setting_weather_works(self):
    def test_apply_and_reverse_setting_weather_works_with_weather_previously_existing(self):
    def test_setting_field(self):
    def test_reverse_setting_field(self):
    def test_apply_and_reverse_field(self):
    def test_apply_and_reverse_field_when_previous_field_exists(self):
    def test_end_active_field(self):
    def test_reversing_end_active_field(self):
    def test_toggle_trickroom_sets_trickroom(self):
    def test_reverse_instruction_unsets_trickroom(self):
    def test_reverse_instruction_sets_trickroom(self):
    def test_toggle_trickroom_unsets_trickroom(self):
    def test_apply_and_reverse_trickroom(self):
    def test_change_types_properly_changes_types(self):
    def test_reverse_change_types(self):
    def test_apply_and_reverse_change_types(self):
    def test_changing_item(self):
    def test_reversing_changE_item(self):
    def test_changing_item_and_reversing_item(self):
    def test_wish_starting(self):
    def test_wish_starting_and_reversing(self):
    def test_previous_wish_reverses_to_exactly_the_same(self):
    def test_decrement_wish(self):
    def test_decrement_wish_and_reverse_decrement_wish(self):
    def test_change_stats_basic_case(self):
    def test_reverse_change_stats_basic_case(self):
```


## Ankimon/poke_engine/special_effects/moves/modify_move.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 583 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from ... import constants
from ...data import pokedex
from ...damage_calculator import is_super_effective


def collisioncourse(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    if is_super_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.3
    return attacking_move


def suckerpunch(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    if not first_move or defending_move.get(constants.CATEGORY) not in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = 0

    return attacking_move


def eruption(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    attacking_move = attacking_move.copy()
    attacker_hp_percent = attacking_pokemon.hp / attacking_pokemon.maxhp
    attacking_move[constants.BASE_POWER] *= attacker_hp_percent
    return attacking_move


def tailslap(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    # skill-link will boost damage by 5x, so no need to do it again here if that is the pokemon's ability
    if attacking_pokemon.ability != 'skilllink':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 3.2
    return attacking_move


def freezedry(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    if 'water' in defending_pokemon.types:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 4
    return attacking_move


def hex(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    if defending_pokemon.status is not None:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def barbbarrage(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    if defending_pokemon.status in [constants.POISON, constants.TOXIC]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def foulplay(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    attacking_move = attacking_move.copy()
    attacking_move[constants.BASE_POWER] *= defending_pokemon.calculate_boosted_stats()[constants.ATTACK] / \
                                            attacking_pokemon.calculate_boosted_stats()[constants.ATTACK]
    return attacking_move


def storedpower(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    multiplier = attacking_pokemon.attack_boost + attacking_pokemon.defense_boost + \
                 attacking_pokemon.special_attack_boost + attacking_pokemon.special_defense_boost + \
                 attacking_pokemon.speed_boost
    if multiplier > 0:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= multiplier
    return attacking_move


def psyshock(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    defending_stats = defending_pokemon.calculate_boosted_stats()
    attacking_move = attacking_move.copy()
    attacking_move[constants.BASE_POWER] *= (defending_stats[constants.SPECIAL_DEFENSE] / defending_stats[constants.DEFENSE])
    return attacking_move


def facade(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    if attacking_pokemon.status is not None:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def avalanche(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    if first_move is False and defending_move.get(constants.CATEGORY) in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def gyroball(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    # power = (25 × TargetSpeed ÷ UserSpeed) + 1
    attacking_move = attacking_move.copy()
    attacker_speed = attacking_pokemon.calculate_boosted_stats()[constants.SPEED]
    defender_speed = defending_pokemon.calculate_boosted_stats()[constants.SPEED]
    attacking_move[constants.BASE_POWER] = min(150, (25 * defender_speed / attacker_speed) + 1)
    return attacking_move


def electroball(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    speed_ratio = defending_pokemon.calculate_boosted_stats()[constants.SPEED] / attacking_pokemon.calculate_boosted_stats()[constants.SPEED]

    attacking_move = attacking_move.copy()
    if speed_ratio < 0.25:
        attacking_move[constants.BASE_POWER] = 150
    elif speed_ratio < 0.33:
        attacking_move[constants.BASE_POWER] = 120
    elif speed_ratio < 0.50:
        attacking_move[constants.BASE_POWER] = 80
    elif speed_ratio < 1:
        attacking_move[constants.BASE_POWER] = 60
    else:
        attacking_move[constants.BASE_POWER] = 40

    return attacking_move


def focuspunch(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    # technically wrong - a move missing would allow focuspunch to hit, however that information is not present here
    if first_move or defending_move.get(constants.CATEGORY) in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0
    return attacking_move


def acrobatics(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    # acrobatics is 110 by default. If the pokemon has an item, it will go to 55
    # technically this should be the other way around, but the evaluation logic should
    # assume that the opponent's pokemon has a 110 BP move (worst case unless known)
    if attacking_pokemon.item not in [None, "None", constants.UNKNOWN_ITEM]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 0.5
    return attacking_move


def technoblast(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
    if attacking_pokemon.item == 'burndrive':
        attacking_move = attacking_move.copy()
        attacking_move[constants.TYPE] = 'fire'

    elif attacking_pokemon.item == 'chilldrive':
        attacking_move = attacking_move.copy()
        attacking_move[constants.TYPE] = 'ice'

    elif attacking_pokemon.item == 'dousedrive':
        attacking_move = attacking_move.copy()

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def collisioncourse(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def suckerpunch(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def eruption(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def tailslap(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def freezedry(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def hex(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def barbbarrage(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def foulplay(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def storedpower(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def psyshock(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def facade(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def avalanche(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def gyroball(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def electroball(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def focuspunch(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def acrobatics(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def technoblast(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def multiattack(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def ragingbull(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def knockoff(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def tripledive(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def twinbeam(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def hurricane(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def blizzard(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def solarbeam(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def toxic(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def strengthsap(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def revelationdance(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def lowkick(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def painsplit(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def pursuit(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def aurawheel(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def dynamaxcannon(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def dragondarts(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def geargrind(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def bonemerang(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def boltbeak(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def clangoroussoul(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def filletaway(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def terablast(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def bodypress(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def lifedew(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def steelbeam(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def doubleironbash(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def morningsun(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def shoreup(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def heavyslam(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def noretreat(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def growth(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def expandingforce(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def psyblade(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def risingvoltage(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def steelroller(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def mistyexplosion(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def terrainpulse(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def poltergeist(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def tripleaxel(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def dualwingbeat(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def flowertrick(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def wickedblow(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def surgingstrikes(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def weatherball(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def futuresight(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def lastrespects(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def populationbomb(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def doubleshock(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def hydrosteam(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
def modify_attack_being_used(attacking_side, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather, terrain):
```


## Ankimon/poke_engine/special_effects/abilities/modify_attack_against.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 450 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from ... import constants

from ...damage_calculator import is_super_effective


def levitate(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ground' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT and attacking_move[constants.ID] != 'thousandarrows':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0
    return attacking_move


def lightningrod(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'electric' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.BOOSTS] = {
            constants.SPECIAL_ATTACK: 1
        }
    return attacking_move


def stormdrain(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'water' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.BOOSTS] = {
            constants.SPECIAL_ATTACK: 1
        }
    return attacking_move


def goodasgold(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.STATUS:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = False
    return attacking_move


def voltabsorb(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'electric' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.HEAL_TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.HEAL] = [
            1,
            4
        ]
    return attacking_move


def waterabsorb(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'water' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.HEAL_TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.HEAL] = [
            1,
            4
        ]
    return attacking_move


def eartheater(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ground' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.HEAL_TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.HEAL] = [
            1,
            4
        ]
    return attacking_move


def thermalexchange(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'fire' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.SECONDARY] = {
            constants.CHANCE: 100,
            constants.BOOSTS: {constants.ATTACK: 1}
        }
    return attacking_move


def motordrive(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'electric' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.BOOSTS] = {
            constants.SPEED: 1
        }
    return attacking_move


def sapsipper(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'grass' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.VOLATILE_STATUS] = None
        attacking_move[constants.TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.BOOSTS] = {
            constants.ATTACK: 1
        }
    return attacking_move


def multiscale(attacking_move, attacking_pokemon, defending_pokemon):
    if defending_pokemon.hp >= defending_pokemon.maxhp:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] /= 2

    return attacking_move


def thickfat(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] in ['fire', 'ice']:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] /= 2
    return attacking_move


def solidrock(attacking_move, attacking_pokemon, defending_pokemon):
    if is_super_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= (3/4)
    return attacking_move


def contrary(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        if constants.BOOSTS in attacking_move:

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def levitate(attacking_move, attacking_pokemon, defending_pokemon):
def lightningrod(attacking_move, attacking_pokemon, defending_pokemon):
def stormdrain(attacking_move, attacking_pokemon, defending_pokemon):
def goodasgold(attacking_move, attacking_pokemon, defending_pokemon):
def voltabsorb(attacking_move, attacking_pokemon, defending_pokemon):
def waterabsorb(attacking_move, attacking_pokemon, defending_pokemon):
def eartheater(attacking_move, attacking_pokemon, defending_pokemon):
def thermalexchange(attacking_move, attacking_pokemon, defending_pokemon):
def motordrive(attacking_move, attacking_pokemon, defending_pokemon):
def sapsipper(attacking_move, attacking_pokemon, defending_pokemon):
def multiscale(attacking_move, attacking_pokemon, defending_pokemon):
def thickfat(attacking_move, attacking_pokemon, defending_pokemon):
def solidrock(attacking_move, attacking_pokemon, defending_pokemon):
def contrary(attacking_move, attacking_pokemon, defending_pokemon):
def noguard(attacking_move, attacking_pokemon, defending_pokemon):
def flashfire(attacking_move, attacking_pokemon, defending_pokemon):
def wellbakedbody(attacking_move, attacking_pokemon, defending_pokemon):
def armortail(attacking_move, attacking_pokemon, defending_pokemon):
def bulletproof(attacking_move, attacking_pokemon, defending_pokemon):
def windrider(attacking_move, attacking_pokemon, defending_pokemon):
def furcoat(attacking_move, attacking_pokemon, defending_pokemon):
def fluffy(attacking_move, attacking_pokemon, defending_pokemon):
def magicbounce(attacking_move, attacking_pokemon, defending_pokemon):
def ironbarbs(attacking_move, attacking_pokemon, defending_pokemon):
def roughskin(attacking_move, attacking_pokemon, defending_pokemon):
def wonderguard(attacking_move, attacking_pokemon, defending_pokemon):
def stamina(attacking_move, attacking_pokemon, defending_pokemon):
def waterbubble(attacking_move, attacking_pokemon, defending_pokemon):
def queenlymajesty(attacking_move, attacking_pokemon, defending_pokemon):
def tanglinghair(attacking_move, attacking_pokemon, defending_pokemon):
def cottondown(attacking_move, attacking_pokemon, defending_pokemon):
def marvelscale(attacking_move, attacking_pokemon, defending_pokemon):
def justified(attacking_move, attacking_pokemon, defending_pokemon):
def shielddust(attacking_move, attacking_pokemon, defending_pokemon):
def competitive(attacking_move, attacking_pokemon, defending_pokemon):
def defiant(attacking_move, attacking_pokemon, defending_pokemon):
def weakarmor(attacking_move, attacking_pokemon, defending_pokemon):
def liquidooze(attacking_move, attacking_pokemon, defending_pokemon):
def innerfocus(attacking_move, attacking_pokemon, defending_pokemon):
def soundproof(attacking_move, attacking_pokemon, defending_pokemon):
def darkaura(attacking_move, attacking_pokemon, defending_pokemon):
def fairyaura(attacking_move, attacking_pokemon, defending_pokemon):
def icescales(attacking_move, attacking_pokemon, defending_pokemon):
def punkrock(attacking_move, attacking_pokemon, defending_pokemon):
def steamengine(attacking_move, attacking_pokemon, defending_pokemon):
def damp(attacking_move, attacking_pokemon, defending_pokemon):
def guarddog(attacking_move, attacking_pokemon, defending_pokemon):
def purifyingsalt(attacking_move, attacking_pokemon, defending_pokemon):
def ability_modify_attack_against(ability_name, attacking_move, attacking_pokemon, defending_pokemon):
```


## Ankimon/poke_engine/damage_calculator.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 325 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from copy import copy
from copy import deepcopy

from . import constants
from .data import all_move_json
from .data import pokedex


pokemon_type_indicies = {
    'normal': 0,
    'fire': 1,
    'water': 2,
    'electric': 3,
    'grass': 4,
    'ice': 5,
    'fighting': 6,
    'poison': 7,
    'ground': 8,
    'flying': 9,
    'psychic': 10,
    'bug': 11,
    'rock': 12,
    'ghost': 13,
    'dragon': 14,
    'dark': 15,
    'steel': 16,
    'fairy': 17,

    # ??? and typeless are the same thing
    'typeless': 18,
    '???': 18,
}

# Note : I changed the 0s to 1/8. Also, the following matrix seems to be taken from https://pokemondb.net/type
damage_multipication_array = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1/2, 1/8, 1, 1, 1/2, 1, 1],
                              [1, 1/2, 1/2, 1, 2, 2, 1, 1, 1, 1, 1, 2, 1/2, 1, 1/2, 1, 2, 1, 1],
                              [1, 2, 1/2, 1, 1/2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1/2, 1, 1, 1, 1],
                              [1, 1, 2, 1/2, 1/2, 1, 1, 1, 1/8, 2, 1, 1, 1, 1, 1/2, 1, 1, 1, 1],
                              [1, 1/2, 2, 1, 1/2, 1, 1, 1/2, 2, 1/2, 1, 1/2, 2, 1, 1/2, 1, 1/2, 1, 1],
                              [1, 1/2, 1/2, 1, 2, 1/2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1/2, 1, 1],
                              [2, 1, 1, 1, 1, 2, 1, 1/2, 1, 1/2, 1/2, 1/2, 2, 1/8, 1, 2, 2, 1/2, 1],
                              [1, 1, 1, 1, 2, 1, 1, 1/2, 1/2, 1, 1, 1, 1/2, 1/2, 1, 1, 1/8, 2, 1],
                              [1, 2, 1, 2, 1/2, 1, 1, 2, 1, 1/8, 1, 1/2, 2, 1, 1, 1, 2, 1, 1],
                              [1, 1, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1/2, 1, 1],
                              [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1/2, 1, 1, 1, 1, 1/8, 1/2, 1, 1],
                              [1, 1/2, 1, 1, 2, 1, 1/2, 1/2, 1, 1/2, 2, 1, 1, 1/2, 1, 2, 1/2, 1/2, 1],
                              [1, 2, 1, 1, 1, 2, 1/2, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 1/2, 1, 1],
                              [1/8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1/2, 1/8, 1],
                              [1, 1, 1, 1, 1, 1, 1/2, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1/2, 1],
                              [1, 1/2, 1/2, 1/2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1/2, 2, 1],
                              [1, 1/2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1, 1, 1, 2, 2, 1/2, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]


SPECIAL_LOGIC_MOVES = {
    "seismictoss": lambda attacker, defender: [int(attacker.level)] if "ghost" not in defender.types else None,
    "nightshade": lambda attacker, defender: [int(attacker.level)] if "normal" not in defender.types else None,
    "superfang": lambda attacker, defender: [int(defender.hp / 2)] if "ghost" not in defender.types else None,
    "naturesmadness": lambda attacker, defender: [int(defender.hp / 2)],
    "guardianofalola": lambda attacker, defender: [int(3*defender.hp / 4)],
    "ruination": lambda attacker, defender: [int(defender.hp / 2)],
    "finalgambit": lambda attacker, defender: [int(attacker.hp)] if "ghost" not in defender.types else None,
    "endeavor": lambda attacker, defender: [int(defender.hp - attacker.hp)] if defender.hp > attacker.hp and "ghost" not in defender.types else None,
    "painsplit": lambda attacker, defender: [defender.hp - (attacker.hp + defender.hp)/2],
}


TERRAIN_DAMAGE_BOOST = 1.3


def _calculate_damage(attacker, defender, move, conditions=None, calc_type='average'):
    # This function assumes the `move` dictionary has already been updated to account for move/item/ability special-effects
    # You may want to use `calculate_damage`

    acceptable_calc_types = ['average', 'min', 'max', 'min_max', 'min_max_average', 'all']
    if calc_type not in acceptable_calc_types:
        raise ValueError("{} is not one of {}".format(calc_type, acceptable_calc_types))

    attacking_move = get_move(move)
    if attacking_move is None:
        raise TypeError("Invalid move: {}".format(move))

    attacking_type = attacking_move.get(constants.CATEGORY)
    if attacking_type == constants.PHYSICAL:
        attack = constants.ATTACK
        defense = constants.DEFENSE
    elif attacking_type == constants.SPECIAL:
        attack = constants.SPECIAL_ATTACK
        defense = constants.SPECIAL_DEFENSE
    else:
        return None

    try:
        return SPECIAL_LOGIC_MOVES[attacking_move[constants.ID]](attacker, defender)
    except KeyError:
        pass

    if attacking_move[constants.BASE_POWER] == 0:
        return [0]

    if conditions is None:
        conditions = {}

    attacking_stats = attacker.calculate_boosted_stats()
    defending_stats = defender.calculate_boosted_stats()

    if attacker.ability == 'unaware':
        if defense == constants.DEFENSE:
            defending_stats[defense] = defender.defense
        elif defense == constants.SPECIAL_DEFENSE:
            defending_stats[defense] = defender.special_defense
    if defender.ability == 'unaware':
        if attack == constants.ATTACK:
            attacking_stats[attack] = attacker.attack
        elif defense == constants.SPECIAL_ATTACK:
            attacking_stats[attack] = attacker.special_attack

    defending_types = defender.types
    if attacking_move[constants.ID] == 'thousandarrows' and 'flying' in defending_types:
        defending_types = copy(defender.types)
        defending_types.remove('flying')
    if attacking_move[constants.TYPE] == 'ground' and constants.ROOST in defender.volatile_status:
        defending_types = copy(defender.types)
        try:
            defending_types.remove('flying')
        except ValueError:
            pass

    # rock types get 1.5x SPDEF in sand
    # ice types get 1.5x DEF in snow
    try:
        if conditions[constants.WEATHER] == constants.SAND and 'rock' in defender.types:
            defending_stats[constants.SPECIAL_DEFENSE] = int(defending_stats[constants.SPECIAL_DEFENSE] * 1.5)
        elif conditions[constants.WEATHER] == constants.SNOW and 'ice' in defender.types:
            defending_stats[constants.DEFENSE] = int(defending_stats[constants.DEFENSE] * 1.5)
    except KeyError:
        pass

    if defender.ability == "tabletsofruin":
        attacking_stats[constants.ATTACK] *= 0.75
    elif defender.ability == "vesselofruin":
        attacking_stats[constants.SPECIAL_ATTACK] *= 0.75
    if attacker.ability == "swordofruin":
        defending_stats[constants.DEFENSE] *= 0.75
    elif attacker.ability == "beadsofruin":
        defending_stats[constants.SPECIAL_DEFENSE] *= 0.75

    damage = int(int((2 * attacker.level) / 5) + 2) * attacking_move[constants.BASE_POWER]
    damage = int(damage * attacking_stats[attack] / defending_stats[defense])

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def _calculate_damage(attacker, defender, move, conditions=None, calc_type='average'):
def is_super_effective(move_type, defending_pokemon_types):
def is_not_very_effective(move_type, defending_pokemon_types):
def calculate_modifier(attacker, defender, defending_types, attacking_move, conditions):
def get_move(move):
def get_damage_rolls(damage, calc_type):
def type_effectiveness_modifier(attacking_move_type, defending_types):
def weather_modifier(attacking_move, weather):
def stab_modifier(attacking_pokemon, attacking_move):
def burn_modifier(attacking_pokemon, attacking_move):
def light_screen_modifier(attacking_move, light_screen):
def reflect_modifier(attacking_move, reflect):
def aurora_veil_modifier(aurora_veil):
def terrain_modifier(attacker, defender, attacking_move, terrain):
def volatile_status_modifier(attacking_move, attacker, defender):
def calculate_damage(state, attacking_side_string, attacking_move, defending_move, calc_type='average'):
def calculate_futuresight_damage(state, attacking_side_string, future_sight_user, calc_type='average'):
```


## Ankimon/poke_engine/special_effects/abilities/modify_attack_being_used.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 303 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from ... import constants

from ...damage_calculator import is_not_very_effective
from ...damage_calculator import is_super_effective


def analytic(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if not first_move:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.3
    return attacking_move


def adaptability(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] in attacking_pokemon.types:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 4/3)
    return attacking_move


def rockypayload(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == "rock":
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 3/2)
    return attacking_move


def aerilate(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'normal':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 1.2)
        attacking_move[constants.TYPE] = 'flying'
    return attacking_move


def galvanize(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'normal':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 1.2)
        attacking_move[constants.TYPE] = 'electric'
    return attacking_move


def liquidvoice(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if constants.SOUND in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.TYPE] = 'water'
    return attacking_move


def compoundeyes(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.ACCURACY] is not True:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] *= 1.3
    return attacking_move


def contrary(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    # look at this logic, I want to fucking die
    if attacking_move[constants.TARGET] in constants.MOVE_TARGET_SELF:
        attacking_move = attacking_move.copy()
        if constants.BOOSTS in attacking_move:
            attacking_move[constants.BOOSTS] = attacking_move[constants.BOOSTS].copy()
            for k, v in attacking_move[constants.BOOSTS].items():
                attacking_move[constants.BOOSTS][k] = -1*v
        if attacking_move[constants.SECONDARY] and constants.BOOSTS in attacking_move[constants.SECONDARY]:
            attacking_move[constants.SECONDARY] = attacking_move[constants.SECONDARY].copy()
            attacking_move[constants.SECONDARY][constants.BOOSTS] = attacking_move[constants.SECONDARY][constants.BOOSTS].copy()
            for k, v in attacking_move[constants.SECONDARY][constants.BOOSTS].items():
                attacking_move[constants.SECONDARY][constants.BOOSTS][k] = -1*v
    elif constants.SELF in attacking_move and constants.BOOSTS in attacking_move[constants.SELF]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.SELF] = attacking_move[constants.SELF].copy()
        attacking_move[constants.SELF][constants.BOOSTS] = attacking_move[constants.SELF][constants.BOOSTS].copy()
        for k, v in attacking_move[constants.SELF][constants.BOOSTS].items():
            attacking_move[constants.SELF][constants.BOOSTS][k] = -1 * v

    elif attacking_move[constants.SECONDARY] and constants.SELF in attacking_move[constants.SECONDARY]:
        if constants.BOOSTS in attacking_move[constants.SECONDARY][constants.SELF]:
            attacking_move = attacking_move.copy()
            attacking_move[constants.SECONDARY] = attacking_move[constants.SECONDARY].copy()
            attacking_move[constants.SECONDARY][constants.SELF] = attacking_move[constants.SECONDARY][constants.SELF].copy()
            attacking_move[constants.SECONDARY][constants.SELF][constants.BOOSTS] = attacking_move[constants.SECONDARY][constants.SELF][constants.BOOSTS].copy()
            for k, v in attacking_move[constants.SECONDARY][constants.SELF][constants.BOOSTS].items():
                attacking_move[constants.SECONDARY][constants.SELF][constants.BOOSTS][k] = -1 * v

    return attacking_move


def hustle(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] *= 0.8
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def ironfist(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if "punch" in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def sharpness(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if "slicing" in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def megalauncher(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if "pulse" in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def noguard(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    attacking_move = attacking_move.copy()
    attacking_move[constants.ACCURACY] = True
    return attacking_move


def pixilate(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'normal':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 1.2)
        attacking_move[constants.TYPE] = 'fairy'
    return attacking_move


def refrigerate(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'normal':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 1.2)
        attacking_move[constants.TYPE] = 'ice'
    return attacking_move


def scrappy(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    # this logic is technically wrong, but it at least allows the move to hit
    # for example, a fighting move on ice/ghost should technically be super-effective
    # this logic would make it do neutral damage instead
    if 'ghost' in defending_pokemon.types:
        attacking_move = attacking_move.copy()
        attacking_move[constants.TYPE] = "typeless"
    return attacking_move



... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def analytic(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def adaptability(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def rockypayload(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def aerilate(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def galvanize(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def liquidvoice(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def compoundeyes(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def contrary(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def hustle(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def ironfist(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def sharpness(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def megalauncher(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def noguard(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def pixilate(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def refrigerate(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def scrappy(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def serenegrace(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def sheerforce(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def strongjaw(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def technician(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def toughclaws(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def toxicboost(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def hugepower(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def guts(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def reckless(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def rockhead(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def parentalbond(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def tintedlens(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def skilllink(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def waterbubble(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def steelworker(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def neuroforce(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def blaze(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def torrent(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def overgrow(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def swarm(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def defeatist(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def sandforce(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def darkaura(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def fairyaura(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def prankster(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def gorillatactics(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def punkrock(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def steelyspirit(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def stakeout(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def solarpower(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def transistor(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def dragonsmaw(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def windrider(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
def ability_modify_attack_being_used(ability_name, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
```


## Ankimon/poke_engine/tests/test_damage_calculator.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 261 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest
from collections import defaultdict

from poke_engine import constants
from poke_engine.damage_calculator import _calculate_damage
from poke_engine.damage_calculator import calculate_damage
from poke_engine.objects import State
from poke_engine.objects import Side
from poke_engine.objects import Pokemon

from poke_engine.battle import Pokemon as StatePokemon


class TestCalculateDamageAmount(unittest.TestCase):
    def setUp(self):
        self.charizard = Pokemon.from_state_pokemon_dict(StatePokemon("charizard", 100).to_dict())
        self.venusaur = Pokemon.from_state_pokemon_dict(StatePokemon("venusaur", 100).to_dict())

    def test_fire_blast_from_charizard_to_venusaur_without_modifiers(self):
        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([300], dmg)

    def test_flashfire_increases_fire_move_damage(self):
        move = 'fireblast'
        self.charizard.volatile_status.add('flashfire')

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([450], dmg)

    def test_stab_without_weakness_calculates_properly(self):
        move = 'sludgebomb'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([130], dmg)

    def test_4x_weakness_calculates_properly(self):
        move = 'rockslide'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([268], dmg)

    def test_4x_resistance_calculates_properly(self):
        move = 'gigadrain'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([27], dmg)

    def test_immunity_calculates_properly(self):
        move = 'earthquake'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([0], dmg)

    def test_burn_modifier_properly_halves_physical_damage(self):
        move = 'rockslide'

        self.venusaur.status = constants.BURN

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([134], dmg)

    def test_burn_does_not_modify_special_move(self):
        move = 'fireblast'

        self.venusaur.status  = constants.BURN

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([300], dmg)

    def test_sun_stab_and_2x_weakness(self):

        conditions = {
            'weather': constants.SUN
        }

        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')
        self.assertEqual([450], dmg)

    def test_sun_weakens_water_moves(self):

        conditions = {
            'weather': constants.SUN
        }

        move = 'surf'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, conditions, calc_type='max')
        self.assertEqual([87], dmg)

    def test_sand_increases_rock_spdef(self):

        self.venusaur.types = ['rock']

        conditions = {
            'weather': constants.SAND
        }

        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')
        self.assertEqual([51], dmg)

    def test_sand_does_not_double_ground_spdef(self):

        self.venusaur.types = ['water']

        conditions = {
            'weather': constants.SAND
        }

        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')
        self.assertEqual([75], dmg)

    def test_electric_terrain_increases_electric_damage_for_grounded_pokemon(self):
        self.charizard.types = ['fire']

        conditions = {
            constants.TERRAIN: constants.ELECTRIC_TERRAIN
        }

        move = 'thunderbolt'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')

        # normally this is 41
        self.assertEqual([53], dmg)

    def test_psychic_terrain_increases_psychic_damage(self):
        self.charizard.types = ['fire']

        conditions = {
            constants.TERRAIN: constants.PSYCHIC_TERRAIN
        }

        move = 'psychic'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')

        # normally this is 164
        self.assertEqual([213], dmg)

    def test_damage_is_not_increased_if_attacker_is_not_grounded(self):
        self.charizard.types = ['fire', 'flying']


... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestCalculateDamageAmount(unittest.TestCase):
    def setUp(self):
    def test_fire_blast_from_charizard_to_venusaur_without_modifiers(self):
    def test_flashfire_increases_fire_move_damage(self):
    def test_stab_without_weakness_calculates_properly(self):
    def test_4x_weakness_calculates_properly(self):
    def test_4x_resistance_calculates_properly(self):
    def test_immunity_calculates_properly(self):
    def test_burn_modifier_properly_halves_physical_damage(self):
    def test_burn_does_not_modify_special_move(self):
    def test_sun_stab_and_2x_weakness(self):
    def test_sun_weakens_water_moves(self):
    def test_sand_increases_rock_spdef(self):
    def test_sand_does_not_double_ground_spdef(self):
    def test_electric_terrain_increases_electric_damage_for_grounded_pokemon(self):
    def test_psychic_terrain_increases_psychic_damage(self):
    def test_damage_is_not_increased_if_attacker_is_not_grounded(self):
    def test_grassy_terrain_increases_grass_type_move(self):
    def test_misty_terrain_halves_dragon_moves(self):
    def test_psychic_terrain_makes_priority_move_do_nothing(self):
    def test_psychic_terrain_does_not_affect_priority_on_non_grounded(self):
    def test_rain_properly_amplifies_water_damage(self):
    def test_rain_properly_reduces_fire_damage(self):
    def test_reflect_properly_halves_damage(self):
    def test_light_screen_properly_halves_damage(self):
    def test_aurora_veil_properly_halves_damage(self):
    def test_boosts_properly_affect_damage_calculation(self):
    def test_move_versus_partially_typeless_pokemon(self):
    def test_move_versus_partially_typeless_pokemon_with_question_mark_type(self):
    def test_move_versus_completely_typeless_pokemon(self):
    def test_move_versus_completely_typeless_pokemon_with_question_mark_type(self):
    def test_terastallized_pokemon_gets_2x_stab_when_terratype_in_original_types(self):
    def test_terastallized_pokemon_gets_normal_stab_when_terratype_not_in_original_types(self):
    def test_terastallized_pokemon_gets_normal_stab_with_original_types(self):
    def test_terastallized_pokemon_does_not_get_stab_on_nonterra_type(self):
class TestCalculateDamage(unittest.TestCase):
    def setUp(self):
    def test_earthquake_into_levitate_does_zero_damage(self):
    def test_bots_reflect_does_not_reduce_its_own_damage(self):
    def test_moldbreaker_ignores_levitate(self):
    def test_solarbeam_move_produces_damage_amount(self):
    def test_phantomforce_move_produces_damage_amount(self):
```


## Ankimon/poke_engine/tests/test_team_datasets.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 250 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from unittest import TestCase

from poke_engine import constants
from poke_engine.data.team_datasets import _TeamDatasets, PokemonSet, PokemonMoveset
from poke_engine.battle import Pokemon, Move, StatRange


class TestTeamDatasets(TestCase):
    def setUp(self):
        self.team_datasets = _TeamDatasets()

    def test_populating_datasets_from_file_with_empty_list(self):
        self.team_datasets.set_pokemon_sets([])

    def test_populating_datasets_using_known_pokemon(self):
        self.team_datasets.set_pokemon_sets(["garchomp"])
        self.assertIn("garchomp", self.team_datasets.pokemon_sets)

    def test_predict_set_returns_pokemonset(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|jolly|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 1
            }
        }
        garchomp = Pokemon("garchomp", 100)
        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)

        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "jolly",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )

        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_predict_set_returns_more_common_set(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|jolly|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 1,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
                "water|roughskin|rockyhelmet|timid|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 3,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)

        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",  # adamant is more common
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )

        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_predict_set_returns_none_when_no_set_matches(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|jolly|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 1,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.moves = [
            Move("watergun")  # none of the above sets have this
        ]

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertIsNone(predicted_garchomp_set)

    def test_predict_set_returns_set_if_moves_are_a_subset(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|jolly|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 1,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.moves = [
            Move("earthquake")
        ]

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)

        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )

        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_matching_ability_returns_valid_set(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.ability = "roughskin"

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )
        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_mismatching_ability_means_set_is_not_returned(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.ability = "sandforce"

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertIsNone(predicted_garchomp_set)

    def test_item_being_none_allows_set_to_match(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.item = None

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class TestTeamDatasets(TestCase):
    def setUp(self):
    def test_populating_datasets_from_file_with_empty_list(self):
    def test_populating_datasets_using_known_pokemon(self):
    def test_predict_set_returns_pokemonset(self):
    def test_predict_set_returns_more_common_set(self):
    def test_predict_set_returns_none_when_no_set_matches(self):
    def test_predict_set_returns_set_if_moves_are_a_subset(self):
    def test_matching_ability_returns_valid_set(self):
    def test_mismatching_ability_means_set_is_not_returned(self):
    def test_item_being_none_allows_set_to_match(self):
    def test_item_being_unknown_allows_set_to_match(self):
    def test_item_mismatching_does_not_match_set(self):
    def test_item_matching_matches_set(self):
    def test_omits_ability_mismatch_when_flag_is_unset(self):
    def test_omits_item_mismatch_when_flag_is_unset(self):
    def test_omits_item_and_ability_mismatch_when_both_flags_are_unset(self):
    def test_does_not_set_lifeorb_if_can_have_lifeorb_is_false(self):
    def test_does_not_set_heavydutyboots_if_can_have_heavydutyboots_is_false(self):
    def test_does_not_set_choice_item_if_can_have_can_have_choice_item_is_false(self):
    def test_does_not_set_choice_band_if_can_not_have_band_is_true(self):
    def test_min_speed_check_invalidates_a_set(self):
    def test_max_speed_check_invalidates_a_set(self):
    def test_choicescarf_set_properly_fails_when_speed_range_is_present(self):
    def test_boosting_ability_with_speed_range(self):
    def test_pkmn_not_existing_in_datasets_returns_none(self):
    def test_pokemon_with_less_than_four_moves_works(self):
```


## Ankimon/poke_engine/data/scripts/update_moves.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 155 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
# -*- coding: utf-8 -*-
import requests
import json
import copy
import subprocess


"""
This can be run to create a new_moves.json

There is logic in this file to adjust the PokemonShowdown moves.ts into a JSON file
that this bot can use.

Requires `tsc` and `node` on your system

Versions used when writing this:

➜  ~ node --version
v15.3.0
➜  ~ tsc --version
Version 4.2.3

"""


# Fetch latest version
data = requests.get(
    "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/moves.ts"
).text

# write .ts temp file
with open("/tmp/moves.ts", "w") as f:
    f.write(data)

# compile the .ts file into .js. Requires `tsc` on your system
p = subprocess.Popen(['tsc', '/tmp/moves.ts'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = p.stdout.read()
stderr = p.stderr.read()

# exit if stderr is not empty
if stderr:
    print("Something went wrong? stderr: {}".format(stderr))

# add a console log to the .js file. This will error if the file doesn't exist
with open("/tmp/moves.js", "a") as f:
    f.write("console.log(JSON.stringify(exports.Moves));")

# run node on the .js file to get the console log we added
# Requires `node` on your system
p = subprocess.Popen(['node', '/tmp/moves.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = p.stdout.read()
stderr = p.stderr.read()

# stdout should now be parse-able as JSON
moves_dict = json.loads(stdout)


# make modifications to some values for the bot
# shallow copy the dictionary because we might delete things from it
for k, v in moves_dict.copy().items():

    # the bot doesn't care about Z-Moves or Gmax moves. They're omitted entirely
    if v.get("isZ") or v.get("isMax"):
        del[moves_dict[k]]
        continue

    # the bot needs an `id` attribute
    moves_dict[k]["id"] = k

    # some secondary effects had javascript code for them
    # JSON.stringify would've left only the chance reminaing - remove these
    if v.get("secondary") and len(v["secondary"]) == 1 and "chance" in v["secondary"]:
        v["secondary"] = None

    if "secondary" not in v:
        v["secondary"] = None

    if "sideCondition" in v:
        moves_dict[k]["side_conditions"] = moves_dict[k].pop("sideCondition")

    if "forceSwitch" in v and v["forceSwitch"]:
        moves_dict[k]["flags"]["drag"] = 1
        moves_dict[k].pop("forceSwitch")

    # the bot wants some attributes to be lowercase
    moves_dict[k]["category"] = v["category"].lower()
    moves_dict[k]["type"] = v["type"].lower()

    # the bot doesn't care about some attributes
    # they can be removed from this list if the bot
    # ever wants to start using them
    moves_dict[k].pop("selfSwitch", None)
    moves_dict[k].pop("stallingMove", None)
    moves_dict[k].pop("condition", None)
    moves_dict[k].pop("smartTarget", None)
    moves_dict[k].pop("onDamagePriority", None)
    moves_dict[k].pop("contestType", None)
    moves_dict[k].pop("critRatio", None)
    moves_dict[k].pop("num", None)
    moves_dict[k].pop("zMove", None)
    moves_dict[k].pop("isNonstandard", None)
    moves_dict[k].pop("ignoreImmunity", None)
    moves_dict[k].pop("overrideOffensiveStat", None)
    moves_dict[k].pop("maxMove", None)
    moves_dict[k].pop("slotCondition", None)
    moves_dict[k].pop("noSketch", None)
    moves_dict[k].pop("ignoreDefensive", None)
    moves_dict[k].pop("pseudoWeather", None)
    moves_dict[k].pop("ignoreEvasion", None)
    moves_dict[k].pop("hasCrashDamage", None)
    moves_dict[k].pop("realMove", None)
    moves_dict[k].pop("breaksProtect", None)
    moves_dict[k].pop("secondaries", None)
    moves_dict[k].pop("pressureTarget", None)
    moves_dict[k].pop("mindBlownRecoil", None)
    moves_dict[k].pop("selfdestruct", None)
    moves_dict[k].pop("nonGhostTarget", None)
    moves_dict[k].pop("isFutureMove", None)

    if k.startswith("hiddenpower") and k != "hiddenpower":
        hp_move = moves_dict.pop(k)
        moves_dict[f"{k}60"] = hp_move
        moves_dict[f"{k}60"]["id"] = f"{k}60"
        moves_dict[f"{k}70"] = copy.deepcopy(hp_move)
        moves_dict[f"{k}70"]["id"] = f"{k}70"
        moves_dict[f"{k}70"]["basePower"] = 70


# the bot needs these keys to be named differently
string_json = json.dumps(moves_dict)
string_json = string_json.replace('"atk"', '"attack"')
string_json = string_json.replace('"def"', '"defense"')
string_json = string_json.replace('"spa"', '"special-attack"')
string_json = string_json.replace('"spd"', '"special-defense"')
string_json = string_json.replace('"spe"', '"speed"')
moves_dict = json.loads(string_json)

# custom changes for the bot to work
# some of these are dumb, but here we are

moves_dict["return"]["basePower"] = 102
moves_dict["return102"] = copy.deepcopy(moves_dict["return"])
moves_dict["return102"]["id"] = "return102"

moves_dict["obstruct"]["volatileStatus"] = "protect"

moves_dict["roost"]["volatileStatus"] = "roost"

moves_dict["saltcure"]["volatileStatus"] = "saltcure"
moves_dict["saltcure"]["secondary"] = None

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
```


## Ankimon/battle_loop.py
*   **Why it was selected**: High structural centrality. It acts as a `glue` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 132 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import copy
import random
from dataclasses import dataclass, field
from typing import Any, Optional

from aqt import mw
from aqt.qt import QDialog

from .singletons import (
    main_pokemon,
    enemy_pokemon,
    settings_obj,
    reviewer_obj,
    ankimon_tracker_obj,
    test_window,
    evo_window,
    logger,
    achievements,
    trainer_card,
    translator,
)
from .functions.encounter_functions import handle_enemy_faint, handle_main_pokemon_faint
from .functions.badges_functions import (
    handle_review_count_achievement,
    check_for_badge,
    receive_badge,
)
from .functions.battle_functions import (
    update_pokemon_battle_status,
    validate_pokemon_status,
    process_battle_data,
)
from .functions.drawing_utils import tooltipWithColour
from .utils import safe_get_random_move, play_effect_sound, play_sound
from .functions.ankimon_hooks_to_poke_engine import simulate_battle_with_poke_engine
from .classes.choose_move_dialog import MoveSelectionDialog
from .pyobj.error_handler import show_warning_with_traceback


@dataclass
class BattleState:
    new_state: Any = None
    mutator_full_reset: int = 1
    user_hp_after: int = 0
    opponent_hp_after: int = 0
    dmg_from_enemy_move: int = 0
    dmg_from_user_move: int = 0
    item_receive_value: int = 0
    collected_pokemon_ids: set = field(default_factory=set)


_state = BattleState()


def init_battle_state(collected_pokemon_ids: set):
    _state.item_receive_value = random.randint(3, 385)
    _state.collected_pokemon_ids = collected_pokemon_ids


def _get_cards_per_round() -> int:
    cards_per_round = settings_obj.get("battle.cards_per_round")
    if isinstance(cards_per_round, int):
        return cards_per_round
    if isinstance(cards_per_round, str) and "-" in cards_per_round:
        try:
            min_val, max_val = map(int, cards_per_round.split("-"))
            return random.randint(min_val, max_val)
        except (ValueError, IndexError):
            return 2
    return 2


def on_review_card(*args):
    global _state
    s = _state

    try:
        multiplier = ankimon_tracker_obj.multiplier
        user_attack = random.choice(main_pokemon.attacks) if main_pokemon.attacks else "splash"
        enemy_attack = random.choice(enemy_pokemon.attacks) if enemy_pokemon.attacks else "splash"

        battle_sounds = settings_obj.get("audio.battle_sounds")

        ankimon_tracker_obj.cards_battle_round += 1
        ankimon_tracker_obj.cry_counter += 1
        cry_counter = ankimon_tracker_obj.cry_counter
        total_reviews = ankimon_tracker_obj.get_total_reviews()
        reviewer_obj.seconds = 0
        reviewer_obj.myseconds = 0
        ankimon_tracker_obj.general_card_count_for_battle += 1

        color = "#F0B27A"

        handle_review_count_achievement(total_reviews, achievements)

        s.item_receive_value -= 1
        if s.item_receive_value <= 0:
            s.item_receive_value = random.randint(3, 385)
            test_window.display_item()
            if not check_for_badge(achievements, 6):
                receive_badge(6, achievements)

        if total_reviews == settings_obj.get("battle.daily_average"):
            settings_obj.set("trainer.cash", settings_obj.get("trainer.cash") + 200)
            trainer_card.cash = settings_obj.get("trainer.cash")

        if battle_sounds == True and ankimon_tracker_obj.general_card_count_for_battle == 1:
            play_sound(enemy_pokemon.id, settings_obj)

        if ankimon_tracker_obj.cards_battle_round >= _get_cards_per_round():
            ankimon_tracker_obj.cards_battle_round = 0
            ankimon_tracker_obj.attack_counter = 0
            ankimon_tracker_obj.pokemon_encounter += 1
            multiplier = ankimon_tracker_obj.multiplier

            if (
                ankimon_tracker_obj.pokemon_encounter > 0
                and enemy_pokemon.hp > 0
                and multiplier < 1
            ):
                enemy_move = safe_get_random_move(enemy_pokemon.attacks, logger=logger)
                enemy_move_category = enemy_move.get("category")
                if enemy_move_category == "Status":
                    color = "#F7DC6F"
                elif enemy_move_category == "Special":
                    color = "#D2B4DE"
                else:
                    color = "#F0B27A"
            else:
                enemy_attack = "splash"

            move = safe_get_random_move(main_pokemon.attacks, logger=logger)
            category = move.get("category")

            if (
                ankimon_tracker_obj.pokemon_encounter > 0
                and main_pokemon.hp > 0
                and enemy_pokemon.hp > 0
            ):
                if settings_obj.get("controls.allow_to_choose_moves") == True:
                    dialog = MoveSelectionDialog(main_pokemon.attacks)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        if dialog.selected_move:
                            user_attack = dialog.selected_move

                if category == "Status":
                    color = "#F7DC6F"
                elif category == "Special":
                    color = "#D2B4DE"
                else:

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
class BattleState:
def init_battle_state(collected_pokemon_ids: set):
def _get_cards_per_round() -> int:
def on_review_card(*args):
        class Container:
```


## Ankimon/poke_engine/special_effects/items/modify_attack_being_used.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 80 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from ... import constants

from ...damage_calculator import is_super_effective


def choiceband(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def choicespecs(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.SPECIAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def lifeorb(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.3
        attacking_move[constants.HEAL] = [-1, 10]
        attacking_move[constants.HEAL_TARGET] = constants.SELF
    return attacking_move


def expertbelt(attacking_move, attacking_pokemon, defending_pokemon):
    if is_super_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def blackglasses(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'dark':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def magnet(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'electric':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def spelltag(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ghost':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def thickclub(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_pokemon.id in ['cubone', 'marowak', 'marowakalola'] and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def whiteherb(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.BOOSTS in attacking_move and attacking_move[constants.TARGET] in constants.MOVE_TARGET_SELF:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BOOSTS] = attacking_move[constants.BOOSTS].copy()
        for k in attacking_move[constants.BOOSTS].copy():
            if attacking_move[constants.BOOSTS][k] < 0:
                del attacking_move[constants.BOOSTS][k]
    return attacking_move


def wiseglasses(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.SPECIAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.1
    return attacking_move


def blackbelt(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'dark':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def charcoal(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'fire':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def dragonfang(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'dragon':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def hardstone(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'rock':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def metalcoat(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'steel':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def miracleseed(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'grass':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def mysticwater(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'water':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def nevermeltice(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ice':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def poisonbarb(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'poison':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def sharpbeak(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'flying':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move



... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def choiceband(attacking_move, attacking_pokemon, defending_pokemon):
def choicespecs(attacking_move, attacking_pokemon, defending_pokemon):
def lifeorb(attacking_move, attacking_pokemon, defending_pokemon):
def expertbelt(attacking_move, attacking_pokemon, defending_pokemon):
def blackglasses(attacking_move, attacking_pokemon, defending_pokemon):
def magnet(attacking_move, attacking_pokemon, defending_pokemon):
def spelltag(attacking_move, attacking_pokemon, defending_pokemon):
def thickclub(attacking_move, attacking_pokemon, defending_pokemon):
def whiteherb(attacking_move, attacking_pokemon, defending_pokemon):
def wiseglasses(attacking_move, attacking_pokemon, defending_pokemon):
def blackbelt(attacking_move, attacking_pokemon, defending_pokemon):
def charcoal(attacking_move, attacking_pokemon, defending_pokemon):
def dragonfang(attacking_move, attacking_pokemon, defending_pokemon):
def hardstone(attacking_move, attacking_pokemon, defending_pokemon):
def metalcoat(attacking_move, attacking_pokemon, defending_pokemon):
def miracleseed(attacking_move, attacking_pokemon, defending_pokemon):
def mysticwater(attacking_move, attacking_pokemon, defending_pokemon):
def nevermeltice(attacking_move, attacking_pokemon, defending_pokemon):
def poisonbarb(attacking_move, attacking_pokemon, defending_pokemon):
def sharpbeak(attacking_move, attacking_pokemon, defending_pokemon):
def silkscarf(attacking_move, attacking_pokemon, defending_pokemon):
def silverpowder(attacking_move, attacking_pokemon, defending_pokemon):
def softsand(attacking_move, attacking_pokemon, defending_pokemon):
def twistedspoon(attacking_move, attacking_pokemon, defending_pokemon):
def souldew(attacking_move, attacking_pokemon, defending_pokemon):
def adamantorb(attacking_move, attacking_pokemon, defending_pokemon):
def lustrousorb(attacking_move, attacking_pokemon, defending_pokemon):
def griseousorb(attacking_move, attacking_pokemon, defending_pokemon):
def lightball(attacking_move, attacking_pokemon, defending_pokemon):
def item_modify_attack_being_used(item_name, attacking_move, attacking_pokemon, defending_pokemon):
```


## Ankimon/poke_engine/special_effects/abilities/on_switch_in.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Excerpted
*   **Omissions**: Omitted 56 lines of deep implementation logic, preserving only structural definitions and the top of the file.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from ... import constants


def sandstream(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER and state.weather != constants.SAND:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.SAND,
            state.weather
        )]
    return None


def snowwarning(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER and state.weather != constants.ICE_WEATHER:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.ICE_WEATHER,
            state.weather
        )]
    return None


def drought(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER and state.weather != constants.SUN:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            state.weather
        )]
    return None


def drizzle(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER and state.weather != constants.RAIN:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.RAIN,
            state.weather
        )]
    return None


def desolateland(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_WEATHER_START,
        constants.DESOLATE_LAND,
        state.weather
    )]


def primordialsea(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_WEATHER_START,
        constants.HEAVY_RAIN,
        state.weather
    )]


def electricsurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field != constants.ELECTRIC_TERRAIN:
        return [(
            constants.MUTATOR_FIELD_START,
            constants.ELECTRIC_TERRAIN,
            state.field
        )]


def psychicsurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field != constants.PSYCHIC_TERRAIN:
        return [(
            constants.MUTATOR_FIELD_START,
            constants.PSYCHIC_TERRAIN,
            state.field
        )]


def grassysurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field != constants.GRASSY_TERRAIN:
        return [(
            constants.MUTATOR_FIELD_START,
            constants.GRASSY_TERRAIN,
            state.field
        )]


def mistysurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field != constants.MISTY_TERRAIN:
        return [(
            constants.MUTATOR_FIELD_START,
            constants.MISTY_TERRAIN,
            state.field
        )]


def intimidate(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if defending_pokemon.ability in ['fullmetalbody', 'clearbody', 'hypercutter', 'whitesmoke', 'innerfocus', 'oblivious', 'owntempo', 'scrappy']:
        return None
    if defending_pokemon.item in constants.IMMUNE_TO_STAT_LOWERING_ITEMS:
        return None

    # I shouldn't be doing this here but w/e sue me
    if defending_pokemon.ability == 'defiant' or defending_pokemon.ability == "guarddog":
        return [(
            constants.MUTATOR_BOOST,
            defending_side,
            constants.ATTACK,
            min(6-defending_pokemon.attack_boost, 1) #stop boosting when it reaches 6
        )]

    # same as above, shouldn't be done here
    if defending_pokemon.ability == 'rattled':
        return [(
            constants.MUTATOR_UNBOOST,
            defending_side,
            constants.ATTACK,
            1
        ), (
            constants.MUTATOR_BOOST,
            defending_side,
            constants.SPEED,
            min(6-defending_pokemon.speed_boost, 1) #stop boosting when it reaches 6
        )]

    if defending_pokemon.ability == 'competitive':
        return [(
            constants.MUTATOR_UNBOOST,
            defending_side,
            constants.ATTACK,
            1
        ), (
            constants.MUTATOR_BOOST,
            defending_side,
            constants.SPECIAL_ATTACK,
            min(6-defending_pokemon.special_attack_boost, 2) #stop boosting when it reaches 6
        )]

    if defending_pokemon.attack_boost == -6:
        return None

    return [(
        constants.MUTATOR_UNBOOST,
        defending_side,
        constants.ATTACK,
        min(1, 6+defending_pokemon.attack_boost)
    )]


def dauntlessshield(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(

... [EXCERPT TRUNCATED FOR LENGTH] ...

# Core structural definitions:
def sandstream(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def snowwarning(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def drought(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def drizzle(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def desolateland(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def primordialsea(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def electricsurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def psychicsurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def grassysurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def mistysurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def intimidate(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def dauntlessshield(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def intrepidsword(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def screencleaner(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
def ability_on_switch_in(ability_name, state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
```


## Ankimon/poke_engine/tests/test_items.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
import unittest
from unittest.mock import MagicMock
from poke_engine import constants
from poke_engine.special_effects.items.modify_attack_being_used import item_modify_attack_being_used
from poke_engine.special_effects.items.modify_attack_against import item_modify_attack_against


class TestChoiceBand(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.item_name = "choiceband"

    def test_choice_band_boosts_physical(self):

        move = {
            "accuracy": 100,
            "basePower": 40,
            "category": "physical",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "tackle",
            "priority": 0,
            "target": "normal",
            "type": "normal",
            "pp": 15
        }
        expected_move_power = 60
        pkmn = MagicMock()
        actual_power = item_modify_attack_being_used(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)

    def test_choice_band_does_not_boost_special(self):

        move = {
            "accuracy": 100,
            "basePower": 90,
            "category": "special",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "flamethrower",
            "priority": 0,
            "target": "normal",
            "type": "fire",
            "pp": 15
        }
        expected_move_power = 90
        pkmn = MagicMock()
        actual_power = item_modify_attack_being_used(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)


class TestChoiceSpecs(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.item_name = "choicespecs"

    def test_choice_scarf_does_not_boost_physical(self):

        move = {
            "accuracy": 100,
            "basePower": 40,
            "category": "physical",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "tackle",
            "priority": 0,
            "target": "normal",
            "type": "normal",
            "pp": 15
        }
        expected_move_power = 40
        pkmn = MagicMock()
        actual_power = item_modify_attack_being_used(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)

    def test_choice_scarf_boosts_special(self):

        move = {
            "accuracy": 100,
            "basePower": 90,
            "category": "special",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "flamethrower",
            "priority": 0,
            "target": "normal",
            "type": "fire",
            "pp": 15
        }
        expected_move_power = 135
        pkmn = MagicMock()
        actual_power = item_modify_attack_being_used(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)


class TestEviolite(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.item_name = "eviolite"

    def test_reduces_physical_move(self):

        move = {
            "accuracy": 100,
            "basePower": 40,
            "category": "physical",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "tackle",
            "priority": 0,
            "target": "normal",
            "type": "normal",
            "pp": 15
        }
        expected_move_power = 26.666666666666668
        pkmn = MagicMock()
        actual_power = item_modify_attack_against(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)

    def test_reduces_special_move(self):

        move = {
            "accuracy": 100,
            "basePower": 90,
            "category": "special",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "flamethrower",
            "priority": 0,
            "target": "normal",
            "type": "fire",
            "pp": 15
        }
        expected_move_power = 60.0
        pkmn = MagicMock()
        actual_power = item_modify_attack_against(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)

```


## Ankimon/poke_engine/data/team_datasets.py
*   **Why it was selected**: High structural centrality. It acts as a `domain logic` layer and is imported by 39 other files.
*   **Status**: Included in full
*   **Omissions**: None.
*   **Preface**: Future agents should pay attention to the global state it modifies and the specific function signatures it exposes to the rest of the application.

```python
from __future__ import annotations

from dataclasses import dataclass
import os
import json
import logging
import typing
from typing import Tuple
from typing import Optional

from .. import constants
from ..helpers import calculate_stats

if typing.TYPE_CHECKING:
    from ..battle import Pokemon

logger = logging.getLogger(__name__)

PWD = os.path.dirname(os.path.abspath(__file__))


@dataclass(frozen=True)
class PokemonMoveset:
    moves: Tuple[str, ...]

    def pkmn_can_have_moves(self, pkmn: Pokemon) -> bool:
        for mv in pkmn.moves:
            if mv.name not in self.moves:
                return False
        return True

    def __iter__(self):
        yield from self.moves


@dataclass(frozen=True)
class PokemonSet:
    tera_type: str
    ability: str
    item: str
    nature: str
    evs: Tuple[int, int, int, int, int, int]
    moves: PokemonMoveset

    def item_check(self, pkmn: Pokemon) -> bool:
        if self.item == "lifeorb" and not pkmn.can_have_life_orb:
            return False
        elif self.item == "heavydutyboots" and not pkmn.can_have_heavydutyboots:
            return False
        elif self.item == "assaultvest" and not pkmn.can_have_assaultvest:
            return False
        elif self.item in constants.CHOICE_ITEMS and not pkmn.can_have_choice_item:
            return False
        elif self.item == "choiceband" and pkmn.can_not_have_band:
            return False
        elif self.item == "choicespecs" and pkmn.can_not_have_specs:
            return False
        else:
            return self.item == pkmn.item or pkmn.item is None or pkmn.item == constants.UNKNOWN_ITEM

    def speed_check(self, pkmn: Pokemon):
        """
        The only non-observable speed modifier that should allow a
        Pokemon's speed_range to be set is choicescarf
        """
        stats = calculate_stats(pkmn.base_stats, pkmn.level, evs=self.evs, nature=self.nature)
        speed = stats[constants.SPEED]
        if self.item == "choicescarf":
            speed = int(speed * 1.5)

        return pkmn.speed_range.min <= speed <= pkmn.speed_range.max

    def pkmn_can_contain_set(self, pkmn: Pokemon, match_ability=True, match_item=True, speed_check=True) -> bool:
        ability_check = not match_ability or (
            self.ability == pkmn.ability or pkmn.ability is None
        )
        item_check = not match_item or self.item_check(pkmn)
        speed_check = not speed_check or self.speed_check(pkmn)

        return ability_check and item_check and speed_check and self.moves.pkmn_can_have_moves(pkmn)


class _TeamDatasets:
    def __init__(self):
        self.pokemon_sets = {}

    def set_pokemon_sets(self, pkmn_names):
        """
        To not have to hold the entire `team_datasets.json` in memory,
        this allows you to only populate team_datasets with only the
        sets of the pokemon you provide. Ideally this is called during
        team preview
        """
        self.pokemon_sets = {}
        self.append_to_team_datasets(pkmn_names)

    def append_to_team_datasets(self, pkmn_names):
        sets = os.path.join(PWD, 'team_datasets.json')
        with open(sets, 'r') as f:
            sets_dict = json.load(f)["pokemon"]

        for pkmn in pkmn_names:
            try:
                self.pokemon_sets[pkmn] = sets_dict[pkmn]
            except KeyError:
                logger.warning("No pokemon information being added for {}".format(pkmn))

    @staticmethod
    def get_exact_team(pkmn_names):
        sets = os.path.join(PWD, 'team_datasets.json')
        with open(sets, 'r') as f:
            teams_dict = json.load(f)["teams"]

        pkmn_lookup = "|".join(pkmn_names)
        try:
            return teams_dict[pkmn_lookup][0]
        except KeyError:
            return None

    @staticmethod
    def to_pokemon_set(pkmn_set_str: str) -> PokemonSet:
        tera_type, ability, item, nature, evs, *moves = pkmn_set_str.split("|")
        split_evs = evs.split(",")
        return PokemonSet(
            tera_type,
            ability,
            item,
            nature,
            (
                int(split_evs[0]),
                int(split_evs[1]),
                int(split_evs[2]),
                int(split_evs[3]),
                int(split_evs[4]),
                int(split_evs[5]),
            ),
            PokemonMoveset(tuple(moves))
        )

    def predict_set(self, pkmn: Pokemon, match_ability=True, match_item=True) -> Optional[PokemonSet]:
        """
        Finds the most likely PokemonSet that this Pokemon can have from self.team_datasets

        Returns None if a PokemonSet cannot be found
        """
        if not self.pokemon_sets:
            logger.warning("Called `predict_set` when team_datasets was empty")

        try:
            pkmn_data = self.pokemon_sets[pkmn.name]
        except KeyError:
            pkmn_data = {}

        for pkmn_set, _ in sorted(pkmn_data.items(), key=lambda x: x[1], reverse=True):
            pkmn_set = self.to_pokemon_set(pkmn_set)
            if pkmn_set.pkmn_can_contain_set(pkmn, match_ability=match_ability, match_item=match_item):
                return pkmn_set

        return None


TeamDatasets = _TeamDatasets()

```
