from evennia import Command
from evennia.comms.models import ChannelDB

class CmdThink(Command):
    """
    Externalize your character's thoughts. Sends to 'thoughts' channel.
    Usage:
        think <your thought>
    """
    key = "think"
    help_category = "Communication"

    def func(self):
        if not self.args:
            self.caller.msg("What do you want to think?")
            return
        thought = self.args.strip()
        # Show to user
        self.caller.msg(f"You think . o O ( {thought} )")
        # Send to thoughts channel
        channel = ChannelDB.objects.get_channel("thoughts")
        if channel:
            channel.msg(f"{self.caller.key}: {thought}")
        else:
            self.caller.msg("Thoughts channel not found.")

        # Send thought directly to anyone in room with Mind's Eye chrome installed
        location = self.caller.location
        if location:
            for obj in location.contents:
                if obj == self.caller or not hasattr(obj, 'ndb'):
                    continue
                installed = getattr(obj.ndb, 'installed_chrome', None)
                if not installed or not isinstance(installed, list):
                    continue
                if any(getattr(chrome, 'db', None) and getattr(chrome.db, 'shortname', None) == 'mindseye' for chrome in installed):
                    obj.msg(f"You overhear {self.caller.key}'s thoughts: {thought}")
