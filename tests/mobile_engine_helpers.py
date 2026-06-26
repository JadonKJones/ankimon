"""Headless test stand-in for the (deferred) web-shell ``MobileBridge``.

The Mobile/Web Reviews ENGINE lives in ``Ankimon.functions.mobile_sync``. In
production the Qt/WebEngine ``MobileBridge`` (in ``ankimon_items_web/shop_obj.py``)
is a thin wrapper that pulls game state off ``mw.*`` and delegates to the engine.
That web shell is deferred (and its WebEngine import cannot initialise on the CI
Pi), so these tests exercise the engine through this faithful headless copy of the
bridge's method bodies — the QObject/pyqtSlot decorators and the non-pytest
``QueryOp`` branches are the only things removed.

``mw`` is fetched at call time (not import time) so each test's freshly-built
``aqt.mw`` mock is honoured.
"""

import math
import os
import time


def _mw():
    from aqt import mw
    return mw


class MobileBridge:
    """Headless stand-in for ankimon_items_web.shop_obj.MobileBridge."""

    def __init__(self, window=None):
        self._w = window
        self._current_pending_outcome = None

    # --- status / read-only ------------------------------------------------

    def getMobileStatus(self) -> dict:
        mw = _mw()
        try:
            db = mw.ankimon_db
            rows = db.execute(
                """SELECT ease, COUNT(*) as cnt FROM pending_mobile_battles
                   WHERE resolved = 0 GROUP BY ease"""
            ).fetchall()
            pending_count = sum(r[1] for r in rows)

            from Ankimon.functions import mobile_sync
            settings_obj = mw.settings_obj
            cards_per_round, _ = mobile_sync._parse_cards_per_round(settings_obj)

            cursor = db.execute("SELECT value FROM metadata WHERE key = 'mobile_resolved_encounters_count'")
            row = cursor.fetchone()
            resolved_battles = int(row[0]) if row else 0
            battle_count = resolved_battles + math.ceil(pending_count / cards_per_round)

            if pending_count == 0:
                return {"pending_count": 0, "cap": 10000, "battle_count": 0}

            ease_breakdown = {"1": 0, "2": 0, "3": 0, "4": 0}
            for row in rows:
                ease_breakdown[str(row[0])] = row[1]

            settings_obj = mw.settings_obj
            main_pokemon = getattr(mw, "main_pokemon", None)
            trainer_card = getattr(mw, "trainer_card", None)
            ankimon_tracker_obj = getattr(mw, "ankimon_tracker_obj", None)

            auto_battle_mode_names = {
                0: "Manual (Auto-Resolve)",
                1: "Auto-Catch",
                2: "Auto-Defeat",
                3: "Catch Uncollected",
            }
            auto_battle_val = 0
            try:
                auto_battle_val = int(settings_obj.get("battle.automatic_battle", 0))
            except Exception:
                pass
            auto_battle_mode = auto_battle_mode_names.get(auto_battle_val, "Manual")

            rare_catch_active = False
            if settings_obj:
                rare_catch_active = (
                    settings_obj.get("battle.auto_catch_legendary", True)
                    or settings_obj.get("battle.auto_catch_mythical", True)
                    or settings_obj.get("battle.auto_catch_ultra", True)
                    or settings_obj.get("battle.auto_catch_starter", True)
                    or settings_obj.get("battle.auto_catch_mega", True)
                    or settings_obj.get("battle.auto_catch_gmax", True)
                    or settings_obj.get("battle.auto_catch_regional", True)
                    or bool(settings_obj.get("battle.auto_catch_wishlist", []))
                )

            main_pokemon_name = None
            main_pokemon_level = None
            main_pokemon_sprite = None
            sprite_mode = "static"
            if main_pokemon:
                main_pokemon_name = main_pokemon.name
                main_pokemon_level = main_pokemon.level

                from Ankimon.functions.sprite_functions import get_relative_sprite_path
                main_pokemon_sprite = get_relative_sprite_path(
                    main_pokemon.id, bool(main_pokemon.shiny), (main_pokemon.gender or "N"), main_pokemon.name, "gif"
                )

            if settings_obj:
                sprite_mode = settings_obj.get(
                    "ankidex.spriteMode",
                    settings_obj.get("pokedex_v2.spriteMode", "static"),
                )

            estimates_loading = False
            estimates = {
                "xp": 0,
                "encounters": 0,
                "catches": 0,
                "caught_list": [],
                "is_truncated": False,
                "total_reviews": 0,
                "simulated_reviews": 0,
                "cash": 0,
            }
            if pending_count > 0:
                estimates_loading = True

                trainer_card = getattr(mw, "trainer_card", None)
                ankimon_tracker_obj = getattr(mw, "ankimon_tracker_obj", None)

                def run_sim(col):
                    reviews_rows_thread = db.execute(
                        """SELECT id, revlog_id, card_id, ease, review_time, review_type, queued_at
                           FROM pending_mobile_battles
                           WHERE resolved = 0
                           ORDER BY id ASC LIMIT 105"""
                    ).fetchall()
                    reviews_list_thread = [
                        {
                            "id": r[0],
                            "revlog_id": r[1],
                            "card_id": r[2],
                            "ease": r[3],
                            "review_time": r[4],
                            "review_type": r[5],
                            "queued_at": r[6],
                        }
                        for r in reviews_rows_thread
                    ]
                    if pending_count > len(reviews_list_thread):
                        reviews_list_thread.extend([{"ease": 3}] * (pending_count - len(reviews_list_thread)))

                    from Ankimon.functions.mobile_sync import simulate_pending_mobile_battles
                    return simulate_pending_mobile_battles(
                        reviews_list_thread,
                        main_pokemon,
                        settings_obj,
                        trainer_card,
                        ankimon_tracker_obj,
                        ankimon_db=db,
                    )

                # Always synchronous in tests.
                sim_res = run_sim(None)
                estimates = {
                    "xp": sim_res["xp"],
                    "encounters": sim_res["encounters"],
                    "catches": sim_res.get("catches_count", len(sim_res["caught"])),
                    "caught_list": sim_res["caught"],
                    "is_truncated": sim_res.get("is_truncated", False),
                    "total_reviews": sim_res.get("total_reviews", 0),
                    "simulated_reviews": sim_res.get("simulated_reviews", 0),
                    "cash": sim_res.get("cash", 0),
                }
                estimates_loading = False
                battle_count = estimates["encounters"]

            return {
                "pending_count": pending_count,
                "pending_count_at_start": pending_count,
                "cards_per_round": cards_per_round,
                "battle_count": battle_count,
                "cap": 10000,
                "ease_breakdown": ease_breakdown,
                "estimates": estimates,
                "estimates_loading": estimates_loading,
                "auto_battle_mode": auto_battle_mode,
                "rare_catch_active": rare_catch_active,
                "main_pokemon_name": main_pokemon_name,
                "main_pokemon_level": main_pokemon_level,
                "main_pokemon_sprite": main_pokemon_sprite,
                "sprite_mode": sprite_mode,
                "team_status": self.getTeamStatus(),
            }
        except Exception as e:
            import traceback
            logger = getattr(mw, "logger", None)
            if logger:
                logger.log("error", f"getMobileStatus failed: {e}\n{traceback.format_exc()}")
            return {"error": str(e), "pending_count": 0, "pending_count_at_start": 0, "cap": 10000}

    def getMobileHistory(self) -> list:
        try:
            return _mw().ankimon_db.get_mobile_history(limit=500)
        except Exception:
            return []

    def clearMobileHistory(self) -> bool:
        try:
            return _mw().ankimon_db.clear_mobile_history()
        except Exception:
            return False

    def getTeamStatus(self) -> dict:
        mw = _mw()
        try:
            db = mw.ankimon_db
            team_rows = db.get_team()
            settings_obj = mw.settings_obj
            inactive = set(settings_obj.get("mobile.inactive_companions", [])) if settings_obj else set()
            from Ankimon.functions.sprite_functions import get_relative_sprite_path

            team_list = []
            for t in team_rows:
                ind_id = t.get("individual_id")
                if ind_id:
                    if hasattr(db, "get_pokemon_by_individual_id"):
                        data = db.get_pokemon_by_individual_id(ind_id)
                    else:
                        data = db.get_pokemon(ind_id)
                    if data:
                        from Ankimon.pyobj.pokemon_obj import PokemonObject
                        pkmn = PokemonObject(**data)
                        name = pkmn.display_name
                        level = data.get("level", 5)
                        shiny = bool(data.get("shiny", False))
                        gender = data.get("gender") or "N"
                        pkmn_id = data.get("id")
                        pkmn_type = data.get("type", ["Normal"])
                        if isinstance(pkmn_type, str):
                            pkmn_type = [pkmn_type]

                        sprite_path = get_relative_sprite_path(pkmn_id, shiny, gender, pkmn.name, "gif")
                        is_inactive = ind_id in inactive

                        team_list.append({
                            "individual_id": ind_id,
                            "name": name,
                            "level": level,
                            "sprite_path": sprite_path,
                            "type": pkmn_type,
                            "inactive": is_inactive,
                        })

            return {"team": team_list, "inactive": list(inactive)}
        except Exception as e:
            return {"team": [], "inactive": [], "error": str(e)}

    # --- actions -----------------------------------------------------------

    def dismissAll(self) -> dict:
        mw = _mw()
        try:
            db = mw.ankimon_db
            count_before = db.get_pending_mobile_count()
            with db._get_connection() as conn:
                conn.execute(
                    "UPDATE pending_mobile_battles SET resolved=1, resolved_at=? WHERE resolved=0",
                    (int(time.time() * 1000),)
                )
            from Ankimon.menu_buttons import update_mobile_badge
            update_mobile_badge(0)
            return {"dismissed": count_before, "success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def resolveAll(self) -> dict:
        mw = _mw()
        try:
            from Ankimon.functions.mobile_sync import resolve_all
            db = mw.ankimon_db
            settings_obj = mw.settings_obj
            tracker = getattr(mw, "ankimon_tracker_obj", None)
            trainer_card = getattr(mw, "trainer_card", None)
            main_pokemon = getattr(mw, "main_pokemon", None)
            day_cutoff = mw.col.sched.day_cutoff if (mw and getattr(mw, "col", None)) else 0

            return resolve_all(
                db=db,
                settings_obj=settings_obj,
                tracker=tracker,
                trainer_card=trainer_card,
                main_pokemon=main_pokemon,
                logger=getattr(mw, "logger", None),
                day_cutoff=day_cutoff,
            )
        except Exception as e:
            import traceback
            logger = getattr(mw, "logger", None)
            if logger:
                logger.log("error", f"resolveAll failed: {e}\n{traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    def resolveNext(self, companion_id: str = "") -> dict:
        mw = _mw()
        try:
            from Ankimon.functions.mobile_sync import resolve_next
            db = mw.ankimon_db
            settings_obj = mw.settings_obj
            tracker = getattr(mw, "ankimon_tracker_obj", None)
            trainer_card = getattr(mw, "trainer_card", None)
            main_pokemon = getattr(mw, "main_pokemon", None)
            day_cutoff = mw.col.sched.day_cutoff if (mw and getattr(mw, "col", None)) else 0

            res = resolve_next(
                companion_id=companion_id,
                db=db,
                settings_obj=settings_obj,
                tracker=tracker,
                trainer_card=trainer_card,
                main_pokemon=main_pokemon,
                logger=getattr(mw, "logger", None),
                day_cutoff=day_cutoff,
            )
            if isinstance(res, dict) and "current_pending_outcome" in res:
                outcome = res["current_pending_outcome"]
                if outcome:
                    outcome.update({
                        "main_pokemon": main_pokemon,
                        "trainer_card": trainer_card,
                        "settings_obj": settings_obj,
                    })
                self._current_pending_outcome = outcome
                return res["result"]
            return res
        except Exception as e:
            import traceback
            logger = getattr(mw, "logger", None)
            if logger:
                logger.log("error", f"resolveNext failed: {e}\n{traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    def commitReplayOutcome(self, choice: str) -> dict:
        mw = _mw()
        try:
            from Ankimon.functions.mobile_sync import commit_replay_outcome
            db = mw.ankimon_db
            settings_obj = mw.settings_obj
            trainer_card = getattr(mw, "trainer_card", None)
            main_pokemon = getattr(mw, "main_pokemon", None)
            achievements_dict = getattr(mw, "achievements_dict", None)
            logger = getattr(mw, "logger", None)
            outcome_data = getattr(self, "_current_pending_outcome", None)

            res = commit_replay_outcome(
                choice=choice,
                outcome_data=outcome_data,
                db=db,
                settings_obj=settings_obj,
                trainer_card=trainer_card,
                main_pokemon=main_pokemon,
                achievements_dict=achievements_dict,
                logger=logger,
            )
            if res.get("success"):
                self._current_pending_outcome = None
            return res
        except Exception as e:
            import traceback
            logger = getattr(mw, "logger", None)
            if logger:
                logger.log("error", f"commitReplayOutcome failed: {e}\n{traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    def toggleMobileCompanion(self, individual_id: str) -> dict:
        mw = _mw()
        try:
            settings_obj = mw.settings_obj
            inactive = settings_obj.get("mobile.inactive_companions", [])
            if not isinstance(inactive, list):
                inactive = []
            inactive = [str(x) for x in inactive]
            if individual_id in inactive:
                inactive.remove(individual_id)
            else:
                inactive.append(individual_id)
            settings_obj.set("mobile.inactive_companions", inactive)
            return {"inactive": inactive, "success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def triggerAnkiSync(self) -> dict:
        mw = _mw()
        try:
            if hasattr(mw, "onSync"):
                from aqt.qt import QTimer
                QTimer.singleShot(0, mw.onSync)
                return {"success": True}
            else:
                return {"success": False, "error": "mw.onSync not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
