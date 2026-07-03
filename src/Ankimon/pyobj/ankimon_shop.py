import random
from datetime import datetime
import json

from ..services import services
from ..utils import daily_item_list
from ..resources import pokemon_tm_learnset_path

# Daily Rotating Items Pool
DAILY_ITEMS_POOL = daily_item_list()


class PokemonShopManager:
    """Daily Mart data provider.

    The retro ``QDialog`` storefront that used to live here (toggle_window /
    create_gui / _create_* / buy_item / reroll_daily_items + their theme helpers)
    was retired when the web shell took over the Mart UI: menu_buttons.py now
    routes the shop action to ``_open_shell_at("items", "in_shop")`` and
    ``ankimon_items_web/shop_obj.py`` reimplements buy/reroll against these data
    methods. Only the data surface the web shell reads remains — the daily
    item/TM pools plus the cash callbacks it uses.
    """

    def __init__(self, logger, settings_obj, set_callback, get_callback):
        self.logger = logger
        self.settings_obj = settings_obj
        self.set_callback = set_callback
        self.get_callback = get_callback
        self.number_of_daily_items = 3
        self.daily_items_reroll_cost = 100
        self.todays_daily_items = []
        self.todays_daily_tms = []
        self.tm_price = 1000

    def get_daily_items(self):
        """Generate daily items based on the current date."""
        db = services.db
        shop_data = db.get_user_data("todays_shop")
        if shop_data:
            if shop_data.get("items") and shop_data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                return shop_data.get("items")

        seed = datetime.now().strftime("%Y-%m-%d")
        random.seed(seed)
        return random.sample(DAILY_ITEMS_POOL, self.number_of_daily_items)

    def get_daily_tms(self):
        """Works like get_daily_items, but for TMs"""
        db = services.db
        shop_data = db.get_user_data("todays_shop")
        if shop_data:
            if shop_data.get("technical_machines") and shop_data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                return shop_data.get("technical_machines")

        tm_pool = self.get_tm_pool()
        seed = datetime.now().strftime("%Y-%m-%d")
        random.seed(seed)
        return random.sample(tm_pool, self.number_of_daily_items)

    def get_tm_pool(self) -> list[dict]:
        # Cached: pokemon_tm_learnset.json is immutable at runtime, and this
        # is on the hot path of the Items window's data fetch.
        cached = getattr(self, "_tm_pool_cache", None)
        if cached is not None:
            return cached

        with open(pokemon_tm_learnset_path, "r") as f:
            pokemon_tm_learnset = json.load(f)

        def flatten(xss):
            return [x for xs in xss for x in xs]

        all_tms = flatten(pokemon_tm_learnset.values())
        all_tms = set(all_tms)
        all_tms = list(
            {
                "name": tm,
                "description": f"Allows a Pokemon to be taught the move {tm} (if able).",
                "price": self.tm_price,
                "item_type": "TM",
            }
            for tm in all_tms
        )

        # Ensure deterministic order
        all_tms.sort(key=lambda tm: tm["name"])

        self._tm_pool_cache = all_tms
        return all_tms
