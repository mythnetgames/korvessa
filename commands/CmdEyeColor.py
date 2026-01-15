"""
Eye Color command for setting character eye appearance with automatic nakeds override.
"""

from evennia import Command


class CmdEyeColor(Command):
    """
    Set your character's eye color.
    
    Usage:
        eyecolor <color>  - Set your eye color
        eyecolor list     - Show available eye colors
        eyecolor clear    - Clear your eye color (back to nakeds)
    
    When set, your eye color will automatically override any "eye" or "eyes" 
    text in your naked body part descriptions.
    
    Available colors:
        ice blue, steel, slate, blue, navy, green, hazel, brown, amber,
        gray, black, violet, crimson, gold
    """
    key = "eyecolor"
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        if not self.args or self.args.lower() == "list":
            self.show_list(caller)
            return
        
        if self.args.lower() == "clear":
            self.clear_eye_color(caller)
            return
        
        color = self.args.strip().lower()
        self.set_eye_color(caller, color)
    
    def show_list(self, caller):
        """Show available eye colors with previews."""
        try:
            from world.combat.constants import EYE_COLOR_PALETTE, VALID_EYE_COLORS
        except ImportError:
            caller.msg("|REye color system not available.|n")
            return
        
        current_color = getattr(caller.db, 'eye_color', None)
        
        msg = "|C=== Available Eye Colors ===|n\n"
        for color_name in sorted(EYE_COLOR_PALETTE.keys()):
            color_code = EYE_COLOR_PALETTE[color_name]
            marker = " |G(current)|n" if color_name == current_color else ""
            msg += f"  {color_code}{color_name}|n {marker}\n"
        
        caller.msg(msg)
    
    def set_eye_color(self, caller, color):
        """Set the character's eye color."""
        try:
            from world.combat.constants import EYE_COLOR_PALETTE, VALID_EYE_COLORS
        except ImportError:
            caller.msg("|REye color system not available.|n")
            return
        
        if color not in VALID_EYE_COLORS:
            caller.msg(f"|RUnknown eye color: {color}|n")
            caller.msg(f"|CValid colors: {', '.join(sorted(VALID_EYE_COLORS))}|n")
            return
        
        caller.db.eye_color = color
        color_code = EYE_COLOR_PALETTE.get(color, "")
        caller.msg(f"|GEye color set to: {color_code}{color}|n")
    
    def clear_eye_color(self, caller):
        """Clear eye color setting."""
        if hasattr(caller.db, 'eye_color') and caller.db.eye_color:
            delattr(caller.db, 'eye_color')
            caller.msg("|GEye color cleared. Back to naked descriptions.|n")
        else:
            caller.msg("|YYou have no eye color set.|n")
