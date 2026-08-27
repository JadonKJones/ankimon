"""Localized Pokémon type names.

Types are a fixed set of 18, so the translations live inline rather than in a
generated data file. Anything not covered (or an unsupported language) falls
back to the capitalized English name.
"""
from .move_names import _current_lang_code

_TYPE_NAMES = {
    "jp": {
        "normal": "ノーマル", "fire": "ほのお", "water": "みず", "electric": "でんき",
        "grass": "くさ", "ice": "こおり", "fighting": "かくとう", "poison": "どく",
        "ground": "じめん", "flying": "ひこう", "psychic": "エスパー", "bug": "むし",
        "rock": "いわ", "ghost": "ゴースト", "dragon": "ドラゴン", "dark": "あく",
        "steel": "はがね", "fairy": "フェアリー",
    },
    "sp": {
        "normal": "Normal", "fire": "Fuego", "water": "Agua", "electric": "Eléctrico",
        "grass": "Planta", "ice": "Hielo", "fighting": "Lucha", "poison": "Veneno",
        "ground": "Tierra", "flying": "Volador", "psychic": "Psíquico", "bug": "Bicho",
        "rock": "Roca", "ghost": "Fantasma", "dragon": "Dragón", "dark": "Siniestro",
        "steel": "Acero", "fairy": "Hada",
    },
}
_TYPE_NAMES["es_latam"] = _TYPE_NAMES["sp"]


def format_type_name(type_name: str) -> str:
    if not type_name:
        return type_name
    table = _TYPE_NAMES.get(_current_lang_code())
    key = str(type_name).strip().lower()
    if table and key in table:
        return table[key]
    return str(type_name).capitalize()


def format_type_list(types, separator: str = "/") -> str:
    """Join a list of type names, each localized."""
    if not types:
        return format_type_name("normal")
    return separator.join(format_type_name(t) for t in types)
