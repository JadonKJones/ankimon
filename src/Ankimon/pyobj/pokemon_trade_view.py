import json
import string
from typing import TYPE_CHECKING, List

from PyQt6.QtWidgets import QDialog, QSizePolicy, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor, QMovie, QImage
from PyQt6.QtCore import QSize, Qt

from aqt import mw
from aqt import QBoxLayout

from ..functions.sprite_functions import get_sprite_path

# Prevent cyclic imports when using PokemonTradeController import for type hints
if TYPE_CHECKING: 
    from ..pyobj.pokemon_trade import PokemonTrade

class PokemonTradeView():
    """
    Part of the Model-View-Controller (MVC) architecture handling Pokemon Trading.
    It uses a PokemonTradeController instance to retrieve data about the pokemon.
    A successful trade consists of a trade code and password exchange.

    This class only handles user input and display logic and delegates core trading logic to the respective trade controller.
    Any issues during trade will be presented to the user by this view class
    """

    
    # The pokemon sprite size to display during trade code enter
    # TODO: Check if we need the sprite size – For rescaling the screen, this kind of looks bad
    PKMN_SPRITE_SIZE = QSize(64, 64)

    def __init__(self, controller: 'PokemonTrade', parent_window=None):
        self.controller = controller
        self.parent_window = parent_window

        # A dict containing all QLabels pokemon sprites that this view object displays with the keys being the variable name
        self.sprite_collection = {}

        # A dict containing all QLabels pokemon names that this view object displays with the keys being the variable name
        self.name_collection = {}

    def open_trade_code_window(self):
        """
        Opens the UI window for trading pokemon with a given trade code

        The layout consists of three parts:
            - The window layout containing window settings
            - The pokemon layout containing info about the pokemon that are up to trade
            - The code layout containing User Input for the other person's pokemon trade code     
        """

        # Window Details
        parent = self.parent_window if self.parent_window is not None else mw
        window = QDialog(parent)
        window.setWindowTitle(f"Trade Pokémon: {string.capwords(self.controller.get_pokemon().get('name'))}")
        window.setWindowModality(Qt.WindowModality.ApplicationModal)
        window.setMinimumSize(550, 400)
        #window.setMinimumSize(200, 200)

        main_layout = QVBoxLayout(window)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Trade Caption
        title_label = QLabel(f"Trading Away: {string.capwords(self.controller.get_pokemon().get('name'))}")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Trade Window Contents
        sprite_layout = self._setup_trade_pokemon_layout()
        main_layout.addLayout(sprite_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        code_layout = self._setup_trade_code_layout(window)
        main_layout.addLayout(code_layout)

        window.exec()

    def open_trade_password_window():
        """
        Opens the UI window for trading pokemon with a given trade password
        """

    def _setup_trade_pokemon_layout(self) -> QBoxLayout:
        """
        Returns the layout for the pokemon section.
        
        Returns:
            QBoxLayout: The layout of the pokemon section
        """
        
        sprites_layout = QHBoxLayout()
        sprites_layout.setSpacing(20)

        # Pokemon To Trade
        
        my_pokemon_sprite_layout = QVBoxLayout()
        my_pokemon_sprite_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        my_pokemon_sprite_label = QLabel()
        my_pokemon_sprite_label.setMaximumSize(self.PKMN_SPRITE_SIZE)
        my_pokemon_sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_collection.update({'my_pokemon_sprite_label' : my_pokemon_sprite_label})
        
        my_pokemon_name_label = QLabel(f"{string.capwords(self.controller.get_pokemon().get('name'))}")
        my_pokemon_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        my_pokemon_name_label.setFont(QFont("Arial", 14))
        self.name_collection.update({'my_pokemon_name_label' : my_pokemon_name_label})

        self.update_pokemon_display_info(self.controller.get_my_pokemon_code(), my_pokemon_sprite_label, my_pokemon_name_label)

        my_pokemon_sprite_layout.addWidget(my_pokemon_sprite_label)
        my_pokemon_sprite_layout.addWidget(my_pokemon_name_label)
        sprites_layout.addLayout(my_pokemon_sprite_layout)

        # Arrow Indicator
        trade_arrow_label = QLabel("⟶")
        trade_arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trade_arrow_label.setFont(QFont("", 40))
        sprites_layout.addWidget(trade_arrow_label)

        # Pokemon To Receive
        their_pokemon_layout = QVBoxLayout()
        their_pokemon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        their_pokemon_sprite_label = QLabel()
        their_pokemon_sprite_label.setMaximumSize(self.PKMN_SPRITE_SIZE)
        their_pokemon_sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_collection.update({'their_pokemon_sprite_label' : their_pokemon_sprite_label})

        their_pokemon_name_label = QLabel()
        their_pokemon_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        their_pokemon_name_label.setFont(QFont("Arial", 14))
        self.name_collection.update({'their_pokemon_name_label' : their_pokemon_name_label})

        self.update_pokemon_display_info("", their_pokemon_sprite_label, their_pokemon_name_label) # Initialize with defaults
        
        their_pokemon_layout.addWidget(their_pokemon_sprite_label)
        their_pokemon_layout.addWidget(their_pokemon_name_label)
        sprites_layout.addLayout(their_pokemon_layout)
        
        ########## DEBUG ##########
        my_pokemon_sprite_label.setStyleSheet("""background-color: #ffcbd1;""")
        my_pokemon_name_label.setStyleSheet("""background-color: #aed9e9;""")

        trade_arrow_label.setStyleSheet("""background-color: #ffcbd1;""")

        their_pokemon_sprite_label.setStyleSheet("""background-color: #ffcbd1;""")
        their_pokemon_name_label.setStyleSheet("""background-color: #aed9e9;""")

        return sprites_layout

    def _setup_trade_code_layout(self, window) -> QBoxLayout:
        # TODO: Button Only pressable after the input is deemed valid 
        # TODO: Remove window parameter

        """
        Returns the layout for the code section.

        Args:
            window: TEMPORARY - Contains reference to this window instance
        
        Returns:
            QBoxLayout: The layout of the pokemon section
        """

        trade_code_layout = QVBoxLayout() # Contains QObjects layouts from both trade sides
        trade_code_layout.setSpacing(15)

        # MyCode
        my_trade_code_layout = QVBoxLayout() # Contains QObjects regarding my trade code
        my_trade_code_layout.setSpacing(5)

        my_code_label = QLabel("Your Trade Code:")
        my_code_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        my_code_display_layout = QHBoxLayout() # Contains TextField (Code) and Button (Copy)

        my_code_text = QLineEdit(self.controller.get_my_pokemon_code())
        my_code_text.setFont(QFont("Courier New", 10))
        my_code_text.setReadOnly(True)

        my_code_copy_button = QPushButton("Copy")
        my_code_copy_button.setToolTip("Copy the trade code to your clipboard")
        my_code_copy_button.clicked.connect(lambda: self.controller.copy_to_clipboard(my_code_text.text()))

        my_code_display_layout.addWidget(my_code_text)
        my_code_display_layout.addWidget(my_code_copy_button)
        
        my_trade_code_layout.addWidget(my_code_label)
        my_trade_code_layout.addLayout(my_code_display_layout)


        # TheirCode
        their_trade_code_layout = QVBoxLayout() # Contains QObjects regarding their trade code
        their_trade_code_layout.setSpacing(5)

        their_code_label = QLabel("Enter Their Trade Code:")
        their_code_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        their_code_text = QLineEdit()
        their_code_text.setFont(QFont("Courier New", 10))
        their_code_text.setPlaceholderText("Paste trade code here")
        their_code_text.textChanged.connect(lambda text: self.update_pokemon_display_info(text, self.sprite_collection.get('their_pokemon_sprite_label'), self.name_collection.get('their_pokemon_name_label')))
        # TODO: Have a look at the editingFinished() signal that QLineEdit throws – might be better in this case?

        their_trade_code_layout.addWidget(their_code_label)
        their_trade_code_layout.addWidget(their_code_text)

        button_trade_with_password = QPushButton("Generate Trade Password")
        button_trade_with_password.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        button_trade_with_password.setStyleSheet("padding: 10px;")
        button_trade_with_password.clicked.connect(lambda: self.controller.generate_and_show_passwords(window))

        trade_code_layout.addLayout(my_trade_code_layout)
        trade_code_layout.addLayout(their_trade_code_layout)
        trade_code_layout.addWidget(button_trade_with_password)

        return trade_code_layout

    def update_pokemon_display_info(self, code: str, sprite_label: QPixmap, name_label: QLabel):
        pkmn_sprite, pkmn_name = self.controller.get_pokemon_display_info(code)

        self._update_pokemon_sprite_label(pkmn_sprite, sprite_label)
        self._update_pokemon_name_label(pkmn_name, name_label)
        

    def _update_pokemon_sprite_label(self, pkmn_sprite: str, sprite_label: QLabel):
        """
        Update the pokemon sprite based on the given QLabel by wrapping it in using a QMovie instance
        The pokemon to update is determined by the given label.
        
        Args:
            pkmn_sprite (str): The sprite path of the pokemon 
            label (QLabel): The label to place the sprite in
        """
        
        pkmn_movie = QMovie(pkmn_sprite)

        sprite_label.setMovie(pkmn_movie)
        
        pkmn_movie.start()
    
    def _update_pokemon_name_label(self, pkmn_name: str, name_label: QLabel):
        """
        Update the pokemon name label determined based on the given string.
        The label to update is determined by the given name_label

        Args:
            pkmn_name (str): The name of the pokemon
            name_label (QLabel): The label to place the name in
        """
        name_label.setText(pkmn_name)

    def update_other_pokemon_sprite(self, code):
        from PyQt6.QtGui import QMovie
        try:
            parts = code.split(',')
            self.other_pokemon_sprite_label.clear()
            self.other_pokemon_sprite_label.setPixmap(QPixmap())
            self.other_pokemon_name_label.setText("")
            if len(parts) > 0 and parts[0].isdigit():
                pokemon_id = int(parts[0])
                other_gender = "M"
                other_shiny = False
                if len(parts) > 2:
                    gender_map = {"0": "M", "1": "F", "2": "N"}
                    other_gender = gender_map.get(parts[2], "M")
                
                sprite_path = get_sprite_path(side="front", sprite_type="gif", id=pokemon_id, shiny=other_shiny, gender=other_gender)
                
                if hasattr(self, '_other_pokemon_movie') and self._other_pokemon_movie is not None:
                    self._other_pokemon_movie.stop()
                    self._other_pokemon_movie.deleteLater()
                    self._other_pokemon_movie = None
                other_pokemon_movie = QMovie(sprite_path)
                self._other_pokemon_movie = other_pokemon_movie
                
                def set_other_frame():
                    frame = other_pokemon_movie.currentImage()
                    if not frame.isNull():
                        scaled = QPixmap.fromImage(frame).scaled(self.PKMN_SPRITE_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self.other_pokemon_sprite_label.setPixmap(scaled)
                other_pokemon_movie.frameChanged.connect(lambda _: set_other_frame())
                self.other_pokemon_sprite_label.setMovie(other_pokemon_movie)
                other_pokemon_movie.start()
                set_other_frame()
                name = self.get_pokemon_name_by_id(pokemon_id)
                self.other_pokemon_name_label.setText(name if name else "Unknown Pokémon")
            else:
                self.other_pokemon_sprite_label.setPixmap(QPixmap(":/icons/pokeball.png").scaled(QSize(64, 64), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                self.other_pokemon_name_label.setText("")
        except Exception:
            self.other_pokemon_sprite_label.setPixmap(QPixmap(":/icons/pokeball.png").scaled(QSize(64, 64), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.other_pokemon_name_label.setText("")

    def get_pokemon_name_by_id(self, pokemon_id):
        try:
            with open(self.pokedex_path, 'r', encoding='utf-8') as file:
                pokedex = json.load(file)
                for details in pokedex.values():
                    if details.get('num') == pokemon_id:
                        return details.get('name', str(pokemon_id))
        except Exception as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message=f"An error occurred while getting the Pokémon name for ID {pokemon_id}.")
        return str(pokemon_id)