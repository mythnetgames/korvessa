"""
Skintone command for setting character appearance color.
"""

from evennia import Command


class CmdSkintone(Command):
    """
    Set your character's skintone for appearance descriptions.
    
    Usage:
        skintone <tone>  - Set your skintone
        skintone/list    - Show available skintones
    
    Available skintones:
        porcelain - Pure white
        pale      - Very pale with slight warmth
        fair      - Fair peachy tone
        light     - Light peach tone
        golden    - Golden tone
        tan       - Tan
        olive     - Olive undertone
        brown     - Brown
        rich      - Rich brown
    """
    key = "skintone"
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        if not self.args or self.args.lower() == "list":
            self.show_list(caller)
            return
        
        tone = self.args.strip().lower()
        self.set_skintone(caller, tone)
    
    def show_list(self, caller):
        """Show available skintones."""
        try:
            from world.combat.constants import SKINTONE_PALETTE
        except ImportError:
            caller.msg("|RSkintone system not available.|n")
            return
        
        current_tone = getattr(caller.db, 'skintone', None)
        
        msg = "|C=== Available Skintones ===|n\n"
        for tone_name, color_code in sorted(SKINTONE_PALETTE.items()):
            marker = " |G(current)|n" if tone_name == current_tone else ""
            msg += f"{color_code}{tone_name}|n{marker}\n"
        
        caller.msg(msg)
    
    def set_skintone(self, caller, tone):
        """Set the character's skintone."""
        try:
            from world.combat.constants import SKINTONE_PALETTE, VALID_SKINTONES
        except ImportError:
            caller.msg("|RSkintone system not available.|n")
            return
        
        if tone not in VALID_SKINTONES:
            caller.msg(f"|RUnknown skintone: {tone}|n")
            caller.msg(f"|CValid tones: {', '.join(sorted(VALID_SKINTONES))}|n")
            return
        
        caller.db.skintone = tone
        color_code = SKINTONE_PALETTE.get(tone, "")
        caller.msg(f"|GSkintone set to: {color_code}{tone}|n|n")
