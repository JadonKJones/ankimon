# File Cards

This document provides a repository navigation layer, mapping the structural purpose of every major file.

## Ankimon/resources.py
*   **Primary responsibility**: Contains 0 classes and 1 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 75 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: ensure_ankimon_infrastructure
*   **Key imports**: pathlib, os, json, subprocess
*   **Inbound dependencies**: 75 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 630 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/addon_files/lib/pypresence/utils.py
*   **Primary responsibility**: Contains 0 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 75 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: remove_none, test_ipc_path, get_ipc_path, get_event_loop
*   **Key imports**: asyncio, json, os, sys, tempfile
*   **Inbound dependencies**: 75 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 68 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/drawing_utils.py
*   **Primary responsibility**: Contains 1 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 73 other modules.
*   **Major symbols**:
    *   Classes: CustomLabel
    *   Functions: tooltipWithColour, draw_gender_symbols, draw_stat_boosts, mousePressEvent
*   **Key imports**: typing, aqt, aqt.qt, PyQt6.QtGui, PyQt6.QtCore
*   **Inbound dependencies**: 73 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 227 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/utils.py
*   **Primary responsibility**: Contains 0 classes and 35 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 72 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: format_pokemon_name, check_folders_exist, check_file_exists, test_online_connectivity, addon_config_editor_will_display_json...
*   **Key imports**: os, pathlib, requests, json, random
*   **Inbound dependencies**: 72 known importing files.
*   **Outbound dependencies**: 20 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 938 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/gui_classes/choose_trainer_sprite_graphical.py
*   **Primary responsibility**: Contains 1 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 60 other modules.
*   **Major symbols**:
    *   Classes: TrainerSpriteGraphicalDialog
    *   Functions: __init__, populate_grid, format_sprite_name, on_sprite_clicked
*   **Key imports**: PyQt6.QtCore, PyQt6.QtWidgets, PyQt6.QtGui, aqt, utils
*   **Inbound dependencies**: 60 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 82 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/classes/choose_move_dialog.py
*   **Primary responsibility**: Contains 1 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 59 other modules.
*   **Major symbols**:
    *   Classes: MoveSelectionDialog
    *   Functions: __init__, create_mouse_press_handler, select_move, keyPressEvent, handle_mouse_press
*   **Key imports**: sys, PyQt6.QtWidgets, PyQt6.QtGui, PyQt6.QtCore, functions.pokedex_functions
*   **Inbound dependencies**: 59 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 61 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/data/scripts/parse_random_battle_raw_sets.py
*   **Primary responsibility**: Contains 0 classes and 1 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 58 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: add_thing_to_dict_or_increment
*   **Key imports**: json, copy, constants, showdown.engine.helpers
*   **Inbound dependencies**: 58 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 136 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/error_handler.py
*   **Primary responsibility**: Contains 0 classes and 10 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 48 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: get_environment_info, set_image_from_url, scrub_traceback, load_error_images, create_error_label...
*   **Key imports**: os, re, json, random, traceback
*   **Inbound dependencies**: 48 known importing files.
*   **Outbound dependencies**: 15 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 259 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/ankimon_hooks_to_poke_engine.py
*   **Primary responsibility**: Contains 0 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 45 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: reset_stat_boosts, reset_side, simulate_battle_with_poke_engine, diff_states, print_state_changes
*   **Key imports**: random, collections, copy, traceback, typing
*   **Inbound dependencies**: 45 known importing files.
*   **Outbound dependencies**: 13 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 461 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/battle_functions.py
*   **Primary responsibility**: Contains 0 classes and 10 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 44 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: update_pokemon_battle_status, _process_battle_effects, validate_pokemon_status, process_battle_data, _handle_special_battle_status...
*   **Key imports**: copy, json, poke_engine, pyobj.error_handler, move_names
*   **Inbound dependencies**: 44 known importing files.
*   **Outbound dependencies**: 6 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 669 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/helpers.py
*   **Primary responsibility**: Contains 0 classes and 8 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 44 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: get_pokemon_info_from_condition, normalize_name, set_makes_sense, spreads_are_alike, remove_duplicate_spreads...
*   **Key imports**: math, , data
*   **Inbound dependencies**: 44 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 212 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_helpers.py
*   **Primary responsibility**: Contains 6 classes and 27 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 44 other modules.
*   **Major symbols**:
    *   Classes: TestBattleIsOver, TestSpreadsAreAlike, TestRemoveDuplicateSpreads, TestSetMakesSense, TestNormalizeName...
    *   Functions: setUp, test_returns_true_when_all_pokemon_for_user_are_dead, test_returns_true_when_all_pokemon_for_opponent_are_dead, test_returns_false_when_all_pokemon_are_alive, test_returns_false_when_only_active_is_dead...
*   **Key imports**: unittest, poke_engine.battle, poke_engine.helpers, poke_engine.helpers, poke_engine.helpers
*   **Inbound dependencies**: 44 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 210 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/data/helpers.py
*   **Primary responsibility**: Contains 0 classes and 10 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 44 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: get_pokemon_sets, get_all_possible_moves_for_random_battle, get_most_likely_ability_for_random_battle, get_most_likely_item_for_random_battle, get_all_likely_moves...
*   **Key imports**: , , data, data.parse_smogon_stats, data.parse_smogon_stats
*   **Inbound dependencies**: 44 known importing files.
*   **Outbound dependencies**: 10 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 197 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/abilities/before_move.py
*   **Primary responsibility**: Contains 0 classes and 3 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 44 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: stancechange, protean, ability_before_move
*   **Key imports**: data, , helpers
*   **Inbound dependencies**: 44 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 75 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/pokedex_functions.py
*   **Primary responsibility**: Contains 0 classes and 21 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 43 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: _normalize_language_id, special_pokemon_names_for_min_level, search_pokedex, search_pokedex_by_id, get_mainpokemon_evo...
*   **Key imports**: typing, resources, aqt.utils, aqt, json
*   **Inbound dependencies**: 43 known importing files.
*   **Outbound dependencies**: 9 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 651 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_battle_mechanics.py
*   **Primary responsibility**: Contains 3 classes and 679 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: TestBattleMechanics, TestRemoveDuplicateInstructions, TestUserMovesFirst
    *   Functions: setUp, test_two_pokemon_switching, test_powder_move_into_tackle_produces_correct_states, test_superpower_correctly_unboosts_opponent, test_psyshock_damage_is_the_same_regardless_of_spdef_boost...
