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
