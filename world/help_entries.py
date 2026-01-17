"""
File-based help entries. These complements command-based help and help entries
added in the database using the `sethelp` command in-game.

Control where Evennia reads these entries with `settings.FILE_HELP_ENTRY_MODULES`,
which is a list of python-paths to modules to read.

A module like this should hold a global `HELP_ENTRY_DICTS` list, containing
dicts that each represent a help entry. If no `HELP_ENTRY_DICTS` variable is
given, all top-level variables that are dicts in the module are read as help
entries.

Each dict is on the form
::

    {'key': <str>,
     'text': <str>}``     # the actual help text. Can contain # subtopic sections
     'category': <str>,   # optional, otherwise settings.DEFAULT_HELP_CATEGORY
     'aliases': <list>,   # optional
     'locks': <str>       # optional, 'view' controls seeing in help index, 'read'
                          #           if the entry can be read. If 'view' is unset,
                          #           'read' is used for the index. If unset, everyone
                          #           can read/view the entry.

"""

HELP_ENTRY_DICTS = [
    {
        "key": "evennia",
        "aliases": ["ev"],
        "category": "General",
        "locks": "read:perm(Developer)",
        "text": """
            Evennia is a MU-game server and framework written in Python. You can read more
            on https://www.evennia.com.

            # subtopics

            ## Installation

            You'll find installation instructions on https://www.evennia.com.

            ## Community

            There are many ways to get help and communicate with other devs!

            ### Discussions

            The Discussions forum is found at https://github.com/evennia/evennia/discussions.

            ### Discord

            There is also a discord channel for chatting - connect using the
            following link: https://discord.gg/AJJpcRUhtF

        """,
    },
    {
        "key": "calendar",
        "aliases": ["months", "korvessan calendar", "common field reckoning"],
        "category": "General",
        "text": """
|cThe Korvessan Calendar - Common Field Reckoning|n

Korvessa uses a grounded, agrarian system of timekeeping known as the Common Field Reckoning. Time is measured by labor, harvest, and consequence rather than celestial events or divine perfection.

The year is divided into twelve months of thirty days each, for a total of 360 days. Years are counted in AH (After Herding).

|wMonths of the Year|n

|c 1. Plowbreak|n
   The ground softens enough to be worked. Plows break, animals strain, and labor resumes after scarcity. Early decisions made here shape the year.

|c 2. Seedwake|n
   Seed is sown while frost still threatens. Too early risks loss, too late risks hunger. This month defines hope and fear in equal measure.

|c 3. Sproutmere|n
   First green shoots appear. Growth begins, but so do weeds, pests, and theft. Optimism is cautious.

|c 4. Tallgrow|n
   Crops stretch high and require constant tending. Days are long, rest is scarce, and mistakes compound quickly.

|c 5. Sunpress|n
   Heat bears down on fields and people alike. Water grows precious. Illness spreads among laborers and livestock.

|c 6. Firstreap|n
   Early harvests begin. Barley and greens offer relief, but success here does not guarantee survival.

|c 7. Fullreap|n
   The primary harvest month. The outcome of the entire year is decided. Plenty or famine is set here.

|c 8. Stubblewake|n
   Fields are cut bare. Leftovers are gathered. Livestock graze the remains. Waste is remembered.

|c 9. Turnsoil|n
   Fields are worked again or abandoned. Long-term decisions are made. Regret often begins here.

|c10. Coldroot|n
   Root crops are pulled and cellars filled. Mistakes become visible. What was not stored will be missed.

|c11. Storethin|n
   Supplies begin to run low. Rations quietly shrink. Tempers shorten. Fear grows communal.

|c12. Lastseed|n
   Nothing remains to plant. Survival depends entirely on preparation. The year ends in endurance, not hope.

Months are commonly referenced in speech by implication rather than date, such as "late Fullreap" or "deep into Storethin".

See also: |chelp weekdays|n, |chelp holidays|n
        """,
    },
    {
        "key": "weekdays",
        "aliases": ["week", "turning", "six-day turning"],
        "category": "General",
        "text": """
|cThe Six-Day Turning|n

Korvessa does not observe a seven-day week or a day of rest. Instead, the week is a six-day cycle marking shifts in social expectation, scrutiny, and consequence. Labor continues every day, but actions carry different weight depending on the day.

|wWeekdays|n

|c1. Eveday|n
   The opening of the week. Plans are laid, journeys begun, and intentions revealed. What begins on Eveday is expected to be carried through. Breaking word given on this day marks one as unreliable.

|c2. Watchday|n
   Dedicated to the Watcher. Favored for oaths, inspections, testimony, and judgment. Truth is believed harder to hide. Those with secrets avoid notice.

|c3. Trialday|n
   Dedicated to the Three Children. A day of learning, first attempts, and forgivable failure. Apprentices are tested and new hands set to work. Effort matters more than outcome.

|c4. Velorday|n
   Dedicated to Velora, the Path of Order. A day for disciplined labor, repair, healing, and service. Work done carefully on this day is believed to endure.

|c5. Feyday|n
   Dedicated to Feyliks, the Path of Chance. Markets swell, games are played, and risks are taken. Fortune and disaster are equally expected. Boldness is admired.

|c6. Regaldy|n
   Dedicated to Regalus, the Path of Dominion. The final day of the week. Accounts are settled, punishments delivered, and authority enforced. Violence and decree on this day are seen as deliberate and carry greater consequence.

The next week begins immediately after Regaldy, without pause or rest.

See also: |chelp calendar|n, |chelp holidays|n
        """,
    },
    {
        "key": "holidays",
        "aliases": ["observances", "holy days", "religious holidays"],
        "category": "General",
        "text": """
|cKorvessan Religious and Superstitious Holidays|n

Each month holds three notable observances. These are not universal days of rest. They are days when behavior changes, risks are weighed differently, and the gods are acknowledged through restraint, effort, or fear.

Use the |ctime|n command to see if today is a holiday.

|wPlowbreak|n
  Day 3 - Turning Oath (Velora)
  Day 12 - The Watched Furrow (Watcher)
  Day 21 - The Uneven Line (Superstitious)

|wSeedwake|n
  Day 2 - Casting of Hands (Three Children)
  Day 11 - Held Seed (Watcher)
  Day 23 - Open Palm (Feyliks)

|wSproutmere|n
  Day 5 - Green Oath (Velora)
  Day 14 - Small Feet (Three Children)
  Day 26 - Watching Leaves (Watcher)

|wTallgrow|n
  Day 4 - Bound Work (Velora)
  Day 13 - Foolstep (Feyliks)
  Day 22 - The Quiet Mark (Superstitious)

|wSunpress|n
  Day 6 - Thirstcount (Watcher)
  Day 15 - Heat Mercy (Velora)
  Day 27 - Flygift (Superstitious)

|wFirstreap|n
  Day 1 - First Sheaf (Velora)
  Day 10 - Bread of Chance (Feyliks)
  Day 19 - Counted Silence (Watcher)

|wFullreap|n
  Day 3 - Open Field (Regalus)
  Day 16 - Measure True (Velora)
  Day 28 - Feast of Plenty (Feyliks)

|wStubblewake|n
  Day 7 - Gleaning Right (Three Children)
  Day 18 - Herd Turn (Superstitious)
  Day 25 - The Last Look (Watcher)

|wTurnsoil|n
  Day 4 - Second Claim (Regalus)
  Day 14 - Ashmark (Superstitious)
  Day 26 - Broken Spade (Velora)

|wColdroot|n
  Day 5 - Rootpull (Velora)
  Day 17 - Cellar Seal (Watcher)
  Day 24 - Mistwalk (Superstitious)

|wStorethin|n
  Day 6 - Short Measure (Regalus)
  Day 15 - Quiet Hearth (Watcher)
  Day 27 - Coin Turn (Feyliks)

|wLastseed|n
  Day 3 - Final Count (Watcher)
  Day 14 - Hard Night (Velora)
  Day 30 - Dominion Mark (Regalus)

See also: |chelp calendar|n, |chelp weekdays|n
        """,
    },
]

