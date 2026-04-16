import json
import hashlib
import requests
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import QSize, Qt
from aqt.utils import showWarning, showInfo
from aqt import mw, utils
from ..resources import mainpokemon_path, mypokemon_path, moves_file_path, pokedex_path, rate_path
from ..functions.sprite_functions import get_sprite_path
from datetime import datetime
import uuid
from ..functions.pokedex_functions import get_base_experience, get_growth_rate
from .error_handler import show_warning_with_traceback

from ..pyobj.pokemon_trade_view import PokemonTradeView

# --- Module-level functions for Monthly Challenges ---

def create_monthly_challenge_pokemon(pokemon_data, make_shiny=False):
    """Creates a Pokémon dictionary from monthly challenge data."""
    base_stats = pokemon_data.get("stats", {})
    return {
        "name": pokemon_data["name"],
        "nickname": pokemon_data.get("nickname", ""),
        "id": pokemon_data["id"],
        "level": pokemon_data.get("level", 1),
        "ability": pokemon_data.get("ability", "No Ability"),
        "type": pokemon_data.get("type", ["Normal"]),
        "stats": base_stats,
        "ev": pokemon_data.get("ev", {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}),
        "iv": pokemon_data.get("iv", {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15}),
        "attacks": pokemon_data.get("attacks", ["Tackle"]),
        "growth_rate": pokemon_data.get("growth_rate", "medium"),
        "base_experience": pokemon_data.get("base_experience", 64),
        "gender": pokemon_data.get("gender", "N"),
        "shiny": pokemon_data.get("shiny", False) or make_shiny,
        "xp": pokemon_data.get("xp", 0),
        "current_hp": pokemon_data.get("current_hp", base_stats.get("hp")),
        "friendship": pokemon_data.get("friendship", 0),
        "pokemon_defeated": pokemon_data.get("pokemon_defeated", 0),
        "everstone": pokemon_data.get("everstone", False),
        "mega": pokemon_data.get("mega", False),
        "special_form": pokemon_data.get("special_form", None),
        "tier": pokemon_data.get("tier", "Normal"),
        "captured_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "individual_id": pokemon_data["individual_id"],
        "is_favorite": pokemon_data.get("is_favorite", False),
        "held_item": pokemon_data.get("held_item", None)
    }

def add_pokemon_to_collection(new_pokemon, refresh_callback=None, parent_window=None):
    """Adds a Pokémon to the user's collection file."""
    try:
        with open(mypokemon_path, "r", encoding="utf-8") as file:
            pokemon_list = json.load(file)
        pokemon_list.append(new_pokemon)
        with open(mypokemon_path, "w", encoding="utf-8") as file:
            json.dump(pokemon_list, file, indent=2)
        if refresh_callback:
            refresh_callback()
    except Exception as e:
        show_warning_with_traceback(parent=parent_window, exception=e, message="Error adding Pokemon to collection")

