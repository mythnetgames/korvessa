"""
Control command for admins to force input for players and see the output.
"""

from evennia import Command
from evennia.utils.search import search_object

class CmdControl(Command):
    """
    Force a player to execute a command or input, and see their output.
    
    Usage:
        control <player> = <command>
    
    Example:
        control TestDummy = emote dances wildly
        control TestDummy = say Hello!
    
    The player will see the command as if they typed it, and the admin will see the output as well.
    """
    key = "control"
    locks = "cmd:perm(Immortal) or perm(Builder)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        if not self.args or '=' not in self.args:
            caller.msg("Usage: control <player> = <command>")
            return
        target_name, command = [part.strip() for part in self.args.split('=', 1)]
        if not target_name or not command:
            caller.msg("Usage: control <player> = <command>")
            return
        
        # Find the target
        targets = search_object(target_name)
        if not targets:
            caller.msg(f"No player found matching '{target_name}'.")
            return
        target = targets[0]
        
        # Save the original msg method
        orig_msg = target.msg
        output_buffer = []
        
        def intercept_msg(text=None, **kwargs):
            if text:
                output_buffer.append(str(text))
            return orig_msg(text, **kwargs)
        
        # Monkeypatch target's msg to intercept output
        target.msg = intercept_msg
        try:
            target.execute_cmd(command)
        finally:
            target.msg = orig_msg
        
        # Show output to admin
        if output_buffer:
            caller.msg(f"|w[CONTROL OUTPUT from {target.key}]:|n\n" + "\n".join(output_buffer))
        else:
            caller.msg(f"|w[CONTROL]:|n No output was produced.")
        
        # (No notification to the target; admin control is silent)
