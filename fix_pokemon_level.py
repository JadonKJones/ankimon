with open("src/Ankimon/functions/encounter_functions.py", "r") as f:
    content = f.read()

search_block = """        if not _in_bulk_resolve():
            if settings_obj.get("gui.pop_up_dialog_message_on_defeat") is True:
                logger.log_and_showinfo("info", f"{msg}")"""

replace_block = """        if not _in_bulk_resolve():
            if settings_obj.get("gui.pop_up_dialog_message_on_defeat") is True:
                logger.log_and_showinfo("info", f"{msg}")

        try:
            if trainer_card is not None:
                trainer_card.sync_to_leaderboard()
        except Exception:
            pass"""

if search_block in content:
    content = content.replace(search_block, replace_block)
    with open("src/Ankimon/functions/encounter_functions.py", "w") as f:
        f.write(content)
else:
    print("Could not find search block")