def check_and_award_monthly_pokemon(logger):
    """Checks for and automatically awards the current monthly challenge Pokémon."""
    try:
        should_check = False
        if rate_path.is_file():
            with open(rate_path, "r", encoding="utf-8") as f:
                if json.load(f).get("rate_this") is True:
                    should_check = True
        
        if not should_check:
            logger.log("info", "Monthly Pokemon check skipped: user has not rated the addon.")
            return

        logger.log("info", "Checking for monthly challenge Pokemon award.")
        now = datetime.now()
        month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        current_month_str = f"{month_names[now.month - 1]} {now.year}"
        monthly_data_url = "https://raw.githubusercontent.com/h0tp-ftw/ankimon/refs/heads/main/assets/challenges/monthly_challenges.json"
        
        try:
            response = requests.get(monthly_data_url, timeout=2)
            response.raise_for_status()
            monthly_challenges = response.json()
        except requests.exceptions.RequestException as e:
            logger.log("error", f"Could not fetch monthly challenges; likely no internet connection. Details: {e}")
            return  # Exit gracefully if fetching fails

        current_challenge = next((c for c in monthly_challenges if c.get("month") == current_month_str), None)

        if not current_challenge:
            logger.log("info", f"No monthly challenge found for {current_month_str}.")
            return

        challenge_pokemon_data = current_challenge.get("pokemon")
        if not challenge_pokemon_data:
            logger.log("warning", f"Monthly challenge for {current_month_str} is missing 'pokemon' data.")
            return

        challenge_individual_id = challenge_pokemon_data.get("individual_id")
        if not challenge_individual_id:
            logger.log("warning", f"Monthly challenge for {current_month_str} is missing 'individual_id' in 'pokemon' data.")
            return

        try:
            with open(mypokemon_path, "r", encoding="utf-8") as f:
                my_pokemon = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.log("error", f"Failed to load or parse mypokemon.json: {e}")
            return

        if any(p.get("individual_id") == challenge_individual_id for p in my_pokemon):
            logger.log("info", f"User already has the Pokémon for {current_month_str} (ID: {challenge_individual_id}).")
            return

        logger.log("info", f"Awarding Pokémon for {current_month_str}: {challenge_pokemon_data.get('name')}")
        make_shiny = False
        prev_id = current_challenge.get("previous_challenge_individual_id")
        threshold = current_challenge.get("defeat_threshold")

        if prev_id and threshold:
            logger.log("info", f"Checking for shiny eligibility: prev_id={prev_id}, threshold={threshold}")
            for p in my_pokemon:
                if p.get("individual_id") == prev_id and p.get("pokemon_defeated", 0) >= threshold:
                    logger.log("info", f"Shiny criteria met for {challenge_pokemon_data.get('name')}.")
                    make_shiny = True
                    break
        
        new_pokemon = create_monthly_challenge_pokemon(challenge_pokemon_data, make_shiny=make_shiny)
        add_pokemon_to_collection(new_pokemon)

        shiny_text = " (Shiny)" if new_pokemon["shiny"] else ""
        description = current_challenge.get("description", "")
        message = f"Congratulations! You've received your monthly challenge Pokémon: {new_pokemon['name']}{shiny_text}!"
        if description:
            message += f"\n\n{description}"
        message += "\n\nFor more information on monthly challenges and to redeem higher-tier prizes for your performance, please check the Ankimon Discord!"
        
        utils.showInfo(message)
        logger.log("info", f"Successfully awarded {new_pokemon['name']}{shiny_text}.")

    except Exception as e:
        logger.log("error", f"An unexpected error occurred in check_and_award_monthly_pokemon: {e}")
        # Still failing silently on the user's end, but with more detailed logs for debugging.
        pass

