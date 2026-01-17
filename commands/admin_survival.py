"""
Admin Commands for Testing and Debugging the Survival System

These commands allow staff to test hunger, thirst, intoxication, and other
survival system features.
"""

from evennia import Command
from evennia.utils.utils import inherits_from


class CmdSurvivalTest(Command):
    """
    Admin command to test survival system.
    
    Usage:
        @survivaltest [set_hunger|set_thirst|set_intoxication|set_con|status|clear] <value>
        
    Examples:
        @survivaltest set_hunger 6 - Set hunger to 6 hours ago
        @survivaltest set_thirst 18 - Set thirst to 18 hours ago
        @survivaltest set_intoxication 80 - Set intoxication to 80 (drunk)
        @survivaltest set_con 75 - Set Constitution to 75
        @survivaltest status - Show detailed survival status
        @survivaltest clear - Clear all survival state
        
    This is an admin-only debugging tool.
    """
    
    key = "@survivaltest"
    aliases = ["@survtest", "@survival"]
    help_category = "Admin"
    locks = "cmd:perm(Admin) or perm(Developers)"
    
    def func(self):
        """Execute the survival test command."""
        caller = self.caller
        
        # Default to self
        if not self.args:
            caller.msg("Usage: @survivaltest <command> [target] [value]")
            caller.msg("Commands: set_hunger, set_thirst, set_intoxication, set_con, status, clear")
            return
        
        args = self.args.split()
        command = args[0].lower()
        
        # Determine target character
        target = caller
        value = None
        
        if len(args) > 1:
            # Could be: target value, or just value
            if len(args) > 2:
                # Has both target and value
                target_search = caller.search(args[1])
                if not target_search:
                    caller.msg(f"Cannot find character '{args[1]}'.")
                    return
                target = target_search
                value = args[2]
            else:
                # Only one arg after command - could be target or value
                # Try to interpret as character first
                search_result = caller.search(args[1], quiet=True)
                if search_result:
                    target = search_result
                else:
                    # Treat as value for self
                    value = args[1]
        
        # Execute command
        from world.survival.core import (
            get_survival_state, save_survival_state,
            get_intoxication_level, get_intoxication_tier,
            INTOXICATION_TIERS, _get_constitution_modifier
        )
        import time
        
        if command == "status":
            self._show_status(caller, target)
        
        elif command == "clear":
            target.db.survival_state = None
            caller.msg(f"|gCleared survival state for {target.name}.|n")
        
        elif command == "set_hunger":
            if not value:
                caller.msg("Usage: @survivaltest set_hunger <hours>")
                return
            try:
                hours = int(value)
                state = get_survival_state(target)
                state["last_meal_time"] = time.time() - (hours * 3600)
                save_survival_state(target, state)
                caller.msg(f"|gSet {target.name}'s hunger to {hours} hours ago.|n")
            except ValueError:
                caller.msg(f"Invalid hours: {value}")
        
        elif command == "set_thirst":
            if not value:
                caller.msg("Usage: @survivaltest set_thirst <hours>")
                return
            try:
                hours = int(value)
                state = get_survival_state(target)
                state["last_drink_time"] = time.time() - (hours * 3600)
                save_survival_state(target, state)
                caller.msg(f"|gSet {target.name}'s thirst to {hours} hours ago.|n")
            except ValueError:
                caller.msg(f"Invalid hours: {value}")
        
        elif command == "set_intoxication":
            if not value:
                caller.msg("Usage: @survivaltest set_intoxication <level>")
                return
            try:
                level = int(value)
                level = max(0, min(200, level))
                state = get_survival_state(target)
                state["intoxication"] = level
                save_survival_state(target, state)
                
                tier = get_intoxication_tier(level)
                tier_desc = INTOXICATION_TIERS.get(tier, {}).get("description", tier)
                caller.msg(f"|gSet {target.name}'s intoxication to {level} ({tier_desc}).|n")
            except ValueError:
                caller.msg(f"Invalid intoxication level: {value}")
        
        elif command == "set_con":
            if not value:
                caller.msg("Usage: @survivaltest set_con <constitution>")
                return
            try:
                con = int(value)
                con = max(0, min(100, con))
                target.db.con = con
                modifier = _get_constitution_modifier(target)
                caller.msg(f"|gSet {target.name}'s CON to {con} (hunger timer multiplier: {modifier:.2f}x).|n")
            except ValueError:
                caller.msg(f"Invalid constitution: {value}")
        
        else:
            caller.msg(f"Unknown command: {command}")
            caller.msg("Commands: set_hunger, set_thirst, set_intoxication, set_con, status, clear")
    
    def _show_status(self, caller, target):
        """Show detailed survival status for a character."""
        from world.survival.core import (
            get_survival_state, is_hungry, is_thirsty, is_starving, is_dehydrated,
            get_intoxication_level, get_intoxication_tier, has_nutrition_bonus,
            get_nutrition_bonus_remaining, check_survival_effects,
            INTOXICATION_TIERS, _get_constitution_modifier
        )
        import time
        
        state = get_survival_state(target)
        if not state:
            caller.msg(f"No survival state for {target.name}.")
            return
        
        lines = [f"|c=== Survival Status for {target.name} ===|n"]
        
        # Constitution
        con = target.db.con or 50
        con_mod = _get_constitution_modifier(target)
        lines.append(f"Constitution: {con} (hunger multiplier: {con_mod:.2f}x)")
        
        # Hunger
        time_since_meal = time.time() - state["last_meal_time"]
        hours_since_meal = time_since_meal / 3600
        lines.append(f"Hunger: {hours_since_meal:.1f}h since last meal (hungry at {24 * con_mod:.1f}h)")
        lines.append(f"  Status: {'STARVING' if is_starving(target) else 'HUNGRY' if is_hungry(target) else 'FED'}")
        lines.append(f"  Starvation counter: {state.get('login_days_without_food', 0)} days")
        
        # Thirst
        time_since_drink = time.time() - state["last_drink_time"]
        hours_since_drink = time_since_drink / 3600
        lines.append(f"Thirst: {hours_since_drink:.1f}h since last drink (thirsty at {12 * con_mod:.1f}h)")
        lines.append(f"  Status: {'DEHYDRATED' if is_dehydrated(target) else 'THIRSTY' if is_thirsty(target) else 'HYDRATED'}")
        
        # Intoxication
        intox_level = get_intoxication_level(target)
        intox_tier = get_intoxication_tier(intox_level)
        tier_desc = INTOXICATION_TIERS.get(intox_tier, {}).get("description", intox_tier)
        lines.append(f"Intoxication: {intox_level} ({tier_desc})")
        
        # Nutrition bonus
        if has_nutrition_bonus(target):
            remaining = get_nutrition_bonus_remaining(target)
            mins = remaining / 60
            lines.append(f"Nutrition Bonus: Active ({mins:.0f} minutes remaining)")
        else:
            lines.append(f"Nutrition Bonus: None")
        
        caller.msg("\n".join(lines))


