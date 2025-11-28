from evennia import Command

class CmdSpawnChrome(Command):
    """
    Spawn chrome (cybernetic augmentation) items for a character.
    Usage:
        spawnchrome <number> <chromeshortname>
    Example:
        spawnchrome 2 cyberarm
    Spawns the specified number of chrome items with the given shortname in your inventory.
    """
    key = "spawnchrome"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: spawnchrome <number> <chromeshortname>")
            return
        args = self.args.strip().split()
        if len(args) != 2:
            self.caller.msg("Usage: spawnchrome <number> <chromeshortname>")
            return
        number, chromeshortname = args
        try:
            number = int(number)
        except ValueError:
            self.caller.msg("Number must be an integer.")
            return
        if number < 1:
            self.caller.msg("Number must be at least 1.")
            return
        # Replace this with your actual chrome prototype lookup/creation logic
        for _ in range(number):
            # Example: create chrome item using Evennia's create_object
            # You may want to use prototypes or a chrome factory here
            chrome = self.caller.create_object("typeclasses.items.Item", key=chromeshortname)
            self.caller.msg(f"Spawned chrome: {chrome.key}")
