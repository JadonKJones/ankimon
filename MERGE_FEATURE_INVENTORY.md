# MERGE_FEATURE_INVENTORY.md — the feature-preservation ledger

Every BRRRR_Experimental feature/fix, one row. **This is the anti-loss mechanism: a feature is
"preserved" only if it has a row here.** Stage B reads exactly one unit per `DEFERRED-TO-STAGE-B`
row and never creates a unit for a `DONE-IN-BASE` row.

## Ground truth & method
- **Git is ground truth.** Enumerated from `git diff a8abbd66..origin/BRRRR_Experimental` (the
  merge-base..exp tips) and `git log --no-merges`. The two in-repo docs
  (`main_vs_BRRRR_Experimental_diff_report.md`, `_BRRR_EXPERIMENTAL_FEATURE_LIST.md`) were treated
  as **non-exhaustive hints**; where a doc disagreed with the diff, the diff won and it is noted in
  the row's `doc↔diff` field. Enumeration + classification were produced by a fan-out of read-only
  git-grounded agents and **independently cross-checked** (see the partition assertion below).
- **Every LEAF feature appears with disposition `DEFERRED-TO-STAGE-B`.** `DONE-IN-BASE` rows are the
  shared scaffolding synthesised in Stage A. No feature is dropped; items with an open question also
  have an entry in `MERGE_NEEDS_REVIEW.md` (referenced inline as `NR-xx`).

## Partition guarantee (verified)
The union of all rows' **Source location(s)** is a **1:1 partition of the 165-file exp-only change
set**: `git diff --name-only a8abbd66..origin/BRRRR_Experimental` = 165 files; the 52 rows cover
exactly those 165 — **every exp file in exactly one row, none unassigned, none double-assigned**
(set-equality verified programmatically, and re-verified by an independent subagent — see
`MERGE_ARCH_MAP.md` §Cross-check). Reconstruct any feature with
`git diff a8abbd66..origin/BRRRR_Experimental -- <its Source location(s)>`.

## Counts
- **52** features/fixes · **31** LEAF · **16** MIXED · **5** SCAFFOLDING (by class).
- Stage-A disposition: **5** DONE-IN-BASE · **47** DEFERRED-TO-STAGE-B · 0 dropped.
- DONE-IN-BASE rows: **F10** (web-shell host+bridge), **F25** (thread-safe DB layer), **F33**
  (thread helpers) — plus **F09** (Comfey/Magby monthly challenges) and **F47** (XP-share
  friendship hook) which main already ships. *(IDs are the F-numbers in the rows below.)*

## How to re-fit a DEFERRED feature in Stage B (mechanical recipe)
1. `git diff a8abbd66..origin/BRRRR_Experimental -- <Source location(s)>` → the whole feature, nothing else.
2. For files that exist ONLY on exp: `git checkout origin/BRRRR_Experimental -- <path>` is safe.
   For files that already exist in the base (the ~34 co-edited modules): **port only the feature's
   hunks onto the base version** — three-way / re-author; never a wholesale checkout (it would revert
   main's seam wiring and guards).
3. Replace every direct `aqt.mw.*` the feature uses with the seam entrypoint named in
   **Seam-entrypoints-required** (see `MERGE_ARCH_MAP.md` for the full old→new map):
   `mw.ankimon_db→services.db`, `mw.settings_obj→services.settings`,
   `mw.main_pokemon/enemy_pokemon→services.*`, notifications→`services.ui.notify/warn/report_error`,
   state/sounds→`events.emit`, windows→`services.{test_window,evo_window,pokemon_pc,reviewer}`,
   web-shell screens→`host.mount(...)` on the base `WebShellHost`.
4. Re-apply any guard in **Notes / guards**. Prove with **Verification**; the base gate must stay green.

---

# Feature rows

### F01 — i18n leaf-feature string additions (all lang JSON)
- **ID:** F01
- **Source location(s):** `src/Ankimon/lang/ch_text.json`, `src/Ankimon/lang/cz_text.json`, `src/Ankimon/lang/de_text.json`, `src/Ankimon/lang/en_text.json`, `src/Ankimon/lang/es_latam_text.json`, `src/Ankimon/lang/fr_text.json`, `src/Ankimon/lang/it_text.json`, `src/Ankimon/lang/jp_text.json`, `src/Ankimon/lang/kr_text.json`, `src/Ankimon/lang/po_text.json`, `src/Ankimon/lang/sp_text.json`, `src/Ankimon/lang/setting_description.json`, `src/Ankimon/lang/setting_name.json`
- **Evidence tag:** [DIFF] · doc↔diff: exp reindented setting_name.json wholesale (4-space -> 2-space) producing a full-file edit-vs-edit conflict against main. Keys that MAIN already added (cp_label/bp_label/combat_power/battle_power, pokemon_about_to_evolve_friendship, evolution.timezone_auto/offset, trainer.cash_reward_amount/interval) are DONE-IN-BASE but exp duplicates them with divergent cash-economy text. exp-only leaf keys: battle.auto_catch_{legendary,mythical,ultra,starter,mega,gmax,regional,wishlist}, misc.active_region, controls.team_cycle_key, nature_chart_button, friendship_label/tooltip, bff_tooltip, evolve_now_button, badge_ready/wait_day/wait_night.
- **Target location (new org + seam):** Same paths under src/Ankimon/lang/ on main. Additive keys should be cherry-picked per owning Stage-B leaf, NOT bulk-merged, to avoid clobbering main's divergent values.
  - Seam wiring: Pure data files; no aqt.mw.* access. Strings are consumed via translator.py / gui_presenter text rendering on the seam. No seam entrypoint needed for the JSON itself.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** EV-yield/auto-catch leaf, encounter-overhaul regions leaf, evolution-overhaul leaf, team-builder/team-cycle leaf, cash-rewards leaf, nature-chart UI leaf
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** Pure data files; no aqt.mw.* access. Strings are consumed via translator.py / gui_presenter text rendering on the seam. No seam entrypoint needed for the JSON itself.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Edit-vs-edit collision with main on every lang file (both branches touched the tail of *_text.json and both setting_*.json). Only the leaf-specific keys travel to Stage B; the whitespace reformat of setting_name.json must be dropped and keys inserted surgically onto main's 4-space file. Bulk-adopting exp's files would regress main's cash-reward caps and drop evolution.friendship_time_enabled. | GUARDS-TO-REAPPLY: Preserve main's trainer.cash_reward_* descriptions (main caps Max 400 / 400¥ daily; exp caps Max 2000 / 100¥ per card — do NOT overwrite with exp economy text); Preserve main's evolution.friendship_time_enabled key (exp omits it)

### F02 — Translator.change_language() live language reload
- **ID:** F02
- **Source location(s):** `src/Ankimon/pyobj/translator.py`
- **Evidence tag:** [DIFF]
- **Target location (new org + seam):** src/Ankimon/pyobj/translator.py on main — append change_language(language) method (reloads translations from LANG_PATHS on the Language setting change).
  - Seam wiring: No aqt.mw.* access; pure file I/O + json.load. Would be invoked by the settings/Language-setting handler (settings plumbing on the seam) when the user changes language ID.
- **Class:** SCAFFOLDING
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: NR-03 (single-consumer; deferred, low risk)
- **Dependencies:** scaffolding already in base
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** No aqt.mw.* access; pure file I/O + json.load. Would be invoked by the settings/Language-setting handler (settings plumbing on the seam) when the user changes language ID.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Small additive reload helper (10 lines), no-newline-at-EOF. Generic plumbing but only a single consumer (Language setting); classify NEEDS-REVIEW since it is scaffolding-shaped but not yet depended on by 2+ leaves. Safe, low-risk to port. Missing trailing newline should be fixed on adoption.

### F03 — repository-analysis intelligence docs (21 files)
- **ID:** F03
- **Source location(s):** `repository-analysis/00-executive-overview.md`, `repository-analysis/01-architecture-map.md`, `repository-analysis/02-file-cards.md`, `repository-analysis/03-startup-and-control-flow.md`, `repository-analysis/04-source-of-truth.md`, `repository-analysis/05-risk-register.md`, `repository-analysis/06-conventions-observed.md`, `repository-analysis/07-glossary.md`, `repository-analysis/08-reading-order.md`, `repository-analysis/09-module-boundaries.md`, `repository-analysis/10-test-intelligence.md`, `repository-analysis/11-editing-playbook.md`, `repository-analysis/12-unknowns-and-questions.md`, `repository-analysis/13-core-file-appendix.md`, `repository-analysis/14-import-and-call-hotspots.md`, `repository-analysis/15-agent-handoff.md`, `repository-analysis/16-data-models-and-schemas.md`, `repository-analysis/17-config-surface-map.md`, `repository-analysis/18-event-hooks-and-side-effects.md`, `repository-analysis/19-ui-surface-to-logic-map.md`, `repository-analysis/20-persistence-deep-dive.md`
- **Evidence tag:** [DIFF] · doc↔diff: Docs describe exp's architecture (web-shell, direct aqt.mw.*, thread-safe SQLite), which CONTRADICTS main's service seam. Content would need rewrite to match main's org before it is accurate.
- **Target location (new org + seam):** New repository-analysis/ tree at repo root (absent on main). Ships as the 'repository-analysis docs' Stage-B leaf unit.
  - Seam wiring: Documentation only; no runtime code, no mw.* access, no seam wiring.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** scaffolding already in base
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** Documentation only; no runtime code, no mw.* access, no seam wiring.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Pure add relative to MB and main (main has none). Non-shipping meta-docs; low risk but describe the opposite (exp) architecture, so bringing them onto main as-is would document a codebase that does not exist on main. Defer as a documentation leaf.

### F04 — AGENTS.md agent/contributor guide (edit-vs-edit)
- **ID:** F04
- **Source location(s):** `AGENTS.md`
- **Evidence tag:** [DIFF] · doc↔diff: Both main (+126 lines) and exp (+373 lines) modified AGENTS.md from the same MB blob = direct edit-vs-edit conflict. exp text mirrors to .agents/AGENTS.md/.claude/GEMINI and references the 21 repository-analysis docs and direct mw.* access.
- **Target location (new org + seam):** AGENTS.md at repo root — main already has its own +126-line seam-oriented version; exp's +373-line version must be reconciled, not overwritten.
  - Seam wiring: Documentation; no code. exp version instructs agents to use direct aqt.mw / mw singleton and points at repository-analysis/, contradicting main's seam guidance.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: doc edit-vs-edit; reconcile onto main's seam guidance, do NOT adopt exp's direct-mw text
- **Dependencies:** repository-analysis docs leaf
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** Documentation; no code. exp version instructs agents to use direct aqt.mw / mw singleton and points at repository-analysis/, contradicting main's seam guidance.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Edit-vs-edit collision with main. exp's guide documents the web-shell/direct-mw architecture; adopting it verbatim would contradict main's decided seam architecture. Needs manual merge, not a straight port. | GUARDS-TO-REAPPLY: Preserve main's AGENTS.md service-seam guidance / harness references

### F05 — docs/encounter_overhaul_spec.md
- **ID:** F05
- **Source location(s):** `docs/encounter_overhaul_spec.md`
- **Evidence tag:** [DIFF]
- **Target location (new org + seam):** docs/encounter_overhaul_spec.md (new; absent on main). Ships with the encounter-overhaul (8-tier/Megas/Gmax/regions/catch-chains) Stage-B leaf.
  - Seam wiring: Spec document; no code or mw.* access.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** encounter-overhaul leaf
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** Spec document; no code or mw.* access.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Pure-add spec (217 lines) supporting a single leaf feature. Defer with that leaf; no standalone value on main.

### F06 — docs/updater_porting_guide.md
- **ID:** F06
- **Source location(s):** `docs/updater_porting_guide.md`
- **Evidence tag:** [DIFF] · doc↔diff: Guide documents exp's self-updater flow; must be validated against main's clone-protection guard which it may not account for.
- **Target location (new org + seam):** docs/updater_porting_guide.md (new; absent on main). Ships with the branch self-updater Stage-B leaf.
  - Seam wiring: Guide document; no code. Describes exp's updater which must respect main's git-clone update protection.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** branch self-updater leaf
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** Guide document; no code. Describes exp's updater which must respect main's git-clone update protection.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Pure-add doc (474 lines) tied to the self-updater leaf. Defer; ensure it does not encourage bypassing main's updater guard. | GUARDS-TO-REAPPLY: Cross-check against main's is_git_clone/git_pull_ff_only + MIN_UPDATER_VERSION guard before any updater code lands

### F07 — _BRRR_EXPERIMENTAL_FEATURE_LIST.md meta index
- **ID:** F07
- **Source location(s):** `src/Ankimon/_BRRR_EXPERIMENTAL_FEATURE_LIST.md`
- **Evidence tag:** [DIFF] · doc↔diff: Enumerates all exp leaf features; overlaps the repository-analysis set and is exp-branding meta.
- **Target location (new org + seam):** Not intended for main. This is exp's internal feature-tracking index; if kept at all it belongs as a transient planning doc, not shipped addon content.
  - Seam wiring: Documentation only; no code.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** scaffolding already in base
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** Documentation only; no code.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Pure-add (295 lines) meta list living inside the shipped addon dir (src/Ankimon/). Likely should NOT be ported to main at all; review/drop.

### F08 — .gitignore infra ignore entries
- **ID:** F08
- **Source location(s):** `.gitignore`
- **Evidence tag:** [DIFF] · doc↔diff: exp adds `.claude/` to .gitignore, directly contradicting main which keeps .claude/ skills tracked. Edit-vs-edit risk on this line.
- **Target location (new org + seam):** .gitignore at repo root — selectively add the SQLite WAL/shm + updater-state + simulator-output ignores; do NOT adopt the .claude/ ignore line.
  - Seam wiring: No code. Infra: ignores ankimon.db-shm/-wal, ankimonDEV.db(+shm/wal), update_state.json, tests/encounter_weighting_simulations outputs, .agents, __pycache__.
- **Class:** SCAFFOLDING
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: trivial infra ignores; bring with the feature that needs them (e.g. -wal/-shm with WAL, NR-05)
- **Dependencies:** thread-safe SQLite/WAL layer scaffolding, branch self-updater leaf, encounter simulator leaf
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** No code. Infra: ignores ankimon.db-shm/-wal, ankimonDEV.db(+shm/wal), update_state.json, tests/encounter_weighting_simulations outputs, .agents, __pycache__.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Mostly benign infra ignores that support the SQLite WAL scaffolding, updater state, and simulator. The `.claude/` line is a guard regression and must be dropped when porting. tests/encounter_weighting_simulations entries reference the encounter-simulator leaf (harness/ deleted on exp, present on main). | GUARDS-TO-REAPPLY: Do NOT ignore .claude/ — main tracks .claude/ skills as part of its infra; exp's `.claude/` gitignore line would untrack them (regression against main's guard)