*   **Key imports**: unittest, unittest, poke_engine.config, poke_engine, collections
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 16 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 14076 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_battle_modifiers.py
*   **Primary responsibility**: Contains 30 classes and 309 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: TestRequestMessage, TestSwitchOrDrag, TestHealOrDamage, TestActivate, TestPrepare...
    *   Functions: setUp, test_request_sets_force_switch_to_false, test_force_switch_properly_sets_the_force_switch_flag, test_wait_properly_sets_wait_flag, test_wait_does_not_initialize_pokemon...
*   **Key imports**: unittest, json, collections, poke_engine, poke_engine.helpers
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 41 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 4192 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_instruction_generator.py
*   **Primary responsibility**: Contains 13 classes and 136 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: TestGetInstructionsFromFlinched, TestGetInstructionsFromConditionsThatFreezeState, TestGetInstructionsFromDamage, TestGetInstructionsFromSideConditions, TestGetInstructionsFromHazardClearingMoves...
    *   Functions: setUp, test_flinch_sets_state_to_frozen_and_returns_one_state, test_flinch_being_false_does_not_freeze_the_state, setUp, test_paralyzed_attacker_results_in_two_instructions...
*   **Key imports**: unittest, poke_engine, poke_engine, poke_engine.battle, poke_engine.objects
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 10 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 3432 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_battle.py
*   **Primary responsibility**: Contains 7 classes and 77 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: TestPokemonInit, TestGetPossibleMoves, TestGetPossibleAbilities, TestGetPossibleItems, TestConvertToMega...
    *   Functions: test_alternate_pokemon_name_initializes, test_gets_four_moves_when_none_are_known, test_gets_only_first_3_moves_when_one_move_is_known, test_chance_moves_are_not_affected_by_known_moves, test_chance_moves_are_not_guessed_if_known_plus_expected_equals_four...
*   **Key imports**: unittest, unittest, poke_engine, poke_engine.battle, poke_engine.battle
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 1472 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/instruction_generator.py
*   **Primary responsibility**: Contains 0 classes and 26 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: get_instructions_from_move_special_effect, get_instructions_from_volatile_statuses, get_instructions_from_switch, get_instructions_from_flinched, get_instructions_from_statuses_that_freeze_the_state...
*   **Key imports**: copy, , logging, damage_calculator, special_effects.abilities.on_switch_in
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 11 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 1385 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/battle_modifier.py
*   **Primary responsibility**: Contains 0 classes and 49 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: can_have_priority_modified, can_have_speed_modified, find_pokemon_in_reserves, find_reserve_pokemon_by_nickname, is_opponent...
*   **Key imports**: re, json, copy, logging,
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 17 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 1255 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/battle.py
*   **Primary responsibility**: Contains 4 classes and 46 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: Battle, Battler, Pokemon, Move
    *   Functions: __init__, initialize_team_preview, during_team_preview, start_non_team_preview_battle, mega_evolve_possible...
*   **Key imports**: itertools, collections, collections, copy, copy
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 33 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 755 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/objects.py
*   **Primary responsibility**: Contains 5 classes and 72 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: State, Side, Pokemon, TransposeInstruction, StateMutator
    *   Functions: __init__, get_self_options, get_opponent_options, get_all_options, battle_is_finished...
*   **Key imports**: collections, copy, , data
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 749 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_initialize_battler.py
*   **Primary responsibility**: Contains 1 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: TestInitializeBattler
    *   Functions: setUp, test_initialize_with_z_move_available, test_initialize_with_hidden_power_produces_correct_hidden_power, test_initialize_pokemon_with_no_item, test_reviving_pokemon
*   **Key imports**: unittest, poke_engine.battle, poke_engine.battle
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 672 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/constants.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 646 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/find_state_instructions.py
*   **Primary responsibility**: Contains 0 classes and 10 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 42 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: lookup_move, get_effective_speed, get_effective_priority, user_moves_first, update_attacking_move...
*   **Key imports**: copy, , config, data,
*   **Inbound dependencies**: 42 known importing files.
*   **Outbound dependencies**: 15 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 497 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_team_converter.py
*   **Primary responsibility**: Contains 1 classes and 19 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 41 other modules.
*   **Major symbols**:
    *   Classes: TestSinglePokemonExportToDict
    *   Functions: setUp, test_pokemon_with_item, test_pokemon_with_level, test_pkmn_with_space_in_name, test_pkmn_with_space_in_name_with_gender...
*   **Key imports**: unittest, poke_engine.teams.team_converter
*   **Inbound dependencies**: 41 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 254 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/singletons.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 41 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: json, uuid, aqt, pyobj.ankimon_tracker, pyobj.settings
*   **Inbound dependencies**: 41 known importing files.
*   **Outbound dependencies**: 26 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 210 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/teams/team_converter.py
*   **Primary responsibility**: Contains 0 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 41 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: json_to_packed, single_pokemon_export_to_dict, export_to_packed, from_json, get_species
*   **Key imports**: helpers
*   **Inbound dependencies**: 41 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 102 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_select_best_move.py
*   **Primary responsibility**: Contains 1 classes and 19 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 40 other modules.
*   **Major symbols**:
    *   Classes: TestGetAllOptions
    *   Functions: setUp, test_returns_all_options_in_normal_situation, test_partiallytrapped_removes_switch_options_for_bot, test_partiallytrapped_removes_switch_options_for_opponent, test_bot_with_shadowtag_prevents_switch_options_for_opponent...
*   **Key imports**: unittest, collections, poke_engine, poke_engine.objects, poke_engine.objects
*   **Inbound dependencies**: 40 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 531 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/evaluate.py
*   **Primary responsibility**: Contains 1 classes and 3 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 40 other modules.
*   **Major symbols**:
    *   Classes: Scoring
    *   Functions: evaluate_pokemon, evaluate, BURN
