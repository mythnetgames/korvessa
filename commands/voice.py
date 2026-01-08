"""
Voice (@voice) command for setting character voice descriptions.

This command allows players to set a persistent description of their character's voice
that appears when they speak.
"""

from evennia import Command


class CmdVoice(Command):
    """
    Set a description of your character's voice.
    
    Usage:
        @voice me is <description>
        @voice                           (check current setting)
    
    This command sets a persistent description of how your character's voice sounds.
    When you speak, others will hear it described as "*in a [description]* [your speech]".
    
    The description should be 2-3 words accurately describing your voice. Valid endings
    include: Accent, Tone, Drawl, Voice, Rasp, and Cadence.
    
    Examples:
        @voice me is "thick Korean accented"
        @voice me is "slow southern drawl"
        @voice me is "disturbing arrhythmic cadence"
        @voice me is "ominous tone"
        @voice me is "squeaky feminine"
    
    Important:
        - Once set, your @voice cannot be cleared, only replaced with a new one
        - You can change your voice to disguise yourself, but should do so reasonably
          based on your character's disguise skills
        - If you have no disguise skill, hints of your original voice should remain
    """
    key = "voice"
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        
        # No arguments - show current voice
        if not self.args:
            current = getattr(caller.db, 'voice', None)
            if current:
                caller.msg(f"|GYour @voice:|n {current}")
            else:
                caller.msg("|YYou have no @voice set yet.|n")
            return
        
        args = self.args.strip()
        
        # Set voice - must have 'me is' separator
        if not args.lower().startswith("me is "):
            caller.msg("|RUsage: @voice me is <description>|n")
            return
        
        description = args[6:].strip()  # Skip "me is "
        
        # Remove quotes if present
        if (description.startswith('"') and description.endswith('"')) or \
           (description.startswith("'") and description.endswith("'")):
            description = description[1:-1].strip()
        
        if not description:
            caller.msg("|RYou must provide a voice description.|n")
            return
        
        self.set_voice(caller, description)

    def set_voice(self, caller, description):
        """Set the voice description."""
        caller.db.voice = description
        caller.msg(f"|GSet @voice:|n {description}")
