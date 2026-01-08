"""
Custom Say command that integrates voice descriptions.
"""

from evennia.commands.default.general import CmdSay as DefaultCmdSay


class CmdSay(DefaultCmdSay):
    """
    Speak as your character with optional voice description.
    
    Usage:
        say <message>
        "<message>
    
    If you have set a @voice, others will hear your speech as:
    *in a [voice description]* <message>
    
    Examples:
        say Hello there!
        "How are you?
    """
    
    def func(self):
        """Override say to include voice description."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Say what?")
            return
        
        speech = self.args
        
        # Check if character has a voice set
        voice = getattr(caller.db, 'voice', None)
        
        if voice:
            # Format message with voice
            message = f'|c{caller.name}|n says, "*in a {voice}* {speech}"|n'
            
            # Send to caller
            caller.msg(message)
            
            # Send to others in location
            if caller.location:
                caller.location.msg_contents(message, exclude=[caller])
        else:
            # No voice - use default behavior
            super().func()