*   **Key imports**: , data
*   **Inbound dependencies**: 40 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 144 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/select_best_move.py
*   **Primary responsibility**: Contains 0 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 40 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: remove_guaranteed_opponent_moves, pick_safest, move_item_to_front_of_list, get_payoff_matrix
*   **Key imports**: math, collections, , evaluate, find_state_instructions
*   **Inbound dependencies**: 40 known importing files.
*   **Outbound dependencies**: 5 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 136 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/data/parse_smogon_stats.py
*   **Primary responsibility**: Contains 0 classes and 3 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 40 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: get_smogon_stats_file_name, pokemon_is_similar, get_pokemon_information
*   **Key imports**: logging, ntpath, datetime, requests, helpers
*   **Inbound dependencies**: 40 known importing files.
*   **Outbound dependencies**: 6 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 121 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_parse_smogon_stats.py
*   **Primary responsibility**: Contains 1 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 40 other modules.
*   **Major symbols**:
    *   Classes: TestGetSmogonStatsFileName
    *   Functions: setUp, test_returns_single_digit_month_properly, test_works_with_double_digit_month, test_returns_previous_year_properly
*   **Key imports**: unittest, unittest, datetime, poke_engine.data.parse_smogon_stats
*   **Inbound dependencies**: 40 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 34 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/teams/load_team.py
*   **Primary responsibility**: Contains 0 classes and 1 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 40 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: load_team
*   **Key imports**: random, os, team_converter
*   **Inbound dependencies**: 40 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 29 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/battle_text_functions.py
*   **Primary responsibility**: Contains 0 classes and 1 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 40 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: effectiveness_text
*   **Key imports**:
*   **Inbound dependencies**: 40 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: utility
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 15 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/config.py
*   **Primary responsibility**: Contains 1 classes and 1 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 40 other modules.
*   **Major symbols**:
    *   Classes: _ShowdownConfig
    *   Functions: __init__
*   **Key imports**:
*   **Inbound dependencies**: 40 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 8 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_state_mutator.py
*   **Primary responsibility**: Contains 1 classes and 58 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: TestStatemutator
    *   Functions: setUp, test_switch_instruction_replaces_active, test_switch_instruction_replaces_active_for_opponent, test_switch_instruction_places_active_into_reserve, test_reverse_switch_instruction_replaces_active...
*   **Key imports**: unittest, collections, poke_engine, poke_engine.battle, poke_engine.objects
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 5 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 861 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/moves/modify_move.py
*   **Primary responsibility**: Contains 0 classes and 68 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: collisioncourse, suckerpunch, eruption, tailslap, freezedry...
*   **Key imports**: , data, damage_calculator
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 733 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/abilities/modify_attack_against.py
*   **Primary responsibility**: Contains 0 classes and 49 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: levitate, lightningrod, stormdrain, goodasgold, voltabsorb...
*   **Key imports**: , damage_calculator
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 600 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/damage_calculator.py
*   **Primary responsibility**: Contains 0 classes and 17 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: _calculate_damage, is_super_effective, is_not_very_effective, calculate_modifier, get_move...
*   **Key imports**: copy, copy, , data, data
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 475 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/abilities/modify_attack_being_used.py
*   **Primary responsibility**: Contains 0 classes and 50 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: analytic, adaptability, rockypayload, aerilate, galvanize...
*   **Key imports**: , damage_calculator, damage_calculator
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 453 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_damage_calculator.py
*   **Primary responsibility**: Contains 2 classes and 40 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: TestCalculateDamageAmount, TestCalculateDamage
    *   Functions: setUp, test_fire_blast_from_charizard_to_venusaur_without_modifiers, test_flashfire_increases_fire_move_damage, test_stab_without_weakness_calculates_properly, test_4x_weakness_calculates_properly...
*   **Key imports**: unittest, collections, poke_engine, poke_engine.damage_calculator, poke_engine.damage_calculator
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 9 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 411 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_team_datasets.py
*   **Primary responsibility**: Contains 1 classes and 26 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: TestTeamDatasets
    *   Functions: setUp, test_populating_datasets_from_file_with_empty_list, test_populating_datasets_using_known_pokemon, test_predict_set_returns_pokemonset, test_predict_set_returns_more_common_set...
*   **Key imports**: unittest, poke_engine, poke_engine.data.team_datasets, poke_engine.battle
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 400 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/data/scripts/update_moves.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: requests, json, copy, subprocess
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 305 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/battle_loop.py
*   **Primary responsibility**: Contains 2 classes and 3 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: BattleState, Container
    *   Functions: init_battle_state, _get_cards_per_round, on_review_card
*   **Key imports**: copy, random, dataclasses, typing, aqt
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 15 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 282 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/items/modify_attack_being_used.py
*   **Primary responsibility**: Contains 0 classes and 30 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: choiceband, choicespecs, lifeorb, expertbelt, blackglasses...
*   **Key imports**: , damage_calculator
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 230 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/abilities/on_switch_in.py
*   **Primary responsibility**: Contains 0 classes and 15 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: sandstream, snowwarning, drought, drizzle, desolateland...
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 206 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_items.py
*   **Primary responsibility**: Contains 3 classes and 9 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: TestChoiceBand, TestChoiceSpecs, TestEviolite
    *   Functions: setUp, test_choice_band_boosts_physical, test_choice_band_does_not_boost_special, setUp, test_choice_scarf_does_not_boost_physical...
*   **Key imports**: unittest, unittest.mock, poke_engine, poke_engine.special_effects.items.modify_attack_being_used, poke_engine.special_effects.items.modify_attack_against
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 5 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 167 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/data/team_datasets.py
*   **Primary responsibility**: Contains 3 classes and 11 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: PokemonMoveset, PokemonSet, _TeamDatasets
    *   Functions: pkmn_can_have_moves, __iter__, item_check, speed_check, pkmn_can_contain_set...
