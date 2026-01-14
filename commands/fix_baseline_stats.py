"""
Admin command to fix baseline_stats for existing characters.
Subtracts chrome bonuses from current stats to calculate baseline.
"""

from evennia import Command


class CmdFixBaselineStats(Command):
    """
    Fix baseline stats for a character by subtracting chrome bonuses.
    
    Usage:
        fixbaseline <character>
        
    This command calculates a character's baseline stats by subtracting
    all chrome bonuses from their current stats, then stores those
    baseline stats for future clone restoration.
    """
    
    key = "fixbaseline"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: fixbaseline <character>")
            return
        
        from evennia import search_object
        
        # Find the target character
        target = search_object(self.args.strip(), typeclass="typeclasses.characters.Character")
        if not target:
            self.caller.msg(f"Character '{self.args}' not found.")
            return
        
        target = target[0]
        
        # Get chrome bonuses
        chrome_bonuses = self._get_chrome_stat_bonuses(target)
        
        # Calculate baseline stats
        baseline_stats = {
            'body': getattr(target, 'body', 1) - chrome_bonuses.get('body', 0),
            'ref': getattr(target, 'ref', 1) - chrome_bonuses.get('ref', 0),
            'dex': getattr(target, 'dex', 1) - chrome_bonuses.get('dex', 0),
            'tech': getattr(target, 'tech', 1) - chrome_bonuses.get('tech', 0),
            'smrt': getattr(target, 'smrt', 1) - chrome_bonuses.get('smrt', 0),
            'will': getattr(target, 'will', 1) - chrome_bonuses.get('will', 0),
            'edge': getattr(target, 'edge', 1) - chrome_bonuses.get('edge', 0),
            'emp': getattr(target, 'emp', 1) - chrome_bonuses.get('emp', 0)
        }
        
        # Store baseline stats
        target.db.baseline_stats = baseline_stats
        
        # Report
        self.caller.msg(f"|gFixed baseline stats for {target.key}:|n")
        self.caller.msg(f"  Chrome bonuses: {chrome_bonuses}")
        self.caller.msg(f"  Baseline stats: {baseline_stats}")
        self.caller.msg("|yNote: Stats will revert to baseline on next death/clone.|n")
    
    def _get_chrome_stat_bonuses(self, character):
        """Calculate total stat bonuses from all installed chrome."""
        bonuses = {}
        
        # Stat name mapping
        stat_map = {
            "smarts": "smrt",
            "willpower": "will",
            "edge": "edge",
            "reflexes": "ref",
            "body": "body",
            "dexterity": "dex",
            "empathy": "emp",
            "technique": "tech",
        }
        
        # Get installed chrome list
        chrome_list = getattr(character.db, 'installed_chrome_list', None) or []
        
        for chrome_entry in chrome_list:
            shortname = chrome_entry.get("shortname", "")
            if not shortname:
                continue
            
            # Get chrome prototype
            proto = self._get_chrome_prototype(shortname)
            if not proto:
                continue
            
            # Add buffs from this chrome
            if proto.get("buffs") and isinstance(proto["buffs"], dict):
                for stat, bonus in proto["buffs"].items():
                    short_stat = stat_map.get(stat.lower(), stat)
                    bonuses[short_stat] = bonuses.get(short_stat, 0) + bonus
        
        return bonuses
    
    def _get_chrome_prototype(self, shortname):
        """Get chrome prototype definition by shortname."""
        try:
            from world import chrome_prototypes
            
            for name in dir(chrome_prototypes):
                obj = getattr(chrome_prototypes, name)
                if isinstance(obj, dict) and obj.get("shortname", "").lower() == shortname.lower():
                    return obj
        except ImportError:
            pass
        return None
