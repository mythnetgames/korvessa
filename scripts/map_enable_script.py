from evennia import DefaultScript
from evennia.accounts.models import AccountDB

class MapEnableScript(DefaultScript):
    """
    Script to force-enable mapper for all accounts at server start.
    """
    def at_script_creation(self):
        self.key = "map_enable_script"
        self.desc = "Enables mapper for all accounts on server start."
        self.persistent = True
        self.interval = None  # Run only once
        self.start_delay = True

    def at_start(self):
        # Set mapper_enabled for all accounts
        for account in AccountDB.objects.all():
            account.db.mapper_enabled = True
        self.stop()