*   **Key imports**: __future__, dataclasses, os, json, logging
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 11 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 162 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/data/mods/apply_mods.py
*   **Primary responsibility**: Contains 0 classes and 11 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: apply_move_mods, apply_pokedex_mods, set_random_battle_sets, apply_gen_3_mods, apply_gen_4_mods...
*   **Key imports**: os, json, logging, constants, data
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 133 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/moves/move_special_effect.py
*   **Primary responsibility**: Contains 0 classes and 14 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: trickroom, futuresight, trick, weather_move, chillyreception...
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 101 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/abilities/end_of_turn.py
*   **Primary responsibility**: Contains 0 classes and 8 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: poisonheal, speedboost, hydration, solarpower, raindish...
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 81 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_state.py
*   **Primary responsibility**: Contains 2 classes and 10 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: TestPokemonInit, TestPokemon
    *   Functions: test_state_serialization_and_loading_results_in_the_same_state, test_pokemon_init_gives_correct_number_of_physical_moves, setUp, test_pokemon_item_can_be_removed_returns_true_in_basic_case, test_item_can_be_removed_returns_false_if_item_is_none...
*   **Key imports**: unittest, poke_engine, poke_engine.objects, poke_engine.battle
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 69 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/moves/after_move.py
*   **Primary responsibility**: Contains 0 classes and 9 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: knockoff, phantomforce, fly, bounce, dig...
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 67 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/items/modify_attack_against.py
*   **Primary responsibility**: Contains 0 classes and 7 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: eviolite, rockyhelmet, assaultvest, airballoon, weaknesspolicy...
*   **Key imports**: , damage_calculator
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 67 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/data/scripts/update_pokedex.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: requests, re, json
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 67 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_decide.py
*   **Primary responsibility**: Contains 1 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: TestPickSafest
    *   Functions: test_returns_only_options_from_one_item_dictionary, test_returns_better_option_for_two_different_moves, test_returns_option_with_the_lowest_minimum_in_2_by_2, test_returns_option_with_the_lowest_minimum_in_3_by_3
*   **Key imports**: unittest, unittest, poke_engine.select_best_move
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 56 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/items/on_switch_in.py
*   **Primary responsibility**: Contains 0 classes and 6 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: grassyseed, mistyseed, psychicseed, electricseed, boosterenergy...
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 50 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/items/end_of_turn.py
*   **Primary responsibility**: Contains 0 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: leftovers, blacksludge, flameorb, toxicorb, item_end_of_turn
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 48 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/test_move_special_effects.py
*   **Primary responsibility**: Contains 1 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: TestSuckerPunch
    *   Functions: setUp, test_suckerpunch_misses_when_opponent_selects_non_damaging_move, test_suckerpunch_misses_verus_a_switch, test_suckerpunch_misses_when_it_is_the_second_move, test_suckerpunch_hits_when_opponent_tries_to_attack
*   **Key imports**: unittest, poke_engine.data, poke_engine, poke_engine.special_effects.moves.modify_move
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 38 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/setup.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: setuptools
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 30 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/switch_out_moves.py
*   **Primary responsibility**: Contains 0 classes and 2 functions related to its domain.
*   **Why it matters**: Acts as a domain logic for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: switch_out_move_triggered, get_best_switch_pokemon
*   **Key imports**: , select_best_move
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: domain logic
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 29 lines of code. The file clearly exhibits characteristics of a domain logic layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/data/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: os, json, logging
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 24 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/tests/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: logging, os, sys
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 11 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: battle, config, evaluate, objects, objects
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 5 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 6 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/teams/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: load_team
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 1 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 0 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/moves/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 0 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/items/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 0 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/special_effects/abilities/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 0 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/poke_engine/data/mods/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 39 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 39 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 0 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/pokemon_obj.py
*   **Primary responsibility**: Contains 2 classes and 23 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 36 other modules.
*   **Major symbols**:
    *   Classes: PokemonObject, PokemonEncoder
    *   Functions: __init__, calc_stat, stats, stats, cp...
*   **Key imports**: typing, uuid, json, os, typing
*   **Inbound dependencies**: 36 known importing files.
*   **Outbound dependencies**: 12 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 489 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/addon_files/lib/pypresence/exceptions.py
*   **Primary responsibility**: Contains 12 classes and 12 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 36 other modules.
*   **Major symbols**:
    *   Classes: PyPresenceException, DiscordNotFound, InvalidPipe, InvalidArgument, ServerError...
    *   Functions: __init__, __init__, __init__, __init__, __init__...
*   **Key imports**:
*   **Inbound dependencies**: 36 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 65 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/addon_files/lib/pypresence/payloads.py
*   **Primary responsibility**: Contains 1 classes and 21 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 35 other modules.
*   **Major symbols**:
    *   Classes: Payload
    *   Functions: __init__, __str__, time, set_activity, authorize...
*   **Key imports**: json, os, time, typing, utils
*   **Inbound dependencies**: 35 known importing files.
*   **Outbound dependencies**: 6 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 315 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/InfoLogger.py
*   **Primary responsibility**: Contains 1 classes and 6 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 35 other modules.
*   **Major symbols**:
    *   Classes: ShowInfoLogger
    *   Functions: __init__, log_and_showinfo, log, game_log, toggle_log_window...
*   **Key imports**: logging, PyQt6.QtWidgets, PyQt6.QtCore, os
*   **Inbound dependencies**: 35 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 126 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/badges_functions.py
*   **Primary responsibility**: Contains 0 classes and 6 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 35 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: get_achieved_badges, populate_achievements_from_badges, check_for_badge, save_badges, receive_badge...
*   **Key imports**: json, typing, resources, aqt
*   **Inbound dependencies**: 35 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 71 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/addon_files/lib/pypresence/types.py
*   **Primary responsibility**: Contains 1 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 35 other modules.
*   **Major symbols**:
    *   Classes: ActivityType
    *   Functions: None
*   **Key imports**: enum
*   **Inbound dependencies**: 35 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: glue
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 15 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/create_css_for_reviewer.py
*   **Primary responsibility**: Contains 0 classes and 1 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 34 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: create_css_for_reviewer
*   **Key imports**:
*   **Inbound dependencies**: 34 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 471 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/business.py
*   **Primary responsibility**: Contains 0 classes and 24 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 34 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: get_image_as_base64, split_string_by_length, split_japanese_string_by_length, resize_pixmap_img, calc_experience...
*   **Key imports**: base64, csv, functools, json, math
*   **Inbound dependencies**: 34 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 356 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/reviewer_obj.py
*   **Primary responsibility**: Contains 1 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 34 other modules.
*   **Major symbols**:
    *   Classes: Reviewer_Manager
    *   Functions: __init__, reviewer_reset_life_bar_inject, get_boost_values_string, inject_life_bar, update_life_bar