### F09 — Monthly challenges Comfey/Magby data (already in main)
- **ID:** F09
- **Source location(s):** `assets/challenges/monthly_challenges.json`
- **Evidence tag:** [GIT] · doc↔diff: exp blob and main blob are byte-identical (both MB->exp and MB->main resolve to blob 98c6f940). No divergence.
- **Target location (new org + seam):** assets/challenges/monthly_challenges.json on main — already contains the identical June 2026 Comfey + July 2026 Magby entries.
  - Seam wiring: Data file; no mw.* access.
- **Class:** LEAF
- **Stage-A disposition:** DONE-IN-BASE
- **Dependencies:** scaffolding already in base
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** Data file; no mw.* access.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** exp's addition equals main's addition exactly — nothing to port. Confirms the monthly-challenge guard is already satisfied on main. | GUARDS-TO-REAPPLY: monthly-challenge June/July 2026 (Comfey, Magby) presence + None-safety already satisfied by main

### F10 — QWebEngine web-shell HOST frame + nav dropdown + QWebChannel live-update bridge
- **ID:** F10
- **Source location(s):** `src/Ankimon/ankimon_items_web/__init__.py`, `src/Ankimon/ankimon_items_web/nav-switcher.css`, `src/Ankimon/ankimon_items_web/nav-switcher.js`, `src/Ankimon/ankimon_items_web/LIVE_UPDATES.md`, `src/Ankimon/ankimon_items_web/shop_obj.py`
- **Evidence tag:** [DIFF] · doc↔diff: LIVE_UPDATES.md documents notify_stats_changed importing from .singletons and refresh_live_screen coalescing via QTimer.singleShot(0); matches shop_obj.py refresh_live_screen/_run_live_refresh. Doc frames the mechanism as reusable scaffolding for future Stats/Team live screens, consistent with SCAFFOLDING classification.
- **Target location (new org + seam):** New package src/Ankimon/ankimon_items_web/ on main. Only the HOST is Stage-A: the AnkimonItemsWeb QDialog shell (QWebEngineView + QStackedWidget load_screen/_on_screen_load_finished, geometry save/restore, show/hide/close lifecycle), NavBridge, and the refresh_live_screen/_run_live_refresh QWebChannel live-update dispatcher, plus nav-switcher.js/css and empty __init__.py. Wire the dialog construction and menu-open through ui_port/gui_presenter; per-screen data reads go through services.* rather than the bridges reading mw.* directly.
  - Seam wiring: shop_obj.py reaches gameplay via direct aqt.mw.*: mw.ankimon_db (NavBridge.getPendingReviewsCount, inventory/shop/settings reads), mw.settings_obj.set (TeamBridge.saveSpriteMode/saveCycleCount, SettingsBridge.saveSettings), mw.main_pokemon, mw.ankimon_tracker, window state. Live-update entrypoint is `from .singletons import notify_stats_changed` -> shop_obj.refresh_live_screen(). Seam target: DB reads -> services.get_db()/data accessors; settings writes -> a settings service; notify_stats_changed should live on the seam (events.py) not singletons.py. The host is scaffolding for Items/Shop/Settings/Profile/Team/Ankidex/Mobile screens.
- **Class:** MIXED
- **Stage-A disposition:** DONE-IN-BASE
  - Stage-A: Host FRAME + nav + QWebChannel live-update bridge extracted from exp shop_obj.py into NEW base package src/Ankimon/webshell/ (WebShellHost + LiveUpdateBridge; commit c2b16b44), ZERO screens — see NR-02/NR-04. The Shop/Items/Settings SCREENS + their bridges (shop_obj.py, shop/settings html/js/css, ItemsBridge etc.) remain DEFERRED leaves that mount via host.mount().
