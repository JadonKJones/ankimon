<<<<<<< SEARCH
        if row:
            # Update existing - preserve is_main
            cursor.execute(
                "UPDATE captured_pokemon SET data = ? WHERE individual_id = ?",
                (obfuscated_data, individual_id)
            )
        else:
            # Insert new with is_main = 0
            cursor.execute(
                "INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 0, ?)",
                (individual_id, obfuscated_data)
            )
        conn.commit()
        self._clear_reviewer_ownership_cache()
        return True
=======
        if row:
            # Update existing - preserve is_main
            cursor.execute(
                "UPDATE captured_pokemon SET data = ? WHERE individual_id = ?",
                (obfuscated_data, individual_id)
            )
        else:
            # Insert new with is_main = 0
            cursor.execute(
                "INSERT INTO captured_pokemon (individual_id, is_main, data) VALUES (?, 0, ?)",
                (individual_id, obfuscated_data)
            )

        # Hook: auto-register caught pokemon
        pokemon_id = pokemon_data.get("id")
        if pokemon_id:
            try:
                self.mark_as_caught(int(pokemon_id))
            except Exception as e:
                self._log("warning", f"Failed to mark pokemon {pokemon_id} as caught: {e}")

        conn.commit()
        self._clear_reviewer_ownership_cache()
        return True
>>>>>>> REPLACE