*   **Key imports**: aqt, aqt.utils, functions.pokemon_functions, business, functions.create_css_for_reviewer
*   **Inbound dependencies**: 34 known importing files.
*   **Outbound dependencies**: 10 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 312 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/pokemon_functions.py
*   **Primary responsibility**: Contains 0 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 34 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: pick_random_gender, calculate_max_hp_wildpokemon, find_experience_for_level, shiny_chance, save_fossil_pokemon
*   **Key imports**: csv, json, random, uuid, datetime
*   **Inbound dependencies**: 34 known importing files.
*   **Outbound dependencies**: 12 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 252 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/addon_files/lib/pypresence/baseclient.py
*   **Primary responsibility**: Contains 1 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 34 other modules.
*   **Major symbols**:
    *   Classes: BaseClient
    *   Functions: __init__, update_event_loop, _err_handle, send_data
*   **Key imports**: asyncio, inspect, json, os, struct
*   **Inbound dependencies**: 34 known importing files.
*   **Outbound dependencies**: 11 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 131 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/learnset_retrieval.py
*   **Primary responsibility**: Contains 0 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 34 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: _get_learnset_moves, get_all_pokemon_moves, get_random_moves_for_pokemon, get_levelup_move_for_pokemon
*   **Key imports**: json, random, resources
*   **Inbound dependencies**: 34 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 64 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/settings_window.py
*   **Primary responsibility**: Contains 1 classes and 13 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 33 other modules.
*   **Major symbols**:
    *   Classes: SettingsWindow
    *   Functions: create_rounded_pixmap, __init__, is_dark_mode, _apply_stylesheet, load_descriptions...
*   **Key imports**: json, os, typing, aqt.qt, aqt.utils
*   **Inbound dependencies**: 33 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 567 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/reviewer_iframe.py
*   **Primary responsibility**: Contains 0 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 33 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: list_audio_files, create_html_code, create_iframe_html, prepare, create_head_code
*   **Key imports**: os, fnmatch, aqt, pokemon_functions
*   **Inbound dependencies**: 33 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 479 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/settings.py
*   **Primary responsibility**: Contains 1 classes and 9 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 33 other modules.
*   **Major symbols**:
    *   Classes: Settings
    *   Functions: __init__, get_description, load_config, _apply_type_coercion, save_config...
*   **Key imports**: json, os, shutil, aqt, aqt.utils
*   **Inbound dependencies**: 33 known importing files.
*   **Outbound dependencies**: 13 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 279 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/create_gui_functions.py
*   **Primary responsibility**: Contains 0 classes and 2 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 33 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: create_status_label, create_status_html
*   **Key imports**: PyQt6.QtWidgets, PyQt6.QtCore, PyQt6.QtGui, const
*   **Inbound dependencies**: 33 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 109 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/sprite_functions.py
*   **Primary responsibility**: Contains 0 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 33 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: _path_format, _try_gendered, _try_back, get_sprite_path
*   **Key imports**: os, aqt, resources
*   **Inbound dependencies**: 33 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 83 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/gui_classes/AnkimonWindow copy.py
*   **Primary responsibility**: Contains 1 classes and 22 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 32 other modules.
*   **Major symbols**:
    *   Classes: TestWindow
    *   Functions: __init__, init_ui, open_dynamic_window, display_first_start_up, pokemon_display_first_encounter...
*   **Key imports**: PyQt6.QtWidgets, PyQt6.QtGui, PyQt6.QtCore, aqt.utils, aqt
*   **Inbound dependencies**: 32 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 625 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/addon_files/lib/pypresence/client.py
*   **Primary responsibility**: Contains 2 classes and 29 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 32 other modules.
*   **Major symbols**:
    *   Classes: Client, AioClient
    *   Functions: __init__, register_event, unregister_event, on_event, authorize...
*   **Key imports**: asyncio, inspect, struct, json, os
*   **Inbound dependencies**: 32 known importing files.
*   **Outbound dependencies**: 10 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 384 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/reviewer_ui.py
*   **Primary responsibility**: Contains 0 classes and 7 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 32 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: set_collected_ids, catch_shortcut_function, defeat_shortcut_function, setup_reviewer_ui, _shortcutKeys_wrap...
*   **Key imports**: anki.hooks, aqt.reviewer, aqt.utils, singletons, functions.encounter_functions
*   **Inbound dependencies**: 32 known importing files.
*   **Outbound dependencies**: 6 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 92 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/addon_files/lib/pypresence/presence.py
*   **Primary responsibility**: Contains 2 classes and 7 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 32 other modules.
*   **Major symbols**:
    *   Classes: Presence, AioPresence
    *   Functions: __init__, update, clear, connect, close...
*   **Key imports**: json, os, time, sys, baseclient
*   **Inbound dependencies**: 32 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 91 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/translator.py
*   **Primary responsibility**: Contains 1 classes and 2 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 32 other modules.
*   **Major symbols**:
    *   Classes: Translator
    *   Functions: __init__, translate
*   **Key imports**: json, resources
*   **Inbound dependencies**: 32 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 73 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/addon_files/lib/pypresence/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 32 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: baseclient, client, exceptions, types, presence
*   **Inbound dependencies**: 32 known importing files.
*   **Outbound dependencies**: 5 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 18 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/encounter_functions.py
*   **Primary responsibility**: Contains 1 classes and 15 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 31 other modules.
*   **Major symbols**:
    *   Classes: Container
    *   Functions: modify_percentages, get_random_pokemon_in_tier, get_tier, choose_random_pkmn_from_tier, check_min_generate_level...
