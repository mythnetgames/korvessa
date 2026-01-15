"""
Set your preferred fighting style for grappling.

Lets you choose between Brawling (street fighting) and Martial Arts (trained combat)
for your grappling skill. The system will use whichever you set as your fighting style.
"""

from evennia.commands.command import Command


class CmdFightingStyle(Command):
    """
    Set your preferred fighting style for grappling.
    
    Usage:
        fightingstyle brawling       - Use brawling skill for grappling
        fightingstyle martial arts   - Use martial arts skill for grappling
        fightingstyle                - See your current fighting style
    
    Your fighting style determines which skill is used for grappling contests.
    """
    
    key = "fightingstyle"
    aliases = ["style", "fightstyle"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            # Show current fighting style
            style = getattr(caller.db, "fighting_style", "brawling") or "brawling"
            caller.msg(f"Your current fighting style: |y{style}|n")
            
            # Show skill levels
            brawling = getattr(caller.db, "brawling", 0) or 0
            martial_arts = getattr(caller.db, "martial_arts", 0) or 0
            caller.msg(f"  Brawling: |c{brawling}|n")
            caller.msg(f"  Martial Arts: |c{martial_arts}|n")
            return
        
        style_input = self.args.strip().lower()
        
        # Normalize input
        if style_input in ("brawling", "street", "fist", "unarmed"):
            new_style = "brawling"
        elif style_input in ("martial arts", "martial_arts", "trained", "traditional"):
            new_style = "martial_arts"
        else:
            caller.msg(f"|rUnknown fighting style: {self.args}|n")
            caller.msg("Available styles: |ybrawling|n, |ymarital arts|n")
            return
        
        # Set the fighting style
        caller.db.fighting_style = new_style
        
        # Get the skill level for the chosen style
        skill_level = getattr(caller.db, new_style, 0) or 0
        
        caller.msg(f"Your fighting style is now set to: |y{new_style}|n (skill level: |c{skill_level}|n)")
        caller.location.msg_contents(f"|y{caller.key}|n adjusts their fighting stance.", exclude=[caller])
