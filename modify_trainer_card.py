with open("src/Ankimon/pyobj/trainer_card.py", "r") as f:
    content = f.read()

import re

new_content = content.replace("        self.league = league\n        cash = int(settings_obj.get(\"trainer.cash\"))\n        self.cash = cash\n\n        # Sync Data to ankimon leaderboard\n        data = {\n            \"trainerRank\": f\"{league}\",  # Example rank\n            \"trainerName\": trainer_name,  # Example trainer name\n            \"level\": max(1, int(settings_obj.get(\"trainer.level\"))),\n            \"pokedex\": services.db.execute(\"SELECT COUNT(DISTINCT pokedex_id) FROM captured_pokemon WHERE pokedex_id IS NOT NULL\").fetchone()[0],\n            \"caughtPokemon\": services.db.get_pokemon_count(),\n            \"trainerLevel\": self.level,  # Add a logic for trainer's level if applicable\n            \"highestLevel\": highest_pokemon_level,  # Example highest level\n            \"shinies\": f\"{services.db.get_shiny_count()}\",  # Example shinies\n            \"cash\": cash,  # Example cash,\n            \"trainerSprite\": f\"{settings_obj.get('trainer.sprite') + '.png'}\",\n        }\n        try:\n            # Lazy import: ankimon_leaderboard pulls in Qt/Anki, so importing it\n            # at module top would break the headless core. Imported here instead,\n            # and an ImportError simply means \"no leaderboard available\" (harness).\n            from .ankimon_leaderboard import sync_data_to_leaderboard\n            sync_data_to_leaderboard(data)\n        except ImportError:\n            pass\n        except Exception as e:\n            self.logger.log_and_showinfo(\n                \"error\", f\"Error in syncing data to leaderboard {e}\"\n            )", "        self.league = league\n        cash = int(settings_obj.get(\"trainer.cash\"))\n        self.cash = cash\n        self.sync_leaderboard()")

new_content = re.sub(
    r"    def display_card_data\(self\):",
    r"""    def sync_leaderboard(self):
        \"\"\"Sync TrainerCard data to the Ankimon leaderboard.\"\"\"
        try:
            data = {
                "trainerRank": f"{self.league}",
                "trainerName": self.trainer_name,
                "level": max(1, self.level),
                "pokedex": services.db.execute("SELECT COUNT(DISTINCT pokedex_id) FROM captured_pokemon WHERE pokedex_id IS NOT NULL").fetchone()[0],
                "caughtPokemon": services.db.get_pokemon_count(),
                "trainerLevel": self.level,
                "highestLevel": int(self.highest_pokemon_level()),
                "shinies": f"{services.db.get_shiny_count()}",
                "cash": self.cash,
                "trainerSprite": f"{self.settings_obj.get('trainer.sprite') + '.png'}",
            }
            from .ankimon_leaderboard import sync_data_to_leaderboard
            sync_data_to_leaderboard(data)
        except ImportError:
            pass
        except Exception as e:
            self.logger.log_and_showinfo(
                "error", f"Error in syncing data to leaderboard {e}"
            )

    def display_card_data(self):""",
    new_content
)


with open("src/Ankimon/pyobj/trainer_card.py", "w") as f:
    f.write(new_content)