*   **Key imports**: json, random, math, typing, datetime
*   **Inbound dependencies**: 31 known importing files.
*   **Outbound dependencies**: 29 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 878 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/gui_entities.py
*   **Primary responsibility**: Contains 11 classes and 30 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 31 other modules.
*   **Major symbols**:
    *   Classes: MovieSplashLabel, UpdateNotificationWindow, AgreementDialog, Version_Dialog, License...
    *   Functions: __init__, showEvent, hideEvent, __init__, open...
*   **Key imports**: markdown, json, PyQt6.QtGui, PyQt6.QtWidgets, aqt
*   **Inbound dependencies**: 31 known importing files.
*   **Outbound dependencies**: 13 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 360 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/hook_registry.py
*   **Primary responsibility**: Contains 0 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 31 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: add_catch_pokemon_hook, add_defeat_pokemon_hook, CatchPokemonHook, DefeatPokemonHook
*   **Key imports**: singletons, functions.encounter_functions
*   **Inbound dependencies**: 31 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 56 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/test_window.py
*   **Primary responsibility**: Contains 1 classes and 22 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 30 other modules.
*   **Major symbols**:
    *   Classes: TestWindow
    *   Functions: __init__, init_ui, open_dynamic_window, display_first_start_up, _draw_cp_pp...
*   **Key imports**: json, aqt, aqt.qt, aqt.utils, PyQt6.QtGui
*   **Inbound dependencies**: 30 known importing files.
*   **Outbound dependencies**: 16 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 925 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/database_manager.py
*   **Primary responsibility**: Contains 1 classes and 46 functions related to its domain.
*   **Why it matters**: Acts as a persistence for the system, interacting with 29 other modules.
*   **Major symbols**:
    *   Classes: AnkimonDB
    *   Functions: get_db, __init__, _log, _get_connection, close...
*   **Key imports**: json, sqlite3, uuid, pathlib, typing
*   **Inbound dependencies**: 29 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: persistence
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 981 lines of code. The file clearly exhibits characteristics of a persistence layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/encounter_data.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 29 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 29 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 349 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/texts.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 29 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 29 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 242 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/gui_classes/backup_manager_dialog.py
*   **Primary responsibility**: Contains 2 classes and 9 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 29 other modules.
*   **Major symbols**:
    *   Classes: BackupItemWidget, BackupManagerDialog
    *   Functions: __init__, __init__, init_ui, apply_stylesheet, refresh_backup_list...
*   **Key imports**: PyQt6.QtWidgets, PyQt6.QtCore, PyQt6.QtGui, pathlib, pyobj.backup_manager
*   **Inbound dependencies**: 29 known importing files.
*   **Outbound dependencies**: 6 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 236 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/ankimon_tracker_window.py
*   **Primary responsibility**: Contains 1 classes and 6 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 29 other modules.
*   **Major symbols**:
    *   Classes: AnkimonTrackerWindow
    *   Functions: __init__, get_text_color, create_gui, update_stats, start_real_time_updates...
*   **Key imports**: PyQt6.QtWidgets, PyQt6.QtCore, PyQt6.QtGui, aqt
*   **Inbound dependencies**: 29 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 171 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/update_main_pokemon.py
*   **Primary responsibility**: Contains 0 classes and 2 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 29 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: update_main_pokemon, save_main_pokemon
*   **Key imports**: json, uuid, typing, functions.pokedex_functions, resources
*   **Inbound dependencies**: 29 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 118 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/pc_box.py
*   **Primary responsibility**: Contains 4 classes and 34 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: PokemonSlotButton, ScaledMovieLabel, PokemonPC, GiveItemWindow
    *   Functions: format_item_name, clear_layout, mouseReleaseEvent, __init__, on_frame_changed...
*   **Key imports**: json, uuid, typing, aqt, aqt.qt
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 21 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 1325 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/ankimon_sync.py
*   **Primary responsibility**: Contains 2 classes and 41 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: ImprovedPokemonDataSync, AnkimonDataSync
    *   Functions: get_ankimon_sync, get_sync_info, check_and_sync_pokemon_data, save_ankimon_configs, read_ankimon_configs...
*   **Key imports**: base64, filecmp, json, os, shutil
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 18 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 823 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/evolution_window.py
*   **Primary responsibility**: Contains 2 classes and 10 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: EvoWindow, Container
    *   Functions: __init__, init_ui, open_dynamic_window, display_evo_complete, _display_evo_complete_layout...
*   **Key imports**: json, random, aqt, aqt.qt, PyQt6.QtGui
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 23 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 436 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/download_sprites.py
*   **Primary responsibility**: Contains 2 classes and 15 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: DownloadThread, DownloadDialog
    *   Functions: show_agreement_and_download_dialog, __init__, cancel, _cleanup_temp_files, _fetch_expected_hash...
*   **Key imports**: os, zipfile, requests, time, hashlib
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 11 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 429 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/migration_dialog.py
*   **Primary responsibility**: Contains 1 classes and 9 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: MigrationDialog
    *   Functions: show_migration_dialog_if_needed, __init__, _setup_ui, _update_progress, _on_cancel...
*   **Key imports**: json, shutil, traceback, PyQt6.QtWidgets, PyQt6.QtCore
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 11 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 400 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/ankimon_tracker.py
*   **Primary responsibility**: Contains 1 classes and 23 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: AnkimonTracker
    *   Functions: __init__, get_total_reviews, set_main_pokemon, set_enemy_pokemon, check_streak...
*   **Key imports**: PyQt6.QtCore, pokemon_obj, datetime, error_handler, functions.pokedex_functions
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 267 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/pokemon_showdown_functions.py
*   **Primary responsibility**: Contains 0 classes and 3 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: export_to_pkmn_showdown, export_all_pkmn_showdown, flex_pokemon_collection
*   **Key imports**: json, aqt, aqt.qt, PyQt6.QtWidgets, functions.pokedex_functions
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 266 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/backup_manager.py
*   **Primary responsibility**: Contains 1 classes and 9 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: BackupManager
    *   Functions: __init__, _deobfuscate_data, get_backups, create_backup, _generate_summary...
*   **Key imports**: base64, json, os, shutil, datetime
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 11 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 256 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/discord_function.py
*   **Primary responsibility**: Contains 1 classes and 7 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: DiscordPresence
    *   Functions: check_conflicting_discord_addons, __init__, _get_special_quotes, update_presence, start...
