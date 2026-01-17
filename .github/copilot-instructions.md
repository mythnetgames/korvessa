## Repo orientation for AI coding agents

This file gives targeted, actionable guidance to make an AI coding agent productive in this codebase quickly.

- **Project type**: Evennia-based Python MUD with heavy custom systems (combat, medical, messages). See [README.md](README.md) and [AGENTS.md](AGENTS.md) for full context.

- **High-level hotspots**:
  - Combat system: [world/combat/](world/combat/) (handler, constants, proximity, grappling, messages)
  - Combat commands: [commands/combat/](commands/combat/)
  - Core game objects: [typeclasses/](typeclasses/)
  - Medical system: [world/medical/](world/medical/)
  - Server config: [server/conf/](server/conf/)

- **Key design assumptions to preserve**:
  - Combat is implemented as an Evennia `DefaultScript` (`CombatHandler` in world/combat/handler.py). Do not refactor the handler to a request-driven model without coordinating state migration.
  - Many behaviors rely on NDB transient fields (e.g., `combat_handler`, `in_proximity_with`, `aiming_at`). Use `hasattr(obj.ndb, ...)` patterns used elsewhere and clean up fields on character removal.
  - Messaging is weapon-driven: add new weapon messages by creating a module in world/combat/messages/ exporting a `MESSAGES` dict with `initiate|hit|miss|kill` variants.

- **Common code patterns to follow** (copy these patterns rather than inventing new ones):
  - Handler lifecycle: use `get_or_create_combat(location)`, `handler.add_combatant(...)`, then `handler.start()`.
  - Constants-first: reference values from world/combat/constants.py (avoid magic strings for NDB/DB keys).
  - Message sending: use `get_combat_message()` and send `attacker_msg`, `victim_msg`, and `observer_msg` separately.

- **Where to change behaviour (examples)**:
  - Add a new weapon message: add file `world/combat/messages/<weapon>.py` with a `MESSAGES` dict. See the `unarmed` message file for shape.
  - Add a combat command: add to `commands/combat/` and register it via the commandset in `commands/combat/default_cmdsets.py`.
  - Modify grapple rules: edit `world/combat/grappling.py` and update cleanup in handler to keep `grappling_dbref` / `grappled_by_dbref` consistent.

- **Debugging & observability**:
  - The project uses a debug channel called `Splattercast` for operational logs. Tests and scripts send messages there; prefer using that channel for high-level state dumps.
  - Useful quick-inspection helpers live in `world/combat/*` (debug helper functions described in [AGENTS.md](AGENTS.md)).

- **Developer workflows**:
  - Run tests: `python -m pytest -q` from repository root.
  - Local server: follow Evennia workflow: `evennia migrate` then `evennia start` (see [README.md](README.md)).
  - Docker: `docker-compose up` is available at the repo root for containerized environments.

- **Files worth reading first (order matters)**:
  1. [AGENTS.md](AGENTS.md) — combat architecture and rules
  2. [world/combat/handler.py](world/combat/handler.py) — main loop and lifecycle
  3. [world/combat/constants.py](world/combat/constants.py) — canonical keys and defaults
  4. [world/combat/messages/](world/combat/messages/) — messaging templates and examples
  5. [commands/combat/](commands/combat/) — how players invoke systems

- **Project-specific gotchas**:
  - NEVER USE EMOJI, curly quotes, or em-dashes in messages (AGENTS.md top-line rule).
  - Many features rely on persistent DB fields paired with transient NDB state; ensure cleanup code runs on exit paths to avoid stale references.
  - There are 95+ weapon message templates; keep new templates consistent with three-perspective formatting.

- **When to run the tests vs. run a local server**:
  - Unit-level changes (utils, small refactors): run `pytest`.
  - Integration behavior involving scripts/handlers or channels: run Evennia locally and exercise interactions in-game or with automated integration tests.

- **If you are making wide changes**:
  - Add small, focused tests next to failing behavior (project already has tests like `test_grapple_disguise.py`).
  - Preserve public DB keys in `constants.py` and provide a migration plan if you must rename them.

If any of these areas are unclear or you want the instructions expanded with concrete code snippets or tests, tell me which section to expand.