# class PokemonTradeController
class PokemonTrade:
    """
    Handles the Pokemon Trade between two users

    Disallows to trade the main Pokemon away
    Trade Code and Trade Password system
    Updates the myPokemon.json file with the aquired pokemon 
    
    Attributes:
        TRADE_VERSION (str): Version identifier for the trade file format.
        individual_id (str): 
        

    
    
    
    """

    # TODO: Explain when incremented
    TRADE_VERSION = "02"

    # TODO: Explain what this is
    _trade_view: 'PokemonTradeView'

    def __init__(self, pokemon, name, id, level, ability, iv, ev, gender, attacks, individual_id, shiny, logger, refresh_callback, parent_window=None):
        self.pokemon = pokemon
        self.name = name # No need
        self.id = id # No need
        self.level = level # No need
        self.ability = ability # No need
        self.iv = iv # No need
        self.ev = ev # No need
        self.gender = gender # No need
        self.attacks = attacks # No need
        self.individual_id = individual_id 
        self.shiny = shiny # No need
        self.refresh_callback = refresh_callback
        self.logger = logger
        self.parent_window = parent_window # No need?
        self.mainpokemon_path = mainpokemon_path # Wir haben doch den Modulimport dafür?!
        self.mypokemon_path = mypokemon_path # Wir haben doch den Modulimport dafür?!
        self.moves_file_path = moves_file_path # Wir haben doch den Modulimport dafür?!
        self.pokedex_path = pokedex_path # Wir haben doch den Modulimport dafür?!
        self.check_and_trade()

    ### Utility Functions ###

    def _load_mainpokemon_data(self) -> dict:
        """
        Load and return the main Pokémon entry from the file at mainpokemon_path.

        Returns:
            dict: The first Pokémon entry if the file is valid; empty dict if the file is not found.

        Raises:
            ValueError: If the file content is not a list containing at least one dictionary
        """
        try:
            with open(mainpokemon_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                if data and isinstance(data, list) and isinstance(data[0], dict):
                    return data[0]
                
                self.logger.log_and_showinfo(
                    "warning", "An error occured checking for the main Pokemon. Have you set it yet?"
                )

                raise ValueError("Invalid format: Expected List containing at least one entry of type Dictionary in mainpokemon.json file.")
        except FileNotFoundError as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message="Main Pokémon file not found!")
            return {}

    def _match_main_pokemon(self, main_pokemon: dict) -> bool:
        """
        Check whether this Pokémon's individual ID matches the main Pokémon's.

        Args:
            main_pokemon (dict): The main Pokémon entry to compare against.

        Returns:
            bool: True if both individual IDs match, False otherwise.
        """
        print("Individual ID of Traded Pokemon and Main Pokemon is identical?: ", self.pokemon["individual_id"] == main_pokemon["individual_id"])
        return self.pokemon.get("individual_id") == main_pokemon.get("individual_id") 
        
    """
    Hier könnte noch ein Fehler existieren. Wenn ich in der PC Collection mein main Pokemon auswähle und dann in die description gehe und bspw. 
    Attacken ändere oder ein Item vergebe, wird das nach dem Pokemon Traade verloren gehen (da das main Pokemon nicht nochmal geupdated wurde).
    Das sollte aber nicht im Pokemon Trade passieren, sondern im PokemonPC
    """

    ### Check if Trading is possible ###

    def check_and_trade(self):
        """
        Check if Trading is possible.

        """
        pokemon_data = self._load_mainpokemon_data()
        #print("Self Pokemon:", self.pokemon)
        #print("Loaded Pokemon Data:", pokemon_data)
        #print(self._match_main_pokemon(pokemon_data))
        
        if self._match_main_pokemon(pokemon_data):
            self.logger.log_and_showinfo("warning", "You can't trade your Main Pokémon!\nPlease pick a different Main Pokémon.")
            return
        
        PokemonTradeView(
            self,
            self.parent_window
        ).open_trade_code_window()

    def generate_password(pokemon: dict) -> str:
        pass

    def generate_and_show_passwords(self, window):
        code1 = self.trade_code_display.text().strip()
        code2 = self.trade_code_input.text().strip()
        if not code1 or not code2 or len(code2) < 16:
            showWarning("Please enter a valid trade code from the other user.")
            return

        parts = code2.split(',')
        if len(parts) > 0 and parts[0].isdigit():
            incoming_id = int(parts[0])
            if incoming_id == self.id:
                showWarning("You cannot trade with a Pokémon of the same species (ID) as the one you're trading away!")
                return

        self.your_code_label.hide()
        self.trade_code_display.hide()
        self.copy_button.hide()
        self.their_code_label.hide()
        self.trade_code_input.hide()
        self.trade_button.hide()

        codes = sorted([code1, code2])
        combo = codes[0] + "|" + codes[1]
        hash_digest = hashlib.sha256(combo.encode()).hexdigest()
        part1 = hash_digest[:len(hash_digest) // 2]
        part2 = hash_digest[len(hash_digest) // 2:]

        if code1 < code2:
            my_part = part1
            self._their_password_part = part2
        else:
            my_part = part2
            self._their_password_part = part1

        my_part += self.TRADE_VERSION
        self._their_password_part += self.TRADE_VERSION

        self.password_interface = QFrame()
        self.password_layout = QVBoxLayout(self.password_interface)
        self.password_layout.setSpacing(5)

        your_password_label = QLabel("Your Password (To Send to Trade Partner):")
        your_password_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.password_layout.addWidget(your_password_label)

        your_password_display_layout = QHBoxLayout()
        your_password_display = QLineEdit(my_part)
        your_password_display.setReadOnly(True)
        your_password_display.setFont(QFont("Courier New", 10))
        your_password_display_layout.addWidget(your_password_display)

        copy_password_button = QPushButton("Copy")
        copy_password_button.setToolTip("Copy your password part to the clipboard")
        copy_password_button.clicked.connect(lambda: self.copy_to_clipboard(my_part))
        your_password_display_layout.addWidget(copy_password_button)
        self.password_layout.addLayout(your_password_display_layout)

        their_password_label = QLabel("Enter Trade Partner's Password:")
        their_password_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.password_layout.addWidget(their_password_label)

        self.other_password_input = QLineEdit()
        self.other_password_input.setPlaceholderText("Enter the other person's password part")
        self.password_layout.addWidget(self.other_password_input)

        self.password_button = QPushButton("Perform Trade")
        self.password_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.password_button.setStyleSheet("padding: 10px;")
        self.password_button.clicked.connect(lambda: self.handle_trade_with_password(window))
        self.password_layout.addWidget(self.password_button)

        window.layout().addWidget(self.password_interface)

    def handle_trade_with_password(self, parent_window):
        their_part_entered = self.other_password_input.text().strip()
        if not their_part_entered:
            showWarning("Please enter the password part from the other user.")
            return

        if len(their_part_entered) < 34:
            showWarning("Incorrect password format.")
            return

        their_version = their_part_entered[-2:]
        if their_version != self.TRADE_VERSION:
            showWarning(f"Trade incompatible due to Ankimon trade versions. \n\nYour version: {self.TRADE_VERSION}, partner's version: {their_version}.\n\nPlease get the latest version of Ankimon for both users!")
            return

        if their_part_entered == self._their_password_part:
            code = self.trade_code_input.text().strip()
            parts = code.split(',')
            if len(parts) > 0 and parts[0].isdigit():
                incoming_id = int(parts[0])
                if incoming_id == self.id:
                    showWarning("You cannot trade with a Pokémon of the same species (ID) as the one you're trading away!")
                    return
            self.confirm_trade(parent_window)
        else:
            showWarning("Incorrect password part. Please check with the other user.")

    def copy_to_clipboard(self, text):
        clipboard = mw.app.clipboard()
        clipboard.setText(text)
        showInfo("Trade code copied to clipboard!")

    def get_pokemon_display_info(self, code):
        """
        Updates the pokemon 
        If the code is less than 4 digits long, return early since sprite path can't be determined by only three parts
        If the code contains any Non-Integer, return image of substitute plush
        """
        parts = code.split(',')
        if len(parts) < 4:
            return "", ""

        if not all([isinstance(part.isdigit(), int) for part in parts]):
            return (
                ":/icons/pokeball.png",
                "Their Pokemon"
            )

        sprite: str = self._get_sprite_from_code(parts)
        name: str = self._get_pokemon_name_by_id(parts[0])

        return sprite, name

    def _get_sprite_from_code(self, parts) -> str:
        """
        Returns the sprite path based on the given code, e.g.: [312, 32, 1, 0, ...] based on the first 4 digits
        """
        # TODO: Make the sprite lookup work, even when less then 4 digits have been entered (by using defaults) – This requires not instant lookup

        pokemon_id = parts[0]
        gender = self._get_gender_from_id(parts[2]) # TODO: Is there a function that does this already?
        shiny = parts[3]
        sprite_path = get_sprite_path(side="front", sprite_type="gif", id=pokemon_id, shiny=shiny, gender=gender)

        return sprite_path

    def _get_pokemon_name_by_id(self, pokemon_id):
        try:
            with open(self.pokedex_path, 'r', encoding='utf-8') as file:
                pokedex = json.load(file)
                for details in pokedex.values():
                    if details.get('num') == pokemon_id:
                        return details.get('name', str(pokemon_id))
        except Exception as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message=f"An error occurred while getting the Pokémon name for ID {pokemon_id}.")
        return str(pokemon_id)
    
    def get_my_pokemon_code(self):
        """
        Returns the code of my pokemon as a string concatenated by a comma as delimiter,
        e.g.:   100,5,0,0, (...)
        """
        id = self.pokemon.get('id')
        level = self.pokemon.get('level')
        gender = self._get_gender_from_char()
        shiny = self._get_shiny_from_bool()
        ev = self._get_ev_string()
        iv = self._get_iv_string()
        attacks = self._get_attacks_string()

        return f"{id},{level},{gender},{shiny},{ev},{iv},{attacks}"

    def confirm_trade(self, parent_window):
        from PyQt6.QtWidgets import QMessageBox
        code = self.trade_code_input.text()
        name = "the other Pokémon"
        parts = code.split(',')
        if len(parts) > 0 and parts[0].isdigit():
            pokemon_id = int(parts[0])
            name = self.get_pokemon_name_by_id(pokemon_id)
        msg = QMessageBox(parent_window)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirm Trade")
        msg.setText(f"Are you sure you want to trade your {self.name} for {name}?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        result = msg.exec()
        if result == QMessageBox.StandardButton.Yes:
            self.trade_pokemon_in(code)

    def trade_pokemon_in(self, number_code):
        code = number_code.strip()
        try:
            numbers = [int(num) for num in code.split(',')]
            if len(numbers) < 16:
                showWarning("Code is incomplete.")
                return
            incoming_id = numbers[0]
            if incoming_id == self.id:
                showWarning("You cannot trade with a Pokémon of the same species (ID) as the one you're trading away!")
                return
            self.process_trade(numbers)
        except ValueError:
            showWarning("Please enter a valid Pokémon Code!")

    def process_trade(self, numbers):
        from ..functions.pokedex_functions import search_pokedex, get_all_pokemon_moves
        import random
        try:
            pokemon_id, level, gender_id, shiny = numbers[0], numbers[1], numbers[2], numbers[3]
            ev_stats = dict(zip(['hp', 'atk', 'def', 'spa', 'spd', 'spe'], numbers[4:10]))
            iv_stats = dict(zip(['hp', 'atk', 'def', 'spa', 'spd', 'spe'], numbers[10:16]))
            attacks = [self.find_move_by_num(attack_id)['name'] for attack_id in numbers[16:]]

            details = self.find_pokemon_by_id(pokemon_id)
            if not details:
                raise ValueError(f"Could not find Pokémon details for ID {pokemon_id}")

            base_experience = get_base_experience(pokemon_id)

            ability = "No Ability"
            possible_abilities = search_pokedex(details["name"], "abilities")
            if possible_abilities:
                numeric_abilities = {k: v for k, v in possible_abilities.items() if k.isdigit()}
                if numeric_abilities:
                    ability = random.choice(list(numeric_abilities.values()))

            if not attacks or any(a == "Unknown Move" for a in attacks):
                all_possible_moves = get_all_pokemon_moves(details["name"], level)
                if len(all_possible_moves) <= 4:
                    attacks = all_possible_moves
                else:
                    attacks = random.sample(all_possible_moves, 4)

            new_pokemon = {
                "name": details["name"],
                "nickname": "",
                "ability": ability,
                "id": pokemon_id,
                "gender": self.gender_from_id(gender_id),
                "level": level,
                "type": details["types"],
                "stats": details["baseStats"],
                "ev": ev_stats,
                "iv": iv_stats,
                "attacks": attacks,
                "growth_rate": get_growth_rate(pokemon_id),
                "current_hp": self.calculate_max_hp(details["baseStats"]["hp"], level, ev_stats, iv_stats),
                "base_experience": base_experience,
                "friendship": 0,
                "pokemon_defeated": 0,
                "everstone": False,
                "shiny": bool(shiny),
                "mega": False,
                "special_form": None,
                "captured_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "individual_id": str(uuid.uuid4())
            }
            new_pokemon["xp"] = 0
            self.replace_pokemon(new_pokemon)
        except Exception as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message="An error occurred while processing the trade.")

    def calculate_max_hp(self, base_hp, level, ev, iv):
        ev_value = ev["hp"] / 4
        iv_value = iv["hp"]
        return int((((2 * base_hp + iv_value + ev_value) * level) / 100) + level + 10)

    def find_move_by_num(self, move_num):
        with open(self.moves_file_path, 'r', encoding='utf-8') as file:
            moves_data = json.load(file)
            return next((move for move in moves_data.values() if move.get('num') == move_num), {"name": "Unknown Move"})

    def find_move_by_name(self, move_name):
        with open(self.moves_file_path, 'r', encoding='utf-8') as file:
            moves_data = json.load(file)
            move = next((move for move in moves_data.values() if move.get('name').lower() == move_name.lower()), None)
            if move:
                return move['num']
            else:
                return 33

    def find_pokemon_by_id(self, pokemon_id):
        try:
            with open(self.pokedex_path, 'r', encoding='utf-8') as file:
                pokedex = json.load(file)
                for details in pokedex.values():
                    if details.get('num') == pokemon_id:
                        return details
            self.logger.log_and_showinfo("warning",f"No Pokémon found with ID: {pokemon_id}")
            return None
        except FileNotFoundError as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message=f"Pokedex file not found.")
            return None

    def replace_pokemon(self, new_pokemon):
        try:
            with open(self.mypokemon_path, 'r+') as file:
                pokemon_list = json.load(file)

                for idx, pokemon in enumerate(pokemon_list):
                    if pokemon.get("individual_id") == self.individual_id:
                        pokemon_list[idx] = new_pokemon
                        break
                else:
                    self.logger.log_and_showinfo("warning","Could not find the Pokémon with the specified Individual ID.")
                    return

                file.seek(0)
                file.truncate()
                json.dump(pokemon_list, file, indent=2)

            self.logger.log_and_showinfo("warning",f"Successfully traded for {new_pokemon['name']}!")
            self.refresh_callback()

        except (FileNotFoundError, json.JSONDecodeError) as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message="Error updating Pokémon data.")
    
    def get_pokemon(self):
        return self.pokemon
    
    def _get_gender_from_char(self):
        gender_map = {"M": 0, "F": 1, "N": 2}
        return gender_map.get(self.pokemon['gender'], 3)

    def _get_gender_from_id(self, gender_id):
        return {0: "M", 1: "F", 2: "N"}.get(gender_id, "N/A")
    
    def _get_shiny_from_bool(self):
        return 1 if self.pokemon['shiny'] else 0
    
    def _get_ev_string(self):
        return ','.join(str(value) for value in self.pokemon['ev'].values())

    def _get_iv_string(self):
        return ','.join(str(value) for value in self.pokemon['iv'].values())
    
    def _get_attacks_string(self):
        return ','.join([str(self.find_move_by_name(attack)) for attack in self.pokemon['attacks']])

    def _find_move_by_name(self, move_name):
        with open(self.moves_file_path, 'r', encoding='utf-8') as file:
            moves_data = json.load(file)
            move = next((move for move in moves_data.values() if move.get('name').lower() == move_name.lower()), None)
            if move:
                return move['num']
            else:
                return 33