*   **Key imports**: threading, random, time, pyobj.ankimon_tracker, addon_files.lib.pypresence
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 9 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 193 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/trainer_functions.py
*   **Primary responsibility**: Contains 0 classes and 2 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: find_trainer_rank, xp_share_gain_exp
*   **Key imports**: json, badges_functions, pokedex_functions, pokemon_functions, pokedex_functions
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 130 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/migration.py
*   **Primary responsibility**: Contains 0 classes and 2 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: get_starter_evolution_ids, migrate_starter_individual_id
*   **Key imports**: json, aqt, aqt.utils, resources
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 123 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/rate_addon_functions.py
*   **Primary responsibility**: Contains 0 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: rate_this_addon, support_button_click, thankyou_message, dont_show_this_button, rate_this_button
*   **Key imports**: PyQt6.QtCore, PyQt6.QtGui, PyQt6.QtWidgets, texts, utils
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: utility
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 87 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/profile_hooks.py
*   **Primary responsibility**: Contains 0 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: _on_profile_did_open, register_profile_hooks, handler, on_profile_loaded
*   **Key imports**: anki.hooks, aqt, singletons, pyobj.ankimon_sync, pyobj.tip_of_the_day
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 79 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/move_names.py
*   **Primary responsibility**: Contains 0 classes and 3 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: _current_lang_code, _load_move_name_lookups, format_move_name
*   **Key imports**: json, functools, aqt, pyobj.translator, resources
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 5 known imports.
*   **File role classification**: glue
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 47 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/card_hooks.py
*   **Primary responsibility**: Contains 0 classes and 6 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: on_show_question, on_show_answer, on_reviewer_did_show_question, answerCard_before, answerCard_after...
*   **Key imports**: aqt, aqt, aqt.utils, singletons
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 4 known imports.
*   **File role classification**: glue
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 45 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/url_functions.py
*   **Primary responsibility**: Contains 0 classes and 6 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: open_browser_window, open_team_builder, rate_addon_url, report_bug, join_discord_url...
*   **Key imports**: PyQt6.QtGui, PyQt6.QtCore
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: utility
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 43 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/hooks.py
*   **Primary responsibility**: Contains 0 classes and 1 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: setupHooks
*   **Key imports**: aqt, utils
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: glue
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 16 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/gui_functions.py
*   **Primary responsibility**: Contains 0 classes and 2 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 28 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: type_icon_path, move_category_path
*   **Key imports**: resources
*   **Inbound dependencies**: 28 known importing files.
*   **Outbound dependencies**: 1 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 11 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/gui_classes/pokemon_details.py
*   **Primary responsibility**: Contains 1 classes and 17 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: RadarChart
    *   Functions: _lookup_move_data, PokemonCollectionDetails, PokemonDetailsStats, createStatBar, create_iv_ev_tab_layout...
*   **Key imports**: math, math, json, typing, re
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 28 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 1173 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/item_window.py
*   **Primary responsibility**: Contains 1 classes and 26 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: ItemWindow
    *   Functions: __init__, initUI, renewWidgets, filter_items, give_held_item...
*   **Key imports**: pathlib, random, json, csv, typing
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 24 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 661 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/pokemon_trade.py
*   **Primary responsibility**: Contains 1 classes and 29 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: PokemonTrade
    *   Functions: create_monthly_challenge_pokemon, add_pokemon_to_collection, check_and_award_monthly_pokemon, __init__, load_pokemon_data...
*   **Key imports**: json, hashlib, requests, PyQt6.QtWidgets, PyQt6.QtGui
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 20 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 613 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/ankimon_shop.py
*   **Primary responsibility**: Contains 1 classes and 15 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: PokemonShopManager
    *   Functions: __init__, _load_early_gameboy_font, _is_night_mode, _get_theme_colors, toggle_window...
*   **Key imports**: os, random, datetime, json, typing
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 11 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 602 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/starter_window.py
*   **Primary responsibility**: Contains 1 classes and 15 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: StarterWindow
    *   Functions: __init__, init_ui, open_dynamic_window, clear_layout, keyPressEvent...
*   **Key imports**: datetime, random, json, uuid, aqt
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 23 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 420 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/gui_classes/pokemon_team_window.py
*   **Primary responsibility**: Contains 1 classes and 9 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: PokemonTeamDialog
    *   Functions: __init__, load_my_pokemon, load_pokemon_team, update_team_display, switch_out_pokemon...
*   **Key imports**: functions.sprite_functions, PyQt6.QtCore, PyQt6.QtWidgets, PyQt6.QtGui, json
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 9 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 327 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/trainer_card.py
*   **Primary responsibility**: Contains 1 classes and 14 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: TrainerCard
    *   Functions: __init__, badge_count, badges, get_highest_level_pokemon, highest_pokemon_level...
*   **Key imports**: resources, functions.trainer_functions, functions.badges_functions, aqt, aqt.utils
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 226 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/achievement_window.py
*   **Primary responsibility**: Contains 1 classes and 7 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: AchievementWindow
    *   Functions: __init__, initUI, renewWidgets, BadgesLabel, clear_layout...
*   **Key imports**: json, aqt, aqt.qt, PyQt6.QtGui, PyQt6.QtWidgets
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 138 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/trainer_card_window.py
*   **Primary responsibility**: Contains 1 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: TrainerCardGUI
    *   Functions: __init__, init_ui, update_display, toggle_window, create_info_label
*   **Key imports**: PyQt6.QtWidgets, PyQt6.QtGui, PyQt6.QtCore, resources, os
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 5 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 137 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/collection_dialog.py
*   **Primary responsibility**: Contains 1 classes and 1 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: Container
    *   Functions: MainPokemon
*   **Key imports**: json, collections, uuid, aqt.utils, pyobj.error_handler
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 19 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 128 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/ankimon_leaderboard.py
*   **Primary responsibility**: Contains 1 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: ApiKeyDialog
    *   Functions: sync_data_to_leaderboard, show_api_key_dialog, __init__, submit, save_credentials