def create_doors_help():
    from evennia import create_help_entry
    text = (
        "|cDoors, Locks, and Keypads (Builder+)|n\n"
        "This helpfile describes how to use doors, locks, and combination keypad locks for exits.\n\n"
        "|wAttaching Components|n\n"
        "- |cattachdoor <direction>|n: Attach a door to an exit.\n"
        "- |cattachlock <direction>|n: Attach a lock to a door on an exit.\n"
        "- |cattachkeypad <direction>|n: Attach a keypad lock to a door on an exit.\n"
        "- |cbulkattach <component> <direction1> [direction2 ...]|n: Bulk attach doors/locks/keypads to multiple exits.\n\n"
        "|wProgramming Keypads|n\n"
        "- |cprogramkeypad <direction> <combo>|n: Set the keypad's 8-digit combination (default: 00000000).\n"
        "- |cshowcombo <direction>|n: Show the keypad combo (builder+ only).\n"
        "- |centercombo <direction> <combo>|n: Enter a combo to unlock a keypad lock.\n"
        "- |cpush <combo> on <direction>|n or |cpress <combo> on <direction>|n: Alternate ways to enter a combo on a keypad lock.\n"
        "- After 5 failed attempts, the keypad buzzes red and requires a 10-minute cooldown before further attempts.\n\n"
        "|wRemoving Components|n\n"
        "- |cremovedoor <direction>|n: Remove a door from an exit.\n"
        "- |cremovelock <direction>|n: Remove a lock from a door on an exit.\n"
        "- |cremovekeypad <direction>|n: Remove a keypad lock from a door on an exit.\n"
        "- |cbulkremove <component> <direction1> [direction2 ...]|n: Bulk remove doors/locks/keypads from multiple exits.\n\n"
        "|wDoor and Keypad State Commands|n\n"
        "- |copendoor <direction>|n: Open a door on an exit.\n"
        "- |cclosedoor <direction>|n: Close a door on an exit.\n"
        "- |clock <direction> [key]|n or |clock exit|n: Lock a door (requires key) or lock a keypad.\n"
        "- |cunlock <direction> [key]|n or |cunlock exit|n: Unlock a door (requires key) or unlock a keypad.\n"
        "- |cpress lock on <direction>|n: Lock a keypad lock on an exit.\n\n"
        "|wStatus and Customization|n\n"
        "- |cdoorstatus <direction>|n: Show status of door, lock, and keypad (builder+ only).\n"
        "- |csetdoormsg <direction> <type> <message>|n: Set custom open/close/lock/unlock messages for a door (builder+ only).\n\n"
        "|wUsage Notes|n\n"
        "- Only builder+ can attach/remove doors, locks, and keypads, or view/program keypad combos.\n"
        "- Keypads are programmable to any 8-digit code; default is 00000000.\n"
        "- All components can be attached/removed at any time by builder+.\n"
        "- Future hooks exist for electronic hacking of keypads.\n"
        "- Exits with closed/locked/keypad-locked doors will block movement until unlocked/opened.\n"
        "- All attach/remove/program actions are logged to the BuilderAudit channel.\n"
        "- Bulk operations allow fast management of multiple exits.\n"
        "- Key objects must match lock key_id to unlock doors.\n"
        "- After 5 failed attempts, keypad requires a 10-minute cooldown before further attempts.\n\n"
        "|wExample|n\n"
        "  attachdoor east\n"
        "  attachlock east\n"
        "  attachkeypad east\n"
        "  programkeypad east 12345678\n"
        "  showcombo east\n"
        "  entercombo east 12345678\n"
        "  push 12345678 on east\n"
        "  press 12345678 on east\n"
        "  opendoor east\n"
        "  closedoor east\n"
        "  lock east mykey\n"
        "  unlock east mykey\n"
        "  lock east\n"
        "  unlock east\n"
        "  press lock on east\n"
        "  doorstatus east\n"
        "  setdoormsg east open 'The heavy door swings open with a creak.'\n"
        "  bulkattach door north south east\n"
        "  bulkremove lock north south east\n"
        "  removedoor east\n"
        "  removelock east\n"
        "  removekeypad east\n\n"
        "See also: help building, help exits, help locks, help keys"
    )
    create_help_entry(
        key="doors",
        category="Building",
        entrytext=text,
        locks="view:perm(Builder)"
    )

# Autoload the doors help entry when this module is imported
try:
    create_doors_help()
except Exception as e:
    print(f"Error creating doors help entry: {e}")
