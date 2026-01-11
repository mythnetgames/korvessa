"""
Test Dummy Commands - Create and manage test dummies for combat training.
"""

from evennia import Command, create_object
from evennia.utils.search import search_object


class CmdSpawnDummy(Command):
    """
    Spawn a test dummy for combat training.
    
    Usage:
        spawndummy [<name>]
        spawndummy <name> = <body>/<dex>/<reflex>/<tech>
    
    Creates a training dummy with optional custom stats.
    Stats range from 1-5 (default 3 for all).
    
    Examples:
        spawndummy
        spawndummy Training Dummy
        spawndummy Tough Dummy = 5/3/3/3
    """
    key = "spawndummy"
    aliases = ["spawn dummy", "dummy"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        # Parse arguments
        if "=" in self.args:
            # Format: name = stats
            parts = self.args.split("=", 1)
            name = parts[0].strip()
            stats_str = parts[1].strip()
            
            # Parse stats
            try:
                stats = [int(s.strip()) for s in stats_str.split("/")]
                if len(stats) != 4:
                    caller.msg("Stats format: body/dexterity/reflexes/technique")
                    return
                body, dex, reflex, tech = stats
                
                # Validate ranges
                for stat in [body, dex, reflex, tech]:
                    if stat < 1 or stat > 10:
                        caller.msg("Stats must be between 1 and 10.")
                        return
            except ValueError:
                caller.msg("Stats must be numbers. Format: body/dexterity/reflexes/technique")
                return
        else:
            # Default name and stats
            name = self.args.strip() or "Test Dummy"
            body, dex, reflex, tech = 3, 3, 3, 3
        
        # Create the dummy
        dummy = create_object(
            typeclass="typeclasses.test_dummy.TestDummy",
            key=name,
            location=caller.location,
            home=caller.location
        )
        
        # Set stats
        dummy.db.body = body
        dummy.db.dexterity = dex
        dummy.db.reflexes = reflex
        dummy.db.technique = tech
        
        caller.msg(f"|gSpawned {name} with stats: Body {body}, Dex {dex}, Reflex {reflex}, Technique {tech}|n")
        caller.location.msg_contents(
            f"|g{name} materializes in a hum of energy.|n",
            exclude=caller
        )


class CmdDummyStats(Command):
    """
    Adjust test dummy combat stats.
    
    Usage:
        dummystats <dummy> = <body>/<dex>/<reflex>/<tech>
        dummystats <dummy> = body:<value>
        dummystats <dummy> = dexterity:<value>
        dummystats <dummy> = reflexes:<value>
        dummystats <dummy> = technique:<value>
    
    Adjust the combat stats of a test dummy.
    
    Examples:
        dummystats Training Dummy = 5/3/3/3
        dummystats Training Dummy = body:5
        dummystats Training Dummy = dexterity:4
    """
    key = "dummystats"
    aliases = ["dummy stats"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: dummystats <dummy> = <stats>")
            return
        
        dummy_name, stats_str = self.args.split("=", 1)
        dummy_name = dummy_name.strip()
        stats_str = stats_str.strip()
        
        # Find the dummy
        dummies = search_object(dummy_name)
        if not dummies:
            caller.msg(f"No test dummy named '{dummy_name}' found.")
            return
        
        dummy = dummies[0]
        if not getattr(dummy.db, 'is_test_dummy', False):
            caller.msg(f"{dummy.key} is not a test dummy.")
            return
        
        # Parse stats
        if "/" in stats_str:
            # Format: body/dex/reflex/tech
            try:
                stats = [int(s.strip()) for s in stats_str.split("/")]
                if len(stats) != 4:
                    caller.msg("Stats format: body/dexterity/reflexes/technique")
                    return
                body, dex, reflex, tech = stats
                
                for stat in [body, dex, reflex, tech]:
                    if stat < 1 or stat > 10:
                        caller.msg("Stats must be between 1 and 10.")
                        return
                
                dummy.db.body = body
                dummy.db.dexterity = dex
                dummy.db.reflexes = reflex
                dummy.db.technique = tech
                
                caller.msg(f"|gUpdated {dummy.key}: Body {body}, Dex {dex}, Reflex {reflex}, Technique {tech}|n")
            except ValueError:
                caller.msg("Stats must be numbers. Format: body/dexterity/reflexes/technique")
                return
        
        elif ":" in stats_str:
            # Format: stat_name:value
            try:
                stat_name, value_str = stats_str.split(":", 1)
                stat_name = stat_name.strip().lower()
                value = int(value_str.strip())
                
                if value < 1 or value > 10:
                    caller.msg("Stats must be between 1 and 10.")
                    return
                
                stat_map = {
                    "body": "body",
                    "dex": "dexterity",
                    "dexterity": "dexterity",
                    "reflex": "reflexes",
                    "reflexes": "reflexes",
                    "tech": "technique",
                    "technique": "technique",
                }
                
                if stat_name not in stat_map:
                    caller.msg("Valid stats: body, dexterity, reflexes, technique")
                    return
                
                db_stat = stat_map[stat_name]
                setattr(dummy.db, db_stat, value)
                
                caller.msg(f"|gUpdated {dummy.key} {db_stat}: {value}|n")
            except ValueError:
                caller.msg("Value must be a number between 1 and 10.")
                return
        else:
            caller.msg("Format: stat_name:value or body/dex/reflex/tech")
            return


class CmdDummyHeal(Command):
    """
    Force heal a test dummy to full health.
    
    Usage:
        dummyheal <dummy>
    
    Immediately restores the dummy to full health regardless of injuries.
    Also resets to active status.
    
    Example:
        dummyheal Training Dummy
    """
    key = "dummyheal"
    aliases = ["dummy heal"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: dummyheal <dummy>")
            return
        
        # Find the dummy
        dummies = search_object(self.args.strip())
        if not dummies:
            caller.msg(f"No test dummy named '{self.args.strip()}' found.")
            return
        
        dummy = dummies[0]
        if not getattr(dummy.db, 'is_test_dummy', False):
            caller.msg(f"{dummy.key} is not a test dummy.")
            return
        
        # Full heal
        dummy.db.is_active = True
        if hasattr(dummy, 'medical_state') and dummy.medical_state:
            for organ in dummy.medical_state.organs.values():
                organ.current_hp = organ.max_hp
                organ.conditions.clear()
        
        dummy.override_place = None
        
        caller.msg(f"|g{dummy.key} has been fully healed.|n")
        if dummy.location:
            dummy.location.msg_contents(
                f"|g{dummy.key} hums, its damage fading away.|n",
                exclude=[caller]
            )


class CmdDummyInfo(Command):
    """
    View detailed information about a test dummy.
    
    Usage:
        dummyinfo <dummy>
    
    Shows the dummy's stats and current status.
    
    Example:
        dummyinfo Training Dummy
    """
    key = "dummyinfo"
    aliases = ["dummy info"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: dummyinfo <dummy>")
            return
        
        # Find the dummy
        dummies = search_object(self.args.strip())
        if not dummies:
            caller.msg(f"No test dummy named '{self.args.strip()}' found.")
            return
        
        dummy = dummies[0]
        if not getattr(dummy.db, 'is_test_dummy', False):
            caller.msg(f"{dummy.key} is not a test dummy.")
            return
        
        # Display info
        info = f"\n|c=== {dummy.key} ===|n\n"
        info += f"|wCombat Stats:|n\n"
        info += f"  Body: {dummy.db.body}\n"
        info += f"  Dexterity: {dummy.db.dexterity}\n"
        info += f"  Reflexes: {dummy.db.reflexes}\n"
        info += f"  Technique: {dummy.db.technique}\n"
        info += f"\n|wStatus:|n "
        if dummy.db.is_active:
            info += "|gActive|n - Ready for combat\n"
        else:
            info += "|rInactive|n - Recovering\n"
        
        info += f"\n|wLocation:|n {dummy.location}\n"
        
        caller.msg(info)