*   **Key imports**: sys, json, PyQt6.QtWidgets, aqt.utils, resources
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 119 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pokedex/pokedex_obj.py
*   **Primary responsibility**: Contains 1 classes and 3 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: Pokedex
    *   Functions: __init__, load_html, showEvent
*   **Key imports**: os, json, aqt, PyQt6.QtCore, aqt.qt
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 6 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 98 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/gui_classes/check_files.py
*   **Primary responsibility**: Contains 1 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: FileCheckerApp
    *   Functions: check_files_in_json, verify_files, __init__, check_files
*   **Key imports**: sys, os, json, PyQt6.QtWidgets, PyQt6.QtWidgets
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 8 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 97 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/const.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**: aqt, pathlib
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: glue
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 47 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/discord_integration.py
*   **Primary responsibility**: Contains 0 classes and 3 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: setup_discord_hooks, on_reviewer_initialized, on_reviewer_will_end
*   **Key imports**: aqt, functions.discord_function, singletons
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 3 known imports.
*   **File role classification**: glue
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 36 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/attack_dialog.py
*   **Primary responsibility**: Contains 1 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: AttackDialog
    *   Functions: __init__, initUI, attackSelected, attackNoneSelected
*   **Key imports**: PyQt6.QtWidgets, PyQt6.QtCore
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 2 known imports.
*   **File role classification**: state container
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 33 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/starters.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a utility for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: utility
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 29 lines of code. The file clearly exhibits characteristics of a utility layer based on its structural dependencies and symbol definitions.

## Ankimon/functions/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 27 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 27 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 0 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/update_dialog.py
*   **Primary responsibility**: Contains 1 classes and 20 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: UpdateDialog
    *   Functions: __init__, _apply_theme, _build_header, _build_releases_tab, _build_dev_tab...
*   **Key imports**: aqt, aqt.operations, aqt.qt, aqt.theme, update_manager
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 6 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 492 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/update_manager.py
*   **Primary responsibility**: Contains 0 classes and 21 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: _make_request, _api_get, _fetch_gitignore_patterns, _should_preserve, fetch_tags...
*   **Key imports**: io, json, os, shutil, tempfile
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 14 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 396 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/gui_classes/overview_team.py
*   **Primary responsibility**: Contains 0 classes and 7 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: _bg_style_from_types, _build_pokeball_style, _build_card_html, load_pokemon_team, _build_pokemon_grid...
*   **Key imports**: __future__, json, os, typing, aqt
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 9 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 392 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/menu_buttons.py
*   **Primary responsibility**: Contains 0 classes and 3 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: create_menu_actions, _open_update_dialog, show_achievements_window
*   **Key imports**: typing, pathlib, aqt.utils, aqt.qt, PyQt6.QtWidgets
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 31 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 290 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/help_window.py
*   **Primary responsibility**: Contains 4 classes and 9 functions related to its domain.
*   **Why it matters**: Acts as a UI surface for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: ExternalLinkWebEnginePage, Bridge, HelpWindow, DummyPage
    *   Functions: acceptNavigationRequest, createWindow, __init__, closeDialog, __init__...
*   **Key imports**: PyQt6.QtGui, PyQt6.QtWidgets, PyQt6.QtCore, aqt.qt, aqt.utils
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 11 known imports.
*   **File role classification**: UI surface
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 150 lines of code. The file clearly exhibits characteristics of a UI surface layer based on its structural dependencies and symbol definitions.

## Ankimon/startup.py
*   **Primary responsibility**: Contains 0 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: run_startup_sequence, _check_assets, _init_first_enemy, _check_starter
*   **Key imports**: json, random, aqt, resources, utils
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 17 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 138 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/tip_of_the_day.py
*   **Primary responsibility**: Contains 1 classes and 5 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: TipOfTheDayDialog
    *   Functions: show_tip_of_the_day, __init__, _load_tips, show_new_tip, accept
*   **Key imports**: json, random, pathlib, aqt, aqt.qt
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 6 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 91 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/changelog.py
*   **Primary responsibility**: Contains 0 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a glue for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: download_changelog, check_and_show_changelog, open_help_window, done
*   **Key imports**: typing, aqt, aqt.operations, aqt.utils, markdown
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 10 known imports.
*   **File role classification**: glue
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 63 lines of code. The file clearly exhibits characteristics of a glue layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/achievements_dialog.py
*   **Primary responsibility**: Contains 1 classes and 2 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: AchievementsDialog
    *   Functions: __init__, load_html
*   **Key imports**: os, json, aqt, aqt.qt, PyQt6.QtCore
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 63 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/backup_files.py
*   **Primary responsibility**: Contains 0 classes and 4 functions related to its domain.
*   **Why it matters**: Acts as a state container for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: create_backup_folder, rotate_backups, is_backup_needed, run_backup
*   **Key imports**: os, shutil, datetime, json, aqt.utils
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 7 known imports.
*   **File role classification**: state container
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 54 lines of code. The file clearly exhibits characteristics of a state container layer based on its structural dependencies and symbol definitions.

## Ankimon/gui_classes/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 26 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 26 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 0 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/__init__.py
*   **Primary responsibility**: Contains 0 classes and 1 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 25 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: on_webview_will_set_content
*   **Key imports**: aqt, aqt, aqt.gui_hooks, aqt.webview, resources
*   **Inbound dependencies**: 25 known importing files.
*   **Outbound dependencies**: 22 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: high

Directly evidenced by AST parsing of the file's 175 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.

## Ankimon/pyobj/__init__.py
*   **Primary responsibility**: Contains 0 classes and 0 functions related to its domain.
*   **Why it matters**: Acts as a entrypoint for the system, interacting with 25 other modules.
*   **Major symbols**:
    *   Classes: None
    *   Functions: None
*   **Key imports**:
*   **Inbound dependencies**: 25 known importing files.
*   **Outbound dependencies**: 0 known imports.
*   **File role classification**: entrypoint
*   **Confidence level**: medium

Directly evidenced by AST parsing of the file's 0 lines of code. The file clearly exhibits characteristics of a entrypoint layer based on its structural dependencies and symbol definitions.