- **Dependencies:** singletons.py notify_stats_changed / reload-safe singletons (out-of-domain scaffolding), thread-safe SQLite layer mw.ankimon_db (out-of-domain scaffolding)
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** shop_obj.py reaches gameplay via direct aqt.mw.*: mw.ankimon_db (NavBridge.getPendingReviewsCount, inventory/shop/settings reads), mw.settings_obj.set (TeamBridge.saveSpriteMode/saveCycleCount, SettingsBridge.saveSettings), mw.main_pokemon, mw.ankimon_tracker, window state. Live-update entrypoint is `from .singletons import notify_stats_changed` -> shop_obj.refresh_live_screen(). Seam target: DB reads -> services.get_db()/data accessors; settings writes -> a settings service; notify_stats_changed should live on the seam (events.py) not singletons.py. The host is scaffolding for Items/Shop/Settings/Profile/Team/Ankidex/Mobile screens.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** shop_obj.py is 2114 lines and genuinely MIXED: it is the shared HOST (scaffolding) but also inlines leaf handlers for Shop (handle_buy/handle_reroll/get_inventory_data/ItemsBridge), Settings (get_settings_data/handle_save_settings/SettingsBridge), Team, Trainer/Profile, Mobile-sync, and Ankidex — most belonging to OTHER domains. NEEDS-REVIEW because Stage A must extract ONLY host+nav+live-bridge and defer every embedded screen handler to Stage B. File does not exist on main (no edit-vs-delete collision). MobileBridge/mobile_sync churn (fd1e2488..e205b25c) is out-of-domain leaf coupling. | GUARDS-TO-REAPPLY: service seam (route mw.ankimon_db / mw.settings_obj through services/events instead of the bridges' direct mw.* access); Developer Mode gating (is_dev_mode import in shop_obj is a leaf gate, keep behind seam)

### F11 — Web Shop screen (daily shop / reroll / buy UI + PokemonShopManager backend)
- **ID:** F11
- **Source location(s):** `src/Ankimon/ankimon_items_web/shop.html`, `src/Ankimon/ankimon_items_web/shop.css`, `src/Ankimon/ankimon_items_web/shop.js`, `src/Ankimon/pyobj/ankimon_shop.py`
- **Evidence tag:** [DIFF]
- **Target location (new org + seam):** src/Ankimon/ankimon_items_web/shop.{html,css,js} as a Stage-B web screen rendered inside the Stage-A host. pyobj/ankimon_shop.py (PokemonShopManager) stays on main but its mw.ankimon_db access routes through services. The one small piece of real scaffolding value here is the _tm_pool_cache in-memory cache on get_tm_pool.
  - Seam wiring: ankimon_shop.py uses direct mw.ankimon_db (get_user_data('todays_shop'), buy_item flow) — route via services db accessor. The exp change is tiny: black-style wrapping plus a _tm_pool_cache memoization of get_tm_pool (immutable learnset, hot path). Shop UI actions reach backend via shop_obj.ItemsBridge.buy/reroll -> handle_buy/handle_reroll (host feature).
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Web-shell HOST frame + nav + live-update bridge, thread-safe SQLite mw.ankimon_db
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** ankimon_shop.py uses direct mw.ankimon_db (get_user_data('todays_shop'), buy_item flow) — route via services db accessor. The exp change is tiny: black-style wrapping plus a _tm_pool_cache memoization of get_tm_pool (immutable learnset, hot path). Shop UI actions reach backend via shop_obj.ItemsBridge.buy/reroll -> handle_buy/handle_reroll (host feature).
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** ankimon_shop.py NOT co-edited on main (no collision); exp diff ~16 lines, mostly reformatting plus the get_tm_pool cache. Shop is a standalone user-facing screen = one Stage-B unit. The _tm_pool_cache memoization is a borderline scaffolding micro-optimization but ships with the leaf; keep with shop. | GUARDS-TO-REAPPLY: service seam for mw.ankimon_db; XP-share None-checks if buy/give paths touch companion/xp_share

### F12 — Items/Bag window web seam (dispatch_use) + held-item lifecycle
- **ID:** F12
- **Source location(s):** `src/Ankimon/pyobj/item_window.py`, `tests/test_held_items.py`
- **Evidence tag:** [GIT] · doc↔diff: item_window.py is edit-vs-edit: main MB..main added trigger-2 held-item evolutions + singleton held_item sync (17 lines); exp MB..exp is 287+/123- but largely black reformatting plus is_alive guards, dispatch_use, and its own singleton held_item sync. exp did NOT include main's trigger-2 held_item_id evolution branch — reconcile so main's guard survives.
- **Target location (new org + seam):** src/Ankimon/pyobj/item_window.py already exists on main. The web Items/Bag leaf adds dispatch_use(item_name,item_type)->result-dict seam method (returns toast payload for the web Items screen) plus is_alive() liveness guards. On main-org, dispatch_use should live behind the service seam / a presenter so the web host calls it without touching aqt.mw. test_held_items.py -> tests/ under main's harness/ test infra.
  - Seam wiring: item_window.py uses direct aqt.mw.*: mw.ankimon_db (update_item_quantity, get/save pokemon), mw.geometry() (window centering), and `from ..singletons import pokemon_pc/get_evo_window`. Route mw.ankimon_db via services, mw.geometry via ui_port. dispatch_use is the seam entrypoint the web Items screen (ItemsBridge.useItem in shop_obj) invokes instead of driving the native Qt widget.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Web-shell HOST frame (ItemsBridge dispatches into dispatch_use), harness/ test infra (test_held_items.py relies on it existing on main; exp deleted harness/)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** item_window.py uses direct aqt.mw.*: mw.ankimon_db (update_item_quantity, get/save pokemon), mw.geometry() (window centering), and `from ..singletons import pokemon_pc/get_evo_window`. Route mw.ankimon_db via services, mw.geometry via ui_port. dispatch_use is the seam entrypoint the web Items screen (ItemsBridge.useItem in shop_obj) invokes instead of driving the native Qt widget.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** EDIT-vs-EDIT collision on item_window.py (both branches modified; not edit-vs-delete). test_held_items.py is exp-only new, 341 lines, self-mocks aqt (does not use main harness helpers), covers held_item give/remove, main_pokemon singleton sync, and web equipped-items serialization/unequip via AnkimonItemsWeb — so it also validates the host feature. NEEDS-REVIEW for the guard-preserving merge of the two item_window edits. | GUARDS-TO-REAPPLY: MAIN-SIDE COLLISION: main added trigger_id=='2' held-item (trade) evolutions (Metal Coat/King's Rock/etc via row.get('held_item_id')) AND main_pokemon.held_item singleton sync in give-held-item path — exp's reformatted Evolve_Fossil/Check_Heal_Item region must NOT drop main's trigger-2 evolution logic; XP-share None-checks (held-item give/remove touches companion held_item); service seam for mw.ankimon_db and mw.geometry

### F13 — Web Settings screen (schema-driven settings UI)
- **ID:** F13
- **Source location(s):** `src/Ankimon/ankimon_items_web/settings.html`, `src/Ankimon/ankimon_items_web/settings.css`, `src/Ankimon/ankimon_items_web/settings.js`, `src/Ankimon/ankimon_items_web/settings_schema.py`
- **Evidence tag:** [DIFF]
- **Target location (new org + seam):** src/Ankimon/ankimon_items_web/settings.{html,css,js} + settings_schema.py as a Stage-B web Settings screen inside the host. settings_schema.GROUPS is the render contract consumed by shop_obj.get_settings_data/handle_save_settings; on main-org, settings read/write must go through the settings service, not mw.settings_obj directly.
  - Seam wiring: settings_schema.py is pure data (GROUPS structure, chip_group keys like battle.auto_catch_*). No direct mw.* itself, but the screen it drives round-trips through shop_obj SettingsBridge.getSettings/saveSettings which call mw.settings_obj — those belong on the settings service seam. New settings keys (per-tier auto-catch, developer mode, spriteMode, team_cycle_count) are settings/schema plumbing that auto-catch/team leaves depend on.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Web-shell HOST frame + nav, settings_obj / settings schema plumbing (out-of-domain scaffolding)
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** settings_schema.py is pure data (GROUPS structure, chip_group keys like battle.auto_catch_*). No direct mw.* itself, but the screen it drives round-trips through shop_obj SettingsBridge.getSettings/saveSettings which call mw.settings_obj — those belong on the settings service seam. New settings keys (per-tier auto-catch, developer mode, spriteMode, team_cycle_count) are settings/schema plumbing that auto-catch/team leaves depend on.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** settings_schema.py explicitly mirrors legacy QMainWindow settings_window.py as data for the web shell. The schema itself (auto-catch tier keys, dev-mode) borders on settings-plumbing scaffolding that other leaves (encounter auto-catch, team, developer-mode gating) depend on, but the screen files (html/css/js) are a standalone Settings screen = one Stage-B unit; kept together as LEAF. Files absent on main (no collision). | GUARDS-TO-REAPPLY: service seam for mw.settings_obj read/write; verify Developer Mode key does not bypass main guards

### F14 — Mobile & Web Reviews sync engine (backend)
- **ID:** F14
- **Source location(s):** `src/Ankimon/functions/mobile_sync.py`, `tests/test_mobile_sync.py`, `tests/test_mobile_replay.py`, `tests/test_mobile_auto_resolve.py`
- **Evidence tag:** [DIFF] · doc↔diff: _BRRR_EXPERIMENTAL_FEATURE_LIST.md references mobile feature; diff confirms a single ~2087-line engine plus 3 test files added on top of MB (no main equivalent). No contradiction found.
- **Target location (new org + seam):** src/Ankimon/functions/mobile_sync.py (net-new module, no main counterpart). On main's org it must route all mw.* access through the service seam (services.py/core.py) instead of `from aqt import mw`; the async resolve path via QueryOp should be mediated through hooks.py/gui_presenter rather than importing aqt.operations directly. Tests belong under top-level harness/tests infra on main.
  - Seam wiring: Heavy DIRECT aqt.mw.* access to replace with seam entrypoints: `from aqt import mw; db = mw.ankimon_db` (record_desktop_review L23-24, _attribute_xp_and_evs L1931-1932) -> services DB accessor; `mw.col.sched.day_cutoff` (L674-676) -> scheduler seam; `mw.achievements_dict` (L1311,L1470) and `mw.main_pokemon` (L1964,L2078) -> services state; `mw.logger`/`log_and_showinfo`/`game_log` (L382,L1976-1980) -> ui_port/logger seam; QueryOp+mw async boot (L1857-1869) -> hooks.py mediated async. Also imports sibling modules `..reviewer_ui._collected_pokemon_ids` (L1313,L1822), `.drawing_utils.tooltipWithColour`, `save_caught_pokemon`, `get_evo_window` — all must resolve on main's tree.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** thread-safe SQLite layer (mw.ankimon_db ConnectionWrapper / watermark table scaffolding), reload-safe singletons + async QueryOp boot scaffolding, ankimon_sync.py MobileBridge (D-sync/web-shell bridge), encounter overhaul / EV-yield leaf helpers (save_caught_pokemon, get_evo_window, MovePickerDialog path), reviewer_ui _collected_pokemon_ids
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** Heavy DIRECT aqt.mw.* access to replace with seam entrypoints: `from aqt import mw; db = mw.ankimon_db` (record_desktop_review L23-24, _attribute_xp_and_evs L1931-1932) -> services DB accessor; `mw.col.sched.day_cutoff` (L674-676) -> scheduler seam; `mw.achievements_dict` (L1311,L1470) and `mw.main_pokemon` (L1964,L2078) -> services state; `mw.logger`/`log_and_showinfo`/`game_log` (L382,L1976-1980) -> ui_port/logger seam; QueryOp+mw async boot (L1857-1869) -> hooks.py mediated async. Also imports sibling modules `..reviewer_ui._collected_pokemon_ids` (L1313,L1822), `.drawing_utils.tooltipWithColour`, `save_caught_pokemon`, `get_evo_window` — all must resolve on main's tree.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Pure exp-only addition (MB:no, MAIN:no) -> NO edit-vs-delete collision. This is a standalone Stage-B leaf (mobile-review sync engine): it simulates offline/mobile-synced reviews into battles, attributes XP/EVs, heals companions, triggers evolutions/level-ups/catches. Runs work on background threads (in_bulk_resolve flag suppresses tooltips) then commits via QueryOp — porting must preserve thread-safety and route mw.* through the seam to avoid cross-thread mw access. Defer entirely; do not bring across in Stage A. | GUARDS-TO-REAPPLY: XP-share None-checks (xp_share_gain_exp / trade-away); encounter level-cap NameError guard (#402); EV-yield None/limit hardening (limit_ev_yield, e002f0f6)

### F15 — Mobile & Web Reviews web-shell UI screens
- **ID:** F15
- **Source location(s):** `src/Ankimon/ankimon_mobile_web/mobile.html`, `src/Ankimon/ankimon_mobile_web/mobile.js`, `src/Ankimon/ankimon_mobile_web/mobile.css`, `src/Ankimon/ankimon_mobile_web/history.html`, `src/Ankimon/ankimon_mobile_web/history.js`
- **Evidence tag:** [DIFF] · doc↔diff: None. All 5 assets are exp-only additions (MB:no, MAIN:no) totaling ~3246 lines.
- **Target location (new org + seam):** src/Ankimon/ankimon_mobile_web/ (net-new web-shell screen dir). On main it would be a new QWebEngine screen served by the web-shell HOST scaffolding, reusing the shared nav-switcher/shop.css assets from ankimon_items_web.
  - Seam wiring: Front-end HTML/JS/CSS: no Python mw.* access. Communicates to backend over the QWebChannel bridge (MobileBridge in ankimon_sync.py). No seam rewrite needed in these files themselves; wiring happens in the bridge/host layer.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** QWebEngine web-shell HOST/frame + QWebChannel bridge scaffolding, shared nav-switcher.css + shop.css from ankimon_items_web (referenced via ../ankimon_items_web/), Mobile & Web Reviews sync engine (backend) feature
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** Front-end HTML/JS/CSS: no Python mw.* access. Communicates to backend over the QWebChannel bridge (MobileBridge in ankimon_sync.py). No seam rewrite needed in these files themselves; wiring happens in the bridge/host layer.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Pure exp-only addition -> no edit-vs-delete collision. mobile.html hard-references shared web-shell assets (../ankimon_items_web/shop.css, nav-switcher.css) and uses shell-mode/sidebar markup identical to other web screens, confirming dependency on the web-shell scaffolding (owned by a sibling domain). This is the UI half of the mobile-reviews leaf; defer with the backend engine.

### F16 — Ankidex (Pokédex V2) HTML5/QtWebEngine SPA + removal of native pokedex
- **ID:** F16
- **Source location(s):** `src/Ankimon/ankidex/abilities.json`, `src/Ankimon/ankidex/ankidex.css`, `src/Ankimon/ankidex/ankidex.html`, `src/Ankimon/ankidex/ankidex.js`, `src/Ankimon/ankidex/ankidex_obj.py`, `src/Ankimon/ankidex/pokedex_flavor.json`, `src/Ankimon/pokedex/pokedex.html`, `src/Ankimon/pokedex/pokedex_obj.py`, `src/Ankimon/pokedex/pokemon_names.json`
- **Evidence tag:** [DIFF] · doc↔diff: Matches arch context (exp deletes old pokedex/ and layers Ankidex web SPA). No discrepancy.
- **Target location (new org + seam):** New Stage-B unit under src/Ankimon/ankidex/ on main; the QtWebEngine Ankidex window (ankidex_obj.Ankidex) must mount on main's decoupled QWebEngine web-shell HOST + QWebChannel bridge (ui_port/gui_presenter) rather than instantiating its own QDialog/QWebEngineView with direct mw access. Native src/Ankimon/pokedex/ stays on main until Ankidex is fully wired and its launch entrypoint swapped.
  - Seam wiring: ankidex_obj.py accesses mw directly: `db = mw.ankimon_db` (get_ankidex_data), `mw.settings_obj.get('misc.active_region')`, viewMode/sortMode/spriteMode reads from mw.settings_obj, and mw.settings_obj.set('ankidex.<key>', val) in save_preferences. DB reads should go through the services/database seam (ankimon_db provider), settings reads/writes through the settings seam / ui_port; runJavaScript state callback should route through gui_presenter.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** QWebEngine web-shell HOST/frame + QWebChannel live-update bridge (scaffolding), thread-safe SQLite layer (mw.ankimon_db), settings/schema keys ankidex.* and pokedex_v2.* (viewMode/sortMode/spriteMode), encounter_data.REGIONAL_FORMS + misc.active_region (from encounter overhaul domain)
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** ankidex_obj.py accesses mw directly: `db = mw.ankimon_db` (get_ankidex_data), `mw.settings_obj.get('misc.active_region')`, viewMode/sortMode/spriteMode reads from mw.settings_obj, and mw.settings_obj.set('ankidex.<key>', val) in save_preferences. DB reads should go through the services/database seam (ankimon_db provider), settings reads/writes through the settings seam / ui_port; runJavaScript state callback should route through gui_presenter.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Deletion of src/Ankimon/pokedex/{pokedex.html,pokedex_obj.py,pokemon_names.json} is NOT an edit-vs-delete collision: main leaves those 3 files byte-identical to MB (0-line MB..main diff). Deletion is safe only after Ankidex replaces the native pokedex launch. pokedex_flavor.json (~151KB) and abilities.json are pure data assets for the SPA. Standalone user-facing screen => LEAF, one Stage-B unit. | GUARDS-TO-REAPPLY: route mw.ankimon_db through service seam (thread-safe SQLite provider); route mw.settings_obj get/set through settings seam / ui_port; preserve native pokedex/ launch path until Ankidex entrypoint is swapped (avoid orphaning existing pokedex menu action)

### F17 — Evolution overhaul: region-aware level evolutions + move-based manual evolutions, form data, and PC-box caught-state fix
- **ID:** F17
- **Source location(s):** `src/Ankimon/functions/pokedex_functions.py`, `src/Ankimon/data_files/pokedex.json`, `tests/test_pokedex_evolution_bug.py`
- **Evidence tag:** [DIFF] · doc↔diff: Caching scaffolding exp adds to pokedex_functions is already present verbatim on main (MB..main = 675 insertions incl. _load_* caches), so that portion is DONE-IN-BASE, not new exp work — file is co-edited and will conflict heavily. pokedex.json MB..main diff is trivial (4 lines); exp diverges by ~1240 lines (Pikachu forme renames, changesFrom, megas/gmax/regional data).
- **Target location (new org + seam):** src/Ankimon/functions/pokedex_functions.py already exists on main WITH the in-memory caching layer (DONE-IN-BASE). Stage-B should layer ONLY the exp-unique evolution logic (check_evolution_by_item / check_evolution_for_pokemon region-branching, get_time_of_day, move-based manual evolution) onto main's version, keeping main's services.ui.warn seam. pokedex.json regional/mega/gmax form rows land in src/Ankimon/data_files/pokedex.json; the evolution regression test lands in tests/ (new on main).
  - Seam wiring: exp REVERTS main's seam call: main `services.ui.warn(...)` -> exp `showWarning(...)` in find_details_move — this must be re-routed back to the seam. New leaf logic reads mw.settings_obj.get('misc.active_region') (guarded with hasattr checks) and mw.ankimon_db directly; route active_region + db through settings/database seams.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** in-memory pokedex caching layer (already DONE-IN-BASE on main), settings key misc.active_region (encounter overhaul / regions), thread-safe SQLite AnkimonDB (mark_as_caught) used by the test, pokedex.json form data (co-located here)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp REVERTS main's seam call: main `services.ui.warn(...)` -> exp `showWarning(...)` in find_details_move — this must be re-routed back to the seam. New leaf logic reads mw.settings_obj.get('misc.active_region') (guarded with hasattr checks) and mw.ankimon_db directly; route active_region + db through settings/database seams.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** test_pokedex_evolution_bug.py validates that pre-evolved caught states persist across manual PC evolutions (Bulbasaur->Ivysaur->Venusaur via AnkimonDB.mark_as_caught) — a gameplay/DB test, ties this feature to the PC Box rework domain. Region-aware + move-based evolution is a LEAF (evolution overhaul), but the file also carries done-in-base caching scaffolding => MIXED. Heavy co-edit with main + seam revert make the merge non-trivial; flag for careful 3-way rather than wholesale take. | GUARDS-TO-REAPPLY: re-apply main's services.ui.warn seam (undo exp's showWarning revert in find_details_move); route mw.settings_obj.get('misc.active_region') through settings seam; route mw.ankimon_db through thread-safe SQLite service seam; preserve main's caching layer (_load_*_cache / clear_pokedex_caches) — do NOT overwrite with exp copy

### F18 — Web Profile & Team screens (unified web-shell SPA)
- **ID:** F18
- **Source location(s):** `src/Ankimon/ankimon_profile_web/__init__.py`, `src/Ankimon/ankimon_profile_web/profile.css`, `src/Ankimon/ankimon_profile_web/profile.html`, `src/Ankimon/ankimon_profile_web/profile.js`, `src/Ankimon/ankimon_profile_web/profile_data.py`, `src/Ankimon/ankimon_profile_web/team.html`, `src/Ankimon/ankimon_profile_web/team.js`, `tests/test_profile_pokedex_completion.py`
- **Evidence tag:** [DIFF] · doc↔diff: None. Docstrings/commits match the diff (SPA screens + profile_data provider added net-new).
- **Target location (new org + seam):** New feature package under main's org, e.g. src/Ankimon/ankimon_profile_web/, but its data provider (profile_data.py) must route mw.ankimon_db / mw.col / mw.main_pokemon through main's service seam (services.py/core.py) instead of `from aqt import mw`. The Profile and Team HTML/JS screens are individual web-shell SCREENS, not the shell host, so they are one Stage-B leaf each riding on the (separately-owned) QWebEngine web-shell HOST + QWebChannel bridge scaffolding.
  - Seam wiring: profile_data.py imports `from aqt import mw` and makes ~15 direct calls: mw.ankimon_db.get_team/get_pokemon/get_all_pokemon/get_main_pokemon/set_main_pokemon/save_team/get_pokemons_by_individual_ids and raw mw.ankimon_db.execute(SQL), plus mw.main_pokemon and update_main_pokemon(mw.main_pokemon). All of these must be replaced by seam entrypoints (a ProfileService/TeamService in services.py backed by the SQLite layer) rather than reaching aqt.mw directly. __init__.py registers the screens with the web-shell host and shared dropdown-nav module.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** QWebEngine web-shell HOST/frame + nav + QWebChannel bridge (scaffolding, other domain), thread-safe SQLite AnkimonDB layer (scaffolding, other domain), pokedex caching layer (format_lore_name/_load_pokedex_cache/search_pokedex), shared dropdown-nav CSS/switcher module (26b5727d/00a0530e)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** profile_data.py imports `from aqt import mw` and makes ~15 direct calls: mw.ankimon_db.get_team/get_pokemon/get_all_pokemon/get_main_pokemon/set_main_pokemon/save_team/get_pokemons_by_individual_ids and raw mw.ankimon_db.execute(SQL), plus mw.main_pokemon and update_main_pokemon(mw.main_pokemon). All of these must be replaced by seam entrypoints (a ProfileService/TeamService in services.py backed by the SQLite layer) rather than reaching aqt.mw directly. __init__.py registers the screens with the web-shell host and shared dropdown-nav module.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** All 7 profile_web paths are net-new (absent on MB and main). profile_data.py is a pure-Python data provider heavily coupled to mw.ankimon_db and is unit-tested by test_profile_pokedex_completion.py (loads AnkimonDB + ProfileData dynamically, mocks mw), which aligns the profile dex-completion count with the Ankidex count (commit 3658c5e2). team.js/team.html also gained animated-sprite toggle and customizable rotation-cycle limits (leaf sub-features). Deferred whole as leaf screens; only the shell host + bridge they sit on are scaffolding. | GUARDS-TO-REAPPLY: monthly-challenge / pokedex-completion None-safety when computing dex counts

### F19 — Team Deck-Overview grid backed by AnkimonDB
- **ID:** F19
- **Source location(s):** `src/Ankimon/gui_classes/overview_team.py`
- **Evidence tag:** [DIFF] · doc↔diff: Module docstring claims hook registration is 'now handled centrally in __init__.py' — verify that __init__ registration actually exists on exp; the diff only shows removal of the import-time registration block here, so the doc asserts a relocation that must be confirmed against __init__.py (potential doc-vs-diff gap).
- **Target location (new org + seam):** src/Ankimon/gui_classes/overview_team.py on main, but the new DB read-path must go through the SQLite service seam and the import-time hook registration (removed by exp, now expected in __init__.py) must be reconciled with main's own MB..main edits to this same file. CO-EDITED: main changed this file (+43/-31 vs MB) independently, so this is a real merge-conflict surface.
  - Seam wiring: Uses `from aqt import gui_hooks, mw` and reads mw.ankimon_db.get_team/get_pokemon/get_all_pokemon plus mw.settings_obj.get('gui.team_deck_view'). Should resolve team via a TeamService seam rather than direct mw.ankimon_db; hook gating on gui.team_deck_view moved out of import-time into central __init__ registration.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** thread-safe SQLite AnkimonDB layer (scaffolding, other domain), pokedex caching (format_lore_name), sprite get_sprite_path signature change (now takes name arg)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** Uses `from aqt import gui_hooks, mw` and reads mw.ankimon_db.get_team/get_pokemon/get_all_pokemon plus mw.settings_obj.get('gui.team_deck_view'). Should resolve team via a TeamService seam rather than direct mw.ankimon_db; hook gating on gui.team_deck_view moved out of import-time into central __init__ registration.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** exp rewrote load_pokemon_team to prefer AnkimonDB with JSON fallback and removed the import-time gui_hooks registration. Because main ALSO edited overview_team.py vs MB, this is an edit-vs-edit collision needing manual reconciliation; classify as team-overview leaf, but the DB layer and central hook-registration it depends on are scaffolding. get_sprite_path now called with an extra name positional arg — ensure main's sprite seam matches. | GUARDS-TO-REAPPLY: defensive isinstance/None fallbacks for legacy JSON (a8c2047c) so the grid never crashes the Deck Browser

### F20 — Profile-open startup: mobile-sync detection, async connectivity & cache-clear hooks
- **ID:** F20
- **Source location(s):** `src/Ankimon/profile_hooks.py`, `tests/test_profile_hooks.py`
- **Evidence tag:** [DIFF] · doc↔diff: Commit history attributes most changes to mobile + startup-perf work; the cache-clear-on-close and race-condition-fallback pieces are not obviously described but are present in the diff — reconcile before porting.
- **Target location (new org + seam):** src/Ankimon/profile_hooks.py on main. HARD COLLISION: main independently rewrote this same file (+43/-31 vs MB), converting connectivity to mw.taskman.run_in_background, while exp converted it to aqt.operations.QueryOp and injected mobile-sync watermark bootstrap + cache-clear-on-close. Must be split: the profile_will_close cache-clear hook (calls clear_pokedex_caches/clear_learnset_cache/clear_encounter_cache) is caching-layer scaffolding and can land on main's seam; the mobile watermark/session/badge bootstrap is a mobile-review-sync LEAF and must be deferred.
  - Seam wiring: Direct `from aqt import gui_hooks, mw`; direct calls: mw.ankimon_db.get_mobile_watermark/set_mobile_watermark/get_pending_mobile_count, mw.col.db.scalar('SELECT MAX(id) FROM revlog'), mw.online_connectivity assignment, mw.col None-check race-condition fallback, and QueryOp(parent=mw). These should be mediated: connectivity via main's existing test_online_connectivity + taskman/QueryOp seam, mobile counts via a MobileSyncService, revlog access via col seam.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** mobile-review sync engine (functions.mobile_sync, menu_buttons.update_mobile_badge) — LEAF, in-memory caching layer (clear_pokedex/learnset/encounter caches) — scaffolding, async QueryOp boot / startup sequence (14f42873) — scaffolding
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** Direct `from aqt import gui_hooks, mw`; direct calls: mw.ankimon_db.get_mobile_watermark/set_mobile_watermark/get_pending_mobile_count, mw.col.db.scalar('SELECT MAX(id) FROM revlog'), mw.online_connectivity assignment, mw.col None-check race-condition fallback, and QueryOp(parent=mw). These should be mediated: connectivity via main's existing test_online_connectivity + taskman/QueryOp seam, mobile counts via a MobileSyncService, revlog access via col seam.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** test_profile_hooks.py (net-new) tests the already-loaded vs not-yet-loaded profile-hook registration and the mobile watermark/badge bootstrap with mocked mw. Because main rewrote profile_hooks.py in parallel, DO NOT wholesale-take exp's version: cherry-pick the cache-clear scaffolding hook, defer the mobile bootstrap, and keep main's connectivity/monthly/changelog structure. Flagged NEEDS-REVIEW for the collision and the leaf-vs-scaffolding split within one file. | GUARDS-TO-REAPPLY: monthly-challenge None-safety around check_and_award_monthly_pokemon (must stay gated on connectivity); branch-update / changelog guards (check_branch_update / check_and_show_changelog) preserved and still gated on connected+ssh; must not drop main's 2.02-E/2.03 changelog wiring during merge

### F21 — Removal of native Qt AchievementsDialog (superseded by web shell)
- **ID:** F21
- **Source location(s):** `src/Ankimon/pyobj/achievements_dialog.py`
- **Evidence tag:** [GIT] · doc↔diff: Commit 3c7b6776 claims the dialog is 'fully unreferenced' — TRUE on exp but FALSE on main, where menu_buttons.py still imports and instantiates it. Classic edit-vs-delete divergence.
- **Target location (new org + seam):** On main this file still EXISTS and is actively imported/instantiated in src/Ankimon/menu_buttons.py (lines 111-117: `from .pyobj.achievements_dialog import AchievementsDialog`). exp deletes it as dead code after routing the menu entry to the web Profile badge. Do NOT delete on main until/unless the web Profile screen replaces the achievements entry point.
  - Seam wiring: No seam concern in the deleted file itself; the concern is the caller menu_buttons.py on main still constructs AchievementsDialog and sets mw._achievements_dialog. Deleting the module would break that call site.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: edit-vs-delete superseded by web Profile; needs delete-AUTHORIZATION in MERGE_ARCH_MAP.md
- **Dependencies:** Web Profile & Team screens (the web replacement that made this dead on exp)
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** No seam concern in the deleted file itself; the concern is the caller menu_buttons.py on main still constructs AchievementsDialog and sets mw._achievements_dialog. Deleting the module would break that call site.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** EDIT-VS-DELETE COLLISION: pure -63-line deletion on exp vs a still-live caller on main. This deletion is a leaf-cleanup that only becomes safe once the web Profile screen is adopted on main and menu_buttons.py is re-routed; taking the delete now (Stage A) would be an unsafe regression. Defer/review. | GUARDS-TO-REAPPLY: preserve main's working Achievements menu entry (menu_buttons.py) — a bare delete regresses it

### F22 — Encounter Overhaul (8-tier + Megas/Gmax + Regions + Catch-chains + EP/Mastery + CP scaling)
- **ID:** F22
- **Source location(s):** `src/Ankimon/functions/encounter_functions.py`, `src/Ankimon/functions/encounter_data.py`, `src/Ankimon/functions/encounter.txt`, `src/Ankimon/data_files/pokemon.csv`, `src/Ankimon/functions/battle_functions.py`, `tests/test_encounter_functions.py`, `tests/test_encounter_overhaul.py`, `tests/test_cp_formula.py`, `tests/encounter_weighting_simulations/test_encounter_simulation.py`, `tests/encounter_weighting_simulations/test_overhaul_simulation.py`
- **Evidence tag:** [DIFF] · doc↔diff: Doc lists 'encounter overhaul (8-tier, Megas/Gmax, regions, catch-chains)+EP/Mastery' as a leaf — matches diff. Extra co-changes not in doc: CP-formula rescale (test_cp_formula cpm cap 0.84->2.45) and battle_functions display_name migration ride along with this leaf. pokemon.csv dragonite-mega height 55->22 looks like an unrelated data correction/possible regression bundled in.
- **Target location (new org + seam):** src/Ankimon/functions/encounter_functions.py + encounter_data.py on main's seam (module already migrated to `from ..services import services` / `from ..events import events`); data tables (REGIONAL_FORMS/MEGA_AND_SPECIAL/gen lists) stay in encounter_data.py; encounter.txt prerequisite-chain data + pokemon.csv mega/regional rows stay as data assets; battle_functions display_name rendering stays but must consume a PokemonObject.display_name property (added out-of-domain in pyobj/pokemon_obj.py). This whole leaf is a Stage-B unit, NOT part of Stage-A scaffolding.
  - Seam wiring: exp REVERTED main's seam: encounter_functions imports `from aqt import mw` and hits `mw.ankimon_db.get_all_pokemon_ids/get_all_pokemon/get_user_data/set_user_data` (pity trackers, EP mastery) and `getattr(mw,'main_pokemon')` directly (~21 mw refs). Main's encounter_functions instead uses `services` + `events`; on re-application every `mw.ankimon_db.*` must route through the services DB registry and `mw.main_pokemon` through services state, and mutating notifications through events — not aqt.mw. battle_functions.py has no mw access (pure translator/display_name).
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** main service seam (services.py/events.py), pyobj/pokemon_obj.py display_name property (out-of-domain, required by battle_functions change), functions/pokedex_functions._load_pokedex_cache, functions/friendship_evolution, business.calculate_cp_from_dict / calculate_cpm (CP formula change asserted by test_cp_formula: cpm cap 0.84 -> 2.45)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp REVERTED main's seam: encounter_functions imports `from aqt import mw` and hits `mw.ankimon_db.get_all_pokemon_ids/get_all_pokemon/get_user_data/set_user_data` (pity trackers, EP mastery) and `getattr(mw,'main_pokemon')` directly (~21 mw refs). Main's encounter_functions instead uses `services` + `events`; on re-application every `mw.ankimon_db.*` must route through the services DB registry and `mw.main_pokemon` through services state, and mutating notifications through events — not aqt.mw. battle_functions.py has no mw access (pure translator/display_name).
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Largest leaf in domain. encounter_functions calls a module-level `_build_regional_lookup()` at import time that reads pokedex.json (import-time side effect / IO — re-express lazily under seam). Pity-tracker persistence writes ankimon_pity_trackers via mw.ankimon_db — new settings/DB keys. auto_catch_regional new settings key. test_cp_formula asserts a formula change in business.py (out-of-domain) — coordinate. The 4 test files here are gameplay/weighting simulations (some run N=200000 Monte-Carlo) — heavy, keep out of default CI. | GUARDS-TO-REAPPLY: encounter level-cap NameError guard (#402); XP-share None-checks in handle_enemy_faint / xp_share_gain_exp + trade-away None-safety; service-seam mediated mw.* access (no direct aqt.mw)

### F23 — Encounter Simulator (QWebEngine dialog + web assets)
- **ID:** F23
- **Source location(s):** `src/Ankimon/pyobj/encounter_simulator_dialog.py`, `src/Ankimon/encounter_simulator/simulator.html`, `src/Ankimon/encounter_simulator/simulator.js`, `tests/test_encounter_simulator.py`
- **Evidence tag:** [DIFF] · doc↔diff: Doc lists 'encounter simulator' as a distinct leaf — matches. No discrepancy.
- **Target location (new org + seam):** New standalone screen under src/Ankimon/ (dialog in pyobj/ or wired as a web-shell screen if the shared QWebEngine host lands first); simulator.html/js as bundled assets. On main it should be built on the shared web-shell HOST/QWebChannel scaffolding rather than instantiating its own QWebEngineView, if that scaffolding is brought across; otherwise ships self-contained as a Stage-B leaf.
  - Seam wiring: encounter_simulator_dialog uses `from aqt import mw` and reads `mw.ankimon_db.get_all_pokemon_ids/get_all_pokemon` directly. WORSE: calculate_rates() MONKEYPATCHES the global `mw.ankimon_db = MockDB()` then restores it (orig_db save/restore) to force deterministic simulation — an unsafe global-state mutation that must be replaced by dependency-injecting a DB/service into the pure calc, via the services seam, not by mutating mw. QWebChannel SimulatorBridge exposes get_initial_state/calculate_rates_js to JS.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Encounter Overhaul feature (imports functions.encounter_functions as ef; exercises overhaul weighting), pokedex_functions._load_pokedex_cache, business module, shared web-shell/QWebChannel host scaffolding (if adopted)
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** encounter_simulator_dialog uses `from aqt import mw` and reads `mw.ankimon_db.get_all_pokemon_ids/get_all_pokemon` directly. WORSE: calculate_rates() MONKEYPATCHES the global `mw.ankimon_db = MockDB()` then restores it (orig_db save/restore) to force deterministic simulation — an unsafe global-state mutation that must be replaced by dependency-injecting a DB/service into the pure calc, via the services seam, not by mutating mw. QWebChannel SimulatorBridge exposes get_initial_state/calculate_rates_js to JS.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** PyQt6 QWebEngineView/QWebChannel/QWebEngineWidgets hard imports at top — must guard/lazy-import for headless. test_encounter_simulator mocks aqt+PyQt6+encounter_functions and backs up/restores sys.modules. Depends on the overhaul leaf, so cannot land before it. | GUARDS-TO-REAPPLY: service-seam mediated DB access (remove mw.ankimon_db monkeypatch)

### F24 — battle_loop.py reviewer-hook integration (cross-cutting: seam revert + cash-reward/mobile-sync/live-refresh glue)
- **ID:** F24
- **Source location(s):** `src/Ankimon/battle_loop.py`
- **Evidence tag:** [DIFF] · doc↔diff: battle_loop is not itself a named leaf; exp's changes here are integration glue for several other leaves. main's parallel rewrite is the seam migration. This is an edit-vs-edit collision, not a clean feature.
- **Target location (new org + seam):** main/src/Ankimon/battle_loop.py already exists on the service seam (imports services/events). exp's genuinely useful bits (ankimon_startup_finished readiness guard, is_alive() window liveness checks) should be re-applied ON TOP of main's seam version; the cash-reward-interval, mobile_sync.record_desktop_review, and singletons.notify_stats_changed hunks belong to OTHER Stage-B leaves (cash rewards, mobile-review sync, web-shell live-update) and should be deferred with those, not landed here.
  - Seam wiring: exp reverts to direct aqt.mw: `getattr(mw,'test_window')`, `getattr(mw,'evo_window')`, `mw.reviewer.web`, `mw.col.db.scalar(...)`, `mw.ankimon_startup_finished`, plus `singletons.notify_stats_changed()`. Main routes window/state/db through services and events. Any re-applied guard (startup-finished, is_alive) must go through the services/events seam, not raw mw.*.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** main service seam (services/events), Cash-rewards leaf (trainer.cash_reward_interval/amount settings keys), Mobile-review sync leaf (functions.mobile_sync.record_desktop_review), Web-shell live-update scaffolding (singletons.notify_stats_changed)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp reverts to direct aqt.mw: `getattr(mw,'test_window')`, `getattr(mw,'evo_window')`, `mw.reviewer.web`, `mw.col.db.scalar(...)`, `mw.ankimon_startup_finished`, plus `singletons.notify_stats_changed()`. Main routes window/state/db through services and events. Any re-applied guard (startup-finished, is_alive) must go through the services/events seam, not raw mw.*.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** EDIT-vs-EDIT COLLISION: both main (+92, seam) and exp (+50, direct-mw) rewrote on_review_card — do NOT take exp's file wholesale (it would revert the seam). Cherry-pick only the readiness/liveness guards; route cash-reward, mobile-sync, and notify_stats_changed hunks to their owning Stage-B leaves. new settings keys trainer.cash_reward_interval/cash_reward_amount replace the old daily_average==total_reviews cash trigger. | GUARDS-TO-REAPPLY: service-seam mediated mw.* (windows/db/reviewer) access; XP-share None-checks preserved in handle_enemy_faint call path

### F25 — Thread-safe SQLite connection layer + schema migrations (AnkimonDB)
- **ID:** F25
- **Source location(s):** `src/Ankimon/pyobj/database_manager.py`, `tests/test_database_manager.py`
- **Evidence tag:** [DIFF] · doc↔diff: Hint doc lists 'thread-safe SQLite layer (ConnectionWrapper, WAL, check_same_thread=False, thread-local conns, switch_database, new-table migrations)' as pure scaffolding; diff confirms all of these but the same file also carries clearly-leaf mobile/pokedex/reviewer methods, so the file is MIXED not pure scaffolding.
- **Target location (new org + seam):** src/Ankimon/pyobj/database_manager.py on main (AnkimonDB). The genuine scaffolding (ConnectionWrapper, WAL/synchronous/temp_store PRAGMAs, check_same_thread=False, threading.local per-thread conns via _is_main_thread(), switch_database(), and the non-short-circuit CREATE...IF NOT EXISTS migration comment) is Stage-A DONE-IN-BASE material and should land in AnkimonDB. The leaf methods must be split out and DEFERRED: pending_mobile_battles / mobile_battle_history tables + get/set_mobile_watermark, queue_mobile_battles, get_pending_mobile_count, get_next_pending_mobile_batch, mark_mobile_battle_resolved, add_mobile_history*, sync_resolutions_to_other_db (mobile-sync leaf); mark_as_seen/caught, get_seen_ids/get_caught_ids and the get_all_pokemon_ids caught/history merge (Ankidex/pokedex leaf); _clear_reviewer_ownership_cache + _all_pokemon_ids_cache invalidation (reviewer-HUD perf leaf).
  - Seam wiring: _clear_reviewer_ownership_cache does direct `from aqt import mw; mw.reviewer_obj._ownership_cache.clear()` — on main this must reach the reviewer via the service seam (services.reviewer / ui_port) not aqt.mw. The rest of the class is mw-free (pure sqlite over user_path) and is seam-neutral.
- **Class:** MIXED
- **Stage-A disposition:** DONE-IN-BASE
  - Stage-A: database_manager.py: ConnectionWrapper + per-thread connections + check_same_thread=False + switch_database + mobile tables (pending_mobile_battles, mobile_battle_history +index) brought (commit 57aaba99). WAL is OPT-IN (default off) to preserve main's single-file persistence guard — see NR-05. DEFERRED leaf hunks in the SAME file, re-applied by their owning Stage-B leaves: caching (_all_pokemon_ids_cache), pokedex-caught (mark_as_caught/get_seen_ids)+save hook, mobile-sync accessors.
- **Dependencies:** scaffolding already in base
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** _clear_reviewer_ownership_cache does direct `from aqt import mw; mw.reviewer_obj._ownership_cache.clear()` — on main this must reach the reviewer via the service seam (services.reviewer / ui_port) not aqt.mw. The rest of the class is mw-free (pure sqlite over user_path) and is seam-neutral.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Co-edited by main (MB..main +30/-2 added set_config_value + reset_db + rate_this fix). Both branches diverged the class independently: bring exp's connection/threading scaffolding onto main's version, drop exp's leaf methods, and preserve main's two new methods. test_database_manager.py exists on MB; exp only added a settings_obj mock + aqt.theme stub so singletons import survives — trivial, port alongside. | GUARDS-TO-REAPPLY: main's incremental set_config_value(key,value) single-row upsert (perf guard for the per-review cash loop) — exp lacks it and must not clobber it; main's reset_db() test/harness isolation helper; main's rate_this migration fix (bool True vs 'true')

### F26 — Branch self-updater (in-app BRRRR_Experimental updater)
- **ID:** F26
- **Source location(s):** `src/Ankimon/pyobj/update_manager.py`, `src/Ankimon/pyobj/update_dialog.py`, `src/Ankimon/changelog.py`, `tests/test_branch_updates.py`
- **Evidence tag:** [DIFF] · doc↔diff: Doc names 'branch self-updater' as a LEAF; diff confirms. No discrepancy, but note exp's apply_update lacks main's git-clone/MIN_UPDATER guards entirely.
- **Target location (new org + seam):** src/Ankimon/pyobj/update_manager.py + update_dialog.py + changelog.py on main. Leaf self-updater UI/logic (BRRRR tab, snooze/skip_until, commit feed, update_state.json persistence, fetch_branch_sha/fetch_branch_commits/fetch_commit_date, apply_update source-tracking params, changelog.check_branch_update QueryOp poll) is a Stage-B unit. The narrow infra bits — _should_preserve() unconditional user_files/ preservation and apply_update() PermissionError skip-locked-file — overlap main's own hardening and can be reconciled there.
  - Seam wiring: changelog.check_branch_update builds a QueryOp with parent=mw and calls show_branch_update_prompt directly; on main the mw handle + boot scheduling should come through the events/hooks seam rather than a bare `mw` import.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** IS_EXPERIMENTAL_BUILD flag in resources (referenced by update_dialog)
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** changelog.check_branch_update builds a QueryOp with parent=mw and calls show_branch_update_prompt directly; on main the mw handle + boot scheduling should come through the events/hooks seam rather than a bare `mw` import.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** EDIT-vs-EDIT collision: both MB..exp and MB..main modify apply_update() signature/body and _should_preserve(). exp changes apply_update(zip_path, source_type, source_name, commit_sha, status_cb) and adds save_update_state; main changes it to add git-clone paths. Merge must union both. test_branch_updates.py is new (not on MB or main); it imports update_manager + changelog and tests update_state read/write + check_branch_update flow. | GUARDS-TO-REAPPLY: is_git_clone / _git_repo_root / git_pull_ff_only git-clone update protection (main-only; exp branched before it — porting exp's apply_update signature change must not delete these); MIN_UPDATER_VERSION (2,0) release/tag filtering via _is_supported_version/_parse_version (main-only); main's _should_preserve() 'Holy Ground' user_files/ rule (both branches added a variant — keep main's plus exp's always_preserve additions ankimonDEV.db/update_state.json)

### F27 — Dual-database (Normal/Dev-Mode) backup system
- **ID:** F27
- **Source location(s):** `src/Ankimon/pyobj/backup_manager.py`, `src/Ankimon/pyobj/backup_files.py`, `tests/test_backup_manager.py`
- **Evidence tag:** [DIFF] · doc↔diff: No dedicated doc entry; classified from diff. Dual-DB backup is a leaf built atop the switch_database scaffolding, consistent with arch notes.
- **Target location (new org + seam):** src/Ankimon/pyobj/backup_manager.py + backup_files.py on main. The dual-DB behaviour (ankimonDEV.db added to FILES_TO_BACKUP/files_to_backup, per-DB normal_stats/dev_stats summaries via _get_db_file_stats, active-DB filtering in get_backups/restore_backup, manual-backup restricted to active DB) is a Stage-B leaf tied to Developer Mode. The infra sliver — PRAGMA wal_checkpoint(TRUNCATE) before backup/folder create — is the WAL-layer scaffolding and pairs with the DB connection feature.
  - Seam wiring: Both files hit `mw.ankimon_db` directly (mw.ankimon_db.db_path.name, .execute, .get_stats, .get_main_pokemon, .get_config_value). On main these must go through services.db; note exp also switched summary trainer reads from db.get_user_data(...) to db.get_config_value(...), matching main's config-table model.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** DB connection scaffolding: switch_database() + db_path.name (feature 1), Developer Mode gating leaf (source of ankimonDEV.db)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** Both files hit `mw.ankimon_db` directly (mw.ankimon_db.db_path.name, .execute, .get_stats, .get_main_pokemon, .get_config_value). On main these must go through services.db; note exp also switched summary trainer reads from db.get_user_data(...) to db.get_config_value(...), matching main's config-table model.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Co-edited by main (MB..main +52/-18 on backup_manager.py) — EDIT-vs-EDIT: reconcile exp's dual-DB summary shape against main's summary changes. backup_files.py not co-edited by main. test_backup_manager.py is new (not on MB/main), exercises dual-DB summary/restore with sqlite fixtures. | GUARDS-TO-REAPPLY: config.obf was intentionally removed from main's FILES_TO_BACKUP (now in ankimon.db) — exp keeps that removal but adds ankimonDEV.db; do not resurrect config.obf backup

### F28 — Settings plumbing + Stage-B config keys (auto-catch/wishlist, regions, cash rewards, evolution TZ, mobile, team-cycle)
- **ID:** F28
- **Source location(s):** `src/Ankimon/pyobj/settings.py`, `src/Ankimon/config.json`, `src/Ankimon/pyobj/settings_window.py`, `tests/test_wishlist_serialization.py`
- **Evidence tag:** [DIFF] · doc↔diff: Doc calls 'settings/schema plumbing new keys depend on' scaffolding and the individual features leaves — matches. But exp's get() has a hardcoded `if key=='evolution.friendship_time_enabled': return True` override and removes config.obf writing; these contradict main's clean seam and are the NEEDS-REVIEW trigger.
- **Target location (new org + seam):** src/Ankimon/pyobj/settings.py (Settings) + config.json + settings_window.py on main. The settings plumbing that new keys depend on (config-dict identity preserve via clear()/update(), None-triggers-default in load_config, get() default-resolution fallback to DEFAULT_CONFIG, save_config dedup + type-coercion for controls.team_cycle_count) is Stage-A schema scaffolding. Everything else is leaf: the config keys themselves (battle.auto_catch_*, battle.auto_catch_wishlist, misc.active_region, trainer.cash_reward_*, evolution.*, mobile.*, controls.team_cycle_*) and all settings_window UI (region QComboBox+gen-gating, auto-catch rows, cash-reward bounds validation, hotkey refresh, mobile).
  - Seam wiring: exp REVERTS settings.py to `from aqt import mw` + direct `mw.ankimon_db.save_all_config/has_config/get_all_config`; main already routes these through `from ..services import services` / `services.db`. Must re-apply the seam: all mw.ankimon_db access goes via services.db. settings_window.on_save calls reviewer_ui.setup_reviewer_ui directly and reads mw — route via ui_port/services.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: NR-03 (settings_schema.py deferred); bring only plumbing 2+ leaves need
- **Dependencies:** services seam (services.db), web shop_obj.AnkimonItemsWeb._serialize_setting (wishlist test target — web-shell leaf), reviewer_ui.setup_reviewer_ui (team-cycle hotkey)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp REVERTS settings.py to `from aqt import mw` + direct `mw.ankimon_db.save_all_config/has_config/get_all_config`; main already routes these through `from ..services import services` / `services.db`. Must re-apply the seam: all mw.ankimon_db access goes via services.db. settings_window.on_save calls reviewer_ui.setup_reviewer_ui directly and reads mw — route via ui_port/services.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Co-edited by main on settings.py (+56/-38, seam migration to services.db + evolution/cash keys), config.json (+5 economy keys, conflicting values), settings_window.py (+84). EDIT-vs-EDIT on all three. exp also removed the config.obf post-migration archive block and the duplicate import line. test_wishlist_serialization.py is new and tests the web shop_obj serializer (not an owned file) for battle.auto_catch_wishlist — keep with this feature but note it exercises the web-shell leaf. | GUARDS-TO-REAPPLY: main ALREADY added evolution.* keys and trainer.cash_reward_amount/interval PLUS trainer.cash_earned_today + trainer.last_cash_reward_date with amount=40; exp uses amount=100 and lacks the earned_today/last_date keys — preserve main's economy schema (June/July cash-reward design) and reconcile values; keep settings.py on the services seam (do not reintroduce config.obf save/archive that main removed)

### F29 — Mobile/web review sync engine (sync_did_finish hook)
- **ID:** F29
- **Source location(s):** `src/Ankimon/pyobj/ankimon_sync.py`
- **Evidence tag:** [DIFF] · doc↔diff: Doc lists 'mobile-review sync engine' as a LEAF — matches; the whole exp addition is the mobile detection/resolution block.
- **Target location (new org + seam):** src/Ankimon/pyobj/ankimon_sync.py on main, inside setup_ankimon_sync_hooks.on_sync_did_finish. This is the mobile-review sync engine leaf: post-sync dual-DB (ankimon.db + ankimonDEV.db) detection/queueing of mobile reviews, watermark maintenance, badge update, and manual/auto resolution via MobileBridge.
  - Seam wiring: Heavy direct aqt.mw usage: mw.ankimon_db.switch_database/get_mobile_watermark/detect/queue/get_pending_mobile_count, mw.col.db.scalar, mw.col. On main these must be mediated by services.db / services.col rather than raw mw. Depends on menu_buttons.update_mobile_badge, functions.mobile_sync, ankimon_items_web.shop_obj.MobileBridge, and singletons.notify_stats_changed (all web-shell/mobile leaf modules not on main).
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** DB mobile tables + methods (feature 1 leaf part), functions.mobile_sync module, web-shell MobileBridge (shop_obj), menu_buttons.update_mobile_badge
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** Heavy direct aqt.mw usage: mw.ankimon_db.switch_database/get_mobile_watermark/detect/queue/get_pending_mobile_count, mw.col.db.scalar, mw.col. On main these must be mediated by services.db / services.col rather than raw mw. Depends on menu_buttons.update_mobile_badge, functions.mobile_sync, ankimon_items_web.shop_obj.MobileBridge, and singletons.notify_stats_changed (all web-shell/mobile leaf modules not on main).
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Co-edited by main (MB..main +86/-11) but main's edit is a DIFFERENT region (dual-DB stat dialog get_db_stats), not the sync hook. exp inserts a large try/except mobile block at the top of on_sync_did_finish. Guarded MagicMock-type checks in exp reveal it was written for the harness. Whole feature deferred; requires its leaf dependencies to exist first. | GUARDS-TO-REAPPLY: preserve main's on_sync_did_finish / dual-DB stat display logic (main independently added dual-DB sqlite stat reading in the ImprovedPokemonDataSync dialog, +86 lines) — do not overwrite with exp's version

### F30 — Pokemon-GO CPM economy tuning
- **ID:** F30
- **Source location(s):** `src/Ankimon/business.py`
- **Evidence tag:** [DIFF] · doc↔diff: Docstring asymptote text updated to 1.2 but the formula 3.5*(1-e^(-lvl/85)) actually asymptotes toward 3.5 (docstring cap is inaccurate) — minor internal doc-vs-code mismatch to flag on port.
- **Target location (new org + seam):** src/Ankimon/business.py calculate_cpm() on main. Pure numeric rebalance of the level-scaling combat-power multiplier (0.84*(1-e^(-lvl/20)) -> 3.5*(1-e^(-lvl/85)), asymptote doc 0.84 -> 1.2). Belongs with the encounter/stats-and-economy Stage-B unit.
  - Seam wiring: No mw access; pure math function. Seam-neutral.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** scaffolding already in base
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** No mw access; pure math function. Seam-neutral.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Not co-edited by main (MB..main empty for business.py). Tiny 2-line balance change; a standalone leaf tuning, no scaffolding value.

### F31 — Reload-safe singletons + lazy window construction
- **ID:** F31
- **Source location(s):** `src/Ankimon/singletons.py`, `src/Ankimon/reloader.py`, `src/Ankimon/card_hooks.py`, `src/Ankimon/functions/rate_addon_functions.py`
- **Evidence tag:** [DIFF] · doc↔diff: Recon doc says exp has 'reload-safe singletons.py' as scaffolding; the diff confirms, but the implementation is the mw.* direct-access pattern that is the OPPOSITE of main's services/core seam — so it cannot be lifted verbatim, only its intent. singletons.py is a hard edit-vs-arch collision with main (main rewrote it to use .services/.core/.gui_presenter).
- **Target location (new org + seam):** main's composition root already split into src/Ankimon/core.py (build_core/bind_runtime_globals) + services.py registry + gui_presenter.py; the reload-safety idea (idempotent construction, lazy get_*_window() factories, is_alive() liveness checks, module-level __getattr__ lazy proxies, restart_ankimon/teardown_ankimon) must be re-expressed ON that seam (services.get-or-create) NOT by re-anchoring on mw.* — exp's approach is the direct-mw architecture main deliberately moved away from.
  - Seam wiring: exp reverts to anchoring EVERY object on mw.* (mw.logger, mw.ankimon_db, mw.settings_obj, mw.settings_ankimon, mw.translator, mw.main_pokemon, mw.enemy_pokemon, mw.trainer_card, mw.ankimon_tracker_obj, mw.shop_manager, mw.reviewer_obj, mw.achievements_dict, mw.*_window, mw.items_web_window) via `getattr(mw, ...) or Construct()`. main routes the same core objects through services.populate()/core.build_core and keeps only mw.<service> back-compat shims. Correct seam = services registry get-or-create; notify_stats_changed() is the QWebChannel live-update push and belongs on ui_port/events, not singletons. swap_ankimon_account (DB switch + full state refresh) reads mw.ankimon_db/mw.* directly and should call services.db.switch_database.
- **Class:** SCAFFOLDING
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: NR-06 (reloader.py mw-coupled, deferred with Dev-Mode/web-shell leaves)
- **Dependencies:** thread-reload-and-misc-utils (is_alive/is_main_thread), async-startup-boot, webshell-and-dev-menu-wiring (get_items_window/ankidex/items_web leaf)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp reverts to anchoring EVERY object on mw.* (mw.logger, mw.ankimon_db, mw.settings_obj, mw.settings_ankimon, mw.translator, mw.main_pokemon, mw.enemy_pokemon, mw.trainer_card, mw.ankimon_tracker_obj, mw.shop_manager, mw.reviewer_obj, mw.achievements_dict, mw.*_window, mw.items_web_window) via `getattr(mw, ...) or Construct()`. main routes the same core objects through services.populate()/core.build_core and keeps only mw.<service> back-compat shims. Correct seam = services registry get-or-create; notify_stats_changed() is the QWebChannel live-update push and belongs on ui_port/events, not singletons. swap_ankimon_account (DB switch + full state refresh) reads mw.ankimon_db/mw.* directly and should call services.db.switch_database.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** singletons.py is a direct collision with main's rewritten composition root (main imports .services/.core/.gui_presenter; exp deletes those imports and inlines mw.* anchoring). reloader.py is NET-NEW (absent on main). rate_addon_functions.py only swaps `from ..singletons import test_window` for lazy get_test_window() — trivial, follows the lazy pattern. card_hooks.py adds an idempotent `_hooks_registered` guard (pure reload safety). Lazy factories also pull in leaf targets (get_items_window -> ankimon_items_web, get_ankidex_window -> ankidex/) that do NOT exist on main. | GUARDS-TO-REAPPLY: Settings DB-before-construction ordering (mw.ankimon_db set before Settings() — exp preserves the getattr order; main's core.build_core encodes the same); service seam (core/services/gui_presenter) must remain the access path; reload-safe singleton idempotency

### F32 — Asynchronous thread-safe startup boot
- **ID:** F32
- **Source location(s):** `src/Ankimon/startup.py`, `src/Ankimon/__init__.py`
- **Evidence tag:** [DIFF] · doc↔diff: Doc lists 'async QueryOp boot' as scaffolding — confirmed. But exp's __init__ collides head-on with main's __init__ which still calls synchronous run_startup_sequence() (main line 79-80). Also exp inlines team-overview hook registration and DROPS the synchronous changelog call, replacing online_connectivity with a False stub (async update-check moved elsewhere) — a behavior change to flag.
- **Target location (new org + seam):** Split run_startup_sequence into run_startup_background_checks (aqt-free, DB/disk work) + run_startup_ui_callbacks (main-thread Qt) driven by aqt.operations.QueryOp(...).without_collection().run_in_background(); on main this belongs in startup.py + __init__ but must call through core/services, and the deferred menu creation must pass real services not the None placeholders exp uses.
  - Seam wiring: __init__ sets mw.ankimon_startup_finished, mw.online_connectivity, mw._ankimon_review_proxy directly on mw; the QueryOp success callback builds BackupManager, calls create_menu_actions(..., None x11, ...), register_profile_hooks, setup_reviewer_ui. The async QueryOp boot itself is genuine shared plumbing (scaffolding); the menu/team-overview/profile wiring inside on_startup_complete is leaf orchestration. On main this reads services, not mw.*.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: boot_async.py primitive already in base (commit e1ea7a0b); the __init__/startup async REWIRING is deferred so main's proven boot is untouched
- **Dependencies:** Reload-safe singletons, thread-reload-and-misc-utils
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** __init__ sets mw.ankimon_startup_finished, mw.online_connectivity, mw._ankimon_review_proxy directly on mw; the QueryOp success callback builds BackupManager, calls create_menu_actions(..., None x11, ...), register_profile_hooks, setup_reviewer_ui. The async QueryOp boot itself is genuine shared plumbing (scaffolding); the menu/team-overview/profile wiring inside on_startup_complete is leaf orchestration. On main this reads services, not mw.*.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Config migration of battle.automatic_catch_special -> 7 new auto_catch_* keys lives in run_startup_background_checks (settings schema plumbing — leaf EV-yield/auto-catch dependency). create_menu_actions is called with 11 None placeholders (windows now lazy) — depends on menu_buttons rewrite. Hard edit-vs-edit collision with main __init__/startup. | GUARDS-TO-REAPPLY: encounter level-cap NameError guard #402 (startup generates first enemy via generate_random_pokemon — verify main_pokemon.level guard survives); monthly-challenge None-safety; persistent reviewer_did_answer_card proxy registered once (reload safety); changelog check must not be dropped — exp sets online_connectivity=False and drops check_and_show_changelog from __init__ (moved/removed): verify changelog 2.02-E/2.03 path still fires

### F33 — Thread/reload helpers + misc utils (is_alive, is_main_thread, is_dev_mode, font cache, EV normalize)
- **ID:** F33
- **Source location(s):** `src/Ankimon/utils.py`
- **Evidence tag:** [DIFF] · doc↔diff: main ALSO edited utils.py (145 lines vs MB) — co-edit conflict. main added its own limit_ev_yield variant (line 751) and did NOT add is_alive/is_main_thread/is_dev_mode/_FONT_CACHE. So the four exp helpers are net-new and land cleanly, but limit_ev_yield is an edit-vs-edit collision (exp replaces the raise-on-unknown-key validation with silent normalize/drop — a behavior/regression change to review).
- **Target location (new org + seam):** is_alive()/is_main_thread() are pure infra -> keep in utils.py (aqt-light) and expose to the seam; is_dev_mode() belongs with Developer-Mode gating (leaf); load_custom_font _FONT_CACHE is a perf micro-opt (safe); limit_ev_yield normalization is an EV-yield leaf change.
  - Seam wiring: is_main_thread() uses QApplication.instance()/QThread; is_alive() probes obj.objectName(); is_dev_mode() reads mw.pm.name and mw.settings_obj.get('trainer.name') directly — should read services.settings once seam-migrated. No hard mw write.
- **Class:** MIXED
- **Stage-A disposition:** DONE-IN-BASE
  - Stage-A: utils.is_main_thread + utils.is_alive brought (commit cafa3788), sys.modules-guarded so utils stays aqt-free. DEFERRED same-file leaf hunks: is_dev_mode (Dev-Mode gating), font cache, EV-normalize.
- **Dependencies:** scaffolding already in base
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** is_main_thread() uses QApplication.instance()/QThread; is_alive() probes obj.objectName(); is_dev_mode() reads mw.pm.name and mw.settings_obj.get('trainer.name') directly — should read services.settings once seam-migrated. No hard mw write.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** limit_ev_yield change removes ValueError guards on unknown EV keys (defensive-to-permissive) — flag as possible silent-regression vs main. is_alive/is_main_thread are the load-bearing scaffolding half; the rest are leaf/perf riders bundled in one file. | GUARDS-TO-REAPPLY: preserve service seam access for settings in is_dev_mode

### F34 — Reviewer HUD rewrite + ownership cache + team-cycle hotkeys
- **ID:** F34
- **Source location(s):** `src/Ankimon/pyobj/reviewer_obj.py`, `src/Ankimon/reviewer_ui.py`, `tests/test_reviewer_ownership_cache.py`
- **Evidence tag:** [DIFF] · doc↔diff: reviewer_obj on main keeps direct `from aqt import gui_hooks, mw, utils` and db=mw.ankimon_db (main did NOT seam-migrate this file) — so exp's HUD sits on the same access style; difference is the +355/-312 rewrite scope (ownership cache, team-cycle, new bottomHTML), which is leaf.
- **Target location (new org + seam):** Stage-B leaf 'reviewer-HUD perf rewrite + hotkeys'; on main goes into pyobj/reviewer_obj.py + reviewer_ui.py but HUD DB reads must route through services.db and shortcut/link wrapping through hooks/ui_port. The in-memory _ownership_cache is a small caching layer riding inside the leaf.
  - Seam wiring: reviewer_obj imports `from aqt import gui_hooks, mw, utils`; update_life_bar reads db = mw.ankimon_db for ownership and clears _ownership_cache on reset; mw.addonManager.addonFromModule for sprite URLs. reviewer_ui reads mw.ankimon_db (team list), mw.settings_obj (controls.team_cycle_count/team_cycle_key), mw.reviewer, and monkeypatches Reviewer._shortcutKeys/_linkHandler/_bottomHTML (stored as _ankimon_orig_* for reloader teardown). Seam target: services.db + a reviewer ui_port; the Reviewer method wrapping is the reload-teardown contract shared with reloader.py.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Reload-safe singletons, async-startup-boot (setup_reviewer_ui called from boot), thread-reload-and-misc-utils (is_dev_mode used in reviewer_ui)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** reviewer_obj imports `from aqt import gui_hooks, mw, utils`; update_life_bar reads db = mw.ankimon_db for ownership and clears _ownership_cache on reset; mw.addonManager.addonFromModule for sprite URLs. reviewer_ui reads mw.ankimon_db (team list), mw.settings_obj (controls.team_cycle_count/team_cycle_key), mw.reviewer, and monkeypatches Reviewer._shortcutKeys/_linkHandler/_bottomHTML (stored as _ankimon_orig_* for reloader teardown). Seam target: services.db + a reviewer ui_port; the Reviewer method wrapping is the reload-teardown contract shared with reloader.py.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** test_reviewer_ownership_cache.py (net-new, 434 lines) validates the cache — carry it with the leaf. team_cycle adds a 4th shortcut arg to setup_reviewer_ui (signature change consumed by __init__ boot). | GUARDS-TO-REAPPLY: reload-safe restore of Reviewer._ankimon_orig_shortcutKeys/_linkHandler/_bottomHTML (paired with reloader.py teardown); XP-share None-checks if HUD touches xp_share display

### F35 — AnkimonTracker robustness (faint guard + language-agnostic review count)
- **ID:** F35
- **Source location(s):** `src/Ankimon/pyobj/ankimon_tracker.py`, `tests/test_ankimon_tracker.py`
- **Evidence tag:** [DIFF] · doc↔diff: main ALSO rewrote get_total_reviews (67-line co-edit, main uses col.studied_today() with try/except at lines 93-109) — this is an edit-vs-edit collision: exp uses a revlog SQL day_cutoff query, main uses a hardened studied_today() parse. Must pick one; they solve the same localized-regex bug differently. faint_processed guard is net-new on top.
- **Target location (new org + seam):** pyobj/ankimon_tracker.py on main; the faint_processed flag is gameplay state, get_total_reviews rewrite is a robustness fix.
  - Seam wiring: get_total_reviews reads mw.col.sched.day_cutoff and mw.col.db.scalar(revlog) directly (was regex on mw.col.studied_today()). Direct mw.col access; core is aqt-free-ish (col passed via mw). No new mw writes.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** scaffolding already in base
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** get_total_reviews reads mw.col.sched.day_cutoff and mw.col.db.scalar(revlog) directly (was regex on mw.col.studied_today()). Direct mw.col access; core is aqt-free-ish (col passed via mw). No new mw writes.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** test_ankimon_tracker.py (net-new, 113 lines) covers the tracker. Small feature but real collision with main — decide which get_total_reviews implementation wins.

### F36 — Web-shell nav menu + Developer/debug menu + account switch wiring
- **ID:** F36
- **Source location(s):** `src/Ankimon/menu_buttons.py`
- **Evidence tag:** [DIFF] · doc↔diff: Depends on ankimon_items_web/ (web-shell) and ankidex/ modules that do NOT exist on main (main still has pokedex/). Confirms exp layered the web-shell; these menu entries are leaf screens per the Stage-A definition.
- **Target location (new org + seam):** Stage-B: menu wiring for the QWebEngine web-shell screens (Items/Shop/Bag/Profile/Team via _open_shell_at + get_items_window), Ankidex SPA, nature chart, Developer-Mode debug submenu, and swap-account action. On main goes in menu_buttons.py but must consume real services and the (not-yet-on-main) web-shell host + ankidex modules.
  - Seam wiring: Builds mw.pokemenu directly and stores it on mw; reads mw.translator/mw.settings_obj; re-creates mw.translator at import time (same anti-pattern main flags). Pulls lazy get_* factories from singletons (get_items_window, get_ankidex_window, get_pokemon_pc, get_test_window, get_item_window, get_eff/gen_id/nature_chart, get_credits/license/version_dialog). Debug submenu gated by is_dev_mode(); update_mobile_badge for mobile-review sync; swap_ankimon_account. Seam: menu is a ui_port concern; these should resolve windows via services.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Reload-safe singletons (lazy get_* factories), thread-reload-and-misc-utils (is_dev_mode), async-startup-boot (create_menu_actions called with None placeholders)
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** Builds mw.pokemenu directly and stores it on mw; reads mw.translator/mw.settings_obj; re-creates mw.translator at import time (same anti-pattern main flags). Pulls lazy get_* factories from singletons (get_items_window, get_ankidex_window, get_pokemon_pc, get_test_window, get_item_window, get_eff/gen_id/nature_chart, get_credits/license/version_dialog). Debug submenu gated by is_dev_mode(); update_mobile_badge for mobile-review sync; swap_ankimon_account. Seam: menu is a ui_port concern; these should resolve windows via services.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Contains a MockWindow/DummyMock branch (`if 'mock' in mw.__class__.__name__`) for headless — infra rider. Mostly leaf: web-shell screen entrypoints, Ankidex, nature chart, dev menu, account swap. | GUARDS-TO-REAPPLY: is_dev_mode gating for debug menu (Developer Mode leaf); mobile badge None-safety

### F37 — Review-based-damage poke_engine multiplier rewrite
- **ID:** F37
- **Source location(s):** `src/Ankimon/functions/ankimon_hooks_to_poke_engine.py`
- **Evidence tag:** [DIFF] · doc↔diff: Not individually named in doc but fits 'encounter/battle' gameplay; also fixes a real bug: state.user.active.id comparison now uses normalize_name(main_pokemon.name) instead of .lower() (correctness). The wrapped get_instructions_from_damage + applied-flag dedup is gameplay logic.
- **Target location (new org + seam):** Stage-B battle/reviewer damage feature; functions/ankimon_hooks_to_poke_engine.py — monkeypatches poke_engine.instruction_generator.get_instructions_from_damage and applies tracker.multiplier.
  - Seam wiring: Adds `from aqt import mw` inside simulate loop; reads settings via `getattr(mw,'settings_obj',None) or settings_obj` and tracker via `getattr(mw,'ankimon_tracker_obj',None) or ankimon_tracker_obj` — a mw-fallback layered over the module singletons; should read services.settings/services.tracker.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Reload-safe singletons (mw fallbacks)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** Adds `from aqt import mw` inside simulate loop; reads settings via `getattr(mw,'settings_obj',None) or settings_obj` and tracker via `getattr(mw,'ankimon_tracker_obj',None) or ankimon_tracker_obj` — a mw-fallback layered over the module singletons; should read services.settings/services.tracker.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Global monkeypatch of poke_engine at import time — reload safety concern (re-wrapping on reload could double-wrap; verify _original_ capture is idempotent). normalize_name fix is a genuine bug fix worth extracting.

### F38 — Encounter tier data expansion + nature-chart resource path
- **ID:** F38
- **Source location(s):** `src/Ankimon/resources.py`
- **Evidence tag:** [DIFF] · doc↔diff: Adds alternate-form IDs (origin/therian/urshifu/zygarde forms) to Ultra/Mythical tiers and Pecharunt to Mythical Gen 9 — part of the encounter-overhaul leaf. nature_chart_html_path supports the nature chart menu item (menu feature).
- **Target location (new org + seam):** Stage-B encounter overhaul (8-tier/Megas/Gmax/regional forms) data + nature-chart leaf; resources.py POKEMON_TIERS table + nature_chart_html_path.
  - Seam wiring: Pure data/path constants; no mw access.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** scaffolding already in base
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** Pure data/path constants; no mw access.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Low-risk data-only change but semantically tied to the deferred encounter overhaul; nature_chart_html_path pairs with get_nature_chart() in menu_buttons/singletons.

### F39 — Test-harness stub plumbing (conftest + integrity test)
- **ID:** F39
- **Source location(s):** `tests/conftest.py`, `tests/test_addon_integrity.py`
- **Evidence tag:** [DIFF] · doc↔diff: conftest.py and test_addon_integrity.py are UNCHANGED between MB and main (main blobs 243829cc / 436db158 == MB) — so no edit-vs-edit; exp's changes apply cleanly on top. BUT exp adds a stub for ankimon_items_web (a leaf web-shell package absent on main) — that stub is inert until the leaf lands. Note main added many OTHER test files exp is not touching.
- **Target location (new org + seam):** tests/ on main (main already owns a large tests/ suite + top-level harness/). exp's conftest autouse restore_package_stubs fixture and the rewritten import-by-submodule integrity test should be reconciled with main's existing conftest/harness rather than overwriting.
  - Seam wiring: Stubs Ankimon/Ankimon.functions/Ankimon.pyobj/Ankimon.ankimon_items_web packages; restores real resources/utils/singletons modules when a test replaces them with MagicMock. No production seam.
- **Class:** SCAFFOLDING
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: synthesize exp conftest/integrity changes WITH main's harness; do not regress main's harness
- **Dependencies:** Reload-safe singletons (restores Ankimon.singletons)
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** Stubs Ankimon/Ankimon.functions/Ankimon.pyobj/Ankimon.ankimon_items_web packages; restores real resources/utils/singletons modules when a test replaces them with MagicMock. No production seam.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** test_addon_integrity rewrite avoids importing Ankimon.__init__ and drops pkgutil.walk_packages to stop 10GB MagicMock blowups — a genuine infra fix worth keeping. The ankimon_items_web stub references a not-yet-present leaf. | GUARDS-TO-REAPPLY: preserve main's harness/ + test infra (exp deletes top-level harness/ overall; do NOT let that deletion ride in)

### F40 — Evolution overhaul (friendship/time/location/item-stone + evolution badge)
- **ID:** F40
- **Source location(s):** `src/Ankimon/functions/friendship_evolution.py`, `src/Ankimon/pyobj/evolution_window.py`, `src/Ankimon/data_files/pokemon_evolution.csv`, `src/Ankimon/addon_sprites/evolution_indicator.png`, `tests/test_friendship_evolution.py`, `tests/test_location_evolutions.py`, `tests/test_evolution_item_consumption.py`
- **Evidence tag:** [GIT]
- **Target location (new org + seam):** src/Ankimon/functions/friendship_evolution.py + src/Ankimon/pyobj/evolution_window.py on main's seam; new asset addon_sprites/evolution_indicator.png; csv/day-night data unchanged location. Keep main's services.settings-backed friendship module and layer region/time/item-stone/MovePicker-on-evolve as a Stage-B leaf.
  - Seam wiring: exp REVERTS main's seam: friendship_evolution swaps `services.settings` back to lazy `from ..singletons import settings_obj` and `mw.settings_obj.get('misc.active_region')`; evolution_window uses `mw.ankimon_db` and `from ..singletons import get_pokemon_pc/get_item_window/get_items_window`, plus `mw.reviewer.web`. On main these must route through services.db/services.settings and the singletons getters already present; do NOT import the reverted aqt.mw form.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Move learning UI (MovePickerDialog), thread-safe SQLite layer (mw.ankimon_db / services.db) [other domain scaffolding], singletons/reload-safe getters [other domain scaffolding], settings schema keys evolution.friendship_time_enabled / misc.active_region / evolution.timezone_* [settings plumbing, other domain]
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp REVERTS main's seam: friendship_evolution swaps `services.settings` back to lazy `from ..singletons import settings_obj` and `mw.settings_obj.get('misc.active_region')`; evolution_window uses `mw.ankimon_db` and `from ..singletons import get_pokemon_pc/get_item_window/get_items_window`, plus `mw.reviewer.web`. On main these must route through services.db/services.settings and the singletons getters already present; do NOT import the reverted aqt.mw form.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Base ALREADY has the friendship-evolution core in seam form (main added friendship_evolution.py 598 lines + tests/test_friendship_evolution.py). exp adds NEW: LevelEvolution.time_of_day, region-aware level evolutions (Pikachu/Exeggcute via misc.active_region), item-stone consumption + item-window refresh, and MovePicker prompt on evolve. csv change (rows 429/430) tags Espeon=day/Umbreon=night. evolution_indicator.png is exp-only new asset (PC-box readiness badge). tests test_location_evolutions & test_evolution_item_consumption are exp-only new. No edit-vs-delete collision (all add/modify). | GUARDS-TO-REAPPLY: service seam (services.settings/services.db); monthly-challenge/None-safety unaffected but keep settings None-checks; encounter level-cap NameError guard #402 (evolve path touches level)

### F41 — Move learning UI (MovePickerDialog)
- **ID:** F41
- **Source location(s):** `src/Ankimon/pyobj/move_picker.py`
- **Evidence tag:** [DIFF]
- **Target location (new org + seam):** src/Ankimon/pyobj/move_picker.py (new module) on main, importable by pc_box, pokemon_details and evolution_window; pure Qt, no seam wiring needed.
  - Seam wiring: No aqt.mw or services usage at all — imports only pokedex_functions/gui_functions/utils. Can port as-is; callers pass data in. No seam entrypoint required.
- **Class:** SCAFFOLDING
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: NR-03 (MovePickerDialog deferred — shared by PC-box + evolution leaves; add purely-additively)
- **Dependencies:** pokedex_functions (find_details_move), gui_functions (type/category icons)
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** No aqt.mw or services usage at all — imports only pokedex_functions/gui_functions/utils. Can port as-is; callers pass data in. No seam entrypoint required.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** exp-only NEW file (not on main). Shared move-selection dialog depended on by 3 leaves (PC-box MoveManagerWidget, pokemon_details remember_attack, evolution learn-move) with NO standalone feature and NO mw.* → fits SCAFFOLDING; flagged NEEDS-REVIEW because it is bundled under the leaf 'evolution overhaul+MovePickerDialog' in the domain map and Stage A must decide whether the shared dialog is pulled forward ahead of its leaf callers.

### F42 — PC Box rework (move manager, evolution button, web-item integration)
- **ID:** F42
- **Source location(s):** `src/Ankimon/pyobj/pc_box.py`, `tests/test_pc_box_evolution_button.py`
- **Evidence tag:** [GIT]
- **Target location (new org + seam):** src/Ankimon/pyobj/pc_box.py on main's seam; heavy DB/UI leaf, wire via services.db + singletons getters + ui_port for cross-window refresh.
  - Seam wiring: Pervasive direct `mw.ankimon_db.*` (execute/get_pokemon/save_pokemon/get_all_items), `mw.pm.profile[GEOMETRY_KEY]` for window geometry, and cross-window pokes `mw.item_window`/`mw.items_web_window` (renewWidgets/update_ui_data). On main these should go through services.db and an events/ui_port seam for item-window refresh instead of reaching mw.* directly.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Move learning UI (MovePickerDialog), Evolution overhaul (EvoWindow, evolution_readiness, evolution_indicator.png), thread-safe SQLite layer, Web Bag/Items web-shell screens (mw.items_web_window) [other domain leaf]
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** Pervasive direct `mw.ankimon_db.*` (execute/get_pokemon/save_pokemon/get_all_items), `mw.pm.profile[GEOMETRY_KEY]` for window geometry, and cross-window pokes `mw.item_window`/`mw.items_web_window` (renewWidgets/update_ui_data). On main these should go through services.db and an events/ui_port seam for item-window refresh instead of reaching mw.* directly.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** +1171/-293 vs main. Adds MoveManagerWidget (forget/learn/TM via MovePickerDialog), friendship evolution badge rendering, geometry persistence, count/slot refresh, and hooks into the web Bag/Items windows. Depends on move_picker + evolution_window features. test_pc_box_evolution_button is exp-only new (asserts MoveManagerWidget replaces the evolution button). No edit-vs-delete collision. | GUARDS-TO-REAPPLY: service seam (services.db); ui_port/events for item-window refresh instead of direct mw.item_window pokes

### F43 — Pokemon details GUI (nature chart, animated stat bars, remember-attack) + native-window lazy-init
- **ID:** F43
- **Source location(s):** `src/Ankimon/gui_classes/pokemon_details.py`, `src/Ankimon/gui_entities.py`, `src/Ankimon/addon_files/nature_chart.html`
- **Evidence tag:** [GIT]
- **Target location (new org + seam):** src/Ankimon/gui_classes/pokemon_details.py + gui_entities.py on main; nature_chart.html asset under addon_files/. Route DB access via services.db and keep main's seam edits to these co-edited files.
  - Seam wiring: pokemon_details uses direct `mw.ankimon_db.execute/get_main_pokemon/get_pokemon/delete_pokemon/add_to_history` and passes `mw` as MovePicker parent; on main these must use services.db. gui_entities adds `nature_chart_html_path` import + lazy-init (initialized/loaded flags, initUI-on-show) for License/Credits/TableWidget/Version_Dialog and a tuple-returning read_github_file — these are UI infra, no mw.* seam.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** Move learning UI (MovePickerDialog), thread-safe SQLite layer, resources.py nature_chart_html_path constant [other domain, resources]
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** pokemon_details uses direct `mw.ankimon_db.execute/get_main_pokemon/get_pokemon/delete_pokemon/add_to_history` and passes `mw` as MovePicker parent; on main these must use services.db. gui_entities adds `nature_chart_html_path` import + lazy-init (initialized/loaded flags, initUI-on-show) for License/Credits/TableWidget/Version_Dialog and a tuple-returning read_github_file — these are UI infra, no mw.* seam.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** pokemon_details diverges heavily from main (+362/-301): AnimatedStatBar, createStatBar, PokemonDetailsStats rewrite, remember_attack_details_window via MovePickerDialog. nature_chart.html is exp-only new asset consumed by gui_entities TableWidget.show_nature_chart. gui_entities co-edited by BOTH main and exp — reconcile carefully (not edit-vs-delete, but overlapping edits). nature_chart_html_path is defined in resources.py which is NOT owned here. | GUARDS-TO-REAPPLY: service seam (services.db); gui_entities is co-edited on main (lazy-init + read_github_file); reconcile so main's version wins and only nature-chart/detail additions are layered

### F44 — Learnset retrieval overhaul (suffix-cleaning, R/S methods, Deoxys/eternamax, gen fallbacks)
- **ID:** F44
- **Source location(s):** `src/Ankimon/functions/learnset_retrieval.py`, `tests/test_learnset_retrieval.py`, `tests/test_learnset_robustness.py`
- **Evidence tag:** [GIT]
- **Target location (new org + seam):** src/Ankimon/functions/learnset_retrieval.py on main (pure function module, no seam); extend the version main already ships.
  - Seam wiring: No aqt.mw/services usage — pure pokedex-backed helpers. No seam entrypoint needed; port as pure logic.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** pokedex_functions (search_pokedex/search_pokedex_by_id/safe_int)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** No aqt.mw/services usage — pure pokedex-backed helpers. No seam entrypoint needed; port as pure logic.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Base ALREADY has learnset_retrieval + both tests on main (seam-free). exp adds NEW leaf logic: clean_pokeapi_name suffix stripping, DEOXYS_EXCLUSIONS, learn-code method parsing (L/R/S), 3-tier canonical-key fallback and base-form merge for Mega/Gmax. test_learnset_retrieval extended (+163), test_learnset_robustness added lines. Pure enhancement, low risk. | GUARDS-TO-REAPPLY: preserve main's in-memory learnset cache/clear_learnset_cache behavior

### F45 — Sprite Mega/Gmax form resolution + sprite download mirror
- **ID:** F45
- **Source location(s):** `src/Ankimon/functions/sprite_functions.py`, `src/Ankimon/pyobj/download_sprites.py`
- **Evidence tag:** [GIT]
- **Target location (new org + seam):** src/Ankimon/functions/sprite_functions.py on main's seam; add pokemon_name-aware Mega/Gmax id lookup on top of main's services.logger version.
  - Seam wiring: exp REVERTS main's `services.logger` back to `mw.logger.log(...)` throughout, and adds `pokemon_name` param + `_get_pokemon_id_from_pokedex` (pokedex cache) for form sprite ids. On main keep services.logger; do not take the aqt.mw reversion.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** pokedex_functions (_load_pokedex_cache/safe_int)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp REVERTS main's `services.logger` back to `mw.logger.log(...)` throughout, and adds `pokemon_name` param + `_get_pokemon_id_from_pokedex` (pokedex cache) for form sprite ids. On main keep services.logger; do not take the aqt.mw reversion.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Base has sprite_functions in seam form (main..exp only 5/-6, the logger reversion + signature). exp adds get_sprite_path(pokemon_name=...) Mega/Gmax/Gigantamax id resolution with base-species fallback. download_sprites.py change is a trivial trailing-comma no-op on the mirror URL list (noise); group here as it belongs to sprite delivery. | GUARDS-TO-REAPPLY: service seam (services.logger)

### F46 — PokemonObject / main-pokemon persistence + display helpers (name, tier, fossil)
- **ID:** F46
- **Source location(s):** `src/Ankimon/pyobj/pokemon_obj.py`, `src/Ankimon/functions/update_main_pokemon.py`, `src/Ankimon/functions/pokemon_functions.py`
- **Evidence tag:** [GIT]
- **Target location (new org + seam):** src/Ankimon/pyobj/pokemon_obj.py, functions/update_main_pokemon.py, functions/pokemon_functions.py on main's seam; keep services.db, add display_name/pokedex_id/generation props + name-preservation + Fossil tier as Stage-B.
  - Seam wiring: exp REVERTS the seam in all three: pokemon_obj `services`->`from aqt import mw` (held_item save via `mw.ankimon_db`, `mw.main_pokemon`, `mw.settings_obj.get('misc.language')`) and drops the documented lazy give_item import for a top-level `from ..utils import give_item`; update_main_pokemon `services.db`->`mw.ankimon_db`; pokemon_functions `services.db`->`mw.ankimon_db` + top-level `from aqt import mw`. On main these must stay on services.db/services.settings.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** thread-safe SQLite layer, pokedex_functions, utils.give_item
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp REVERTS the seam in all three: pokemon_obj `services`->`from aqt import mw` (held_item save via `mw.ankimon_db`, `mw.main_pokemon`, `mw.settings_obj.get('misc.language')`) and drops the documented lazy give_item import for a top-level `from ..utils import give_item`; update_main_pokemon `services.db`->`mw.ankimon_db`; pokemon_functions `services.db`->`mw.ankimon_db` + top-level `from aqt import mw`. On main these must stay on services.db/services.settings.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** pokemon_obj adds display_name/pokedex_id/generation properties + DB-backed held_item give/take. update_main_pokemon adds stored-name preference (falls back to search_pokedex_by_id) — co-edited with main. pokemon_functions adds tier='Fossil' to save_fossil_pokemon + safe_int hp. RISK: exp's top-level `from ..utils import give_item` in pokemon_obj contradicts main's explicit lazy-import cycle guard — potential import-order regression; classify MIXED/NEEDS-REVIEW-worthy but net leaf. | GUARDS-TO-REAPPLY: service seam (services.db/services.settings); preserve pokemon_obj's lazy give_item import to avoid the utils<->pokedex import cycle (exp re-introduced a top-level import that main deliberately avoided); keep find_experience_for_level `experience = 0` default (exp deleted the explanatory guard comment but kept the default — re-add note)

### F47 — XP-Share friendship-evolution hook + None-safety (trainer_functions)
- **ID:** F47
- **Source location(s):** `src/Ankimon/functions/trainer_functions.py`
- **Evidence tag:** [DIFF] · doc↔diff: Both exp and main independently add friendship-evolution + a missing-target guard; main's implementation is strictly stronger (clears the stale setting, guards everstone/name, uses translator). exp version is a weaker superset-subset and is superseded by main.
- **Target location (new org + seam):** src/Ankimon/functions/trainer_functions.py already on origin/main (find_trainer_rank + xp_share_gain_exp) using services.db seam
  - Seam wiring: exp keeps `from aqt import mw` and reads mw.logger / mw.ankimon_db directly; main already refactored this exact file to `from ..services import services` with services.db.execute/get_shiny_count. No re-seaming needed: main is the target.
- **Class:** LEAF
- **Stage-A disposition:** DONE-IN-BASE
- **Dependencies:** friendship_evolution.check_friendship_evolution_for_pokemon (evolution overhaul leaf)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp keeps `from aqt import mw` and reads mw.logger / mw.ankimon_db directly; main already refactored this exact file to `from ..services import services` with services.db.execute/get_shiny_count. No re-seaming needed: main is the target.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Co-edited by both branches. Nothing to port: main already contains a superior version. exp's variant would REGRESS main's XP-share None-guard (it fails to clear trainer.xp_share), so do not carry exp here. | GUARDS-TO-REAPPLY: XP-share None-check on missing xp_share target (main clears trainer.xp_share and returns original_exp; exp only logs+returns exp and does NOT clear the stale setting); return_name_for_id().capitalize() None-guard (main only); pokemon.get('everstone', False) instead of pokemon['everstone']

### F48 — Trade V2 (versioned -200 codes, nature, legacy mode, mega actual_id)
- **ID:** F48
- **Source location(s):** `src/Ankimon/pyobj/pokemon_trade.py`
- **Evidence tag:** [DIFF] · doc↔diff: exp adds a large parse_to_canonical/legacy-checkbox/nature system (Trade V2). main only added small guards to the same file. The two edits overlap in add_pokemon_to_collection and the trade-completion block (edit-vs-edit): a Stage-B merge must keep BOTH exp's canonical trade logic AND main's XP-share-clear guard.
- **Target location (new org + seam):** src/Ankimon/pyobj/pokemon_trade.py on main; direct db access should route through services.db and the trade dialog kept as a Stage-B leaf (or its web-shell equivalent)
  - Seam wiring: exp uses direct `mw.ankimon_db` (lines ~53/68/103/206/702) and `mw.app.clipboard()` (line 483). Main's copy of this file was NOT seam-refactored (still `db = mw.ankimon_db`), but Stage-B port should move db reads to services.db and clipboard to a ui_port helper.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** utils.is_alive + singletons.pokemon_pc (reload-safety guard on refresh_pokemon_grid), sprite_functions.get_sprite_path pokemon_name= param (encounter/sprite overhaul)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp uses direct `mw.ankimon_db` (lines ~53/68/103/206/702) and `mw.app.clipboard()` (line 483). Main's copy of this file was NOT seam-refactored (still `db = mw.ankimon_db`), but Stage-B port should move db reads to services.db and clipboard to a ui_port helper.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Standalone user-facing feature = one Stage-B unit. Do not bring in Stage A. Watch the edit-vs-edit collision in the db.replace_pokemon block: exp's version omits main's XP-share-clear. | GUARDS-TO-REAPPLY: main's XP-share clear after db.replace_pokemon (trade-away sets trainer.xp_share=None when the traded individual_id was the share target) — exp's Trade V2 diff does NOT include this and would regress it; check_and_award_monthly_pokemon None-safety + rate_this in (True,'true') added on main

### F49 — TrainerCard web-shell live-refresh hooks (notify_stats_changed + refresh())
- **ID:** F49
- **Source location(s):** `src/Ankimon/pyobj/trainer_card.py`
- **Evidence tag:** [DIFF] · doc↔diff: Co-edited: main did the seam refactor (DONE-IN-BASE); exp did NOT seam this file and instead layered live-update/refresh hooks. The refresh()/notify hooks depend on web-shell scaffolding not yet on main, so they cannot land until that scaffolding is brought across — hence NEEDS-REVIEW rather than DONE.
- **Target location (new org + seam):** src/Ankimon/pyobj/trainer_card.py on main (already seam-refactored to services.db + services.ui.notify + lazy leaderboard import). exp's refresh() and notify_stats_changed() call must be re-derived on top of main's version.
  - Seam wiring: exp still imports `from aqt import mw` and hits mw.ankimon_db directly; main already converted the whole class to services.db and services.ui.notify with a lazy ankimon_leaderboard import (headless-safe). The exp-only additions are: an on_gain_exp() call to singletons.notify_stats_changed() (QWebChannel live-update bridge) and a refresh() method reloading trainer.* settings — both are web-shell Profile/HUD support.
- **Class:** MIXED
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** singletons.notify_stats_changed (QWebChannel live-update bridge = web-shell SCAFFOLDING), web-shell HOST frame
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** exp still imports `from aqt import mw` and hits mw.ankimon_db directly; main already converted the whole class to services.db and services.ui.notify with a lazy ankimon_leaderboard import (headless-safe). The exp-only additions are: an on_gain_exp() call to singletons.notify_stats_changed() (QWebChannel live-update bridge) and a refresh() method reloading trainer.* settings — both are web-shell Profile/HUD support.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** notify_stats_changed itself is scaffolding (defined in exp singletons.py:269, best-effort try/except); the call site here is a thin hook. refresh() is Profile-screen (leaf) support. Only wire once the web-shell live-update bridge is classified/brought across by its owner. | GUARDS-TO-REAPPLY: main's lazy `from .ankimon_leaderboard import sync_data_to_leaderboard` inside try/except ImportError (headless/core-safe) must survive; services.ui.notify replacing showInfo in get_highest_level_pokemon/highest_pokemon_level

### F50 — Native Qt trainer/team windows removal (web-shell supersedes)
- **ID:** F50
- **Source location(s):** `src/Ankimon/gui_classes/choose_trainer_sprite_graphical.py`, `src/Ankimon/pyobj/trainer_card_window.py`, `src/Ankimon/gui_classes/pokemon_team_window.py`
- **Evidence tag:** [DIFF] · doc↔diff: EDIT-VS-DELETE COLLISION on pokemon_team_window.py: exp DELETES the file (-327) while main HEAVILY REWORKS it (+253/-48: replaces XP-share QComboBox with a 'Choose Pokémon with XP Share' picker dialog + CP calc). Applying exp's delete would destroy main's team-builder/XP-share rework. choose_trainer_sprite_graphical.py and trainer_card_window.py are clean-vs-delete (main untouched relative to MB but files exist). All three must be preserved in Stage A.
- **Target location (new org + seam):** Keep main's files as-is (all three still present on origin/main). exp's deletions are the front of a web-shell Profile/Team/Sprite-picker leaf and must NOT be applied in Stage A.
  - Seam wiring: No seam entrypoints introduced; these are pure deletions on exp side replacing native QWidget windows with web-shell screens.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
  - Escalation/ref: edit-vs-delete (pokemon_team_window.py main-edits/exp-deletes); needs delete-AUTHORIZATION in MERGE_ARCH_MAP.md before Stage B removes
- **Dependencies:** Web-Shell SCREENS (Profile / Team / trainer-sprite picker) — Stage-B leaves
- **Harness tier:** UI-ONLY
- **Parity strategy:** OBSERVABLE — characterization test / import+construct smoke
- **Seam-entrypoints-required:** No seam entrypoints introduced; these are pure deletions on exp side replacing native QWidget windows with web-shell screens.
- **Verification:** targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Significantly-inappropriate-if-applied: exp's deletion of pokemon_team_window.py collides with main's active edits (edit-vs-delete). Defer the web-shell replacement to Stage B and keep main's native windows.

### F51 — Encounter-display rewrite (TestWindow: persistent layout, mega/gmax names)
- **ID:** F51
- **Source location(s):** `src/Ankimon/pyobj/test_window.py`
- **Evidence tag:** [DIFF] · doc↔diff: main did not touch test_window.py; exp rewrites init_ui to a single persistent layout, adds _get_display_name for mega/gmax special forms, fixed window size/styling. Standalone HUD/encounter-display behavior = one Stage-B leaf.
- **Target location (new org + seam):** src/Ankimon/pyobj/test_window.py on main (main untouched vs MB); Stage-B encounter/HUD-display leaf. mw.* access should route through services/ui_port when ported.
  - Seam wiring: exp keeps `from aqt import mw` and uses mw.geometry(), mw.translator.translate, mw.catchpokemon/mw.defeatpokemon, mw.app clipboard indirectly. A Stage-B port would move mw.geometry/translator to ui_port and catch/defeat callbacks to the events/services seam.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** utils.is_alive (reload-safety), pokedex_functions.get_pretty_name_for_name (special-form naming = encounter overhaul)
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** exp keeps `from aqt import mw` and uses mw.geometry(), mw.translator.translate, mw.catchpokemon/mw.defeatpokemon, mw.app clipboard indirectly. A Stage-B port would move mw.geometry/translator to ui_port and catch/defeat callbacks to the events/services seam.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** Part of the encounter/special-forms overhaul (Megas/Gmax display). Leaf, defer. No main-side guard affected.

### F52 — StarterWindow reload-safety guard + captured_date fix
- **ID:** F52
- **Source location(s):** `src/Ankimon/pyobj/starter_window.py`
- **Evidence tag:** [DIFF] · doc↔diff: main untouched; exp adds a two-line is_alive guard and a captured_date bugfix. Trivial, but depends on the is_alive reload-safety helper which is scaffolding brought by another owner.
- **Target location (new org + seam):** src/Ankimon/pyobj/starter_window.py on main (main untouched vs MB); small fix rides with the starter/PC-refresh leaf.
  - Seam wiring: No mw.* change; wraps singletons.pokemon_pc.refresh_pokemon_grid() in `if is_alive(pokemon_pc)` (same reload-safety pattern as pokemon_trade) and sets captured_date to a real timestamp instead of None.
- **Class:** LEAF
- **Stage-A disposition:** DEFERRED-TO-STAGE-B
- **Dependencies:** utils.is_alive (reload-safe singleton guard = shared scaffolding), singletons.pokemon_pc
- **Harness tier:** GAMEPLAY
- **Parity strategy:** DETERMINISTIC/SEEDED — assert seed->golden output via harness Driver seed + event stream
- **Seam-entrypoints-required:** No mw.* change; wraps singletons.pokemon_pc.refresh_pokemon_grid() in `if is_alive(pokemon_pc)` (same reload-safety pattern as pokemon_trade) and sets captured_date to a real timestamp instead of None.
- **Verification:** harness Tier-2 real boot/play + targeted pytest for the ported module; base gate stays green
- **Notes / risks / guards:** captured_date=now() vs None is a genuine small bugfix; the is_alive wrap is a leaf-local application of shared reload-safety scaffolding. Low risk, but defer to keep Stage A leaf-free.
