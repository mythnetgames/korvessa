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
