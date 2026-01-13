"""
Diagnostic command to identify infinite loops in medical/combat systems.
Use: diagnose_loop <character_name>
"""

from evennia import Command, search_object
from evennia.comms.models import ChannelDB
from world.combat.constants import SPLATTERCAST_CHANNEL

class CmdDiagnoseLoop(Command):
    """Diagnose infinite loops on a character."""
    
    key = "diagnose_loop"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: diagnose_loop <character_name>")
            return
        
        # Find target character
        targets = search_object(self.args)
        if not targets:
            caller.msg(f"Character '{self.args}' not found.")
            return
        
        target = targets[0]
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        caller.msg(f"|c=== DIAGNOSTICS FOR {target.key.upper()} ===|n")
        
        # 1. Check active scripts
        caller.msg("|y1. Active Scripts:|n")
        if hasattr(target, 'scripts'):
            all_scripts = target.scripts.all()
            if all_scripts:
                for script in all_scripts:
                    caller.msg(f"  - {script.key}: interval={getattr(script, 'interval', 'N/A')}, "
                             f"is_active={script.is_active}")
            else:
                caller.msg("  No scripts found.")
        else:
            caller.msg("  Target has no scripts attribute.")
        
        # 2. Check medical state
        caller.msg("|y2. Medical State:|n")
        if hasattr(target, 'medical_state'):
            ms = target.medical_state
            caller.msg(f"  Blood Level: {getattr(ms, 'blood_level', 'N/A')}")
            caller.msg(f"  Conditions: {len(getattr(ms, 'conditions', []))}")
            
            # List conditions
            for cond in getattr(ms, 'conditions', []):
                caller.msg(f"    - {cond.condition_type} (severity {cond.severity})")
        else:
            caller.msg("  No medical state found.")
        
        # 3. Check combat state
        caller.msg("|y3. Combat State:|n")
        if hasattr(target, 'ndb'):
            handler = getattr(target.ndb, 'combat_handler', None)
            if handler:
                caller.msg(f"  In Combat: Yes (handler={handler.key})")
                caller.msg(f"  Active: {handler.is_active}")
            else:
                caller.msg("  In Combat: No")
        
        # 4. Check NDB flags
        caller.msg("|y4. Temporary State Flags:|n")
        if hasattr(target, 'ndb'):
            ndb_dict = target.ndb.__dict__
            for key, value in ndb_dict.items():
                if not key.startswith('_'):
                    caller.msg(f"  {key}: {type(value).__name__}")
        
        # 5. Recommendations
        caller.msg("|y5. Recommendations:|n")
        if hasattr(target, 'scripts'):
            medical_scripts = [s for s in target.scripts.all() if 'medical' in s.key.lower()]
            if medical_scripts:
                for script in medical_scripts:
                    if script.is_active:
                        caller.msg(f"  |rWARNING: Medical script '{script.key}' is ACTIVE|n")
                        caller.msg(f"    Try: @script/stop {script.id}")
        
        caller.msg("|n|cEnd of diagnostics.|n")
