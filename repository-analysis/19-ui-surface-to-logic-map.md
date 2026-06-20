# UI Surface to Logic Map

This document explains the structural bindings between the visual interfaces (Qt Windows, WebView overlay portals) and the underlying Python domain logic.

---

### 1. UI Architecture Overview

Ankimon uses a Web-Shell Centric UI paradigm:
1. **Reviewer HUD overlays:** Integrated directly into Anki's reviewer screen for real-time battle HUD panels (using Anki's standard `pycmd` bridge).
2. **Unified Web-Shell QDialog (`AnkimonItemsWeb`):** A single dialogue window hosting a `QStackedWidget` containing five loaded HTML5/QtWebEngine screens (**Items**, **Ankidex**, **Profile**, **Team**, and **Settings**), removing open/close flicker and rendering in a fast, fluid shell.
3. **Native Qt Windows:** Re-styled widgets like the PC Box grid (`PokemonPC`) and evolution transitions (`EvoWindow`).

```
                              ┌───────────────────────────────────┐
                              │       Anki Reviewer Window        │
                              │ ┌───────────────────────────────┐ │
                              │ │      Flashcard Web Page       │ │
                              │ │ ┌───────────────────────────┐ │ │
                              │ │ │    ankimon_hud_portal.js  │ │ │
                              │ │ └─────────────┬─────────────┘ │ │
                              │ └───────────────┼───────────────┘ │
                              └─────────────────┼─────────────────┘
                                                │ pycmd()
                                                ▼
                              ┌───────────────────────────────────┐
                              │       Ankimon Python Engine       │
                              │    (Reviewer_Manager / Singletons)│
                              └──────┬─────────────────────┬──────┘
                                     │                     │
                                     ▼                     ▼
                        ┌────────────────────────┐  ┌──────────────┐
                        │   AnkimonItemsWeb      │  │  PC Box Grid │
                        │  (Unified Web Shell)   │  │  (PokemonPC) │
                        │  - Items Bag & Mart    │  └──────────────┘
                        │  - Ankidex Discovery   │
                        │  - Profile & Badges    │
                        │  - Team Builder        │
                        │  - Web Settings        │
                        └────────────────────────┘
```

---

## 2. Web Shell QWebChannel Bridges

All screens embedded inside the unified web shell use `PyQt6.QtWebChannel` to communicate bi-directionally with the Python backend.

### Python Bridge Mappings (`ankimon_items_web/shop_obj.py`)
Each web view registers the same set of bridge handlers, allowing any screen to trigger navigation or read unified state:
```python
channel = QWebChannel(view)
channel.registerObject("bridge", self.bridge)           # ItemsBag & Mart operations
channel.registerObject("nav", self.nav)                 # Screen navigation switching
channel.registerObject("settings", self.settings_bridge)# Settings queries and saving
channel.registerObject("trainer", self.trainer_bridge)  # Profile data & sprite edits
channel.registerObject("team", self.team_bridge)        # Team builder roster actions
view.page().setWebChannel(channel)
```

### HTML/JS Bridge Setup (`nav-switcher.js`)
Frontend screens initialize the transport channel and attach bridge references on startup:
```javascript
new QWebChannel(qt.webChannelTransport, function (channel) {
    window.bridge = channel.objects.bridge;
    window.nav = channel.objects.nav;
    window.settings = channel.objects.settings;
    window.trainer = channel.objects.trainer;
    window.team = channel.objects.team;
});
```

---

## 3. Map of Core UI Components

### A. Reviewer HUD Portal (`ankimon_hud_portal.js` & `reviewer_ui.py`)
* **Visual Elements:** Left side represents the player Pokémon HP bar, level, and shiny status indicator; right side displays the active wild opponent.
* **Logical Bindings:** Health bars are mutated using `web.eval(f"updateHp({player_hp_pct}, {enemy_hp_pct})")` from Python; clicks send `pycmd("ankimon_action:...")` to the python reviewer listener.

### B. Unified Web Shell (`ankimon_items_web/` and `ankimon_profile_web/`)
* **Items Bag & Mart (`shop.html`):** Renders the inventory of held items and a daily re-rolling item shop. Integrates a smart target picker list directly into the shell for applying evolution stones.
* **Ankidex (`ankidex.html`):** Pokédex discovery chain map showing regional variant forms and caught stats.
* **Settings (`settings.html`):** Exposes settings categories inside a fast chip-row generation format. Validates configurations inside `settings_schema.py:validate_and_clamp()`.
* **Profile (`profile.html`):** Displays overall accomplishments, trainer statistics, unlocked badges, and contains the custom character sprite picker dialog.
* **Team Builder (`team.html`):** Allows dragging and dropping roster configurations, setting cycle limits, toggling animated sprites, and auditing active move indexes.
* **Mobile Reviews (`mobile.html` & `history.html`):** Renders State 1 (no reviews pending), State 2 (landing page with pending counts, ease breakdown, and roster selector), and State 3 (post-resolve summary showing XP, encounters, cash, trainer XP, and a detailed caught list). Supports Auto-Resolve (optimal team matchup selection based on moves, power, and speed matchup simulation) and Manual Replay (step-by-step resolution with full battle animations and a drop-down active companion override selector). Also hosts a **Battle History** tab (`history.html`) showing logs, companion levels, outcomes, and rewards for the last 200 resolved mobile battles. Communicates with `MobileBridge` to query statuses, handle batch dismissals, and deterministically run the battle resolution and reward calculations.


### C. PC Box Box Grid (`pyobj/pc_box.py`)
* **Visual Elements:** Native PyQt window displaying boxed inventory slots.
* **Logical Bindings:** Caches SQLite query data aggressively in memory so switching between boxes triggers zero additional database I/O.

### D. Evolution Window (`pyobj/evolution_window.py`)
* **Visual Elements:** Animated native transition modals showing level, stone, or move-based evolution checks.

### E. Menu Badge (`menu_buttons.py` & `update_mobile_badge`)
* **Visual Elements:** Displays a pending battle count suffix in the main Anki menu bar (e.g. `Ankimon ⚔47` or `Ankimon` when empty).
* **Logical Bindings:** Refreshes on sync finish, startup profile loaded, or battle resolution via `update_mobile_badge(count)`.
---

## 4. Live Updates and notify_stats_changed()

When an active gameplay action mutates character metrics (like capturing a Pokémon, level-ups, or receiving cash awards), Python notifies open shell views using the best-effort, deferred-coalesced refresh cascade:

```
[Catches / Level-up / Cash Awarded]
                │
                ▼
  singletons.notify_stats_changed()
                │
                ▼
  win.refresh_live_screen()  <--- coalesces multiple bursts into one turn
                │
                ▼
  _push_profile_live()  (e.g. if profile view is visible)
                │
                ▼
  runs JS: window.liveRefreshProfile(data) inside the QtWebEngineView page
```

---

## 5. Design Guidelines for UI Extensions

> [!IMPORTANT]
> When extending any UI component:
> 1. **Thread Safety:** Background `QueryOp` operations **MUST NEVER** access or mutate Qt GUI objects or trigger web-view signals directly. Always return dictionaries and run updates inside main-thread callbacks.
> 2. **Compositor Repaint Care:** Do not introduce heavy CSS filter options like `backdrop-filter: blur(...)` inside web sheets. These cause massive render-cycle glitches under Windows DWM.
> 3. **Bridge Validation:** Ensure all parameters received via QWebChannel slots are fully parsed and validated against schema domains prior to committing save actions.