class CmdForceHunger(Command):
    """
    Admin command to force a character into hunger/thirst state.
    
    Usage:
        @forcehunger <character>
        @forcethirst <character>
        @forcestarving <character>
        @forcedehydrated <character>
        
    These instantly set the relevant time flags to trigger survival states.
    """
    
    key = "@forcehunger"
    aliases = ["@forcethirst", "@forcestarving", "@forcedehydrated"]
    help_category = "Admin"
    locks = "cmd:perm(Admin) or perm(Developers)"
    
    def func(self):
        """Execute the force hunger/thirst command."""
        caller = self.caller
        
        if not self.args:
            caller.msg(f"Usage: {self.cmdstring} <character>")
            return
        
        target = caller.search(self.args.strip())
        if not target:
            return
        
        from world.survival.core import get_survival_state, save_survival_state
        import time
        
        state = get_survival_state(target)
        
        if self.cmdstring.lower() == "@forcehunger":
            state["last_meal_time"] = time.time() - (25 * 3600)  # 25 hours ago
            caller.msg(f"|gForced {target.name} into hunger state.|n")
        
        elif self.cmdstring.lower() == "@forcethirst":
            state["last_drink_time"] = time.time() - (13 * 3600)  # 13 hours ago
            caller.msg(f"|gForced {target.name} into thirst state.|n")
        
        elif self.cmdstring.lower() == "@forcestarving":
            state["last_meal_time"] = time.time() - (100 * 3600)  # Way in the past
            state["login_days_without_food"] = 3  # Trigger starvation
            caller.msg(f"|gForced {target.name} into starvation state.|n")
        
        elif self.cmdstring.lower() == "@forcedehydrated":
            state["last_drink_time"] = time.time() - (25 * 3600)  # 25 hours ago
            caller.msg(f"|gForced {target.name} into dehydration state.|n")
        
        save_survival_state(target, state)


class CmdIntoxicate(Command):
    """
    Admin command to intoxicate a character for testing.
    
    Usage:
        @intoxicate <character> [level]
        
    Examples:
        @intoxicate bob - Set Bob to drunk (60)
        @intoxicate bob 150 - Set Bob to alcohol poisoning (150)
        @intoxicate bob sober - Sober up Bob
    """
    
    key = "@intoxicate"
    aliases = ["@sober"]
    help_category = "Admin"
    locks = "cmd:perm(Admin) or perm(Developers)"
    
    def func(self):
        """Execute the intoxicate command."""
        caller = self.caller
        args = self.args.split()
        
        if not args:
            caller.msg(f"Usage: {self.cmdstring} <character> [level|sober]")
            return
        
        target = caller.search(args[0])
        if not target:
            return
        
        from world.survival.core import (
            get_survival_state, save_survival_state,
            get_intoxication_tier, INTOXICATION_TIERS
        )
        
        state = get_survival_state(target)
        
        if len(args) > 1 and args[1].lower() == "sober":
            state["intoxication"] = 0
            caller.msg(f"|gSobered up {target.name}.|n")
        elif len(args) > 1:
            try:
                level = int(args[1])
                level = max(0, min(200, level))
                state["intoxication"] = level
                tier = get_intoxication_tier(level)
                tier_desc = INTOXICATION_TIERS.get(tier, {}).get("description", tier)
                caller.msg(f"|gSet {target.name}'s intoxication to {level} ({tier_desc}).|n")
            except ValueError:
                caller.msg(f"Invalid intoxication level: {args[1]}")
                return
        else:
            # Default to drunk if no level specified
            state["intoxication"] = 60
            caller.msg(f"|gSet {target.name} to drunk.|n")
        
        save_survival_state(target, state)
